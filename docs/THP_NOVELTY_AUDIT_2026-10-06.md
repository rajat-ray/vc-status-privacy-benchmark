# Paper 2 — THP Novelty Audit Matrix (2026-10-06)

## Decision
Temporal Herd Privacy (THP) should be positioned as an **adapted credential-status-specific longitudinal measurement framework**, not as a newly invented entropy/anonymity metric and not as discovery of long-term monitoring or intersection attacks.

## Claim classification

| Concept | Classification | Reason / claim boundary |
|---|---|---|
| Shannon entropy of attacker posterior | PRIOR | Established information-theoretic anonymity metric. |
| Effective anonymity represented as 2^H | PRIOR / ADAPTED | Established interpretation of entropy as an equivalent uniform anonymity-set size. Do not claim mathematical novelty. |
| Normalized entropy H/log2(N) | PRIOR | Established degree-of-anonymity construction. |
| Repeated-observation / intersection attack | PRIOR | Long-term repeated observations reducing anonymity are established in anonymous-communication literature. |
| Long-term monitoring of VC status entries | PRIOR | W3C Bitstring Status List explicitly recognizes monitoring and correlation risks. |
| Correlation from detailed status messages | PRIOR | Explicitly recognized by W3C Bitstring Status List. |
| Minimum large list / herd privacy | PRIOR | W3C Bitstring Status List uses minimum 131072 entries and describes group/herd privacy. |
| Batching / delayed publication as privacy mechanism | PRIOR IDEA / ENGINEERING EVALUATION | Do not claim invention; evaluate quantitatively in declared credential-status model. |
| Privacy-preserving cryptographic revocation | PRIOR | Accumulator and other privacy-preserving revocation approaches predate this work. |
| THP_A(T)=2^H(C|O_1:T,K_A) | ADAPTED | Application of established entropy/effective-anonymity machinery to an explicit credential-status longitudinal observation sequence and attacker knowledge budget. |
| NTHP/TPL | ADAPTED | Normalized entropy/privacy-loss presentation; terminology may be new but underlying mathematics is established. |
| Fixed-cohort credential-status longitudinal evaluation | POTENTIAL CONTRIBUTION | Reproducible methodology applying fixed prior/targets, status publication histories, attacker escalation, horizons, and publication policies to VC status systems. Claim only after literature search remains negative for an equivalent evaluation. |
| Distinguishing snapshot herd size, unconditional longitudinal anonymity, and event-conditional anonymity | POTENTIAL CONTRIBUTION | Strongest current conceptual contribution: a large snapshot list can coexist with much smaller anonymity for credentials whose lifecycle transition becomes observable. |
| Quantifying privacy–freshness–resource trade-offs for W3C-like bitstring publication policies | POTENTIAL CONTRIBUTION / ENGINEERING | Contribution is empirical systems characterization, not invention of privacy/freshness trade-offs. |
| Broad claim that herd privacy collapses over time | REJECTED | v4 does not support universal collapse; degradation is conditional and attacker/model dependent. |
| Claim that noisy target timing necessarily improves attack | REJECTED / NULL | v4 A1=A2 under the declared observable-only model. Preserve the null. |

## Literature anchors

1. W3C Bitstring Status List v1.0 Recommendation (15 May 2025): minimum 131072-entry list, group privacy, verifier caching, unnecessary correlation, monitoring status lists, and correlation of status messages.
2. W3C Bitstring Status List v1.1 FPWD (24 Sep 2026): retains/extends explicit long-term monitoring and status-message correlation discussion.
3. Serjantov/Danezis and Díaz line of anonymity metrics: entropy and normalized entropy are established anonymity measures; 2^H is the equivalent uniform anonymity-set interpretation.
4. Danezis & Serjantov, Statistical Disclosure or Intersection Attacks on Anonymity Systems (2004): repeated observations/statistical disclosure are established.
5. Hayes, Troncoso & Danezis, TASP (WPES 2016): long-term passive intersection attacks progressively narrow potential recipients; persistent anonymity sets are an established problem.
6. Hölzl et al. (SAC 2018): privacy-preserving revocation using dynamic accumulators preserves unlinkability/anonymity beyond revocation.
7. Rometsch et al., UPPR (IEEE Blockchain 2025): privacy-preserving VC revocation using VRFs/Bloom-filter cascade; demonstrates active cryptographic-revocation literature.
8. Current EUDI revocation work compares accumulator/signed-pair privacy-preserving revocation approaches; use only after bibliographic verification for manuscript citation.

## Defensible novelty statement
This work does not introduce entropy anonymity metrics, discover longitudinal correlation, or propose a new revocation primitive. It contributes an attacker-parameterized longitudinal evaluation methodology for bitstring-based credential-status systems that distinguishes snapshot herd size from unconditional longitudinal anonymity and event-conditional anonymity. Using fixed-cohort experiments and declared observation/knowledge budgets, it quantifies how publication granularity and auxiliary knowledge affect effective anonymity over time, while jointly reporting freshness and implementation costs.

## Manuscript language to avoid
- "We introduce the first entropy-based anonymity metric..."
- "We discover that repeated status observations enable correlation..."
- "THP is a new information-theoretic metric..."
- "Bitstring status lists become fully deanonymized over time."
- "Timing always increases linkability."
- "Large herd size provides no privacy."

## Manuscript language preferred
- "We adapt established entropy-based anonymity measurement to a credential-status-specific longitudinal attacker model."
- "We operationalize W3C-recognized monitoring and correlation risks as reproducible quantitative measurements."
- "We distinguish snapshot herd size from longitudinal effective anonymity and event-conditional anonymity."
- "Under the synthetic benchmark, unconditional anonymity remains substantial while observable lifecycle transitions can sharply reduce anonymity for the affected subset."
- "Results are conditional on the declared attacker, event process, publication policy, and auxiliary-information budget."

## Remaining novelty gate
Before final freeze, search specifically for papers that jointly contain: W3C/StatusList2021/Bitstring Status List + repeated snapshots/deltas + entropy/effective anonymity over observation horizon + event-conditional anonymity + publication batching/freshness evaluation. If an equivalent framework is found, narrow the contribution to comparative systems evaluation rather than methodology.
