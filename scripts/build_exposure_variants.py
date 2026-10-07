"""build_exposure_variants.py — Robustness extension (v1.2.0): alternative
Eloundou et al. (2024) rating variants for the occupational AI-exposure score.

Rebuilds theta for all six occ_level.csv rating columns using the EXACT
aggregation of compute_ai_exposure.py:

  for each COD group -> for each SOC code in cod_to_soc.json:
    soc_avg = simple mean of the rating over O*NET-SOC children (7-char prefix)
  across SOCs:
    employment-weighted mean using BLS OEWS May-2021 detailed-level TOT_EMP;
    simple mean across SOCs if ANY contributing SOC lacks employment
  exposure = round(weighted_avg * 10, 1)

Gate: the dv_rating_beta rebuild must reproduce the shipped data/analysis/
scores.json exposure 122/122 (exact) before any variant is used.

Also computes per-group crosswalk dispersion (weighted SD and range of
SOC-level dv_rating_beta within each COD group) as a measurement-error
diagnostic.

Deterministic (no stochastic step). Output:
  <data_dir>/output/variants_scores.json
The shipped copy is data/analysis/variants_scores.json (byte-identical).
Inputs are read-only; shipped analysis inputs are never overwritten.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import resolve_data_dir, ensure_output_dir  # noqa: E402

DATA = resolve_data_dir()
OUT_DIR = ensure_output_dir(DATA)

RATING_COLS = [
    "dv_rating_beta",      # paper baseline (eloundou-2024-dv-beta)
    "dv_rating_alpha",
    "dv_rating_gamma",
    "human_rating_alpha",
    "human_rating_beta",
    "human_rating_gamma",
]

# ---------------------------------------------------------------- load inputs
def load_ratings(path: str) -> dict[str, dict[str, float]]:
    by_col: dict[str, dict[str, float]] = {c: {} for c in RATING_COLS}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = row["O*NET-SOC Code"]
            for c in RATING_COLS:
                by_col[c][code] = float(row[c])
    return by_col

def load_employment(path: str) -> dict[str, float]:
    emp: dict[str, float] = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["O_GROUP"] != "detailed":
                continue
            raw = row["TOT_EMP"].replace(",", "").strip()
            if not raw or not raw.isdigit():
                continue
            emp[row["OCC_CODE"]] = float(raw)
    return emp

ratings = load_ratings(os.path.join(DATA, "external", "occ_level.csv"))
employment = load_employment(os.path.join(DATA, "external", "national_May2021_dl.csv"))
with open(os.path.join(DATA, "reference", "cod_to_soc.json"), encoding="utf-8") as f:
    cod_to_soc = json.load(f)
with open(os.path.join(DATA, "analysis", "scores.json"), encoding="utf-8") as f:
    scores = json.load(f)

# SOC-prefix index (same as compute_ai_exposure.index_by_soc_prefix)
onet_by_soc: dict[str, list[str]] = {}
for code in ratings["dv_rating_beta"]:
    onet_by_soc.setdefault(code[:7], []).append(code)

def soc_stats(soc_code: str):
    matched = onet_by_soc.get(soc_code, [])
    if not matched:
        return None
    avgs = {c: sum(ratings[c][code] for code in matched) / len(matched) for c in RATING_COLS}
    w = employment.get(soc_code)
    return avgs, w, matched

def weighted_sd(pairs):
    """pairs: list of (value, weight); simple SD if any weight missing/<=0."""
    if any(w is None or w <= 0 for _, w in pairs):
        vals = [v for v, _ in pairs]
        m = sum(vals) / len(vals)
        return math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals)), False
    tw = sum(w for _, w in pairs)
    m = sum(v * w for v, w in pairs) / tw
    return math.sqrt(sum(w * (v - m) ** 2 for v, w in pairs) / tw), True

def group_result(soc_codes: list[str]):
    per_soc = [s for s in (soc_stats(sc) for sc in soc_codes) if s]
    if not per_soc:
        return None
    out = {"fallback_simple": not all(w is not None and w > 0 for _, w, _ in per_soc),
           "n_soc": len(per_soc),
           "n_onet": sum(len(codes) for _, _, codes in per_soc)}
    beta_pairs = [(avgs["dv_rating_beta"], w) for avgs, w, _ in per_soc]
    sd, _ = weighted_sd(beta_pairs)
    out["disp_sd_beta"] = round(sd * 10, 3)                       # on the 0-10 scale
    out["disp_range_beta"] = round((max(v for v, _ in beta_pairs) - min(v for v, _ in beta_pairs)) * 10, 3)
    for c in RATING_COLS:
        if out["fallback_simple"]:
            avg = sum(avgs[c] for avgs, _, _ in per_soc) / len(per_soc)
        else:
            tw = sum(w for _, w, _ in per_soc)
            avg = sum(avgs[c] * w for avgs, w, _ in per_soc) / tw
        out[c] = round(avg * 10, 1)
    return out

# ------------------------------------------------------------------ compute
variants: dict[str, dict] = {}
n_exact = 0
n_checked = 0
for code, entry in scores.items():
    if code == "_meta":
        continue
    soc_codes = (cod_to_soc.get(code) or {}).get("soc_codes", [])
    res = group_result(soc_codes)
    if res is None:
        continue
    res["name"] = entry["name"]
    if entry.get("exposure") is not None:
        n_checked += 1
        if abs(res["dv_rating_beta"] - entry["exposure"]) < 1e-9:
            n_exact += 1
        else:
            print(f"MISMATCH {code}: shipped {entry['exposure']} vs rebuilt {res['dv_rating_beta']}")
    variants[code] = res

print(f"verification: {n_exact}/{n_checked} groups reproduce shipped dv_rating_beta exactly")
if n_exact != n_checked:
    raise SystemExit("ABORT: baseline theta rebuild does not match; variants would be invalid")

payload = {
    "_meta": {
        "purpose": "robustness extension (v1.2.0): rating-variant theta rebuild + crosswalk dispersion",
        "algorithm": "identical to scripts/compute_ai_exposure.py (SOC-level mean over O*NET children; OEWS-employment-weighted across SOCs, simple-mean fallback; x10; round 1dp)",
        "employment_source": "BLS OEWS May 2021 national, detailed level",
        "baseline_verification": f"{n_exact}/{n_checked} exact",
        "deterministic": True,
        "seed_note": "no stochastic step; paper seed convention 20260413 (provenance only)",
        "groups": len(variants),
    },
    "groups": variants,
}
out_path = os.path.join(OUT_DIR, "variants_scores.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)

# quick dispersion summary
sds = [g["disp_sd_beta"] for g in variants.values()]
print(f"groups: {len(variants)} | fallback_simple: {sum(g['fallback_simple'] for g in variants.values())}")
print(f"within-group SOC dispersion (0-10 scale): mean SD {sum(sds)/len(sds):.3f}, "
      f"max {max(sds):.3f}, median {sorted(sds)[len(sds)//2]:.3f}")
print(f"-> {out_path}")
print("shipped copy: data/analysis/variants_scores.json (byte-identical; regenerate with this script)")
