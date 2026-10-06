# THP v5 — Publication-Grade Freeze Plan

Date: 2026-10-06

## Status
v5 is the publication-grade confirmation of the preregistered v4 design. It must not change the substantive attacker model in response to observed v4 results. v4 remains development evidence.

## Primary research claim
A large snapshot herd does not imply equivalent longitudinal privacy for every credential. Under a declared status-publication attacker model, unconditional effective anonymity may remain substantial while event-conditional anonymity for credentials whose lifecycle transition becomes observable can be much smaller.

## Primary estimands
1. Unconditional longitudinal effective anonymity across targets sampled from the full baseline cohort before outcomes.
2. Event-conditional effective anonymity for targets whose transition has become observable by horizon T.
3. Unchanged-target effective anonymity.
4. Entropy-normalized privacy loss, reported only with the fixed baseline prior.

## Attacker arms
- A1: longitudinal publication deltas only.
- A2: A1 plus noisy identity-linked target lifecycle timing. Candidate latent event times remain forbidden. A1=A2 is an admissible null.
- A3: A1 plus a disjoint externally-known 10% subset. Interpret as bounded prior elimination, not status-system leakage.

## Design
- fixed cohort: 4096
- targets: 256 uniformly sampled before lifecycle outcomes
- horizon: 64 days
- checkpoints: 1,2,4,8,16,32,64 days
- irreversible revocation hazard: 0.002/day
- seeds: 30, fixed before execution
- strategies: immediate, fixed 15m, fixed 60m, adaptive 10/30, adaptive 25/60
- same baseline prior, targets and lifecycle realization across attacker arms within seed

## Required statistics
For each strategy × attacker × horizon × estimand:
- n seeds
- mean
- standard deviation
- 95% t confidence interval
- paired effect versus immediate strategy where meaningful
- paired A3-vs-A1 effect
- explicit A2-vs-A1 equality/null check
- changed/unchanged target counts

No weighted composite privacy score.

## Required invariants/audits
- 30 unique seeds in every complete cell
- no duplicate seed/strategy/attacker/horizon rows
- expected row count 3150
- per-target entropy cannot increase with cumulative observations under the declared set model
- target sample precedes outcome generation
- target set fixed across horizons
- no future observations
- no candidate latent event times
- changed + unchanged targets = 256
- all THP in [1,4096]
- NTHP and TPL in [0,1]
- A2 must not be declared stronger unless observable information actually changes posterior
- nulls retained

## Existing evidence reconciliation
Phase 5 corrected results remain the publication-policy privacy/freshness experiment. Phase 7 remains sensitivity analysis. Phase 4 remains W3C-like artifact engineering. Phase 6 remains local engineering cost only. v5 supplies the fixed-cohort longitudinal estimands and must not retroactively relabel earlier phases as THP measurements.

## Claim boundaries
- synthetic controlled benchmark, not real-world prevalence
- no W3C conformance claim
- no new cryptographic primitive
- THP is adapted entropy/effective-anonymity measurement, not a new information-theoretic metric
- repeated-observation/intersection attacks are prior art
- W3C-recognized monitoring/correlation risks are operationalized quantitatively, not newly discovered
- irreversible revocation results do not imply repeated unchanged snapshots themselves leak identity
- A3 improvement includes bounded prior candidate elimination
- no universal privacy collapse claim

## Freeze rule
Run v5 once as the publication-grade confirmation using the locked seeds/design. If implementation bugs are found, document the bug, commit the correction, and rerun transparently. Do not tune parameters to improve results. Freeze CSVs, metadata, audit, summary, provenance, commit SHA and SHA-256 hashes after successful audit.
