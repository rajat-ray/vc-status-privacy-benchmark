#!/usr/bin/env python3
import argparse, csv, json, math, random
from pathlib import Path
MIN_W3C_CAPACITY = 131072
def effective_anonymity_uniform(k):
    if k <= 0: return None
    p=1.0/k
    return 1.0/(k*p*p)
def entropy_uniform(k): return None if k<=0 else math.log2(k)
def run_population(n,intervals,event_rate,seed):
    rng=random.Random(seed+n); capacity=max(MIN_W3C_CAPACITY,n)
    indexes=rng.sample(range(capacity),n); state=bytearray(capacity); rows=[]
    for t in range(1,intervals+1):
        active=[idx for idx in indexes if state[idx]==0]
        changed=[idx for idx in active if rng.random()<event_rate]
        before=state[:]
        for idx in changed: state[idx]=1
        observed_delta=[i for i,(a,b) in enumerate(zip(before,state)) if a!=b]
        k=len(observed_delta); csr=None if k==0 else 1.0-(k/n)
        rows.append({"population":n,"capacity":capacity,"interval":t,"event_rate":event_rate,
        "changed_indexes":k,"candidate_set_size_A0":n,"candidate_set_size_A1":k if k else "",
        "candidate_set_reduction_A1":csr if csr is not None else "",
        "entropy_bits_A1":entropy_uniform(k) if k else "",
        "effective_anonymity_A1":effective_anonymity_uniform(k) if k else "","seed":seed})
    return rows
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--populations",nargs="+",type=int,default=[1000,10000,100000])
    ap.add_argument("--intervals",type=int,default=30); ap.add_argument("--event-rate",type=float,default=.001)
    ap.add_argument("--seed",type=int,default=20261004); ap.add_argument("--out",default="results"); args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True); rows=[]
    for n in args.populations: rows.extend(run_population(n,args.intervals,args.event_rate,args.seed))
    with open(out/"phase1_intervals.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    summary={"phase":"Phase 1 baseline","model":"Bitstring Status List-style state with random status-list index allocation",
    "observer_A0":"single snapshot","observer_A1":"successive-state differencing","populations":args.populations,
    "intervals":args.intervals,"event_rate":args.event_rate,"seed":args.seed,"w3c_minimum_capacity_used":MIN_W3C_CAPACITY,
    "interpretation_boundary":"A1 reveals changed pseudonymous indexes, not holder identities. EAS uses a uniform posterior within the observed changed-index set."}
    (out/"phase1_summary.json").write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
