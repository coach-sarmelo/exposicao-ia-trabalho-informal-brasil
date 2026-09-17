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
  - R full canonical pipeline (`00_run_all.R`): **~20.05 seconds** documented; **17.65s** measured on 2026-09-15 (R 4.6.1, same machine class)
  - R econometric test suite (`test_econometrics.R`): **~2.80 seconds** documented; **~3s** measured on 2026-09-15, 100% pass (58 executed expectation successes)
  - Python dual-engine pipeline (`scripts/run_all.py paper`, **shipped and runnable in this package** — auto-detects the package layout; see `scripts/README.md`): **~2 minutes** end-to-end in the verification run of 2026-09-15, dominated by ~5 downloads of `PNADC_012026.zip` (228.6 MB each, streamed in memory) from IBGE's public FTP; the analysis steps themselves take **~5 seconds**
  - Python test suite (`python scripts/run_all.py test`; the package does not ship the upstream `tests/` directory — the driver reports this and exits cleanly. Upstream repository: **~2.20 seconds**)

---

## Core R Package Versions

| Package | Version | Purpose |
| :--- | :--- | :--- |
| **`data.table`** | 1.18.4 | High-performance microdata aggregation & filtering |
| **`fixest`** | 0.14.2 | Fast fixed-effects OLS, WLS and cluster-robust standard errors |
| **`ggplot2`** | 4.0.3 | Vector graphics and academic publication figures |
| **`svglite`** | 2.2.2 | High-fidelity vector SVG rendering |
| **`jsonlite`** | 2.0.0 | Structured cross-engine validation and JSON serialization |
| **`testthat`** | 3.3.2 | Automated econometric test suite (24 assertions, 9 blocks; 58 executed successes) |
| **`here`** | 1.0.2 | Robust cross-platform root path resolution |
| **`sandwich`** | 3.1-3 | Heteroskedasticity and cluster-robust covariance matrices |

*(Complete package hierarchy and dependencies recorded in [`sessionInfo.txt`](sessionInfo.txt))*

---

## Environment Artifacts in Repository

1. `replication_package/output/sessionInfo.txt` — Full human-readable R session capture.
2. `replication_package/output/computational_requirements.md` — Standalone replication requirements.

## Python Data-Construction Pipeline (`scripts/`)

The Python 3 pipeline is **shipped in this package** under `scripts/` and **runs directly from the package root** (`python scripts/run_all.py paper`): `run_all.py` chains `fetch_pnad_layout.py` → `fetch_ibge_microdata.py` → `process_microdata.py` → `build_cod_to_soc_crosswalk.py` → `compute_ai_exposure.py` → … → `compute_econometrics.py` → `build_paper_tables.py`, regenerating all analysis artifacts from public sources into `data/output/`. It is **optional** for replication: the canonical path is the R pipeline in `code/`, which consumes the shipped `data/analysis/` files. Requires `numpy`, `pandas` and `statsmodels`. See `scripts/README.md` for the `paper` vs `pipeline` tasks, the `PNAD_DATA_ROOT` override, and bandwidth notes.

**Dual-engine note.** Python's `compute_econometrics.py`/`compute_robustness.py` exist to cross-check the canonical R estimates. Coefficients and standard errors agree with R to rounding; p-values follow different distributional conventions (Python/statsmodels: normal approximation; R: Student-t with G−1 cluster degrees of freedom), so small p-value differences between `data/output/econometrics.json` (Python) and `data/analysis/econometrics.json` (R, authoritative) are expected by design.

---

## Verification Runs (2026-09-15)

Both engines were re-run end-to-end from a neutral copy of this package, outside any repository:

- **R canonical pipeline** (`Rscript code/00_run_all.R`, 17.65s): `results.rds` and the R-written `data/analysis/econometrics.json` regenerated **md5-identical** to the shipped copies; all 7 LaTeX tables in `output/tables/` byte-identical; all 20 figure files regenerated (PDF/PNG/SVG carry embedded creation timestamps and are therefore not byte-comparable).
- **R test suite** (`Rscript code/test_econometrics.R`): all 9 `test_that` blocks pass — 58 executed expectation successes, 100%.
- **Python pipeline** (`python scripts/run_all.py paper`, live IBGE fetch): regenerated `individual_microdata.csv` **byte-identical** to the shipped extract (md5 `4b1bfdb571617a85d386f9bc3c908d5d`); `scores.json`/`regional_panel.json` identical; `robustness.json` within float noise (worst relative difference 4.3e-16).

**Windows note.** `here::here()` anchors on the nearest enclosing project root, so the package should be run from its own directory (in a neutral folder it resolves to the package root, which is correct). Under MSYS/Git-Bash on Windows, `Rscript` may report exit code 127 after successful completion (a `ggplot2` 4.0.3 DLL-teardown signal quirk); cmd.exe, PowerShell and RStudio report 0. Check the log output ("Pipeline complete") rather than the shell code under Git-Bash.
