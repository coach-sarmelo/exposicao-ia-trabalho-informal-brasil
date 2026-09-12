# Computational Requirements & Environment Specification

**Project:** Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil  
**Author:** Marcelo Moura Freire (Universidade de Coimbra)  
**Standard:** AEA Data and Code Availability Standard (DCAS) / AEA Data Editor Guidelines  
**Date:** 2026-09-12  

---

## Computational requirements

**Software:** R 4.6.1 (2026-06-24 ucrt, x86_64-w64-mingw32)  
**OS used:** Windows 11 x64 (build 26200)  
**Key packages:** `data.table` 1.18.6.1, `fixest` 0.14.2, `ggplot2` 4.0.3, `svglite` 2.2.2, `jsonlite` 2.0.0, `testthat` 3.3.2, `here` 1.0.2, `sandwich` 3.1-3 (full dependency tree in `renv.lock`)  
**Random seeds:** `PROJECT_SEED <- 20260413L` (`set.seed(20260413L)`); `RNGkind("Mersenne-Twister", "Inversion", "Rejection")`  
**Approx. runtime:** ~20.05 seconds (full pipeline `00_run_all.R`), ~2.80 seconds (econometric test suite `test_econometrics.R`)  
**Lockfiles in package:** `renv.lock`, `scripts/R/_outputs/sessionInfo.txt`, `replication_package/output/sessionInfo.txt`  

---

## Core R Package Versions

| Package | Version | Purpose |
| :--- | :--- | :--- |
| **`data.table`** | 1.18.6.1 | High-performance microdata filtering and tabulation |
| **`fixest`** | 0.14.2 | Fast fixed-effects OLS, WLS and cluster-robust standard errors |
| **`ggplot2`** | 4.0.3 | Publication-grade academic figures |
| **`svglite`** | 2.2.2 | High-fidelity vector SVG rendering |
| **`jsonlite`** | 2.0.0 | Structured metric serialization and validation data export |
| **`testthat`** | 3.3.2 | Automated econometric test suite (83 assertions) |
| **`here`** | 1.0.2 | Cross-platform root path resolution |
| **`sandwich`** | 3.1-3 | Heteroskedasticity and cluster-robust covariance matrices |

*(Complete 51-package hierarchy and dependencies recorded in `renv.lock` and `sessionInfo.txt`)*

---

## Verification Status

- **Lockfile Integrity:** `renv.lock` generated via `renv::snapshot()`.
- **Clean Install Check:** `renv::restore()` tested clean in an isolated temporary library (51 packages resolved, downloaded, and installed successfully).
- **Econometric Tests:** 100% assertions passed via `replication_package/code/test_econometrics.R`.
