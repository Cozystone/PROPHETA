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
