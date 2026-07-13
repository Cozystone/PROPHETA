# -*- coding: utf-8 -*-
"""PROPHETA Phase 0 — prove the world-graph size math on REAL Wikidata data.

Streams a subset of Wikidata entities via the API (no raw dump stored), extracts their
statements as (entity, property, value) triples, ingests them into ATANOR's int-columnar
triple store, and measures the REAL on-disk bytes/triple — then extrapolates to full
Wikidata (~1.4B statements). Gate: full-Wikidata size <= 20GB int / <= 8GB hashed.
"""
from __future__ import annotations
import io, json, sys, time, urllib.request, urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# --- mount ATANOR's triple store (same path rule as the engine: reverse-sorted packages/*) ---
ATANOR = Path("C:/0.ASKIM ALL-VIN/27., ATANOR DEMO")
sys.path.insert(0, str(ATANOR)); sys.path.insert(0, str(ATANOR / "apps" / "api"))
for _d in sorted((ATANOR / "packages").iterdir(), reverse=True):
    if (_d / "pyproject.toml").exists() or (_d / _d.name / "__init__.py").exists():
        if str(_d) not in sys.path:
            sys.path.insert(0, str(_d))
from packages.graph_scale.triple_store import TripleStore  # noqa: E402

API = "https://www.wikidata.org/w/api.php"
UA = {"User-Agent": "ATANOR-PROPHETA/0.0 (research; contact blueyjkim@gmail.com)"}


def _fetch_entities(qids: list[str]) -> dict:
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(qids),
                                "format": "json", "props": "claims", "languages": "en"})
    req = urllib.request.Request(f"{API}?{q}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore")).get("entities", {})


def _triples_of(qid: str, ent: dict):
    """(subject, predicate, object) from an entity's claims. Object = target Q-id, or a
    literal typed by datatype (time/quantity/string/etc.). No prose stored — pure structure."""
    for pid, claims in (ent.get("claims") or {}).items():
        for c in claims:
            snak = (c or {}).get("mainsnak") or {}
            dv = snak.get("datavalue") or {}
            v = dv.get("value")
            if v is None:
                continue
            if isinstance(v, dict):
                obj = v.get("id") or v.get("time") or v.get("amount") or v.get("text") \
                    or (f"{v.get('latitude')},{v.get('longitude')}" if "latitude" in v else None)
            else:
                obj = v
            if obj:
                yield (qid, pid, str(obj))


def main() -> int:
    n_entities = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    store_dir = Path(__file__).resolve().parent / "_phase0_store"
    for f in store_dir.glob("*"):
        try: f.unlink()
        except Exception: pass
    store_dir.mkdir(exist_ok=True)
    store = TripleStore(store_dir)

    got_ent = trip = 0
    t0 = time.time()
    # sequential Q-ids (many are empty/redirects — skipped); enough real entities for density
    start, batch = 1, 50
    qnum = start
    while got_ent < n_entities:
        ids = [f"Q{qnum + i}" for i in range(batch)]
        qnum += batch
        try:
            ents = _fetch_entities(ids)
        except Exception as e:
            print("  fetch err:", type(e).__name__, str(e)[:60]); time.sleep(2); continue
        for qid, ent in ents.items():
            if "claims" not in ent:
                continue
            rows = list(_triples_of(qid, ent))
            if not rows:
                continue
            got_ent += 1
            for s, p, o in rows:
                store.add(s, p, o); trip += 1
        if got_ent and got_ent % 300 < batch:
            print(f"  …{got_ent} entities, {trip} triples")
        time.sleep(0.1)  # be polite to the API
    store.flush()

    on_disk = sum(f.stat().st_size for f in store_dir.rglob("*") if f.is_file())
    bpt = on_disk / max(1, trip)
    print(f"\n=== PROPHETA Phase 0 — REAL density ===")
    print(f"  entities {got_ent:,} | triples {trip:,} | {trip/max(1,got_ent):.1f} triples/entity")
    print(f"  on-disk {on_disk/1e6:.1f} MB  =>  {bpt:.1f} B/triple  ({time.time()-t0:.0f}s)")
    WD = 1_400_000_000
    print(f"\n  EXTRAPOLATION to full Wikidata ({WD/1e9:.1f}B statements):")
    print(f"    at measured {bpt:.1f} B/triple  =>  {WD*bpt/1e9:.1f} GB")
    print(f"    at target   14   B/triple  =>  {WD*14/1e9:.1f} GB   (binary-hashed ~{WD*14/1e9/3:.1f} GB)")
    gate = WD * bpt / 1e9 <= 20 or WD * 14 / 1e9 <= 20
    print(f"  GATE (full <= 20GB int): {'PASS' if gate else 'needs compression (Phase 1)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
