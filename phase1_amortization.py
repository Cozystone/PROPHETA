# -*- coding: utf-8 -*-
"""PROPHETA Phase 1 — does the term dictionary AMORTIZE toward ~14 B/triple at scale?

The size claim rests on terms/triple dropping as more triples share the same terms. But
Q-id subjects/objects amortize well while literal values (dates, quantities, strings) do
not. This de-risks the claim empirically: ingest in stages, log B/triple at checkpoints.
Honest — if it plateaus above 14, we say so and lean on binary hashing instead.
"""
from __future__ import annotations
import io, json, sys, time, urllib.request, urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ATANOR = Path("C:/0.ASKIM ALL-VIN/27., ATANOR DEMO")
sys.path.insert(0, str(ATANOR)); sys.path.insert(0, str(ATANOR / "apps" / "api"))
for _d in sorted((ATANOR / "packages").iterdir(), reverse=True):
    if (_d / "pyproject.toml").exists() or (_d / _d.name / "__init__.py").exists():
        if str(_d) not in sys.path:
            sys.path.insert(0, str(_d))
from packages.graph_scale.triple_store import TripleStore  # noqa: E402

API = "https://www.wikidata.org/w/api.php"
UA = {"User-Agent": "ATANOR-PROPHETA/0.0 (research; blueyjkim@gmail.com)"}
CHECKPOINTS = [500, 1000, 2000, 3500]


def _fetch(qids):
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(qids),
                                "format": "json", "props": "claims"})
    with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA), timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore")).get("entities", {})


def _triples(qid, ent):
    for pid, claims in (ent.get("claims") or {}).items():
        for c in claims:
            dv = ((c or {}).get("mainsnak") or {}).get("datavalue") or {}
            v = dv.get("value")
            if v is None:
                continue
            obj = (v.get("id") or v.get("time") or v.get("amount") or v.get("text")
                   or (f"{v.get('latitude')},{v.get('longitude')}" if isinstance(v, dict) and "latitude" in v else None)) \
                if isinstance(v, dict) else v
            if obj:
                yield (qid, pid, str(obj))


def _bpt(store_dir, triples):
    on = sum(f.stat().st_size for f in store_dir.rglob("*") if f.is_file())
    terms = (store_dir / "terms.txt").stat().st_size if (store_dir / "terms.txt").exists() else 0
    return on / max(1, triples), terms / max(1, triples)


def main():
    d = Path(__file__).resolve().parent / "_phase1_store"
    for f in d.glob("*"):
        try: f.unlink()
        except Exception: pass
    d.mkdir(exist_ok=True)
    store = TripleStore(d, write_src=False)
    got = trip = qn = 0
    print(f"{'entities':>8} {'triples':>9} {'B/triple':>9} {'terms/tri':>10}")
    ci = 0
    while ci < len(CHECKPOINTS):
        ids = [f"Q{qn + i + 1}" for i in range(50)]; qn += 50
        try:
            ents = _fetch(ids)
        except Exception:
            time.sleep(1); continue
        for qid, ent in ents.items():
            if "claims" not in ent:
                continue
            rows = list(_triples(qid, ent))
            if not rows:
                continue
            got += 1
            for s, p, o in rows:
                store.add(s, p, o); trip += 1
        if got >= CHECKPOINTS[ci]:
            store.flush()
            b, t = _bpt(d, trip)
            print(f"{got:8d} {trip:9d} {b:9.1f} {t:10.1f}", flush=True)
            ci += 1
        time.sleep(0.05)
    print("\nverdict: terms/triple trend across scale ↑ tells whether pure amortization reaches ~14,")
    print("or binary hashing of the value space is required for the last step to ~6.5GB.")


if __name__ == "__main__":
    main()
