# THP v4 preregistration

Targets are sampled uniformly from the full fixed baseline cohort before lifecycle outcomes are generated. The target set and prior remain fixed across horizons.

Primary estimand: unconditional effective anonymity (THP) across all preselected targets.
Secondary estimands: changed-target conditional THP and unchanged-target THP.

Arms:
- A1: observable longitudinal publication deltas only.
- A2: A1 plus noisy identity-linked lifecycle time. Candidate latent event times are forbidden; if candidates share an observable publication epoch, timing must not break that tie.
- A3: A1 plus a disjoint externally-known 10% subset.

Horizons: 1,2,4,8,16,32,64 days. Seeds: 30. Strategies: immediate, fixed 15m, fixed 60m, adaptive 10/30, adaptive 25/60.

Required invariants: same baseline prior; no future observations; no candidate latent event times; per-target posterior entropy cannot increase as cumulative observations are added.

Nulls are publication-valid. In particular, repeated unchanged snapshots or A2 timing may add no information under the declared observation model.
