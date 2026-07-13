# PROPHETA Phase 2 v0 — real Wikidata Korean world-definition pack (WORKS)

phase2_world_pack.py streams top Wikidata entities → (ko_label, defined_as, ko_description) +
(ko_label, is_a, P31-target), sharded + src.col-free. v0 = 15k entities.

- 29,385 triples, 2 MB, sharded (4GB-safe).
- Answers real-world entities with clean Korean definitions, hallucination-0:
  대한민국→"동아시아의 국가", 산소→"원자 번호 8번의 화학 원소", 광합성→"빛에너지를 화학
  에너지로 바꾸는 생물학적 과정", 커피→"쓴맛이 나는 짙은 갈색의 음료".
- Broader than the Kaikki cartridge; proves the Wikidata→Korean-definition pipeline end-to-end.
- Label-form note: people are stored under full names (알베르트 아인슈타인), so exact
  facts_about("아인슈타인") misses — the lexicon alias/short-name path handles this at answer time.

The full 102GB Wikidata dump is downloading to scale this to the complete world graph; v0 is the
proven seed. Next: parse the dump (ko-filter) into the full pack, then swap it in behind the
Kaikki cartridge.
