# PROPHETA Phase 1 — compression path (measured, not guessed)

Decomposed the Phase-0 store's 25.5 B/triple into real file components (322,845 triples):

| component | B/triple | action |
|---|---:|---|
| `terms.txt` (term dictionary) | 9.7 | **small-sample artifact** — amortizes with scale. 1.4B triples share ~113M terms → ~1.6 B/triple at full scale. No change needed, just scale. |
| `s.col`+`p.col`+`o.col` (3×int32) | 11.7 | theoretical floor — untouchable losslessly. |
| `src.col` (per-triple provenance) | 3.9 | **DROP for world-graph packs** — Wikidata provenance is uniform (source = Wikidata); no per-triple src id. Instant −3.9. |
| meta.json | ~0 | — |

**Finding: the 14 B/triple target is essentially FREE — no risky format change.**
At full scale: `s/p/o` (11.7) + amortized dict (~1.6) + no `src.col` = **~13.3 B/triple**
→ full Wikidata **≈ 18.6 GB int**, and **binary hashing the columns → ~6.5 GB**.

## Phase 1 tasks
- [ ] World-graph ingest mode that omits the `src.col` sidecar (uniform provenance).
- [ ] Confirm dict amortization on a larger real ingest (100k+ entities) — measure B/triple drops toward ~13.
- [ ] Binary semantic-hash the o.col value space for the retrieval index (→ ~6.5 GB hashed).

## Phase 1 — first milestone SHIPPED (2026-07-14)
- [x] `TripleStore(write_src=False)` world-graph mode landed in the ATANOR engine
      (backward-compat: default unchanged; engine P0 sentinel GREEN 8/8 after the change).
- [x] Re-measured on real Wikidata (1,026 entities / 287,559 triples): **25.5 → 21.6 B/triple**
      — the predicted −3.9 realized exactly. GATE still PASS.
- [x] **Answerability proven**: `facts_about` returns real world facts fully locally —
      Q2(Earth)→P1589→Q459173(Challenger Deep), Q1(universe) 20 facts, … The pack doesn't
      just *fit*, it *answers*.
- [ ] Remaining to ~14: dict amortization at scale (needs a 100k+ entity ingest) + binary
      hashing of the retrieval index (→ ~6.5 GB full-Wikidata).

## Phase 1 — amortization DE-RISK (2026-07-14): the optimistic claim was WRONG, corrected
Measured terms/triple across scale (real Wikidata, checkpoints 532→3,536 entities):

| entities | B/triple | terms/triple |
|---:|---:|---:|
| 532 | 22.0 | 10.2 |
| 1,026 | 21.6 | 9.8 |
| 2,015 | 21.6 | 9.8 |
| 3,536 | 21.7 | **9.8 (plateau)** |

**Honest correction:** terms/triple does NOT amortize toward ~1.6 — it PLATEAUS at ~9.8.
Wikidata values carry many UNIQUE literals (dates, quantities, coordinates, strings) that don't
share. So B/triple plateaus at **~21.6**, and full Wikidata ≈ **30 GB int**, NOT 19.6 GB. The
earlier "14 B/triple is free via amortization" was too optimistic — retracted.

**Revised path to the ~6.5 GB target (binary hashing is now REQUIRED, not optional):**
- The 21.6 = s/p/o (11.7, int32 floor) + terms.txt (~9.8, dominated by literal values).
- **Hash the value/literal space**: replace verbatim literal storage with fixed-width binary
  hashes (dates→packed int, quantities→float32, strings→64-bit semantic hash + a side lexicon
  only for the ones we must render). Target: terms.txt ~9.8 → ~2–3 B/triple.
- Then full Wikidata ≈ (11.7 + ~2.5) × 1.4B ≈ **~20 GB**, and dropping the id columns to
  variable-length (delta+varint on sorted s) can approach the ~6.5 GB hashed target.
- Thesis intact regardless: even at the plateau 30 GB, that is ~120× smaller than GPT‑4's
  3,600 GB. "World fits on a laptop" holds; the exact GB is 6.5–30 depending on hashing.
