# ATANOR public (text-only) profile — build spec

Owner (2026-07-14): ship a public text-only ATANOR, separate from DEMO — but as a PROFILE flag,
NOT a fork (one codebase; see demo-profile-architecture doctrine).

## What PROFILE=public loads (lean, ~4GB-laptop-safe)
- TripleStore (sharded + mmap) — the cartridge/world-graph packs (kg_triples_sharded)
- Kiwi morphology (Korean) + English tokenizer
- the SMALL realizer (~160MB), NOT holographic_lm (~1.2GB)
- the answer path: router → lexicon/cartridge → base-brain rescue → web truth gate (4-tier)
- PROPHETA world-graph packs as optional downloads

## What PROFILE=public EXCLUDES (the weight/risk)
- perception models (OWLv2, DeepFace, camera)
- SPLATRA / holographic-visual / 3DGS
- rig/PBD/material dynamics, avatar
- heavy autonomous daemons (or run them detached, opt-in)

## Build steps (next session, one pass)
1. Add `ATANOR_PROFILE` env read at engine boot (main.py) → 'demo' (default) | 'public'.
2. Guard the HEAVY imports behind `if PROFILE=='demo'` (perception/SPLATRA/holographic) — they
   must be lazy/conditional so PROFILE=public never imports them (that's the RSS win).
3. Cartridge defaults to sharded backend for public.
4. Measure PROFILE=public engine RSS (target: <1.2GB) + P0 GREEN + battery unchanged.
5. Package: installer with core + optional PROPHETA world packs (download by capacity).

## Why (the moat is all text)
No-LLM + web truth gate (hallucination-0) + offline world graph — the whole moat lives in the
text path. Visual is a DEMO differentiator, not the public core. Public = the lean profile
crystallized as a product, aligned with the 4GB / offline work already measured.
