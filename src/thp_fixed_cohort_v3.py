from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"thp_fixed_cohort_v3"; OUT.mkdir(parents=True,exist_ok=True)

N=100_000
COHORT=4096
DAYS=64
DAILY_HAZARD=0.002
SIGMA_MIN=2.0
KNOWLEDGE=0.10
SEEDS=range(20261004,20261034)
HORIZONS=[1,2,4,8,16,32,64]
STRATEGIES=[
 ("M0_immediate",{"kind":"fixed","batch":1}),
 ("M1_fixed_15m",{"kind":"fixed","batch":15}),
 ("M2_fixed_60m",{"kind":"fixed","batch":60}),
 ("M6_adaptive_k10_D30",{"kind":"adaptive","k":10,"max":30}),
 ("M7_adaptive_k25_D60",{"kind":"adaptive","k":25,"max":60}),
]

def publication_times(times,cfg,duration):
    if len(times)==0: return np.array([],float)
    if cfg["kind"]=="fixed":
        b=cfg["batch"]; return np.minimum(np.ceil(times/b)*b,duration)
    k,D=cfg["k"],cfg["max"]; pub=np.empty(len(times)); start=0
    while start<len(times):
        deadline=min(times[start]+D,duration); kth=start+k-1
        if kth<len(times) and times[kth]<=deadline: end=kth; pt=times[kth]
        else: end=max(start,np.searchsorted(times,deadline,side="right")-1); pt=deadline
        pub[start:end+1]=pt; start=end+1
    return pub

def normal_cdf(z): return .5*(1+math.erf(z/math.sqrt(2)))
def likelihood(aux,pt,cfg):
    width=cfg["batch"] if cfg["kind"]=="fixed" else cfg["max"]
    lo=max(0.0,pt-width); hi=pt
    if hi<=lo:return 1e-300
    return max((normal_cdf((hi-aux)/SIGMA_MIN)-normal_cdf((lo-aux)/SIGMA_MIN))/(hi-lo),1e-300)

rows=[]
for seed in SEEDS:
    rng=np.random.default_rng(seed)
    # Fixed cohort: each credential is present at baseline and may experience at most
    # one irreversible revocation during the 64-day observation window.
    revoked=rng.random(COHORT) < (1-(1-DAILY_HAZARD)**DAYS)
    event_day=np.full(COHORT,-1,int); event_min=np.full(COHORT,np.nan)
    for cid in np.where(revoked)[0]:
        # geometric first-event day conditioned on occurring within window
        probs=(1-DAILY_HAZARD)**np.arange(DAYS)*DAILY_HAZARD
        probs=probs/probs.sum()
        d=int(rng.choice(DAYS,p=probs)); event_day[cid]=d
        event_min[cid]=d*1440+rng.uniform(0,1440)
    event_ids=np.where(revoked)[0]
    order=np.argsort(event_min[event_ids]); event_ids=event_ids[order]
    true_times=event_min[event_ids]
    targets=event_ids[rng.random(len(event_ids))<KNOWLEDGE]
    aux={int(cid):float(event_min[cid]+rng.normal(0,SIGMA_MIN)) for cid in targets}
    duration=DAYS*1440.0

    for strategy,cfg in STRATEGIES:
        pubs=publication_times(true_times,cfg,duration)
        pub_by_id={int(cid):float(pt) for cid,pt in zip(event_ids,pubs)}
        # Observer sees cumulative list snapshots. Delta epochs identify changed
        # pseudonymous indexes but not identities; target auxiliary time is K_A.
        epochs=np.unique(np.round(pubs,9))
        epoch_members={float(e):event_ids[np.isclose(pubs,e,rtol=0,atol=1e-9)] for e in epochs}
        for H in HORIZONS:
            cutoff=H*1440.0
            observed=[float(e) for e in epochs if e<=cutoff]
            # Prior candidate universe remains the same COHORT for every H.
            # For a target whose event has not yet appeared, all not-yet-changed
            # cohort members remain candidates. Once its delta appears, posterior
            # is restricted to that observable epoch and timing likelihood.
            vals=[]
            for cid in targets:
                prior_h=math.log2(COHORT)
                target_pub=pub_by_id[int(cid)]
                if target_pub>cutoff:
                    changed=sum(len(epoch_members[e]) for e in observed)
                    n=max(1,COHORT-changed)
                    ent=math.log2(n)
                else:
                    members=epoch_members[float(np.round(target_pub,9))]
                    # all members of same observable epoch share publication support;
                    # with target-linked noisy time and no candidate latent times,
                    # they remain tied within that epoch.
                    n=max(1,len(members))
                    ent=math.log2(n)
                thp=2**ent
                nthp=ent/prior_h
                vals.append((ent,thp,nthp,1-nthp))
            if vals:
                a=np.asarray(vals,float)
                rows.append({"seed":seed,"strategy":strategy,"horizon_days":H,
                  "cohort":COHORT,"revoked_events":len(event_ids),"targets":len(targets),
                  "entropy_mean_bits":float(a[:,0].mean()),"thp_mean":float(a[:,1].mean()),
                  "thp_median":float(np.median(a[:,1])),"nthp_mean":float(a[:,2].mean()),
                  "tpl_mean":float(a[:,3].mean())})

df=pd.DataFrame(rows); df.to_csv(OUT/"thp_fixed_cohort_runs.csv",index=False)
summary=df.groupby(["strategy","horizon_days"]).agg(
 seeds=("seed","count"),entropy_mean_bits=("entropy_mean_bits","mean"),
 thp_mean=("thp_mean","mean"),thp_median=("thp_median","median"),
 nthp_mean=("nthp_mean","mean"),tpl_mean=("tpl_mean","mean")).reset_index()
summary.to_csv(OUT/"thp_fixed_cohort_summary.csv",index=False)
meta={
 "status":"development fixed-cohort longitudinal experiment",
 "cohort":COHORT,"days":DAYS,"daily_hazard":DAILY_HAZARD,"seeds":30,
 "horizons_days":HORIZONS,"candidate_universe":"fixed at baseline for all horizons",
 "event_semantics":"at most one irreversible revocation per credential in observation window",
 "observables":["cumulative snapshots","delta publication epoch","changed pseudonymous indexes"],
 "auxiliary_knowledge":"noisy identity-linked lifecycle time for 10% target sample",
 "candidate_latent_event_times_used":False,
 "important_null":"unchanged repeated snapshots add no target-specific evidence in this model",
 "boundary":"Synthetic controlled experiment; candidate THP formalization pending literature validation."
}
(OUT/"metadata.json").write_text(json.dumps(meta,indent=2))
print(summary.to_string(index=False))
