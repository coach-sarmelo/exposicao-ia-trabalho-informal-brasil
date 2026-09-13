# Computational Requirements & Environment Specification

**Project:** Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil  
**Author:** Marcelo Moura Freire  
**Standard:** AEA Data and Code Availability Standard (DCAS)  
**Date:** 2026-08-25  

---

## Computational Requirements

- **Primary Software (Canonical Pipeline):** R 4.6.1 (2026-06-24 ucrt, x86_64-w64-mingw32)
- **Secondary Software (Dual-Engine Validation):** Python 3.14.7
- **Operating System:** Windows 11 x64 (build 26200)
- **Random Seeds & RNG:**
  - R master seed: `set.seed(20260413L)`
  - Python seed: `42` / `20260413`
  - RNG Kind: `Mersenne-Twister` (standard R default)
- **Approximate Execution Time:**
  - R full canonical pipeline (`00_run_all.R`): **~20.05 seconds**
  - R econometric test suite (`test_econometrics.R`): **~2.80 seconds**
  - Python dual-engine pipeline (`data/scripts/run_all.py`): **~5.10 seconds**
  - Pytest test suite (`pytest -q`): **~2.20 seconds**

---

## Core R Package Versions

| Package | Version | Purpose |
| :--- | :--- | :--- |
| **`data.table`** | 1.18.4 | High-performance microdata aggregation & filtering |
| **`fixest`** | 0.14.2 | Fast fixed-effects OLS, WLS and cluster-robust standard errors |
| **`ggplot2`** | 4.0.3 | Vector graphics and academic publication figures |
| **`svglite`** | 2.2.2 | High-fidelity vector SVG rendering |
| **`jsonlite`** | 2.0.0 | Structured cross-engine validation and JSON serialization |
| **`testthat`** | 3.3.2 | Automated econometric test suite (83 assertions) |
| **`here`** | 1.0.2 | Robust cross-platform root path resolution |
| **`sandwich`** | 3.1-3 | Heteroskedasticity and cluster-robust covariance matrices |

*(Complete package hierarchy and dependencies recorded in [`sessionInfo.txt`](sessionInfo.txt))*

---

## Environment Artifacts in Repository

1. `replication_package/output/sessionInfo.txt` — Full human-readable R session capture.
2. `replication_package/output/computational_requirements.md` — Standalone replication requirements.
