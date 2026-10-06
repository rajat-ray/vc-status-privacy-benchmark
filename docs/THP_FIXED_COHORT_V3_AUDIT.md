# THP Fixed-Cohort v3 — Development Audit

Date: 2026-10-06

## Execution
The v3 fixed-cohort implementation was reproduced over 30 seeds, five publication strategies, and horizons {1,2,4,8,16,32,64} days.

Mean simulated lifecycle events per seed: 494.1.
Mean target sample per seed: 48.5.

## Invariant check
Posterior entropy was non-increasing with horizon for every seed/strategy trajectory (0 monotonicity violations). The fixed baseline cohort removes the moving-denominator defect found in v2.

## Development results
Mean THP (effective candidates):
- Immediate: H1 4032.77; H8 3547.89; H16 3010.83; H32 1887.47; H64 1.005.
- Fixed 15m: H1 4032.77; H8 3547.90; H16 3010.85; H32 1887.51; H64 1.069.
- Fixed 60m: H1 4032.78; H8 3547.94; H16 3010.91; H32 1887.63; H64 1.297.
- Adaptive 10/30: H1 4035.80; H8 3548.12; H16 3010.94; H32 1887.67; H64 1.291.
- Adaptive 25/60: H1 4035.86; H8 3548.27; H16 3011.16; H32 1887.86; H64 1.557.

Mean NTHP/TPL at H64:
- Immediate: 0.000431 / 0.999569
- Fixed 15m: 0.005696 / 0.994304
- Fixed 60m: 0.023529 / 0.976471
- Adaptive 10/30: 0.023237 / 0.976763
- Adaptive 25/60: 0.042564 / 0.957436

## Critical interpretation
The monotonicity check passes, but the dramatic H64 collapse is NOT yet a publishable longitudinal-privacy result.

Why: targets are sampled only from credentials that undergo an irreversible revocation during the 64-day window, and the attacker is given a noisy identity-linked lifecycle time for those targets. By H64 every sampled target has transitioned. Under immediate publication, most observable delta epochs are singleton or very small groups, so target identification becomes nearly deterministic. This is an event-identification experiment conditional on known-to-revoke targets, not a general credential-privacy estimate.

The horizon curve also combines:
1. survival information before the target transition (the target is among not-yet-changed credentials), and
2. epoch membership information when the transition becomes observable.

That is legitimate conditional information, but it must be named precisely. It does not establish that repeated unchanged snapshots alone leak identity.

## Decision
v3 fixes the mathematical moving-candidate-universe problem and demonstrates that the estimator can obey the expected entropy monotonicity invariant. However, keep v3 as DEVELOPMENT evidence only.

## v4 requirements
Create a pre-registered fixed-cohort experiment with:
- targets sampled from the full baseline cohort before outcomes are generated/conditioned;
- explicit estimands separating (a) unconditional credential privacy, (b) conditional privacy given a lifecycle event is known to occur, and (c) event-time linkage;
- a no-auxiliary-time A1 arm, noisy-time A2 arm, and bounded auxiliary-knowledge A3 arm;
- the same baseline prior and target set across horizons;
- posterior treatment of both changed and unchanged targets;
- calibration checks and entropy monotonicity tests;
- separate irreversible-revocation and reversible/stateful scenarios only where standards semantics justify them;
- 30 seeds and confidence intervals.

Publication rule: do not use v3's ~1-candidate H64 result as evidence that W3C herd privacy generally collapses over time.
