# Research Protocol v0.1

## Working title
Beyond Herd Privacy: Measuring Temporal Linkability in Verifiable Credential Status Systems

## Primary Phase-1 question
How much does longitudinal observation of successive status-list states narrow the candidate set associated with status-change events, relative to a snapshot-only observer?

## A0 — Snapshot observer
Observes one current status-list state and has no previous state from which to infer newly changed indexes.

## A1 — Longitudinal observer
Stores successive list states and computes the XOR/difference between consecutive states, revealing indexes whose status changed.

## Phase-1 hypothesis
Sparse publication intervals will expose smaller changed-index candidate sets to A1 than dense intervals. This is a candidate-set observation claim, not a holder-identification claim.

## Ground truth
Synthetic credential identity and assigned status-list index are retained only for evaluation.

## Primary Phase-1 measures
- issued population N
- bitstring capacity
- number of changed indexes per interval
- candidate-set size
- candidate-set reduction relative to issued population
- entropy of a uniform posterior over changed indexes
- effective anonymity set (inverse concentration), which equals candidate-set size under this Phase-1 uniform posterior

## Falsification
The Phase-1 sparse-event hypothesis is not supported if reducing status-event density does not systematically reduce A1 candidate-set size under otherwise equivalent conditions.

## Reproducibility
Every run records the random seed and configuration. No post-hoc composite privacy score is used.
