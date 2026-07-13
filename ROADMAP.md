# PROPHETA roadmap

Concrete build order. Each phase has a measurable gate — no phase is "done" without a number.

## Phase 0 — feasibility on real data (prove the ~7–20 GB math)
- [ ] Ingest a Wikidata subset (top ~1M entities + their statements) into the ATANOR
      int-columnar triple store.
- [ ] Measure real on-disk **bytes/triple** after ingest, then after binary hashing.
      **Gate:** extrapolated full-Wikidata size ≤ 20 GB int / ≤ 8 GB hashed on real data.
- [ ] Measure coverage of the adversarial-100 battery from the local subset alone (web OFF).
      **Gate:** report the honest number; no hand-waving.

## Phase 1 — store compression (40.8 → 14 B/triple)
- [ ] The current ATANOR store is ~40.8 B/triple (bloated). Tighten the int-columnar encoding
      + add binary semantic hashing for the embedding sidecar.
      **Gate:** ≤ 16 B/triple with lossless fact recovery.

## Phase 2 — World Graph pack + plugin loader
- [ ] Domain-shard the ingested graph into downloadable packs (by capacity).
- [ ] Plugin manifest + loader that mounts a pack into the live engine's answer path (the same
      cartridge-shadow / lexicon-lane wiring already used for the 2M cartridge).
      **Gate:** engine answers a battery of world questions fully offline, hallucination-0.

## Phase 3 — Plausibility Field (the beat-the-LLM piece, never-abstain)
- [ ] Ingest ConceptNet + ATOMIC commonsense edges into the graph.
- [ ] Build the phase-holographic plausibility field over the graph; for an UNKNOWN query,
      emit a grounded prediction ("not certain, but likely …") marked as inference.
      **Gate:** on a held-out set of genuinely-unknown questions, 0 abstentions, 0 bare
      assertions, predictions rated more accurate than a human's guess.

## Phase 4 — Composition realizer packaging + monthly versioned re-sync
- [ ] Ship the ~100–300 MB realizer as part of the pack.
- [ ] HQ pipeline that emits a versioned monthly delta pack for new events.
      **Gate:** an offline install one month stale still answers correctly + flags what it
      couldn't yet sync.

## Binding constraints (inherited from ATANOR)
- No memorized-weight LLM (no MoE). Knowledge = explicit graph; the realizer holds patterns, not facts.
- Never abstain on the unknown — predict, grounded and marked.
- Zero fabrication: an unverified claim hedges or predicts, never asserts.
