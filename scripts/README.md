# `scripts/` — Python pipeline (data construction + dual-engine validation)

This directory is the **data-construction and dual-engine validation pipeline** that produced the analysis inputs in `data/analysis/`. It documents exactly how `individual_microdata.csv` and the derived artifacts were built from public sources, and it **runs directly from this package**:

```bash
python scripts/run_all.py paper      # paper-relevant chain (13 steps) — see below
python scripts/run_all.py pipeline   # full upstream chain (adds historical series, ~45 quarters)
python scripts/run_all.py test       # test suite (upstream repo only; not shipped here)
```

The canonical replication path for the paper is still the R pipeline in `code/` (`Rscript code/00_run_all.R`), which consumes the shipped `data/analysis/` files and requires no Python. The Python pipeline is an independent second engine.

## Requirements

Python ≥ 3.10 with **`numpy`**, **`pandas`**, **`statsmodels`** (used by `compute_econometrics.py`, `compute_robustness.py`, `stats/logit.py`). Everything else is standard library. There is no `requirements.txt` in the upstream project; install with:

```bash
python -m pip install numpy pandas statsmodels
```

`check-dashboard-integrity.py` additionally needs `pyyaml` and `generate_paper_figures.py` needs `matplotlib`; both are upstream site/exhibit utilities, **not** part of `run_all.py`.

## Tasks

| Task | Steps | Network | Purpose |
| :--- | :--- | :--- | :--- |
| `paper` | 13 | ~5 downloads of the quarter zip (228.6 MB each) | Regenerates every artifact the article uses: current-quarter extract, scores, decomposition, coverage, statistics, panel, econometrics, logit, robustness, tables. |
| `pipeline` | 13 | ~45 quarters, 2015–2026 (multi-GB) | The upstream `make refresh` chain: adds the historical dashboard time-series. Not needed for the paper. |
| `test` | 1 | — | `pytest -q`. Upstream only (the package does not ship `tests/`); the driver says so and exits cleanly. |

`paper` differs from `pipeline` by dropping `fetch_historical_microdata.py` and **adding** `compute_robustness.py`, which produces `robustness.json` (Table 6, R1–R7) even though upstream's `refresh` target omits it.

## Where files go

The scripts never overwrite the shipped analysis inputs. Outputs land in:

```
<data_dir>/output/            all intermediates + regenerated artifacts (JSON/CSV)
<data_dir>/../paper/tables/   LaTeX tables from build_paper_tables.py
```

with `data_dir` resolved as follows:

| Situation | `data_dir` |
| :--- | :--- |
| `PNAD_DATA_ROOT` set | that directory (absolute) |
| upstream repo (`<repo>/data/scripts/`) | `<repo>/data` |
| this package (`<pkg>/scripts/`) | `<pkg>/data` |

The resolution lives in `_paths.py` (`resolve_data_dir()`) and is used by every script, so `python scripts/<step>.py` works standalone from either layout. Set `PNAD_DATA_ROOT` to keep the package clean while writing elsewhere:

```bash
PNAD_DATA_ROOT=/tmp/pnad-work python scripts/run_all.py paper
```

## Bandwidth

Each stage that needs the raw microdata opens its own stream, so the `paper` chain fetches `PNADC_012026.zip` about **five times** (~1.1 GiB total); the archive is decompressed in memory and never written to disk. To fetch once instead, materialise the fixed-width file and point the scripts at it — `process_microdata.py` and `compute_decomposition.py` both honour `MICRODATA_TXT`:

```bash
MICRODATA_TXT=/path/to/PNADC_012026.txt python scripts/run_all.py paper
```

## Files

| Script | Role |
| :--- | :--- |
| `run_all.py` | Driver (tasks above). Propagates `PNAD_DATA_ROOT` to every subprocess. |
| `_paths.py` | Shared path resolution for both layouts. |
| `fetch_pnad_layout.py` | Builds `reference/pnadc_layout.json` (fixed-width field positions) from IBGE's SAS input dictionary. |
| `fetch_ibge_microdata.py` | Streams `PNADC_012026.zip` from IBGE's public FTP (in memory). Honours `IBGE_MICRODATA_YEAR`/`_QUARTER`. |
| `process_microdata.py` | Parses the fixed-width file → `data/output/individual_microdata.csv` (the 9-column extract documented in the README's "Data Extraction Provenance") plus the COD aggregates. |
| `fetch_historical_microdata.py` | Historical vintages for the time-series panel. |
| `build_cod_to_soc_crosswalk.py` | COD → SOC 2010 → O*NET-SOC crosswalk. |
| `compute_ai_exposure.py` | Maps Eloundou et al. (2024) exposure ratings onto COD subgroups → `scores.json`. |
| `compute_decomposition.py`, `compute_statistics.py`, `compute_coverage.py` | Exposure decomposition, descriptive statistics, COD coverage accounting. |
| `build_regional_panel.py` | State-level panel → `regional_panel.json`. |
| `compute_econometrics.py`, `compute_robustness.py` | Dual-engine estimation of S1–S4 and the robustness battery, cross-checking the canonical R results in `code/03_analyze.R`. |
| `stats/` | Dependency-free statistical helpers (`weighted.py`, `regression.py`, `logit.py`, `correlation.py`, `hypothesis.py`). |
| `build_paper_tables.py` | Paper tables from the Python results. |
| `reference/` | Layout and code mappings used by the pipeline (kept local because the scripts resolve it relative to themselves). |
| `check-dashboard-integrity.py`, `generate_paper_figures.py` | Upstream site/exhibit utilities; not part of `run_all.py`. |

## Dual-engine note

`compute_econometrics.py` and `compute_robustness.py` are a cross-check, not the source of the paper's numbers. Coefficients and standard errors agree with the canonical R estimates to rounding; **p-values follow different conventions** — statsmodels reports the normal approximation, while `code/03_analyze.R` uses Student-t with G−1 cluster degrees of freedom. Small p-value differences between `data/output/econometrics.json` (Python) and `data/analysis/econometrics.json` (R, authoritative) are therefore expected. Verified example: S1 `beta[0]`/`se[0]` → t = 1.8339; Python p = 0.0667 (normal), R p = 0.0691 (t, 121 df).

## Verification status

Verified end-to-end on 2026-09-15 from this package root (`python scripts/run_all.py paper`), against IBGE's live server:

- the regenerated `data/output/individual_microdata.csv` is **byte-identical** (md5 `4b1bfdb571617a85d386f9bc3c908d5d`) to the shipped `data/analysis/individual_microdata.csv` — all 228,325 rows, from a live re-download;
- `scripts/reference/pnadc_layout.json` and `cod_to_soc.json` regenerated byte-identically;
- `scores.json` and `regional_panel.json` reproduced exactly; `robustness.json` agrees to floating-point noise (worst relative difference 4.3e-16);
- 511,149 raw PNADC records streamed, matching the archive geometry exactly.
