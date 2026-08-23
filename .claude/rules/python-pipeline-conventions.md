---
paths:
  - "data/scripts/**/*.py"
  - "data/tests/**/*.py"
---

# Python Pipeline & Econometrics Standards

**Standard:** Senior Data Scientist & Quantitative Economist Quality

> **Scope:** These standards apply to all ETL, microdata processing, econometrics, and figure generation scripts within `data/scripts/` and test suites in `data/tests/`.

---

## 1. Reproducibility & Determinism

- **Explicit Seeds:** For any randomized algorithm (e.g., bootstrapping, synthetic controls, train-test splits), set seeds explicitly at the top of the script (`SEED = 42` or `20260822`).
- **Deterministic Grouping:** When aggregating or ranking occupational cells, always specify secondary sorting keys (e.g., `df.sort_values(by=['score', 'cod_code'])`) to ensure identical JSON/CSV outputs across machines and Python versions.
- **Relative Paths:** All paths must be computed relative to project root or script parent directory using `pathlib.Path` or `os.path`. Never use hardcoded machine absolute paths.

---

## 2. Microdata Handling & Performance

- **Column Pruning:** Always select required columns upfront when loading large microdata (e.g. PNAD Contínua text files or raw CSVs) to minimize RAM footprint.
- **Type Efficiency:** Use memory-efficient dtypes (e.g. `category` for UF/occupation strings, `float32`/`float64` appropriately).
- **Validation Checks:** Assert merge coverage after joining occupational crosswalks (e.g. `assert unmapped_employment_pct < 0.05`).

---

## 3. Code Quality & Modularity

- **Type Annotations:** Provide Python type hints on function signatures (`def compute_exposure(df: pd.DataFrame, crosswalk: dict[str, float]) -> pd.DataFrame:`).
- **Docstrings:** Document inputs, outputs, mathematical formulation, and econometric rationale for each transformation step.
- **CLI & Module Dual-Use:** Provide `if __name__ == "__main__":` blocks with argument parsing or clean standalone execution functions.

---

## 4. Visual Identity & Figure Standards

- **Typography & Clean Design:** Use clean, sans-serif fonts, minimal gridlines (`alpha=0.2`), and clear hierarchy for titles, subtitles, and captions.
- **Language & Formatting:** Use Brazilian Portuguese notation for figures in the paper/site (comma as decimal separator if matching Brazilian standards, or standard scientific notation with clear units).
- **Annotated Statistics:** Always include key metrics directly on figures: sample sizes ($N$), point estimates ($\hat{\beta}_1$), standard errors ($\text{SE}$), and confidence intervals.
- **Dual Export:** Save figures simultaneously in vector format (`.pdf`) for LaTeX and high-resolution raster (`.png`, 300+ dpi) for web presentation.

---

## 5. Testing & Verification

- **Pytest Suite:** All core statistics, indices, and aggregations must have corresponding tests in `data/tests/`.
- **Pipeline Check:** After making modifications to data scripts, always run:
  ```bash
  cd data && python scripts/run_all.py test
  ```
