from pathlib import Path
import numpy as np,pandas as pd,json,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"phase7_corrected_sensitivity"; OUT.mkdir(parents=True,exist_ok=True)
N=100_000; CAP=131_072; DURATION=1440
SEEDS=range(20261004,20261034)
SIGMAS=[0.5,2.0,10.0]
RATES=[0.0005,0.002,0.005]
PATTERNS=["uniform","clustered"]
STRATEGIES=[
 ("immediate",{"kind":"fixed","batch":1}),
 ("fixed15",{"kind":"fixed","batch":15}),
 ("fixed60",{"kind":"fixed","batch":60}),
 ("random60",{"kind":"random","D":60}),
 ("adaptive10D30",{"kind":"adaptive","k":10,"max":30}),
]

def gen_times(rng,count,pattern):
    if pattern=="uniform": return np.sort(rng.uniform(0,DURATION,count))
    m=int(round(.7*count)); centers=np.array([9*60,13*60,18*60])
    t=np.concatenate([rng.normal(rng.choice(centers,m),20),rng.uniform(0,DURATION,count-m)])
    return np.sort(np.clip(t,0,DURATION))

def pubs_for(times,cfg,rng):
    if cfg["kind"]=="fixed":
        b=cfg["batch"]; return np.minimum(np.ceil(times/b)*b,DURATION)
    if cfg["kind"]=="random":
        return np.minimum(times+rng.uniform(0,cfg["D"],len(times)),DURATION)
    k,D=cfg["k"],cfg["max"]; pub=np.empty(len(times)); start=0
    while start<len(times):
        deadline=min(times[start]+D,DURATION); kth=start+k-1
        if kth<len(times) and times[kth]<=deadline: end=kth; pt=times[kth]
        else: end=max(start,np.searchsorted(times,deadline,side="right")-1); pt=deadline
        pub[start:end+1]=pt; start=end+1
    return pub

def normcdf(z): return .5*(1+math.erf(z/math.sqrt(2)))
def epoch_likelihood(aux,pt,cfg,sigma):
    if cfg["kind"]=="fixed":
        lo=max(0,pt-cfg["batch"]); hi=pt
    elif cfg["kind"]=="random":
        lo=max(0,pt-cfg["D"]); hi=pt
    else:
        lo=max(0,pt-cfg["max"]); hi=pt
    if hi<=lo: return 1e-300
    return max((normcdf((hi-aux)/sigma)-normcdf((lo-aux)/sigma))/(hi-lo),1e-300)

rows=[]
for seed in SEEDS:
  base=np.random.default_rng(seed)
  for rate in RATES:
    count=int(base.poisson(N*rate))
    for pattern in PATTERNS:
      rng=np.random.default_rng(seed + int(rate*1e7) + (100000 if pattern=="clustered" else 0))
      times=gen_times(rng,count,pattern)
      targets=rng.choice(len(times),size=max(1,int(.10*len(times))),replace=False)
      for sigma in SIGMAS:
        aux=times[targets]+rng.normal(0,sigma,len(targets))
        for si,(name,cfg) in enumerate(STRATEGIES):
          prng=np.random.default_rng(seed+si*99991+int(rate*1e8)+(7 if pattern=="clustered" else 0))
          pubs=pubs_for(times,cfg,prng)
          epochs=np.unique(np.round(pubs,9)); groups=[np.where(np.round(pubs,9)==e)[0] for e in epochs]
          e_top1=[]; e_top5=[]; e_eas=[]
          for tid,a in zip(targets,aux):
            ws=[]; ids=[]
            for pt,g in zip(epochs,groups):
              L=epoch_likelihood(a,float(pt),cfg,sigma)
              ws.extend([L]*len(g)); ids.extend(g.tolist())
            w=np.asarray(ws,float); w/=w.sum(); ids=np.asarray(ids)
            pos=np.where(ids==tid)[0]
            if len(pos)!=1: continue
            ptar=w[pos[0]]
            greater=int(np.sum(w>ptar+1e-15)); tied=int(np.sum(np.isclose(w,ptar,rtol=0,atol=1e-15)))
            e_top1.append(max(0,min(1,(1-greater)/tied)))
            e_top5.append(max(0,min(1,(5-greater)/tied)))
            e_eas.append(1/np.sum(w*w))
          rows.append({"seed":seed,"rate":rate,"pattern":pattern,"sigma_min":sigma,"strategy":name,
                       "events":count,"publications":len(epochs),"mean_delay_min":float(np.mean(pubs-times)),
                       "top1_expected":float(np.mean(e_top1)),"top5_expected":float(np.mean(e_top5)),
                       "eas_mean":float(np.mean(e_eas)),"eas_median":float(np.median(e_eas))})
df=pd.DataFrame(rows); df.to_csv(OUT/"phase7_sensitivity_runs.csv",index=False)
summary=df.groupby(["rate","pattern","sigma_min","strategy"]).agg(
 seeds=("seed","count"),events_mean=("events","mean"),publications_mean=("publications","mean"),
 delay_mean=("mean_delay_min","mean"),top1_mean=("top1_expected","mean"),
 top5_mean=("top5_expected","mean"),eas_mean=("eas_mean","mean"),eas_median=("eas_median","median")).reset_index()
summary.to_csv(OUT/"phase7_sensitivity_summary.csv",index=False)
meta={"purpose":"Corrected observable-only sensitivity matrix and corrected random-delay experiment.",
      "candidate_latent_times_used":False,
      "conditions":{"population":N,"rates":RATES,"patterns":PATTERNS,"sigma_minutes":SIGMAS,"seeds":30},
      "random_delay":"Independent U(0,60m) publication delay; observer sees each resulting publication time and knows the delay distribution.",
      "cluster_model":"70% Gaussian bursts around 09:00, 13:00, 18:00 with SD 20m; 30% uniform background.",
      "boundary":"Synthetic sensitivity study; results are conditional on declared event and auxiliary-timing models."}
(OUT/"phase7_metadata.json").write_text(json.dumps(meta,indent=2))
print(summary[(summary.rate==.002)&(summary.pattern=="uniform")][["sigma_min","strategy","delay_mean","top1_mean","eas_median"]].to_string(index=False))
