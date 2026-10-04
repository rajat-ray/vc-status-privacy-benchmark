from pathlib import Path
import pandas as pd,numpy as np,json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results"/"consolidated_corrected"; OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(ROOT/"results"/"phase5_corrected"/"phase5_corrected_runs.csv")
def bci(x,reps=5000,seed=20261004):
 x=np.asarray(x,float); rng=np.random.default_rng(seed)
 means=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(reps)])
 return float(x.mean()),float(np.quantile(means,.025)),float(np.quantile(means,.975))
recs=[]
for s,g in df.groupby("strategy"):
 r={"strategy":s,"n_seeds":len(g)}
 for col in ["mean_delay_min","top1_expected","top5_expected","eas_mean","eas_median","total_vc_bytes","encode_total_ms"]:
  m,l,h=bci(g[col]); r[col+"_mean"]=m;r[col+"_ci95_low"]=l;r[col+"_ci95_high"]=h
 recs.append(r)
pd.DataFrame(recs).to_csv(OUT/"corrected_bootstrap_ci.csv",index=False)
a=df[df.strategy=="M6_adaptive_k10_D30"].set_index("seed"); f=df[df.strategy=="M2_fixed_60m"].set_index("seed")
pair={}
for col in ["mean_delay_min","top1_expected","top5_expected","eas_mean","eas_median","total_vc_bytes","encode_total_ms"]:
 m,l,h=bci((a[col]-f[col]).dropna()); pair[col]={"adaptive_minus_fixed60_mean":m,"ci95":[l,h]}
pair["delay_relative_reduction"]=float(1-a.mean_delay_min.mean()/f.mean_delay_min.mean())
(OUT/"corrected_paired_adaptive_vs_fixed60.json").write_text(json.dumps(pair,indent=2))
print("Corrected bootstrap and paired statistics regenerated.")
