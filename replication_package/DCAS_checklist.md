# Data and Code Availability Standard (DCAS) Compliance Checklist

**Paper:** *Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil*  
**Author:** Marcelo Moura Freire  
**Date of Verification:** 2026-08-23  
**Replication Package Location:** `replication_package/`  

---

## 1. Compliance Checklist Matrix

| DCAS Standard Requirement | Status | Verification Detail / File Pointer |
| :--- | :---: | :--- |
| **1. Data Availability Statement** | **PASS** | Present in `README.md` (Section 2) with clear statement of rights and open-access status. |
| **2. Dataset Manifest** | **PASS** | Full inventory in `README.md` (Section 3) with formats, row counts (file rows and estimation sample), key variables, and provenance URLs; the microdata CSV is identified as a derived extract. |
| **3. Master One-Command Script** | **PASS** | `code/00_run_all.R` executes the entire pipeline sequentially (01 $\to$ 05). |
| **4. Computational Requirements** | **PASS** | Documented in `README.md` (Section 4); captured `sessionInfo.txt` in `output/sessionInfo.txt`. |
| **5. Table/Figure $\to$ Program:Line Map** | **PASS** | Complete 8-row exhibit map in `README.md` (Section 6) linking every manuscript table/figure (4 main tables, 3 figures incl. the hand-authored DAG, 1 appendix table) to exact script lines; `tab_s4`, `fig3_regional_slopes` and `fig5_robustez_forest` are generated for the deck but not in the manuscript. |
| **6. Path Portability** | **PASS** | Zero absolute paths; all scripts use relative paths via `here::here()` or package root. |
| **7. Seed Discipline** | **PASS** | `PROJECT_SEED <- 20260413L` initialized at master entry point and passed to child scripts. |
| **8. Automated Test Suite** | **PASS** | `code/test_econometrics.R` validates the econometric estimates with a testthat suite of 24 assertions across 9 `test_that` blocks (14 `expect_equal`, 4 `expect_true`, 3 `expect_gt`, 2 `expect_lt`, 1 `expect_type`; loop-based checks expand to 58 executed expectation successes). Re-run 2026-09-15: 100% pass. |
| **9. License & Permissions** | **PASS** | `LICENSE.txt` included (BSD 3-Clause for code, CC-BY 4.0 for data derivations). |
| **10. Confidential / Restricted Data** | **PASS** | Verified: all inputs are open public access (IBGE open data and MIT-licensed benchmark ratings). `data/analysis/individual_microdata.csv` is a **derived 9-column extract** of the official `PNADC_012026.zip` — the raw archive is not redistributed. Extraction code is **shipped in-package** under `scripts/` (`fetch_pnad_layout.py`, `fetch_ibge_microdata.py`, `process_microdata.py`; see `scripts/README.md`) and was independently verified against IBGE's live server; the extract can be regenerated from IBGE's public FTP (228.6 MB download). V1028 calibrated weights are fractional by dictionary definition and untransformed; 696 workers in COD groups without O*NET-SOC coverage (11, 21, 212, 223, 224) are excluded from estimation (228,325 → 227,629). |

---

## 2. Verified Estimates Summary

| Parameter / Statistic | Manuscript Value | Replicated Value | Status |
| :--- | :---: | :---: | :---: |
| Sample Size ($N$) | 227.629 | 227.629 | **PASS** |
| Occupation Clusters ($G$) | 122 | 122 | **PASS** |
| S1 Baseline Gradient ($\hat{\beta}_1$) | $0{,}23$ (0,03) | $0{,}2288$ (0,0278) | **PASS** |
| S2 Wage-Controlled Gradient ($\hat{\beta}_1$) | $0{,}21$ (0,03) | $0{,}2097$ (0,0260) | **PASS** |
| S2 Income Coefficient ($\hat{\beta}_2$) | $0{,}043$ (0,010) | $0{,}0427$ (0,0100) | **PASS** |
| S3a Gross Informality Slope ($\hat{\delta}_1$) | $-6{,}23$ (0,99) | $-6{,}2285$ (0,9871) | **PASS** |
| S3 Net Informality Slope ($\hat{\delta}_1$) | $-3{,}91$ (0,96) | $-3{,}9068$ (0,9565) | **PASS** |
| Oster (2019) Bounding Parameter ($\delta$, standard construction, Rmax = 1.3·R²) | $1{,}93$ | $1{,}9266$ | **PASS** |
| Oster bias-adjusted $\beta^*(\delta=1)$ | $0{,}10$ | $0{,}1008$ | **PASS** |

*Note:* the S4 regional specification ($\hat{\beta}_2$, $\hat{\beta}_3$, and the regional threshold $e^*$) was removed from the final manuscript; its verification rows were retired with the manuscript content. Both engines still compute it (`code/03_analyze.R` S4 block; `scripts/stats/compute_econometrics.py`), and the values remain available in `data/analysis/econometrics.json`.

---

## 3. Verdict

**DCAS COMPLIANCE STATUS: 100% PASS**  
The replication package meets and exceeds the AEA Data Editor Standard for Reproducibility. It is ready for deposit on openICPSR, Zenodo, or Harvard Dataverse.
