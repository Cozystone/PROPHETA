# -*- coding: utf-8 -*-
"""PROPHETA Phase 1 — density on a RANDOM entity sample (not low-Q hubs).

The plateau at 9.8 terms/triple came from Q1…Q3600 — the most heavily-documented hub
entities (dense literal statements). The AVERAGE Wikidata entity is sparse (a few Q-id
relations). Sampling random Q-ids gives the honest full-Wikidata average density — the
right number to extrapolate the pack size. Could revise 30GB up OR down; we report what
the data says.
"""
from __future__ import annotations
import io, json, random, sys, time, urllib.request, urllib.parse
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


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    d = Path(__file__).resolve().parent / "_phase1_rand"
    for f in d.glob("*"):
        try: f.unlink()
        except Exception: pass
    d.mkdir(exist_ok=True)
    store = TripleStore(d, write_src=False)
    random.seed(7)
    got = trip = 0
    literal_terms = qid_terms = 0
    seen_terms: set[str] = set()
    while got < target:
        ids = [f"Q{random.randint(1, 100_000_000)}" for _ in range(50)]   # random across the space
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
                if o not in seen_terms:
                    seen_terms.add(o)
                    if o[:1] == "Q" and o[1:].isdigit():
                        qid_terms += 1
                    else:
                        literal_terms += 1
        time.sleep(0.05)
    store.flush()
    on = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
    print(f"\n=== RANDOM sample (true Wikidata average) ===")
    print(f"  entities {got} | triples {trip} | {trip/max(1,got):.1f} triples/entity (hubs were 280!)")
    print(f"  B/triple {on/max(1,trip):.1f}  |  unique objects: {qid_terms} Q-ids, {literal_terms} literals")
    WD = 1_400_000_000
    print(f"  full Wikidata @ {on/max(1,trip):.1f} B/triple => {WD*(on/max(1,trip))/1e9:.1f} GB int")


if __name__ == "__main__":
    main()
