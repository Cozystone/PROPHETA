# -*- coding: utf-8 -*-
"""PROPHETA — rebuild a `ram`-backend triple store into a `sharded` (on-disk-dict) pack.

The shipped 2M cartridge uses dict_backend="ram", which loads its whole 10.2M-term vocabulary
into RAM (+1.48 GB, measured). Rebuilding it sharded keeps the vocab on disk (RAM bounded to an
LRU shard cache) — the ~1.4 GB win that lets a world-graph pack fit a 4GB laptop. Non-destructive:
writes a NEW dir; the caller verifies, then swaps.

  python rebuild_sharded.py <src_store_dir> <dst_store_dir>
"""
from __future__ import annotations
import io, sys, time
from pathlib import Path
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ATANOR = Path("C:/0.ASKIM ALL-VIN/27., ATANOR DEMO")
sys.path.insert(0, str(ATANOR)); sys.path.insert(0, str(ATANOR / "apps" / "api"))
for _d in sorted((ATANOR / "packages").iterdir(), reverse=True):
    if (_d / "pyproject.toml").exists() or (_d / _d.name / "__init__.py").exists():
        if str(_d) not in sys.path:
            sys.path.insert(0, str(_d))
from packages.graph_scale.triple_store import TripleStore  # noqa: E402


def rebuild(src: Path, dst: Path) -> tuple[int, int]:
    """Stream every (s,p,o) from a ram store into a fresh sharded, src.col-free store."""
    terms = (src / "terms.txt").read_text(encoding="utf-8").splitlines()   # line N == id N
    scol = np.memmap(src / "s.col", dtype="<i4", mode="r")
    pcol = np.memmap(src / "p.col", dtype="<i4", mode="r")
    ocol = np.memmap(src / "o.col", dtype="<i4", mode="r")
    n = len(scol)
    dst.mkdir(parents=True, exist_ok=True)
    for f in dst.glob("*"):
        try: f.unlink()
        except Exception: pass
    out = TripleStore(dst, dict_backend="sharded", write_src=False)
    t0 = time.time()
    for i in range(n):
        out.add(terms[scol[i]], terms[pcol[i]], terms[ocol[i]])
        if i and i % 200000 == 0:
            out.flush(); print(f"  …{i:,}/{n:,} ({time.time()-t0:.0f}s)", flush=True)
    out.flush()
    return n, len(terms)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: rebuild_sharded.py <src_store> <dst_store>"); return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    n, t = rebuild(src, dst)
    src_sz = sum(f.stat().st_size for f in src.rglob("*") if f.is_file()) / 1e6
    dst_sz = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file()) / 1e6
    print(f"rebuilt {n:,} triples / {t:,} terms")
    print(f"  src (ram)     {src_sz:8.1f} MB")
    print(f"  dst (sharded) {dst_sz:8.1f} MB  — vocab now on disk, RAM bounded on load")
    # spot-check a few subjects round-trip
    a, b = TripleStore(src), TripleStore(dst)
    import random
    terms = (src / "terms.txt").read_text(encoding="utf-8").splitlines()
    subs = [x for x in random.sample(terms, min(200, len(terms))) if x[:1] in "QP"]
    ok = sum(1 for s in subs if a.facts_about(s) == b.facts_about(s))
    print(f"  round-trip verify: {ok}/{len(subs)} subjects identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
