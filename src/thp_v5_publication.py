from pathlib import Path
import json, hashlib, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"results"/"thp_preregistered_v4"/"runs.csv"
OUT=ROOT/"results"/"thp_v5_publication"; OUT.mkdir(parents=True,exist_ok=True)

df=pd.read_csv(SRC)
EXPECTED=30*5*3*7
assert len(df)==EXPECTED, (len(df),EXPECTED)
keys=["seed","strategy","attacker","horizon_days"]
assert not df.duplicated(keys).any()
assert (df["changed_targets"]+df["unchanged_targets"]==256).all()
assert df["thp_mean"].between(1,4096).all()
assert df["thp_median"].between(1,4096).all()
assert df["nthp_mean"].between(0,1).all()
assert df["tpl_mean"].between(0,1).all()

# Complete-cell seed audit.
cell=df.groupby(["strategy","attacker","horizon_days"])["seed"].nunique()
assert (cell==30).all()

# A1/A2 exact-null audit under v4's declared observable-only model.
a1=df[df.attacker=="A1_longitudinal"].sort_values(["seed","strategy","horizon_days"])
a2=df[df.attacker=="A2_noisy_time"].sort_values(["seed","strategy","horizon_days"])
for c in ["thp_mean","thp_median","nthp_mean","tpl_mean","changed_thp_mean","unchanged_thp_mean"]:
    x=a1[c].to_numpy(); y=a2[c].to_numpy()
    assert np.allclose(x,y,equal_nan=True,rtol=0,atol=1e-12), c

# Publication summary with 95% t CI (df=29, two-sided).
TCRIT=2.045229642132703
records=[]
for g,sub in df.groupby(["strategy","attacker","horizon_days"]):
    for metric in ["thp_mean","nthp_mean","tpl_mean","changed_thp_mean","unchanged_thp_mean"]:
        x=sub[metric].dropna().to_numpy(float); n=len(x)
        mean=float(np.mean(x)); sd=float(np.std(x,ddof=1)) if n>1 else float("nan")
        half=TCRIT*sd/math.sqrt(n) if n>1 else float("nan")
        records.append({"strategy":g[0],"attacker":g[1],"horizon_days":g[2],
          "metric":metric,"n":n,"mean":mean,"sd":sd,"ci95_low":mean-half,"ci95_high":mean+half})
summary=pd.DataFrame(records)
summary.to_csv(OUT/"publication_summary.csv",index=False)

# Paired effects at every horizon: publication strategies vs immediate, and A3 vs A1.
effects=[]
for attacker in df.attacker.unique():
  for H in sorted(df.horizon_days.unique()):
    base=df[(df.attacker==attacker)&(df.horizon_days==H)&(df.strategy=="immediate")].set_index("seed")
    for strategy in [s for s in df.strategy.unique() if s!="immediate"]:
      alt=df[(df.attacker==attacker)&(df.horizon_days==H)&(df.strategy==strategy)].set_index("seed")
      d=(alt["thp_mean"]-base["thp_mean"]).to_numpy(float); n=len(d); m=float(d.mean()); sd=float(d.std(ddof=1)); half=TCRIT*sd/math.sqrt(n)
      effects.append({"contrast":f"{strategy}-immediate","attacker":attacker,"horizon_days":H,
                      "metric":"thp_mean","n":n,"mean_difference":m,"ci95_low":m-half,"ci95_high":m+half})
for strategy in df.strategy.unique():
  for H in sorted(df.horizon_days.unique()):
    x=df[(df.strategy==strategy)&(df.horizon_days==H)&(df.attacker=="A1_longitudinal")].set_index("seed")
    y=df[(df.strategy==strategy)&(df.horizon_days==H)&(df.attacker=="A3_known10pct")].set_index("seed")
    d=(y["thp_mean"]-x["thp_mean"]).to_numpy(float); n=len(d); m=float(d.mean()); sd=float(d.std(ddof=1)); half=TCRIT*sd/math.sqrt(n)
    effects.append({"contrast":"A3-A1","attacker":"paired","strategy":strategy,"horizon_days":H,
                    "metric":"thp_mean","n":n,"mean_difference":m,"ci95_low":m-half,"ci95_high":m+half})
pd.DataFrame(effects).to_csv(OUT/"paired_effects.csv",index=False)

# Preserve exact v4 run evidence as v5 confirmation input.
df.to_csv(OUT/"v5_confirmed_runs.csv",index=False)
meta={"status":"publication-grade statistical confirmation of preregistered v4 evidence",
      "source":"results/thp_preregistered_v4/runs.csv",
      "expected_rows":EXPECTED,"seeds_per_cell":30,
      "a1_a2_null":"exact within 1e-12 for declared output metrics",
      "ci":"two-sided 95% t interval, df=29 where n=30",
      "claim_boundary":"THP is adapted entropy/effective-anonymity measurement in a synthetic fixed-cohort credential-status model."}
(OUT/"metadata.json").write_text(json.dumps(meta,indent=2))

audit={"rows":len(df),"unique_seeds":int(df.seed.nunique()),"complete_cells":int(len(cell)),
       "duplicate_rows":int(df.duplicated(keys).sum()),"a1_a2_exact_null":True,
       "changed_plus_unchanged_ok":bool((df.changed_targets+df.unchanged_targets==256).all()),
       "bounds_ok":True}
(OUT/"audit.json").write_text(json.dumps(audit,indent=2))

for p in sorted(OUT.iterdir()):
    if p.is_file():
        print(p.name,hashlib.sha256(p.read_bytes()).hexdigest())
