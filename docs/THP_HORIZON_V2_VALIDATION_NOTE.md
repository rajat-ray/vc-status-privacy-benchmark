# THP Horizon v2 — Development Validation Note

Date: 2026-10-06

## Purpose
Validate the first candidate observation-horizon implementation before treating it as publication evidence.

## Development-only local run
The candidate implementation was exercised over 30 seeds and horizons {1,2,4,8,16,32,64}. This was a development validation, not a frozen GitHub Actions evidence run.

The result does **not** support the originally proposed statement that absolute THP necessarily decreases as more publication epochs are included. In the current event-identification model, enlarging the retained history also enlarges the candidate population. Absolute effective anonymity therefore generally increases from H=1 to H=2 and then plateaus, while the normalized entropy ratio falls because the reference candidate population continues to grow.

Representative development means:
- Immediate: THP ~1.13 at H=1, ~1.51 at H=2, ~1.64 from H≈8 onward; normalized THP falls from 1.00 to ~0.12 by H=64.
- Fixed 15m: THP ~3.09 at H=1 and ~3.37 thereafter; normalized THP ~0.28 at H=64.
- Fixed 60m: THP ~9.45 at H=1 and ~9.73 thereafter; normalized THP ~0.53 at H=64.
- Adaptive 10/30: THP ~6.06 at H=1 and ~6.51 thereafter; normalized THP ~0.44 at H=64.
- Adaptive 25/60: THP ~10.33 at H=1 and ~10.70 thereafter; normalized THP ~0.55 at H=64.

## Interpretation
This is a useful null/design finding. The first horizon definition is not a valid demonstration of longitudinal anonymity collapse. It mixes two effects:
1. additional observations/information; and
2. growth of the candidate universe as earlier publication epochs are added.

Consequently, TPL=1-NTHP under this implementation can rise largely because the denominator changes. It must not be presented as measured longitudinal privacy loss.

## Required redesign
Freeze the candidate universe when comparing horizons. The same target and same candidate set must be evaluated as observations accumulate. Candidate longitudinal experiments should use a stateful process in which the same credentials can generate multiple observable state transitions (e.g., suspension/message-state changes where permitted by the modeled status purpose), or another explicitly justified repeated-observation process. For each target:
- define the candidate universe at baseline;
- expose O_1...O_T sequentially without adding/removing candidates merely because T grows;
- update posterior P(C|O_1:T,K_A);
- compare H(C|O_1:T,K_A) against the same H(C|K_A);
- verify entropy non-increase when observations are genuinely cumulative and the model is internally consistent.

For irreversible one-time revocation, repeated unchanged snapshots after the transition may add no information. That null must be preserved rather than manufacturing a degradation curve.

## Publication rule
Do not use results from src/thp_horizon_v2.py as manuscript evidence. Retain the file as a documented failed/developmental estimator until the redesigned experiment is implemented and audited.
