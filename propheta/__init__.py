# -*- coding: utf-8 -*-
"""PROPHETA — ATANOR's offline world-understanding plugin.

Three tiers (see README). This package holds the CONTRACTS; the heavy data (World Graph packs,
field weights, realizer) is downloaded/built separately and is git-ignored.

  world_graph      — WHAT: ingest + query the explicit fact graph (Wikidata/Wiktionary),
                     int-columnar + binary-hashed, hallucination-0.
  plausibility     — the fuzzy-commonsense field: predicts the UNKNOWN (never abstains),
                     grounded in the graph so it cannot fabricate; marks output as inference.
  realizer         — HOW: small pattern-only generator; voices only graph/field-verified content.
  pack             — plugin manifest: shard, size, version; loader that mounts a pack into the
                     ATANOR answer path (reuses the cartridge-shadow / lexicon-lane wiring).

Binding: no memorized-weight LLM (no MoE); knowledge lives in the graph, the realizer holds
patterns not facts; never abstain on the unknown — predict, grounded and marked.
"""
from __future__ import annotations

__version__ = "0.0.1"

TIERS = ("world_graph", "plausibility", "realizer")

# provisional size budget (GB) proven by the Phase-0 feasibility gate on real Wikidata data
SIZE_BUDGET_GB = {"world_graph_hashed": 8.0, "plausibility": 2.0, "realizer": 0.3}
