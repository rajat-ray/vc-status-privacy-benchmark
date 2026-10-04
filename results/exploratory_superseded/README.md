# Superseded exploratory analyses

The Phase 2, Phase 2B, Phase 3, original Phase 5, and original consolidated temporal Top-k/EAS analyses are retained for research traceability.

They are **not primary evidence** for the manuscript because their temporal-ranking implementation used candidate-specific latent event times that would not ordinarily be observable to an attacker watching published batched status-list versions.

The authoritative temporal privacy analysis is:

- `src/phase5_corrected_observable_attacker.py`
- `results/phase5_corrected/`
- `src/phase7_corrected_sensitivity.py`
- `results/phase7_corrected_sensitivity/`
- `results/consolidated_corrected/`

The old files remain in the research archive to preserve provenance and avoid silently rewriting research history.
