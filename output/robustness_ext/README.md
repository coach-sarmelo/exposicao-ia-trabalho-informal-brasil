# Robustness Extensions (package v1.2.0)

Beyond-manuscript robustness battery added in v1.2.0. **The manuscript's
canonical results (`data/analysis/econometrics.json`, `robustness.json`) are
unchanged and remain authoritative** — nothing in this directory feeds the
paper's tables or figures. Every script below first *gates* on exact
reproduction of the shipped results before any variant is estimated.

## What was added

| Extension | Question it answers | Script | Key outputs |
| :--- | :--- | :--- | :--- |
| **P1 — specification variants** | Are S1–S3 coefficients stable to UF fixed effects, income functional form (log/IHS), and the 16-year schooling top-code? | `code/06_polish_variants.R` | `polish_coefficients.csv` (27 rows), `polish_results.json` |
| **P3 — exposure-measurement variants** | Do results depend on *which* Eloundou et al. (2024) rating column defines θ? How much does the 696-worker coverage gap matter? | `scripts/build_exposure_variants.py` + `code/06_polish_variants.R` | `data/analysis/variants_scores.json`, bounding rows in the CSV |
| **P5 — S3 functional form** | Is the informality result an artifact of the LPM? | `code/06_polish_variants.R` | `S3_logit` row (log-odds) |
| **P2 — survey-design inference** | What do design-based (linearized) SEs look like, and is occupation clustering the binding choice? | `scripts/build_design_extract.py` + `code/07_design_inference.R` | `p2_results.json` |
| **Wild cluster bootstrap** | Do the 122-cluster CRVE asymptotics survive a bootstrap? | `scripts/compute_robustness_ext.py` | `p2_wild_bootstrap.json` |

## How to run

From the package root (R packages `fixest`, `survey`; Python `numpy`, `pandas`):

```bash
# P1 + P3 + P5 (~1–2 min; needs data/analysis/variants_scores.json, shipped)
Rscript code/06_polish_variants.R

# P2 (~1 min; needs data/analysis/individual_microdata_design.csv, shipped)
Rscript code/07_design_inference.R

# Wild cluster bootstrap (~1 min)
python scripts/compute_robustness_ext.py

# Regenerate the two shipped extension inputs (deterministic, gated):
python scripts/build_exposure_variants.py    # -> data/output/variants_scores.json (122/122 gate)
python scripts/build_design_extract.py       # -> data/output/individual_microdata_design.csv
                                             #    (downloads PNADC_012026.zip, 228.6 MB; honours
                                             #     MICRODATA_ZIP / MICRODATA_TXT to skip the download)
```

## Headline findings (2026-09-18)

1. **Sign and significance are robust across all 23 variants** (27 models incl. the 4 baselines; weakest p = 8.4e-04). Three *quantified* sensitivities:
   - **Education top-code:** adding a 16-year indicator moves β_schooling (S1) from +0.2288 to +0.1702 (−25.6%) — 21.97% of the sample sits at the ceiling.
   - **Income functional form:** levels overstate the residual schooling gradient ~16% vs log/IHS (S2: 0.2097 → 0.1803/0.1793).
   - **Rating variant:** S1 β ranges 0.06–0.39 across the six Eloundou rating columns; occupation-level Spearman ρ vs the paper baseline is 0.61–0.98 (orderings mostly preserved, scales not).
2. **Coverage-missing bounding is immaterial:** assigning θ=0 or θ=10 to the 696 workers outside O*NET coverage moves S1 β by −0.9%/+1.5%.
3. **Occupation clustering is the conservative and correct choice.** Design-based (linearized, strata × PSU) SEs are ~10× *smaller* than occupation-clustered SEs; the two-way (occupation × UPA) estimator collapses to the occupation dimension. θ varies only between occupations, so any occupation-level shock is correlated with the regressor by construction — occupation clustering is what allows for those shocks, and design-based SEs are the sampling-variance lower bound, not the right primary inference.
4. **Wild cluster bootstrap (restricted Rademacher, 1,000 draws, seed 42) rejects at the floor** for both headline coefficients: S1 t = 8.246 and S3 t = −4.084, wild p = 0.0010 (report as p ≤ 0.001).
5. **Design diagnostics:** 16,026 PSUs, 826 strata (4 singleton-PSU strata, `lonely.psu="adjust"`); Kish ESS 111,461 of 227,629; weighted informality 40.53%; DEFF(informality) 3.42.

## Files

- `polish_coefficients.csv` — 27 rows (4 baselines + 23 variants): estimate, SE, p, R², n, clusters, 95% CI.
- `polish_results.json` — same plus occupation-level Spearman matrix and worker-weighted Pearson concordance vs baseline θ.
- `p2_results.json` — SE battery (occupation / PSU / two-way / svyglm) for S1, S2, S3a, S3; Kish ESS; DEFF.
- `p2_wild_bootstrap.json` — S1/S3 wild cluster bootstrap p-values.
- `fig_polish_forest.pdf/.png` — coefficient-stability forest plot.
- `data/analysis/variants_scores.json` — θ for all six rating columns (122/122 gate vs shipped baseline) + within-group SOC dispersion diagnostics.
- `data/analysis/individual_microdata_design.csv` — the shipped 9 analytic columns + UPA/Estrato/V1008/V2003 (228,325 rows; validated multiset-identical to `individual_microdata.csv`; regenerated deterministically by `scripts/build_design_extract.py`).

## Notes

- `econometrics.json` stores coefficients/SEs rounded to 4 decimal places; all gates compare after applying the same storage rounding.
- The design extract carries IBGE household identifiers (public-domain microdata); it exists for variance estimation only and is a *derived extract*, not a redistribution of the raw archive.
- No stochastic step in `06`/`07`; the bootstrap uses the package convention `np.random.seed(42)`, 1,000 draws.
