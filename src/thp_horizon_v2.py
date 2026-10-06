from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "thp_horizon_v2"
OUT.mkdir(parents=True, exist_ok=True)

N = 100_000
DURATION = 1440.0
DAILY_RATE = 0.002
SIGMA = 2.0
KNOWLEDGE = 0.10
SEEDS = range(20261004, 20261034)
HORIZONS = [1, 2, 4, 8, 16, 32, 64]
STRATEGIES = [
    ("M0_immediate", {"kind": "fixed", "batch": 1}),
    ("M1_fixed_15m", {"kind": "fixed", "batch": 15}),
    ("M2_fixed_60m", {"kind": "fixed", "batch": 60}),
    ("M6_adaptive_k10_D30", {"kind": "adaptive", "k": 10, "max": 30}),
    ("M7_adaptive_k25_D60", {"kind": "adaptive", "k": 25, "max": 60}),
]

def publication_times(times, cfg):
    if cfg["kind"] == "fixed":
        b = cfg["batch"]
        return np.minimum(np.ceil(times / b) * b, DURATION)
    k, dmax = cfg["k"], cfg["max"]
    pub = np.empty(len(times))
    start = 0
    while start < len(times):
        deadline = min(times[start] + dmax, DURATION)
        kth = start + k - 1
        if kth < len(times) and times[kth] <= deadline:
            end, pt = kth, times[kth]
        else:
            end = max(start, np.searchsorted(times, deadline, side="right") - 1)
            pt = deadline
        pub[start:end + 1] = pt
        start = end + 1
    return pub

def normal_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def epoch_likelihood(aux, pt, cfg):
    if cfg["kind"] == "fixed":
        lo, hi = max(0.0, pt - cfg["batch"]), pt
    else:
        lo, hi = max(0.0, pt - cfg["max"]), pt
    if hi <= lo:
        return 1e-300
    mass = normal_cdf((hi - aux) / SIGMA) - normal_cdf((lo - aux) / SIGMA)
    return max(mass / (hi - lo), 1e-300)

def posterior_entropy(aux, epochs, sizes, cfg, horizon):
    # Horizon is the number of most recent observable publication epochs retained.
    # This experiment deliberately uses only observable epoch time/count plus target
    # auxiliary time; candidate latent event times are never used.
    if len(epochs) == 0:
        return np.nan, np.nan
    h = min(horizon, len(epochs))
    e = epochs[-h:]
    s = sizes[-h:]
    L = np.asarray([epoch_likelihood(aux, float(pt), cfg) for pt in e], dtype=float)
    Z = float(np.sum(L * s))
    p_epoch = L / Z
    entropy = -float(np.sum(s * p_epoch * np.log2(p_epoch + 1e-300)))
    thp = float(2.0 ** entropy)
    return entropy, thp

rows = []
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    count = int(rng.poisson(N * DAILY_RATE))
    times = np.sort(rng.uniform(0, DURATION, count))
    targets = np.where(rng.random(count) < KNOWLEDGE)[0]
    aux = times[targets] + rng.normal(0, SIGMA, len(targets))

    for strategy, cfg in STRATEGIES:
        pubs = publication_times(times, cfg)
        rounded = np.round(pubs, 9)
        epochs, inverse, sizes = np.unique(rounded, return_inverse=True, return_counts=True)

        for horizon in HORIZONS:
            entropies, thps, normalized, losses = [], [], [], []
            for tid, a in zip(targets, aux):
                target_epoch = inverse[tid]
                # Evaluate at the target's observable publication epoch and retain
                # at most H publication epochs ending there. This avoids future data.
                prefix_epochs = epochs[:target_epoch + 1]
                prefix_sizes = sizes[:target_epoch + 1]
                entropy, thp = posterior_entropy(a, prefix_epochs, prefix_sizes, cfg, horizon)
                prior_n = int(np.sum(prefix_sizes[-min(horizon, len(prefix_sizes)):]))
                prior_h = math.log2(prior_n) if prior_n > 1 else 0.0
                nthp = entropy / prior_h if prior_h > 0 else 1.0
                entropies.append(entropy); thps.append(thp)
                normalized.append(nthp); losses.append(1.0 - nthp)

            rows.append({
                "seed": seed, "strategy": strategy, "horizon_epochs": horizon,
                "events": count, "targets": len(targets),
                "entropy_mean_bits": float(np.mean(entropies)),
                "thp_mean": float(np.mean(thps)),
                "thp_median": float(np.median(thps)),
                "nthp_mean": float(np.mean(normalized)),
                "tpl_mean": float(np.mean(losses)),
            })

df = pd.DataFrame(rows)
df.to_csv(OUT / "thp_horizon_runs.csv", index=False)
summary = df.groupby(["strategy", "horizon_epochs"]).agg(
    seeds=("seed", "count"),
    entropy_mean_bits=("entropy_mean_bits", "mean"),
    thp_mean=("thp_mean", "mean"),
    thp_median=("thp_median", "median"),
    nthp_mean=("nthp_mean", "mean"),
    tpl_mean=("tpl_mean", "mean"),
).reset_index()
summary.to_csv(OUT / "thp_horizon_summary.csv", index=False)

meta = {
    "status": "development experiment; candidate THP estimator",
    "population": N,
    "daily_rate": DAILY_RATE,
    "sigma_minutes": SIGMA,
    "knowledge_fraction": KNOWLEDGE,
    "seeds": 30,
    "horizons_publication_epochs": HORIZONS,
    "candidate_latent_event_times_used": False,
    "observables": ["publication epoch", "candidate count per epoch", "noisy identity-linked target lifecycle time"],
    "thp_definition": "2**H(C | observable publication history, K_A)",
    "nthp_definition": "H_posterior/log2(number of candidates in retained observable horizon)",
    "tpl_definition": "1-NTHP",
    "causality": "For each target, only publication epochs up to and including its observable publication epoch are used.",
    "boundary": "Synthetic controlled benchmark. Candidate formalization pending literature validation; not a real-world prevalence estimate."
}
(OUT / "thp_horizon_metadata.json").write_text(json.dumps(meta, indent=2))
print(summary.to_string(index=False))
