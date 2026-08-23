# Replication Package Report: Exposição à Inteligência Artificial em um Mercado de Trabalho Informal

**Date:** 2026-08-23  
**Author:** Marcelo Moura Freire  
**Languages:** R 4.6.1 (Canonical Primary) & Python 3.14 (Dual-Engine Cross-Validation)  
**Deposit Target:** openICPSR / Zenodo / Harvard Dataverse  
**Standard:** AEA Data Editor Standard for Reproducibility (DCAS) / openICPSR Guidelines  

---

## 1. DCAS Compliance Checklist

| Item | Status | Notes |
|---|:---:|---|
| **Data Availability Statement** | **PASS** | Section 2 of `README.md` details public open-access status and legal rights. |
| **Dataset Manifest (source · access · license)** | **PASS** | Section 3 lists all microdata, crosswalks, and ratings with exact URLs and licenses. |
| **One-Command Master Script** | **PASS** | `code/00_run_all.R` runs full pipeline (01 $\to$ 05) deterministically in < 45s. |
| **Computational Requirements** | **PASS** | Captured `sessionInfo.txt` and specified minimum RAM/OS requirements. |
| **Table/Figure $\to$ Program:Line Map** | **PASS** | Section 6 maps all 7 tables and 4 figures to exact generating script lines. |
| **No Machine-Specific Paths · Seeds Set** | **PASS** | Fully relative paths with `here::here()`, fixed master seed `PROJECT_SEED <- 20260413L`. |
| **Reproducibility Audit (Phase 3)** | **PASS** | All 83 R `testthat` assertions and 128 `pytest` cross-validation tests passed (100%). |
| **Confidential / Restricted Data Scan** | **PASS** | Verified zero proprietary/restricted inputs; all data is public open data. |

---

## 2. Directory Tree Structure

The assembled replication deposit is located at [`replication_package/`](file:///C:/Users/freir/Documents/research/claude-code-my-workflow/replication_package):

```
replication_package/
├── README.md                # AEA DCAS Replication Manifest & exhibit mapping
├── DCAS_checklist.md        # Comprehensive DCAS verification checklist
├── LICENSE.txt              # BSD 3-Clause (Code) + CC-BY 4.0 (Data)
├── data/
│   ├── analysis/            # Processed microdata (227k obs), scores.json, panel, econometrics
│   ├── external/            # Benchmark datasets (O*NET, ISCO, BLS) + SOURCES.md
│   └── reference/           # COD occupation structure and metadata
├── code/
│   ├── 00_run_all.R         # Master orchestrator script
│   ├── 01_load.R            # Data ingestion
│   ├── 02_clean.R           # Variable derivation & LOO formality
│   ├── 03_analyze.R         # WLS econometrics, Oster bounds, results.rds
│   ├── 04_tables.R          # LaTeX table generation (paper/tables/)
│   ├── 05_figures.R         # ggplot2 vector figures (PDF, SVG, PNG)
│   └── test_econometrics.R  # Automated testthat replication suite
└── output/
    ├── tables/              # All 7 publication LaTeX tables
    ├── figures/             # All 4 figures in PDF, SVG, and PNG
    ├── results.rds          # Serialized model objects and estimates
    └── sessionInfo.txt      # Computational environment snapshot
```

---

## 3. Verified Replicated Estimates

- **Sample Size ($N$):** $227.629$ individuals across $122$ COD occupation clusters.
- **S1 Baseline WLS Gradient ($\hat{\beta}_1$):** $0{,}2288$ (SE $0{,}0278; p < 0{,}001; R^2 = 0{,}2457$).
- **S2 Wage Control Gradient ($\hat{\beta}_1$):** $0{,}2097$ (SE $0{,}0260$), Income ($\hat{\beta}_2$): $0{,}0427$ (SE $0{,}0100$).
- **S3 Mediation Decomposition:** Gross slope $\hat{\delta}_1 = -6{,}2285$ vs. Net slope $\hat{\delta}_1 = -3{,}9068$ (37.2% schooling selection vs. 62.8% direct organizational effect).
- **S4 Regional Interaction:** $\hat{\beta}_2 = +0{,}2786$ (SE $0{,}0649$), $\hat{\beta}_3 = -3{,}1042$ (SE $0{,}7671$), Critical Threshold $e^* = 11{,}14$ years.
- **Oster (2019) Bounding:** $\delta = 1{,}64$ under $R_{\max} = 1{,}3 R^2$.

---

## 4. Open [FILL] Items

*None.* All fields, data sources, code lines, licenses, and computational requirements are completely resolved and verified against the repository.
