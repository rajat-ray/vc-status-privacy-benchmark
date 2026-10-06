# Paper 2 v2 — Temporal Herd Privacy Research Plan

## Status
CSI desk decision: declined for insufficient novelty. This branch preserves the frozen v1.0.0-submission baseline and develops a materially revised research contribution. Do not rewrite the frozen tag.

## Working title
Temporal Herd Privacy: Quantifying Longitudinal Privacy Degradation in Verifiable Credential Status Systems

## Core thesis
Snapshot group/herd size and longitudinal privacy are distinct properties. A large status-list population does not by itself establish strong privacy against an attacker who observes a sequence of status-list states and has bounded temporal or auxiliary knowledge.

This work does NOT claim to discover status correlation, long-term monitoring, intersection attacks, batching, randomized delay, or privacy-preserving revocation. W3C Bitstring Status List already recognizes correlation and long-term-monitoring risks. The intended contribution is a credential-status-specific, attacker-parameterized longitudinal measurement framework plus empirical privacy–freshness–resource evaluation.

## Candidate formal model (to validate against prior literature)
Let C be the target credential/event, O^(0:T) the sequence of observable status-list states through horizon T, and K_A auxiliary knowledge available to attacker A.

Conditional uncertainty:
H_A(T) = H(C | O^(0:T), K_A)

Candidate Temporal Herd Privacy:
THP_A(T) = 2 ^ H_A(T)

Interpretation: effective longitudinal anonymity-set size under the specified attacker and observation horizon.

Normalized THP:
NTHP_A(T) = H_A(T) / H(C)

Temporal Privacy Loss:
TPL_A(T) = 1 - NTHP_A(T)

These are candidate research definitions, not yet claims of mathematical novelty. They must be compared with entropy anonymity, effective anonymity-set, intersection-attack, disclosure-risk, and longitudinal-privacy literature.

## Attacker ladder
- A0 Snapshot: one published status state.
- A1 Longitudinal: repeated status states and list deltas.
- A2 Temporal: A1 plus bounded event-time knowledge.
- A3 Auxiliary: A2 plus bounded known event/subject fraction (0, 1, 5, 10, 25, 50%).
- A4 Bounded collusion: explicitly limited extra information from an ecosystem participant.

Every result must state the attacker, observables, horizon, and knowledge budget.

## Research questions
RQ1. How does effective longitudinal anonymity change as observation horizon grows?
RQ2. How do population size, event rate, update policy, and event clustering affect THP?
RQ3. How does bounded temporal/auxiliary knowledge accelerate degradation?
RQ4. How does degradation differ across A0–A4?
RQ5. What privacy–freshness–bandwidth/storage/processing trade-offs result from publication mitigations?

## Hypotheses
H1. Longitudinal THP decreases with observation horizon under A1+ when observable deltas carry information.
H2. Sparse event regimes can produce smaller effective candidate sets than snapshot herd size suggests.
H3. Additional bounded temporal/auxiliary knowledge weakly decreases THP (nulls retained).
H4. Batching/delay can increase ambiguity at freshness cost.
H5. Population size alone is insufficient to characterize longitudinal privacy.
H6. Adaptive publication can occupy useful privacy–freshness operating points; no universal dominance is assumed.

## Primary new experiment — observation-horizon degradation
Use existing simulation/data-generation semantics where possible. Add horizon checkpoints such as T={1,2,4,8,16,32,64} (or justified equivalents based on the event model).

For each attacker A0–A4 and mitigation:
- compute posterior/candidate probabilities using only permitted observables;
- report H_A(T), THP_A(T), NTHP_A(T), TPL_A(T);
- retain existing EAS/candidate-set metrics and Top-1/5/10 as secondary operational measures;
- report 30 seeds, confidence intervals, effect sizes, and null results;
- prohibit target/ground-truth leakage into attacker features.

Primary figure: THP/effective anonymity versus observation horizon, stratified by attacker. Do not use illustrative numbers in final results.

## Existing evidence to reuse
Retain the existing Phase 4 W3C-like artifact experiment, Phase 5 mitigation benchmark, Phase 6 local engineering measurements, and Phase 7 sensitivity experiments where their semantics remain valid. Recompute/relabel metrics only when mathematically justified; never retroactively present old measurements as THP if the required posterior/horizon data were not recorded.

Existing Phase 5 benchmark includes immediate, fixed 15-minute, fixed 60-minute, adaptive 10/30 and adaptive 25/60 policies. These become evidence for a privacy–freshness frontier, not novelty by themselves.

## Required novelty audit
Before claiming THP as new, compare the formalization against:
1. entropy/effective anonymity-set metrics;
2. intersection and disclosure attacks under repeated observations;
3. revocation/status-list privacy and anonymous-credential revocation;
4. longitudinal privacy metrics;
5. privacy–freshness publication/traffic-analysis trade-offs;
6. W3C Bitstring Status List v1.0/v1.1 and VC threat-model guidance.

Outcome labels:
- NEW: genuinely distinct definition/method.
- ADAPTED: established metric specialized to credential-status longitudinal observation.
- PRIOR: known concept; cite and do not claim.
- ENGINEERING: implementation/evaluation contribution only.

## Claim boundaries
- Synthetic benchmark results are conditional, not real-world prevalence estimates.
- W3C-like artifact experiments are not full W3C Data Integrity conformance unless separately demonstrated.
- Local processing measurements are not Internet/network latency.
- No formal verification unless actually performed.
- No claim that large snapshot lists are intrinsically unsafe.
- No claim that status correlation or long-term monitoring was newly discovered.
- Null results must be preserved.
- Privacy gains must be reported with freshness/resource costs.

## Standards context captured 2026-10-06
W3C Bitstring Status List v1.1 FPWD (24 Sep 2026) explicitly discusses global identifiers, long-term monitoring and correlation of status messages. The W3C VC Data Model Threat Model v2.1 also identifies correlation via status/revocation lookup. The manuscript must position THP as quantitative longitudinal characterization, not discovery of those threats.

## Exit criteria before resubmission
1. Novelty audit finds no equivalent credential-status-specific THP formulation, or claims are narrowed to an adapted methodology.
2. Observation-horizon experiment implemented and independently auditable.
3. A0–A4 features and knowledge budgets documented.
4. 30-seed results frozen with manifest/hashes.
5. THP equations and estimator implementation cross-checked.
6. Existing Phase 5/7 results reconciled with new framework.
7. Manuscript rewritten around longitudinal measurement, not the rejected narrative.
8. Literature and standards refreshed immediately before submission.
9. New immutable release/DOI created only after evidence freeze.
