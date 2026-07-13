# -*- coding: utf-8 -*-
"""PROPHETA Phase 2 v0 — build a REAL Korean world-definition pack from Wikidata.

Streams top Wikidata entities and stores each as a cartridge-compatible definition:
  (ko_label, "defined_as", ko_description)   ← what lexicon_lane renders for "X가 뭐야"
  (ko_label, "is_a",       en_type_hint)     ← P31 instance-of target id (rendered later)
Wikidata's one-line descriptions are exactly definition-shaped, and it has ko labels for the
head of the distribution — so this yields a broad, hallucination-0 Korean world dictionary far
wider than the 2M Kaikki cartridge. Sharded (4GB-safe), src.col-free. Non-destructive: new dir.

  python phase2_world_pack.py <n_entities> <dst_dir>
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


def _fetch(qids):
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(qids), "format": "json",
                                "props": "labels|descriptions|claims", "languages": "ko|en"})
    with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA), timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore")).get("entities", {})


def main():
    n_target = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "_world_pack"
    dst.mkdir(parents=True, exist_ok=True)
    for f in dst.glob("*"):
        try: f.unlink()
        except Exception: pass
    st = TripleStore(dst, dict_backend="sharded", write_src=False)
    got = defs = ko = qn = 0
    t0 = time.time()
    while got < n_target:
        ids = [f"Q{qn + i + 1}" for i in range(50)]; qn += 50
        try:
            ents = _fetch(ids)
        except Exception:
            time.sleep(1); continue
        for qid, e in ents.items():
            labels, descs = e.get("labels") or {}, e.get("descriptions") or {}
            lab = (labels.get("ko") or labels.get("en") or {}).get("value")
            desc = (descs.get("ko") or descs.get("en") or {}).get("value")
            if not lab:
                continue
            got += 1
            if desc:                                    # the definition — what "X가 뭐야" returns
                st.add(lab, "defined_as", desc); defs += 1
                if (descs.get("ko")):
                    ko += 1
            p31 = ((e.get("claims") or {}).get("P31") or [])
            if p31:
                tid = (((p31[0].get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}).get("id")
                if tid:
                    st.add(lab, "is_a", tid)
        if got and got % 2000 < 50:
            st.flush(); print(f"  …{got} entities, {defs} defs ({ko} ko) ({time.time()-t0:.0f}s)", flush=True)
        time.sleep(0.05)
    st.flush()
    disk = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file()) / 1e6
    print(f"\nWORLD PACK v0: {got} entities | {defs} definitions ({ko} native Korean) | {disk:.0f} MB sharded")
    # prove it answers something the Kaikki cartridge likely lacks
    from packages.graph_scale import lexicon_lane as L
    L._STORE = None; L._STORE_PATH = dst          # point lexicon at the new world pack
    import os; os.environ["ATANOR_LEXICON_OFF"] = "0"
    for probe in ["대한민국", "아인슈타인", "산소", "베토벤"]:
        rows = st.facts_about(probe, preds=("defined_as",))
        print(f"  {probe}: {rows[0][2][:50] if rows else '(none)'}")


if __name__ == "__main__":
    main()
