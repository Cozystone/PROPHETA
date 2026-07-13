# PROPHETA — the 36GB is DISK, not RAM (on-demand is mostly already built)

The honest ~36GB is a DISK / download-size number. Verified (2026-07-14) that RAM stays
bounded to the query working set at ANY pack size, because the ATANOR store already does
on-demand loading:

- **Columns are `np.memmap` (mode="r")** — confirmed by source inspection. The OS pages in
  only the file regions a query actually touches (a subject's rows), never the whole 36GB.
  Measured: opening a store + 3,000 subject lookups grew process RSS by ~6 MB.
- **Sharded term-dict backend** (`dict_backend="sharded"`) keeps the dictionary on disk with
  bounded RAM — the option a 36GB world-graph pack uses instead of the RAM dict.

**Verdict:** Gemini's "tiered on-demand loading" (path 2) is LARGELY ALREADY REALIZED via mmap
+ sharded dict — not a new build. A 36GB pack sleeps on SSD; RAM footprint for a query is
hundreds of MB, so the 60–160 MB lightweight core stays lightweight. Path 2's remaining work is
just the pack manifest/loader + domain sharding for download-by-capacity.

Path 1 (literal binary hashing, 36→~25 GB) reduces DISK/download size, orthogonal to RAM.
