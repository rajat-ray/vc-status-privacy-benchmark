# Beyond Herd Privacy: VC Status Privacy Benchmark

Reproducibility package for:

**Beyond Herd Privacy: Measuring Temporal Linkability in Verifiable Credential Status Systems**

Author: **Rajat Ray** — Independent Researcher, Singapore  
ORCID: `0009-0008-1948-3264`

## Research question

This project measures how longitudinal observation of public Verifiable Credential status-list updates can reduce effective herd privacy, and evaluates publication policies as privacy–freshness–publication-cost trade-offs.

The project is designed around W3C Bitstring Status List-style public state. It does **not** claim that observing a changed status-list index reveals a holder identity.

## Authoritative evidence

| Evidence | Purpose | Authoritative path |
|---|---|---|
| Phase 1 / 1B | Longitudinal differencing and candidate-set narrowing | `src/phase1.py`, `results/phase1b/` |
| Corrected Phase 5 | Observable-only temporal attacker and publication-policy comparison | `src/phase5_corrected_observable_attacker.py`, `results/phase5_corrected/` |
| Phase 7 | Corrected timing/event-density/clustering sensitivity and random delay | `src/phase7_corrected_sensitivity.py`, `results/phase7_corrected_sensitivity/` |
| Phase 7 | Timing/event-density/clustering sensitivity and random-delay analysis | `src/phase7_corrected_sensitivity.py`, `results/phase7_corrected_sensitivity/` |
| Corrected statistics | Bootstrap CIs and paired policy comparison | `src/corrected_statistics.py`, `results/consolidated_corrected/` |
| Reproduced Phase 4 | Actual bitstring/GZIP/base64url artifact benchmark | `src/phase4_w3c_artifacts.py`, `results/phase4_reproduced/` |
| Phase 6 | Local engineering feasibility | `results/phase6_engineering/` |

## Methodological correction

Exploratory Phase 2/2B/3 and original Phase 5 temporal-ranking code used candidate-specific latent event times. Those hidden times are not normally observable from published batched status-list versions.

Those temporal Top-k/EAS results are therefore **superseded** and MUST NOT be used as primary manuscript evidence. See `results/exploratory_superseded/README.md`.

The corrected attacker observes publication epochs and pseudonymous changed indexes, may possess a noisy external timestamp for a target lifecycle event, never observes candidate-specific latent true event times, and handles equal-posterior candidates with expected Top-k inclusion probabilities.

## Reproduce

Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
python reproduce.py
```

The reproduction workflow regenerates corrected Phase 5, reproduced Phase 4, corrected Phase 7 sensitivity/random-delay outputs, and corrected bootstrap statistics, then checks core invariants.

## Scope boundaries

- Synthetic lifecycle/status data; no human participants or PII.
- Temporal matching probabilities are model-conditional, not deployed-world attack rates.
- Phase 4 uses actual bitstrings, GZIP and base64url encoding in an unsigned VC-shaped JSON envelope; it does not implement VC proof generation or HTTP/CDN retrieval.
- Phase 6 uses loopback HTTP and a raw Ed25519 primitive; it is not a W3C Data Integrity conformance test.
- Adaptive batching is evaluated as a trade-off point, not claimed as globally optimal or novel in itself.
- Index rotation and privacy-preserving revocation mechanisms are prior art; the contribution is quantitative measurement of temporal anonymity degradation and mitigation trade-offs.

## Citation

See `CITATION.cff`.

## License

Research code is provided under the MIT License. Manuscript text and generated research results remain attributable to the author.


## Tested environment

The final pre-freeze audit passed on Python 3.13.5 with the exact package versions recorded in `requirements-lock.txt` and `environment.json`. `python reproduce.py` completed successfully in the audited environment and regenerated the authoritative corrected Phase 5, Phase 4, Phase 7, and corrected statistical outputs.

## Versioning

`v1.0.0-submission` is the intended immutable scholarly submission snapshot. Development after that snapshot should use later tags rather than modifying the frozen release.

## Archival DOI

The persistent scholarly snapshot for the submission reproducibility package is archived on Zenodo:

**DOI:** `10.5281/zenodo.23134118`  
**Archived release:** `v1.0.1-archive`  
**DOI:** https://doi.org/10.5281/zenodo.23134118

The Zenodo record is the canonical archival snapshot. The GitHub repository may continue to evolve after the archived release.
