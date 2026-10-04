from pathlib import Path
import numpy as np, pandas as pd, gzip, base64, json, time, math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"phase5_corrected"; OUT.mkdir(parents=True,exist_ok=True)
N=100_000; CAP=131_072; NBYTES=CAP//8
DAILY_RATE=.002; DURATION=1440; SIGMA=2.0; KNOWLEDGE=.10
SEEDS=range(20261004,20261034)

STRATEGIES=[
 ("M0_immediate",{"kind":"fixed","batch":1}),
 ("M1_fixed_15m",{"kind":"fixed","batch":15}),
 ("M2_fixed_60m",{"kind":"fixed","batch":60}),
 ("M6_adaptive_k10_D30",{"kind":"adaptive","k":10,"max":30}),
 ("M7_adaptive_k25_D60",{"kind":"adaptive","k":25,"max":60}),
]

def publication_times(times,cfg):
    if cfg["kind"]=="fixed":
        b=cfg["batch"]
        return np.minimum(np.ceil(times/b)*b,DURATION)
    k,D=cfg["k"],cfg["max"]; pub=np.empty(len(times)); start=0
    while start<len(times):
        deadline=min(times[start]+D,DURATION); kth=start+k-1
        if kth<len(times) and times[kth]<=deadline:
            end=kth; pt=times[kth]
        else:
            end=max(start,np.searchsorted(times,deadline,side="right")-1); pt=deadline
        pub[start:end+1]=pt; start=end+1
    return pub

def posterior_for_target(target_aux_time, unique_pub_times, groups, cfg):
    eps=1e-300
    weights=[]; candidates=[]
    for pt, ids in zip(unique_pub_times,groups):
        if cfg["kind"]=="fixed":
            b=cfg["batch"]; lo=max(0.0,pt-b); hi=pt
        else:
            lo=max(0.0,pt-cfg["max"]); hi=pt
        xs=np.linspace(lo,hi,64) if hi>lo else np.array([hi])
        dens=np.exp(-0.5*((target_aux_time-xs)/SIGMA)**2)/(SIGMA*np.sqrt(2*np.pi))
        L=max(float(dens.mean()),eps)
        for cid in ids:
            candidates.append(cid); weights.append(L)
    w=np.asarray(weights,float); w/=w.sum()
    return np.asarray(candidates,int),w

def setbits(buf,idxs):
    if len(idxs):
        np.bitwise_or.at(buf,idxs//8,(1 << (7-(idxs%8))).astype(np.uint8))

rows=[]
for seed in SEEDS:
    rng=np.random.default_rng(seed)
    count=int(rng.poisson(N*DAILY_RATE))
    times=np.sort(rng.uniform(0,DURATION,count))
    indexes=rng.choice(CAP,size=count,replace=False)
    targets=np.where(rng.random(count)<KNOWLEDGE)[0]
    aux=times[targets]+rng.normal(0,SIGMA,len(targets))
    for name,cfg in STRATEGIES:
        pubs=publication_times(times,cfg)
        obs=np.round(pubs,9); epochs=np.unique(obs)
        groups=[np.where(obs==e)[0] for e in epochs]
        total_vc=0; enc_ns=0; cumulative=[]
        for e,g in zip(epochs,groups):
            cumulative.extend(indexes[g].tolist())
            buf=np.zeros(NBYTES,dtype=np.uint8); setbits(buf,np.asarray(cumulative,dtype=np.int64))
            t0=time.perf_counter_ns()
            gz=gzip.compress(buf.tobytes(),compresslevel=9,mtime=0)
            enc="u"+base64.urlsafe_b64encode(gz).decode().rstrip("=")
            vc={"@context":["https://www.w3.org/ns/credentials/v2"],"id":"https://example.org/status/revocation/1",
                "type":["VerifiableCredential","BitstringStatusListCredential"],"issuer":"did:example:issuer",
                "validFrom":"2026-10-04T00:00:00Z","credentialSubject":{"id":"https://example.org/status/revocation/1#list",
                "type":"BitstringStatusList","statusPurpose":"revocation","encodedList":enc}}
            payload=json.dumps(vc,separators=(",",":")).encode()
            enc_ns+=time.perf_counter_ns()-t0; total_vc+=len(payload)
        top1_exp=[]; top5_exp=[]; eas=[]; entropy=[]
        for tid,a in zip(targets,aux):
            cand,p=posterior_for_target(a,epochs,groups,cfg)
            loc=np.where(cand==tid)[0]
            if len(loc)!=1: continue
            pt=float(p[loc[0]])
            greater=int(np.sum(p>pt+1e-15))
            tied=int(np.sum(np.isclose(p,pt,rtol=0,atol=1e-15)))
            top1_exp.append(max(0,min(1,(1-greater)/tied)))
            top5_exp.append(max(0,min(1,(5-greater)/tied)))
            eas.append(float(1/np.sum(p*p)))
            entropy.append(float(-np.sum(p*np.log2(p+1e-300))))
        delays=pubs-times
        rows.append({"seed":seed,"strategy":name,"events":count,"targets":len(targets),
                     "publications":len(epochs),"mean_delay_min":float(delays.mean()),
                     "p95_delay_min":float(np.quantile(delays,.95)),
                     "top1_expected":float(np.mean(top1_exp)),"top5_expected":float(np.mean(top5_exp)),
                     "eas_mean":float(np.mean(eas)),"eas_median":float(np.median(eas)),
                     "entropy_mean":float(np.mean(entropy)),"total_vc_bytes":total_vc,
                     "encode_total_ms":enc_ns/1e6})
df=pd.DataFrame(rows); df.to_csv(OUT/"phase5_corrected_runs.csv",index=False)
agg=df.groupby("strategy").agg(
 runs=("seed","count"),publications_mean=("publications","mean"),
 mean_delay_min=("mean_delay_min","mean"),p95_delay_min=("p95_delay_min","mean"),
 top1_expected=("top1_expected","mean"),top5_expected=("top5_expected","mean"),
 eas_mean=("eas_mean","mean"),eas_median=("eas_median","median"),
 entropy_mean=("entropy_mean","mean"),total_vc_bytes_mean=("total_vc_bytes","mean"),
 encode_total_ms_mean=("encode_total_ms","mean")).reset_index()
agg.to_csv(OUT/"phase5_corrected_summary.csv",index=False)
meta={"correction":"Candidate-specific latent true event times are excluded from attacker observations.",
 "attacker_observes":["successive publication epochs","changed pseudonymous indexes per epoch","noisy identity-linked target lifecycle time for A3 targets"],
 "attacker_does_not_observe":["true event time of each candidate index"],
 "tie_handling":"Expected Top-k inclusion probability under random ordering within equal-posterior ties.",
 "adaptive_likelihood_boundary":"Uses only observable publication epoch plus known Dmax support; does not infer hidden trigger event identity.",
 "status":"Corrected primary analysis; supersedes Phase2/2B/3 temporal Top-k claims that used latent candidate event times."}
(OUT/"phase5_corrected_metadata.json").write_text(json.dumps(meta,indent=2))
print(agg.to_string(index=False))
