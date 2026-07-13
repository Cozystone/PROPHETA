# PROPHETA — the offline world-understanding plugin for ATANOR

Propheta is ATANOR's downloadable **world plugin**: an offline knowledge core that lets the
engine answer about the world with **no internet**, at a fraction of a large LLM's size, with
**zero fabrication**. The name is the thesis — for what it has, it answers; for what it has
*never seen*, it does not abstain, it **predicts** (a grounded, superhuman "I'm not certain,
but wouldn't it be like this?") from the structure it holds.

## Why this can exist (the math, not hype)

Big LLMs conflate **understanding** with **memorization** — they store terabytes of float
weights to reach it. But understanding is *structure* (relations, causality, analogy), not a
list of facts. Stored as an **explicit graph** instead of memorized weights, the world's
knowledge is small:

| | facts | local size |
|---|---|---|
| All of Wikidata | ~1.4B statements | **~20 GB** int-columnar / **~6.5 GB** binary-hashed |
| + Wiktionary + ConceptNet | ~2.0B | **~9 GB** hashed |
| GPT‑4 weights (for scale) | 1.8T params | ~3,600 GB |

The world's *knowledge* is **100–180× smaller** than a big LLM that memorized it — and smaller
than one person's raw sensory life. Nobody shipped offline omniscience this way because everyone
stored knowledge as weights (LLM). Propheta stores it as **structure** (graph), so the world
fits on a laptop.

**This is not a small LLM in a box (no MoE).** It is ATANOR's doctrine scaled to world size.

## Architecture — 3 tiers (~10–25 GB, sharded, download by capacity)

1. **World Graph (WHAT)** — all of Wikidata + Wiktionary ingested into ATANOR's int-columnar
   triple store, binary-hashed. Every entity/relation, lossless, hallucination‑0.
2. **Plausibility Field (the beat-the-LLM piece)** — ConceptNet/ATOMIC commonsense + a
   continuous topological (phase‑holographic) field that holds *fuzzy* commonsense
   ("you can't push a rope") as geometry, not discrete triples. Grounded in the graph, so it
   reproduces an LLM's "vibe knowledge" **without hallucinating**, and it is what powers the
   **prediction for the unknown** (never abstain).
3. **Composition Realizer (HOW)** — a small (~100–300 MB) generator that learns *speaking
   patterns*, not facts; it voices only graph+field-verified content (sever knowing from
   speaking).

## Delivery
- **Plugin packs**, domain-sharded, download by capacity — core small, most users stay online,
  fully-local users pull the packs they want; none too large.
- **Versioned monthly re-sync from HQ** for new events (the one thing an offline core can't
  self-derive).

## Honest scope
- Beats *current* large LLMs on **efficiency + honesty + speed**, not literal infinite
  omniscience.
- For the genuinely unknown: **grounded prediction, clearly marked as inference — never a bare
  assertion, never an abstention.**

Developed in parallel with the main ATANOR engine; updated here periodically.
