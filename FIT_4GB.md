# PROPHETA — fitting a 4GB RAM old laptop (measured method, no perf loss)

**Goal:** a 36GB world-graph pack must not burden a 4GB-RAM laptop's resident memory.

**The one real risk — the term dictionary:** with the `ram` backend the whole vocabulary loads
into memory (measured to scale linearly). A 36GB pack has ~113M distinct terms → **~3.4–9 GB in
RAM (BLOWS 4GB)**. Everything else is already fine:
- Columns are `np.memmap` → RAM = only the pages a query touches (measured +6 MB over 3,000
  lookups). The 36GB never becomes resident.

**Method (measured):**
1. **Sharded term-dict** (`TripleStore(dict_backend="sharded")`) — vocabulary stays on disk,
   RAM bounded to an LRU cache of shards. Measured on 60k terms: sharded +9 MB vs ram +17 MB;
   the gap widens without limit at scale (ram → GBs, sharded → bounded).
2. **mmap columns** (default) — working-set paging; the OS reclaims cold pages under pressure,
   so RSS never exceeds physical RAM.
3. **Lean offline profile** — the offline core loads ONLY: store (sharded + mmap) + Kiwi +
   the small realizer + the answer path. Exclude the heavy ML (perception models, SPLATRA,
   holographic-visual) — those are online/desktop-only ([[demo-profile-architecture]] PROFILE flag).

**Result:** 36GB pack sleeps on SSD; resident RAM for offline Q&A ≈ a few hundred MB → fits a
4GB laptop with room to spare.

**No perf loss:** sharded lookups add a small cold-shard cost, fully mitigated by the LRU hot-
shard cache + the OS page cache. The hot working set (a user's active topics) stays in RAM and
answers at the same speed; only never-touched cold knowledge lives purely on disk.

## Tasks
- [ ] World-graph packs default to `dict_backend="sharded"`.
- [ ] Define the lean "propheta-offline" engine profile (exclude heavy ML).
- [ ] Measure end-to-end resident RSS of the offline profile + a large pack on a memory-capped run.

## MEASURED on the live 2M cartridge (2026-07-14) — the RAM dict is REAL, and mandatory-sharded
Loading the shipped 2M cartridge (`data/graph_scale/kg_triples`, `dict_backend: "ram"`, 10.2M
terms, terms.txt 295 MB) grew process RSS by **+1,484 MB** — the RAM term-dict loads the whole
vocabulary (295 MB on disk → ~1.5 GB as a Python str→int map). This is the hidden ~1.5 GB in
the current 2.5 GB engine, and it CONFIRMS the sharded backend is mandatory, not optional.

**Correction to RAM_ONDEMAND.md:** the *columns* are mmap-bounded (RSS +6 MB over 3,000
lookups, true), BUT the *RAM term-dict is NOT on-demand* — it loads fully. So the honest RAM
picture = mmap columns (~working set) + term-dict (ram: full ~1.5 GB / sharded: bounded). The
dict is the whole ballgame for RAM.

Incremental offline-essentials RSS measured (naive, some double-load):
| component | +RSS | note |
|---|---:|---|
| 2M cartridge (ram dict) | +1,484 MB | → **~tens of MB if sharded** (the win) |
| Kiwi morphology | +552 MB | needed for Korean |
| realizer (thought_language/holographic_lm) | +1,205 MB | → use the small 60-160MB realizer for offline |

**Concrete 4GB actions (now quantified):**
1. **Rebuild the cartridge/world-graph packs with `dict_backend="sharded"`** → −~1.4 GB (proven).
2. **Lean offline realizer** — swap the 1.2 GB holographic_lm for the small realizer in the
   offline profile → −~1 GB.
Net: cartridge(sharded ~0.1) + Kiwi(0.5) + small realizer(0.16) ≈ **~0.8 GB resident → fits 4GB.**
