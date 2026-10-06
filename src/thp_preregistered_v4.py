from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"thp_preregistered_v4"; OUT.mkdir(parents=True,exist_ok=True)

COHORT=4096; DAYS=64; HAZARD=.002; SIGMA=2.0
SEEDS=range(20261004,20261034); HORIZONS=[1,2,4,8,16,32,64]
TARGET_N=256
STRATEGIES=[
 ("immediate",{"kind":"fixed","batch":1}),
 ("fixed15",{"kind":"fixed","batch":15}),
 ("fixed60",{"kind":"fixed","batch":60}),
 ("adaptive10D30",{"kind":"adaptive","k":10,"max":30}),
 ("adaptive25D60",{"kind":"adaptive","k":25,"max":60}),
]
ATTACKERS=["A1_longitudinal","A2_noisy_time","A3_known10pct"]

def pubs(times,cfg,duration):
    if len(times)==0:return np.array([],float)
    if cfg["kind"]=="fixed":
        b=cfg["batch"]; return np.minimum(np.ceil(times/b)*b,duration)
    k,D=cfg["k"],cfg["max"]; out=np.empty(len(times)); s=0
    while s<len(times):
        dl=min(times[s]+D,duration); kth=s+k-1
        if kth<len(times) and times[kth]<=dl: e=kth; pt=times[kth]
        else:e=max(s,np.searchsorted(times,dl,side="right")-1); pt=dl
        out[s:e+1]=pt;s=e+1
    return out

def target_entropy(cid,cutoff,event_ids,pub_by_id,epoch_members,attacker,aux,known_ids):
    # Fixed prior over baseline credential identities. Observations are publication
    # deltas up to cutoff. No candidate latent event times are exposed.
    changed={int(x) for e,m in epoch_members.items() if e<=cutoff for x in m}
    if cid in changed:
        ep=float(np.round(pub_by_id[cid],9)); candidates=set(map(int,epoch_members[ep]))
    else:
        candidates=set(range(COHORT))-changed
    if attacker=="A3_known10pct":
        # Bounded auxiliary knowledge removes identities whose lifecycle outcome
        # through cutoff is externally known and inconsistent with target observation.
        candidates-=({int(x) for x in known_ids if int(x)!=cid})
        candidates.add(cid)
    # A2 target-linked noisy time is used only after a transition is observable.
    # Within one publication epoch candidate latent times remain hidden, so members tie.
    # This intentionally tests whether timing adds anything beyond epoch grouping.
    n=max(1,len(candidates)); return math.log2(n),n

rows=[]
for seed in SEEDS:
    rng=np.random.default_rng(seed)
    # PRE-REGISTERED target sample: chosen before lifecycle outcomes.
    targets=np.sort(rng.choice(COHORT,size=TARGET_N,replace=False))
    known_ids=set(rng.choice([x for x in range(COHORT) if x not in set(targets)],
                             size=int(.10*COHORT),replace=False).tolist())
    revoked=rng.random(COHORT)<(1-(1-HAZARD)**DAYS)
    event_min=np.full(COHORT,np.nan)
    probs=(1-HAZARD)**np.arange(DAYS)*HAZARD; probs/=probs.sum()
    for cid in np.where(revoked)[0]:
        d=int(rng.choice(DAYS,p=probs)); event_min[cid]=d*1440+rng.uniform(0,1440)
    event_ids=np.where(revoked)[0]; order=np.argsort(event_min[event_ids])
    event_ids=event_ids[order]; times=event_min[event_ids]
    aux={int(cid):float(event_min[cid]+rng.normal(0,SIGMA)) for cid in targets if revoked[cid]}
    duration=DAYS*1440.0

    for strategy,cfg in STRATEGIES:
        p=pubs(times,cfg,duration); pub_by_id={int(c):float(x) for c,x in zip(event_ids,p)}
        epochs=np.unique(np.round(p,9))
        epoch_members={float(e):event_ids[np.isclose(p,e,rtol=0,atol=1e-9)] for e in epochs}
        for attacker in ATTACKERS:
            prev={int(c):math.log2(COHORT) for c in targets}
            for H in HORIZONS:
                cutoff=H*1440.0; vals=[]; changed_vals=[]; unchanged_vals=[]
                for cid0 in targets:
                    cid=int(cid0)
                    ent,n=target_entropy(cid,cutoff,event_ids,pub_by_id,epoch_members,
                                         attacker,aux.get(cid),known_ids)
                    # Internal invariant: cumulative observations may not increase
                    # posterior entropy for a fixed target under this set model.
                    if ent>prev[cid]+1e-12:
                        raise AssertionError(f"entropy increased seed={seed} target={cid} H={H}")
                    prev[cid]=ent
                    rec=(ent,2**ent,ent/math.log2(COHORT),1-ent/math.log2(COHORT))
                    vals.append(rec)
                    if revoked[cid] and pub_by_id[cid]<=cutoff: changed_vals.append(rec)
                    else: unchanged_vals.append(rec)
                a=np.asarray(vals,float)
                rows.append({"seed":seed,"strategy":strategy,"attacker":attacker,
                    "horizon_days":H,"targets":TARGET_N,
                    "changed_targets":len(changed_vals),"unchanged_targets":len(unchanged_vals),
                    "entropy_mean_bits":float(a[:,0].mean()),"thp_mean":float(a[:,1].mean()),
                    "thp_median":float(np.median(a[:,1])),"nthp_mean":float(a[:,2].mean()),
                    "tpl_mean":float(a[:,3].mean()),
                    "changed_thp_mean":float(np.mean([x[1] for x in changed_vals])) if changed_vals else np.nan,
                    "unchanged_thp_mean":float(np.mean([x[1] for x in unchanged_vals])) if unchanged_vals else np.nan})

df=pd.DataFrame(rows); df.to_csv(OUT/"runs.csv",index=False)
summary=df.groupby(["strategy","attacker","horizon_days"]).agg(
 seeds=("seed","count"),thp_mean=("thp_mean","mean"),thp_median=("thp_median","median"),
 nthp_mean=("nthp_mean","mean"),tpl_mean=("tpl_mean","mean"),
 changed_thp_mean=("changed_thp_mean","mean"),unchanged_thp_mean=("unchanged_thp_mean","mean")).reset_index()
summary.to_csv(OUT/"summary.csv",index=False)
meta={
 "status":"pre-registered development v4; requires independent audit before manuscript use",
 "target_sampling":"256 identities sampled uniformly from full baseline cohort before lifecycle outcomes",
 "cohort":COHORT,"days":DAYS,"daily_hazard":HAZARD,"seeds":30,"horizons_days":HORIZONS,
 "estimands":["unconditional credential privacy","changed-target conditional privacy","unchanged-target privacy"],
 "attackers":{"A1_longitudinal":"publication deltas only",
              "A2_noisy_time":"A1 plus noisy identity-linked time; candidate latent times forbidden",
              "A3_known10pct":"A1 plus identities of a disjoint 10% baseline subset externally known"},
 "important_design_null":"A2 noisy time cannot discriminate candidates tied within one observable publication epoch when candidate latent times are hidden.",
 "candidate_latent_event_times_used":False,
 "prior":"same uniform baseline cohort for all targets and horizons",
 "boundary":"synthetic controlled benchmark; no real-world prevalence or W3C-conformance claim"}
(OUT/"metadata.json").write_text(json.dumps(meta,indent=2))
print(summary.to_string(index=False))
