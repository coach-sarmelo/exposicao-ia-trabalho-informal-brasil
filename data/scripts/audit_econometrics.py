"""audit_econometrics.py — Performs full econometric and numerical verification."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(ROOT, 'data/output/econometrics.json'), 'r', encoding='utf-8') as f:
    econ = json.load(f)

with open(os.path.join(ROOT, 'data/output/robustness.json'), 'r', encoding='utf-8') as f:
    rob = json.load(f)

with open(os.path.join(ROOT, 'data/output/statistics.json'), 'r', encoding='utf-8') as f:
    stats = json.load(f)

print("="*70)
print("1. ECONOMETRIC SPECIFICATIONS AUDIT (S1 - S4)")
print("="*70)

for s in ['S1', 'S2', 'S3', 'S3a', 'S4']:
    res = econ['specifications'][s]['results_clustered_occupation']
    betas = [round(b, 4) for b in res['beta']]
    ses = [round(se, 4) for se in res['se']]
    pvals = [f"{p:.2e}" for p in res['p_value']]
    print(f"\nSpecification {s}:")
    print(f"  Description : {econ['specifications'][s]['description']}")
    print(f"  Sample N    : {res['n']} (Clusters: {res['n_clusters']})")
    print(f"  R-squared   : {res['r_squared']:.4f}")
    print(f"  Betas (1-4) : {betas[:4]}")
    print(f"  SEs (1-4)   : {ses[:4]}")
    print(f"  P-vals (1-4): {pvals[:4]}")

print("\n" + "="*70)
print("2. PARITY CHECKS AGAINST MANUSCRIPT CLAIMS")
print("="*70)

# S1
b_s1 = econ['specifications']['S1']['results_clustered_occupation']['beta'][1]
se_s1 = econ['specifications']['S1']['results_clustered_occupation']['se'][1]
r2_s1 = econ['specifications']['S1']['results_clustered_occupation']['r_squared']
print(f"S1 Schooling beta: {b_s1:.4f} vs Paper 0,23 | SE: {se_s1:.4f} vs Paper 0,03 | R2: {r2_s1:.4f} vs Paper 0,246 [MATCH: {abs(b_s1 - 0.23) < 0.005}]")

# S2
b_s2_e = econ['specifications']['S2']['results_clustered_occupation']['beta'][1]
se_s2_e = econ['specifications']['S2']['results_clustered_occupation']['se'][1]
b_s2_w = econ['specifications']['S2']['results_clustered_occupation']['beta'][2] * 1000.0
se_s2_w = econ['specifications']['S2']['results_clustered_occupation']['se'][2] * 1000.0
print(f"S2 Schooling beta: {b_s2_e:.4f} vs Paper 0,21 | SE: {se_s2_e:.4f} vs Paper 0,03 [MATCH: {abs(b_s2_e - 0.21) < 0.005}]")
print(f"S2 Income/1k beta: {b_s2_w:.4f} vs Paper 0,043 | SE: {se_s2_w:.4f} vs Paper 0,010 [MATCH: {abs(b_s2_w - 0.043) < 0.001}]")

# S3 & S3a
b_s3a = econ['specifications']['S3a']['results_clustered_occupation']['beta'][1]
se_s3a = econ['specifications']['S3a']['results_clustered_occupation']['se'][1]
b_s3 = econ['specifications']['S3']['results_clustered_occupation']['beta'][1]
se_s3 = econ['specifications']['S3']['results_clustered_occupation']['se'][1]
b_s3_e = econ['specifications']['S3']['results_clustered_occupation']['beta'][2]
se_s3_e = econ['specifications']['S3']['results_clustered_occupation']['se'][2]
att = (abs(b_s3a) - abs(b_s3)) / abs(b_s3a) * 100.0
direct = 100.0 - att

print(f"S3a Exposure beta: {b_s3a:.4f} vs Paper -6,23 | SE: {se_s3a:.4f} vs Paper 0,99 [MATCH: {abs(b_s3a - -6.23) < 0.005}]")
print(f"S3 Exposure beta : {b_s3:.4f} vs Paper -3,91 | SE: {se_s3:.4f} vs Paper 0,96 [MATCH: {abs(b_s3 - -3.91) < 0.005}]")
print(f"S3 Schooling beta: {b_s3_e:.4f} vs Paper -2,61 | SE: {se_s3_e:.4f} vs Paper 0,27 [MATCH: {abs(b_s3_e - -2.61) < 0.005}]")
print(f"Mediation Attenuation: {att:.2f}% vs Paper 37,2% [MATCH: {abs(att - 37.2) < 0.1}]")
print(f"Direct Effect Retained: {direct:.2f}% vs Paper 62,8% [MATCH: {abs(direct - 62.8) < 0.1}]")

# S4
b_s4_e = econ['specifications']['S4']['results_clustered_occupation']['beta'][1]
se_s4_e = econ['specifications']['S4']['results_clustered_occupation']['se'][1]
b_s4_int = econ['specifications']['S4']['results_clustered_occupation']['beta'][2]
se_s4_int = econ['specifications']['S4']['results_clustered_occupation']['se'][2]
b_s4_f = econ['specifications']['S4']['results_clustered_occupation']['beta'][3]
se_s4_f = econ['specifications']['S4']['results_clustered_occupation']['se'][3]
print(f"S4 Interaction beta: {b_s4_int:.4f} vs Paper 0,28 | SE: {se_s4_int:.4f} vs Paper 0,06 [MATCH: {abs(b_s4_int - 0.28) < 0.005}]")
print(f"S4 Formality beta  : {b_s4_f:.4f} vs Paper -3,10 | SE: {se_s4_f:.4f} vs Paper 0,77 [MATCH: {abs(b_s4_f - -3.10) < 0.005}]")
print(f"S4 Schooling beta  : {b_s4_e:.4f} vs Paper 0,07 | SE: {se_s4_e:.4f} vs Paper 0,03 [MATCH: {abs(b_s4_e - 0.07) < 0.005}]")

# Threshold
e_star = abs(b_s4_f) / b_s4_int
print(f"S4 Polarization Threshold e* = {abs(b_s4_f):.4f} / {b_s4_int:.4f} = {e_star:.2f} years (Paper: ~11 anos)")

# State gradients
grad_sp = b_s4_e + b_s4_int * 0.65
grad_ma = b_s4_e + b_s4_int * 0.40
print(f"Gradient SP (65% formal): {grad_sp:.4f} vs Paper ~0,25")
print(f"Gradient MA (40% formal): {grad_ma:.4f} vs Paper ~0,18")

print("\n" + "="*70)
print("3. ROBUSTNESS SUITE AUDIT (R1 - R7)")
print("="*70)
# R1 OLS vs WLS
b_ols = rob['R1_weighting']['unweighted']['beta'][1]
se_ols = rob['R1_weighting']['unweighted']['se'][1]
print(f"R1 OLS Schooling: {b_ols:.4f} (SE {se_ols:.4f}) vs Paper 0,21 (0,03) [MATCH: {abs(b_ols - 0.21) < 0.005}]")

# R2 Wild Bootstrap
w_boot = rob['R2_wild_bootstrap_s4']['bootstrap_region']
print(f"R2 Wild Cluster Bootstrap (27 UFs) S4 interaction p-value: {w_boot.get('p_value', 'N/A')}")

# R4 log outcome
b_log = rob['R4_log_outcome']['results']['beta'][1]
se_log = rob['R4_log_outcome']['results']['se'][1]
print(f"R4 log(1+theta) Schooling: {b_log:.4f} (SE {se_log:.4f}) vs Paper 0,07 (0,01) [MATCH: {abs(b_log - 0.07) < 0.005}]")

# R5 Outliers
b_win = rob['R5_outliers']['winsorized_1_99']['beta'][1]
se_win = rob['R5_outliers']['winsorized_1_99']['se'][1]
print(f"R5 Winsor 1% Schooling: {b_win:.4f} (SE {se_win:.4f}) vs Paper 0,23 (0,03) [MATCH: {abs(b_win - 0.23) < 0.005}]")

b_trim = rob['R5_outliers']['dropped_above_p99']['beta'][1]
se_trim = rob['R5_outliers']['dropped_above_p99']['se'][1]
n_trim = rob['R5_outliers']['dropped_above_p99']['n']
print(f"R5 Excl. p99 Schooling: {b_trim:.4f} (SE {se_trim:.4f}) vs Paper 0,22 (0,03), N={n_trim} vs Paper 225.478 [MATCH: {abs(b_trim - 0.22) < 0.005}]")

# R6 Oster
oster_1_3 = rob['R6_oster']['rmax_1_3r2']
print(f"R6 Oster (2019) Bounds (Rmax = 1.3*R2): delta = {oster_1_3.get('delta_for_zero'):.2f}, beta*(delta=1) = {oster_1_3.get('beta_star_delta1'):.4f}")

# R3 and R7 Subgroups (Table A.1)
print("\nSubgroup Sensitivity Dropping Major Occupation Groups (Table A.1):")
for g_name in rob['R3_drop_major_group']['by_group']:
    r3_g = rob['R3_drop_major_group']['by_group'][g_name]
    r7_g = rob['R7_mediation_stability']['by_group'][g_name]
    b1, se1 = r3_g['beta'][1], r3_g['se'][1]
    b3, se3 = r7_g['beta'][1], r7_g['se'][1]
    print(f"  {g_name[:40]:40s} | S1 beta: {b1:.2f} ({se1:.2f}) | S3 beta: {b3:.2f} ({se3:.2f})")
