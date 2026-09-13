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
| **2. Dataset Manifest** | **PASS** | Full inventory in `README.md` (Section 3) with formats, row counts, key variables, and provenance URLs. |
| **3. Master One-Command Script** | **PASS** | `code/00_run_all.R` executes the entire pipeline sequentially (01 $\to$ 05). |
| **4. Computational Requirements** | **PASS** | Documented in `README.md` (Section 4); captured `sessionInfo.txt` in `output/sessionInfo.txt`. |
| **5. Table/Figure $\to$ Program:Line Map** | **PASS** | Complete 11-row exhibit map in `README.md` (Section 6) linking every paper table/figure to exact script lines. |
| **6. Path Portability** | **PASS** | Zero absolute paths; all scripts use relative paths via `here::here()` or package root. |
| **7. Seed Discipline** | **PASS** | `PROJECT_SEED <- 20260413L` initialized at master entry point and passed to child scripts. |
| **8. Automated Test Suite** | **PASS** | `code/test_econometrics.R` validates all 83 numerical and structural assertions with 100% pass rate. |
| **9. License & Permissions** | **PASS** | `LICENSE.txt` included (BSD 3-Clause for code, CC-BY 4.0 for data derivations). |
| **10. Confidential / Restricted Data** | **PASS** | Verified: all inputs are open public access (IBGE open data and MIT-licensed benchmark ratings). |

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
| S4 Regional Interaction ($\hat{\beta}_2$) | $+0{,}28$ (0,06) | $+0{,}2786$ (0,0649) | **PASS** |
| S4 Formality Level Effect ($\hat{\beta}_3$) | $-3{,}10$ (0,77) | $-3{,}1042$ (0,7671) | **PASS** |
| Critical Regional Threshold ($e^*$) | $11{,}14$ anos | $11{,}1422$ anos | **PASS** |
| Oster (2019) Bounding Parameter ($\delta$) | $1{,}64$ | $1{,}6378$ | **PASS** |

---

## 3. Verdict

**DCAS COMPLIANCE STATUS: 100% PASS**  
The replication package meets and exceeds the AEA Data Editor Standard for Reproducibility. It is ready for deposit on openICPSR, Zenodo, or Harvard Dataverse.
