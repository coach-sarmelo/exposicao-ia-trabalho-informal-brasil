"""compute_robustness_ext.py — Robustness extension (v1.2.0): wild cluster
bootstrap for S1 and S3 at the occupation level.

Mirrors compute_robustness.py::fast_wild_bootstrap_mc exactly: restricted
(null-imposed) wild cluster bootstrap, Rademacher signs per cluster,
cluster-robust t recomputed per draw, p = (count+1)/(n_draws+1), legacy
np.random.seed(42) RNG, n_draws=1000.

Extends the shipped R2 check (S4, 27 UF clusters) to the paper's headline
coefficients, where occupation clustering leaves 122 clusters — few enough
that CRVE asymptotics deserve a bootstrap cross-check.

UPA-level wild bootstrap deliberately not run: 16,026 PSU clusters make the
cluster-robust variance asymptotically reliable (and PSU SEs are ~10x
smaller — not the binding dimension); the paper's own R2 philosophy applies
the bootstrap where clusters are few.

Inputs (read-only): individual_microdata_design.csv (data/output/ then
data/analysis/), scores.json. Output: output/robustness_ext/p2_wild_bootstrap.json.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import resolve_data_dir  # noqa: E402

DATA = resolve_data_dir()
PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT_OUT = os.path.join(PKG_ROOT, "output", "robustness_ext")
os.makedirs(EXT_OUT, exist_ok=True)


def wild_cluster_bootstrap(y, X, w, clusters, focal_idx, n_draws=1000, seed=42):
    """Restricted (null-imposed) wild cluster bootstrap, Rademacher signs."""
    np.random.seed(seed)  # package convention (compute_robustness.py)
    n, k = X.shape
    w = np.asarray(w, float); y = np.asarray(y, float); X = np.asarray(X, float)
    clusters = np.asarray(clusters)
    uniq, cl_inv = np.unique(clusters, return_inverse=True)
    g = len(uniq)

    w_sqrt = np.sqrt(w)
    X_tilde = w_sqrt[:, None] * X
    XWX_inv = np.linalg.pinv(X_tilde.T @ X_tilde)
    beta_hat = XWX_inv @ (X_tilde.T @ (w_sqrt * y))
    e_tilde = w_sqrt * (y - X @ beta_hat)

    def meat(V):
        # cluster scores via scatter-add: S[g] = sum_{i in g} X_tilde[i]*e_tilde[i]
        S = np.zeros((g, k))
        np.add.at(S, cl_inv, X_tilde * V[:, None])
        return S.T @ S

    V_hat = (g / (g - 1)) * ((n - 1) / (n - k)) * (XWX_inv @ meat(e_tilde) @ XWX_inv)
    t_hat = beta_hat[focal_idx] / np.sqrt(V_hat[focal_idx, focal_idx])

    # null-imposed centering (restricted bootstrap)
    X0 = np.delete(X, focal_idx, axis=1)
    X0_tilde = w_sqrt[:, None] * X0
    X0WX0_inv = np.linalg.pinv(X0_tilde.T @ X0_tilde)
    beta0 = X0WX0_inv @ (X0_tilde.T @ (w_sqrt * y))
    center = X0 @ beta0
    resid = y - center

    count = 0
    for _ in range(n_draws):
        signs = np.random.choice([1.0, -1.0], size=g)
        y_star = center + signs[cl_inv] * resid
        beta_b = XWX_inv @ (X_tilde.T @ (w_sqrt * y_star))
        e_b = w_sqrt * (y_star - X @ beta_b)
        V_b = (g / (g - 1)) * ((n - 1) / (n - k)) * (XWX_inv @ meat(e_b) @ XWX_inv)
        se_b = np.sqrt(V_b[focal_idx, focal_idx])
        if se_b > 0:
            t_b = beta_b[focal_idx] / se_b
            if np.isfinite(t_b) and abs(t_b) >= abs(t_hat):
                count += 1

    return {"p_wild": (count + 1) / (n_draws + 1), "t_stat": float(t_hat),
            "n_draws": n_draws, "n_clusters": int(g), "restricted": True,
            "rademacher": True, "seed": seed}


# ------------------------------------------------------------------ data ----
def find_input(name):
    for cand in (os.path.join(DATA, "output", name), os.path.join(DATA, "analysis", name)):
        if os.path.exists(cand):
            return cand
    raise SystemExit(f"ABORT: {name} not found under data/output/ or data/analysis/ "
                     "(run scripts/build_design_extract.py first)")

design_csv = find_input("individual_microdata_design.csv")
df = pd.read_csv(design_csv,
                 dtype={"occupation": str, "sex": str, "race": str,
                        "upa": str, "estrato": str, "v1008": str, "v2003": str})
with open(os.path.join(DATA, "analysis", "scores.json"), encoding="utf-8") as f:
    scores = json.load(f)
smap = {k: v["exposure"] for k, v in scores.items() if k != "_meta" and v.get("exposure") is not None}
df["exposure"] = df["occupation"].map(smap)
df = df.dropna(subset=["exposure", "years_of_study", "income", "informal", "uf",
                       "occupation", "weight", "age", "sex", "race"])
df["age_sq"] = df["age"] ** 2
df["is_female"] = (df["sex"] == "2").astype(float)
race_d = pd.get_dummies(df["race"], prefix="race", dtype=float)

def design(extra):
    D = pd.DataFrame({"const": 1.0}, index=df.index)
    for c in extra:
        D[c] = df[c]
    for c in race_d.columns:
        if c != "race_1":  # reference = race "1"
            D[c] = race_d[c]
    return D.to_numpy(float)

out = {}
# S1: exposure ~ years_of_study + controls (focal idx 1)
X = design(["years_of_study", "age", "age_sq", "is_female"])
out["S1_occupation_wild"] = wild_cluster_bootstrap(
    df["exposure"].to_numpy(float), X, df["weight"].to_numpy(float),
    df["occupation"].to_numpy(), focal_idx=1)

# S3: informal_pct ~ exposure + years_of_study + controls (focal idx 1)
X = design(["exposure", "years_of_study", "age", "age_sq", "is_female"])
y = df["informal"].to_numpy(float) * 100.0
out["S3_occupation_wild"] = wild_cluster_bootstrap(
    y, X, df["weight"].to_numpy(float), df["occupation"].to_numpy(), focal_idx=1)

out["_meta"] = {
    "method": "restricted wild cluster bootstrap (Rademacher), mirrors compute_robustness.py::fast_wild_bootstrap_mc",
    "cluster": "occupation (122)",
    "n_draws": 1000, "seed": 42,
    "deterministic_given_seed": True,
    "n": int(len(df)),
    "upa_wild_skipped": "16,026 PSU clusters - CRVE asymptotics reliable; bootstrap relevant where clusters are few (paper R2 logic)",
}
with open(os.path.join(EXT_OUT, "p2_wild_bootstrap.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
for k in ("S1_occupation_wild", "S3_occupation_wild"):
    r = out[k]
    print(f"{k}: t = {r['t_stat']:.3f}, wild-cluster p = {r['p_wild']:.4f} "
          f"({r['n_draws']} draws, {r['n_clusters']} clusters)")
print(f"-> {os.path.join(EXT_OUT, 'p2_wild_bootstrap.json')}")
