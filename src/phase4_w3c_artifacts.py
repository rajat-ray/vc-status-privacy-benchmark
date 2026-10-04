from pathlib import Path
import numpy as np,pandas as pd,gzip,base64,json,time
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results"/"phase4_reproduced"; OUT.mkdir(parents=True,exist_ok=True)
POPS=[1000,10000,100000,1000000]; COUNTS=[0,1,10,100,1000,5000]; RUNS=15
rows=[]
for n in POPS:
 cap=max(131072,n); nb=(cap+7)//8
 for rc0 in COUNTS:
  rc=min(rc0,n)
  for run in range(RUNS):
   rng=np.random.default_rng(20261004+n+rc0*31+run)
   issued=rng.choice(cap,size=n,replace=False) if n < cap else np.arange(cap,dtype=np.int64)
   idx=rng.choice(issued,size=rc,replace=False) if rc else np.array([],dtype=np.int64)
   buf=np.zeros(nb,dtype=np.uint8)
   if rc: np.bitwise_or.at(buf,idx//8,(1<<(7-(idx%8))).astype(np.uint8))
   t0=time.perf_counter_ns()
   gz=gzip.compress(buf.tobytes(),compresslevel=9,mtime=0)
   enc="u"+base64.urlsafe_b64encode(gz).decode().rstrip("=")
   t1=time.perf_counter_ns()
   vc={"@context":["https://www.w3.org/ns/credentials/v2"],"id":"https://example.org/status/1",
       "type":["VerifiableCredential","BitstringStatusListCredential"],"issuer":"did:example:issuer",
       "validFrom":"2026-10-04T00:00:00Z","credentialSubject":{"id":"https://example.org/status/1#list",
       "type":"BitstringStatusList","statusPurpose":"revocation","encodedList":enc}}
   payload=json.dumps(vc,separators=(",",":")).encode()
   e=enc[1:]; e+="="*((4-len(e)%4)%4); raw=gzip.decompress(base64.urlsafe_b64decode(e)); t2=time.perf_counter_ns()
   checks=list(idx[:min(1000,len(idx))])
   ok=all(((raw[i//8]>>(7-(i%8)))&1)==1 for i in checks)
   rows.append({"population":n,"capacity":cap,"revoked":rc,"run":run,"gzip_bytes":len(gz),"vc_json_bytes":len(payload),
                "encode_ms":(t1-t0)/1e6,"decode_ms":(t2-t1)/1e6,"checked_ok":ok})
df=pd.DataFrame(rows); df.to_csv(OUT/"phase4_reproduced_runs.csv",index=False)
agg=df.groupby(["population","capacity","revoked"]).agg(runs=("run","count"),gzip_bytes=("gzip_bytes","mean"),
 vc_json_bytes=("vc_json_bytes","mean"),encode_ms=("encode_ms","mean"),decode_ms=("decode_ms","mean"),
 all_checks_ok=("checked_ok","all")).reset_index()
agg.to_csv(OUT/"phase4_reproduced_summary.csv",index=False)
meta={"implementation":["minimum capacity 131072","MSB/left-most bit index convention","GZIP level 9 mtime=0","multibase-style u prefix + base64url no padding","unsigned BitstringStatusListCredential-shaped JSON"],
"index_assignment":"n issued credentials occupy unique random positions within capacity; revoked positions are sampled only from issued positions.",
"not_implemented":["VC proof/signature","HTTP/CDN retrieval"],"boundary":"Local encoding/decoding artifact benchmark, not a complete signed deployment."}
(OUT/"phase4_reproduced_metadata.json").write_text(json.dumps(meta,indent=2))
print(agg[(agg.population.isin([100000,1000000])) & (agg.revoked.isin([10,100,1000,5000]))].to_string(index=False))
