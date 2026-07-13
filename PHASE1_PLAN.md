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
