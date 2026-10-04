#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys, pandas as pd

ROOT=Path(__file__).resolve().parent

def run(script):
    print(f"\n==> {script}")
    subprocess.run([sys.executable, str(ROOT/script)], check=True)

run("src/phase5_corrected_observable_attacker.py")
run("src/phase4_w3c_artifacts.py")
run("src/phase7_corrected_sensitivity.py")
run("src/corrected_statistics.py")

p5=ROOT/"results/phase5_corrected/phase5_corrected_summary.csv"
p4=ROOT/"results/phase4_reproduced/phase4_reproduced_summary.csv"
p7=ROOT/"results/phase7_corrected_sensitivity/phase7_sensitivity_summary.csv"
ci=ROOT/"results/consolidated_corrected/corrected_bootstrap_ci.csv"
assert p5.exists() and p4.exists() and p7.exists() and ci.exists()

d5=pd.read_csv(p5)
required={"M0_immediate","M1_fixed_15m","M2_fixed_60m","M6_adaptive_k10_D30","M7_adaptive_k25_D60"}
assert set(d5["strategy"])==required
assert ((d5["top1_expected"]>=0)&(d5["top1_expected"]<=1)).all()
assert (d5["eas_median"]>=1).all()

d4=pd.read_csv(p4)
assert d4["all_checks_ok"].all()
assert (d4["gzip_bytes"]>0).all()

print("\nReproduction checks passed.")
