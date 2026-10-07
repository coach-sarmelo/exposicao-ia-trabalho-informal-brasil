# Replication Package: Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil

**Author:** Marcelo Moura Freire  
**Standard:** [Social Science Data Editors Data and Code Availability Standard (DCAS)](https://datacodestandard.org/) / AEA Data Editor Template  
**Date:** 2026-08-23 · **Version:** 1.2.0 (updated 2026-09-18 — robustness extensions; see §5 Step 5 and `output/robustness_ext/README.md`)  
**Deposit Target:** openICPSR / Zenodo / Dataverse  

---

## 1. Overview & Paper Citation

This replication package contains the complete data, code, microeconometric analysis pipeline, test suite, and generated artifacts for the research paper:

> **Freire, Marcelo Moura (2026).** *Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil.*

The paper investigates the distribution of artificial intelligence (LLM) exposure across formal and informal employment in Brazil using microdata from the IBGE Continuous National Household Sample Survey (PNAD Contínua) linked to O*NET-SOC occupational exposure ratings (Eloundou et al., 2024).

**v1.2.0** adds a beyond-manuscript **robustness extension battery** (specification variants, exposure-rating variants, coverage bounding, logit, survey-design inference, wild cluster bootstrap) under `code/06–07`, `scripts/*_ext*.py`-adjacent scripts and `output/robustness_ext/`. The manuscript's canonical results are unchanged: every extension script first gates on exact reproduction of the shipped estimates. See §5 Step 5.

---

## 2. Data Availability and Provenance Statements

### Statement of Rights
The author certifies that he has legitimate access to all data used in this study and the right to distribute the replication materials. All primary and secondary data are public, open-access, and reproducible.

### Summary of Data Sources

| Data Name | Source / Citation | Access / URL | License | Provided in Package? |
| :--- | :--- | :--- | :--- | :--- |
| **PNAD Contínua Microdata (2026Q1)** | IBGE (Instituto Brasileiro de Geografia e Estatística) | [ftp.ibge.gov.br — PNADC_012026.zip](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/2026/PNADC_012026.zip) | Public Open Data (Decreto 8.777/2016) | **Derived extract only** (`data/analysis/individual_microdata.csv`, 9 columns), built by the upstream `scripts/` pipeline (`fetch_ibge_microdata.py` + `process_microdata.py`) directly from the official fixed-width file; the full 228.6 MB archive is **not** redistributed. A 13-column **design-variable extract** (`data/analysis/individual_microdata_design.csv`) added in v1.2.0 carries `UPA/Estrato/V1008/V2003` for survey-design inference and is validated multiset-identical to the 9-column extract on the shared columns |
| **AI Exposure Ratings** | Eloundou, Manning, Mishkin, & Rock (2024). *Science*, 384(6702). | [github.com/openai/GPTs-are-GPTs](https://github.com/openai/GPTs-are-GPTs) | MIT License | Yes (`data/external/occ_level.csv`) |
| **BLS OEWS Employment** | U.S. Bureau of Labor Statistics (May 2021) | [bls.gov/oes/](https://www.bls.gov/oes/) | U.S. Public Domain | Yes (`data/external/national_May2021_dl.csv`) |
| **ISCO-08 x SOC 2010 Crosswalk** | BLS / SOC Policy Committee | BLS Crosswalk Archive | U.S. Public Domain | Yes (`data/external/isco08_to_soc2010.csv`) |
| **SOC 2010 x SOC 2018 Crosswalk** | BLS / OMB / SOCPC | BLS Crosswalk Archive | U.S. Public Domain | Yes (`data/external/soc2010_to_soc2018.csv`) |
| **COD Structure & Metadata** | IBGE Classificação de Ocupações | IBGE Documentação Técnica | Public Domain | Yes (`data/reference/cod_estrutura.json`) |

For full metadata and checksums, see [`data/external/SOURCES.md`](data/external/SOURCES.md).

### Data Extraction Provenance (PNAD Contínua microdata)

`data/analysis/individual_microdata.csv` is a **derived extract** of the official IBGE PNAD Contínua 2026Q1 microdata — it is not the raw IBGE file, which is not redistributed. The extract contains 9 analytic columns (`uf, occupation, weight, income, sex, race, informal, age, years_of_study`):

- `occupation` is the 3-digit COD subgroup mapped from the raw 4-digit `V4010` code (`data/reference/cod_estrutura.json`);
- `weight` is IBGE's calibrated household/person weight **V1028, carried through untransformed** — fractional by dictionary definition (6 integer digits + 8 decimal places; e.g. `000240.49527877` → `240.49527877`);
- `informal` follows IBGE's published informality rule: `VD4009` position in {02, 04, 06, 10} → informal, {01, 03, 05, 07} → formal, and employers/self-employed ({08, 09}) per CNPJ registration (`V4019`);
- household/person identifiers (`UPA`, `V1008`, `V2003`) and design variables (strata/PSU) are **intentionally omitted** from `individual_microdata.csv`: the empirical strategy uses WLS with occupation-clustered standard errors, not design-based linearization. *(v1.2.0: the companion extract `individual_microdata_design.csv` adds exactly these four columns for the design-based robustness appendix — `code/07_design_inference.R`; the two extracts agree row-for-row on all 9 analytic columns)*;
- exact duplicates among household members who share the same `V1028` and identical analytic values are expected once identifiers are stripped.

**Extraction code** (in-package, **`scripts/`** — runs directly from the package root; see `scripts/README.md`): `fetch_pnad_layout.py` (builds `pnadc_layout.json` from IBGE's SAS input dictionary), `fetch_ibge_microdata.py` (streams `PNADC_012026.zip` from IBGE's public FTP), `process_microdata.py` (fixed-width parse → extract; `python scripts/run_all.py paper` regenerates it into `data/output/`). The raw archive is not redistributed. The **estimation sample** drops 696 workers in COD groups without O*NET-SOC coverage (11, 21, 212, 223, 224): 228,325 extract rows → 227,629 estimation observations.

Two v1.2.0 extract builders extend this chain, both gated: `scripts/build_design_extract.py` regenerates the design-variable extract (validating it against the shipped extract), and `scripts/build_exposure_variants.py` rebuilds `data/analysis/variants_scores.json` (θ for all six Eloundou rating columns; the `dv_rating_beta` rebuild must reproduce the shipped `scores.json` 122/122 exactly).

---

## 3. Dataset Manifest

| File Path | Format | Obs / Rows | Key Variables | Description |
| :--- | :--- | :--- | :--- | :--- |
| `data/analysis/individual_microdata.csv` | CSV | 228,325 (estimation sample: 227,629) | `uf, occupation, weight, income, sex, race, informal, age, years_of_study` | Derived 9-column extract of PNAD Contínua 2026Q1 occupied workers; weights = untransformed calibrated V1028; identifiers and design variables omitted — see §2 "Data Extraction Provenance". |
| `data/analysis/scores.json` | JSON | 122 groups | `code, name, exposure, soc_codes, onet_soc_codes` | AI occupational task exposure scores ($\theta_j$, 0–10 scale). |
| `data/analysis/regional_panel.json` | JSON | 468 cells (112 COD occupations × 5 macro-regions; 92 of 560 possible cells suppressed by minimum-sample thresholds) | `region, occupation_code, occupation_name, jobs, sample_size, exposure, tier, avg_anos_estudo, avg_idade, renda, informality` | Occupation×macro-region cells built by `scripts/build_regional_panel.py`; input to the Python engine (`stats/logit.py`, `build_paper_tables.py`, `generate_paper_figures.py`). The R pipeline loads it but does not use it. |
| `data/analysis/econometrics.json` | JSON | 5 models | `beta, se, p_value, r_squared, n, n_clusters` | Authoritative econometric estimation outputs for S1–S4. |
| `data/analysis/robustness.json` | JSON | 7 checks | `beta, se, r_squared, delta_for_zero` | Sensitivity checks (R1–R7) and Oster (2019) bounding estimates. |
| `data/analysis/variants_scores.json` | JSON | 122 groups | `dv_rating_{alpha,beta,gamma}, human_rating_{alpha,beta,gamma}, disp_sd_beta, disp_range_beta, fallback_simple` | θ rebuilt for all six Eloundou et al. (2024) rating columns with the exact `compute_ai_exposure.py` aggregation (baseline gate 122/122); input to the v1.2.0 rating-variant robustness. |
| `data/analysis/individual_microdata_design.csv` | CSV | 228,325 | 9 analytic columns + `upa, estrato, v1008, v2003` | Design-variable extract for survey-design inference (v1.2.0); validated multiset-identical to `individual_microdata.csv` on the 9 analytic columns; regenerated deterministically by `scripts/build_design_extract.py`. |
| `output/robustness_ext/` | mixed | 27 model estimates (23 variants + 4 baselines); SE battery; 2 bootstrap p-values | — | v1.2.0 beyond-manuscript robustness battery: `polish_coefficients.csv`, `polish_results.json`, `p2_results.json`, `p2_wild_bootstrap.json`, `fig_polish_forest.{pdf,png}`, `README.md` (see §5 Step 5). |

### Package Structure

```
.
├── README.md                  this file (AEA DCAS replication package guide)
├── DCAS_checklist.md          compliance checklist
├── LICENSE.txt
├── CITATION.cff
├── renv.lock
├── code/                      R pipeline (canonical replication path)
│   ├── 00_run_all.R           driver: Rscript code/00_run_all.R
│   ├── 01_*.R … 05_*.R        data prep, estimation, analysis, tables, figures
│   ├── 06_polish_variants.R   v1.2.0 robustness extension: specification/θ variants (standalone)
│   ├── 07_design_inference.R  v1.2.0 robustness extension: survey-design inference (standalone)
│   └── test_econometrics.R    testthat suite (24 assertions, 9 blocks)
├── data/
│   ├── analysis/              shipped analysis inputs (see manifest above)
│   ├── external/              third-party inputs (O*NET-SOC ratings, crosswalks)
│   └── reference/             fixed-width layout and COD/SOC code mappings
├── docs/                      interactive dashboard & preprint PDF (GitHub Pages)
│   ├── index.html             interactive dashboard
│   ├── paper.pdf              compiled paper
│   └── .nojekyll
├── output/                    generated artifacts (results.rds, figures/, tables/)
│   └── robustness_ext/        v1.2.0 robustness battery artifacts & forest plots
├── paper/                     manuscript (LaTeX sources + compiled PDF)
│   ├── main.tex … main.pdf    article: `make` (or latexmk) rebuilds the PDF
│   ├── sections/              per-section sources (resumo … conclusão, apêndice)
│   ├── tables/                LaTeX table exhibits input by the manuscript
│   └── figures/               figure exhibits in PDF/SVG/PNG (+ TikZ sources)
└── scripts/                   Python data-construction pipeline — see scripts/README.md
                               (runs in place: python scripts/run_all.py paper)
```

---

## 4. Computational Requirements

### Software & Stack
- **Operating System:** Windows 10/11, macOS, or Linux
- **R:** Version 4.0+ (tested on R 4.6.1)
  - Required packages: `here`, `data.table`, `fixest`, `ggplot2`, `svglite`, `jsonlite`, `testthat`
  - Additional package for the v1.2.0 robustness extensions only: `survey` (`code/07_design_inference.R`)
- **LaTeX Distribution (for compiling manuscript):** TeX Live 2026 / MacTeX / MikTeX (`pdflatex` / `xelatex` with `latexmk`)

### Resource Requirements
- **Memory (RAM):** ~4 GB minimum, 8 GB recommended
- **Storage:** ~120 MB disk space (v1.2.0 adds the 14 MB design-variable extract)
- **Runtime:** Master execution pipeline (`00_run_all.R`) runs in under **45 seconds** on a standard multi-core laptop; the v1.2.0 robustness extensions (`06`, `07`, `compute_robustness_ext.py`) add ~4 minutes total.

---

## 5. Step-by-Step Instructions to Replicators

### Step 1: Install R Dependencies
From the R console or terminal:
```R
install.packages(c("here", "data.table", "fixest", "ggplot2", "svglite", "jsonlite", "testthat"), repos="https://cloud.r-project.org")
```

### Step 2: Execute Master Replication Pipeline
Run the canonical pipeline from the root of the replication package:
```bash
Rscript code/00_run_all.R
```
This automatically executes in sequence:
1. `code/01_load.R` — reads the microdata and reference mappings into memory.
2. `code/02_clean.R` — performs type coercion, derives Mincerian covariates, and computes leave-one-out regional formality rates.
3. `code/03_analyze.R` — estimates WLS models (S1–S4), sensitivity checks (R1–R7), and Oster bounds using `fixest::feols()`, saving `output/results.rds`.
4. `code/04_tables.R` — exports all 7 LaTeX publication tables to `output/tables/`.
5. `code/05_figures.R` — exports all 4 publication vector figures in PDF, SVG, and PNG formats to `output/figures/`.

### Step 3: Run the Verification Test Suite
Verify that all estimated parameters reproduce within exact tolerance thresholds:
```bash
Rscript code/test_econometrics.R
```
*Expected output: All testthat assertions PASSED [100%].*

**Verification (2026-09-15).** Re-run from a neutral copy of the package: `00_run_all.R` completed in 17.65s and regenerated `results.rds` and `econometrics.json` **md5-identical** to the shipped copies, with all 7 tables byte-identical; `test_econometrics.R` passed 9/9 blocks (58 executed expectation successes, 100%). See `output/computational_requirements.md` → "Verification Runs".

**Verification (2026-09-16, v1.1.0).** Manuscript added to `paper/` (15 pp, structured PT+EN abstract, S4 retired from the text). Re-run from the shipped tree: `00_run_all.R` regenerated `results.rds`, `econometrics.json`, `robustness.json` and all 7 tables **byte-identical** (across a `data.table` 1.18.4 → 1.18.6.1 library bump); figure PDFs differ only in the embedded creation timestamp — the PNG/SVG renderings are byte-identical. `test_econometrics.R` passed 9/9 blocks (100%). `latexmk -pdf` compiles `paper/main.pdf` standalone from the package (Overleaf-compatible); extracted text matches page-for-page (15/15).

**Verification (2026-09-18, v1.2.0).** Extensions added without touching the canonical chain: `Rscript code/06_polish_variants.R` and `code/07_design_inference.R` reproduce every shipped estimate at their gates (max diff 0.0e+00 after the 4-decimal storage rounding) and regenerate `output/robustness_ext/`; `scripts/build_exposure_variants.py` passes its 122/122 baseline gate; `scripts/compute_robustness_ext.py` reproduces the wild-bootstrap floor (p = 0.0010, S1 t = 8.246 / S3 t = −4.084). `test_econometrics.R` re-run on the v1.2.0 tree: 9/9 blocks, 100% (note: inside a parent git repository, `here::here()` may resolve above the package; run from a neutral copy or create a package-local `.here` sentinel).

### Step 4 (optional): Regenerate the Microdata Extract from IBGE

The Python pipeline ships in `scripts/` and **runs directly from this package root** — it auto-detects the package layout (data at `<pkg>/data/`) and can be forced elsewhere with the `PNAD_DATA_ROOT` environment variable. The `paper` task regenerates only the artifacts the article uses (current quarter + econometrics), downloading `PNADC_012026.zip` (228.6 MB; streamed in memory, re-downloaded by each stage that needs it) from IBGE's public FTP. Requires Python ≥ 3.10 with `numpy`, `pandas` and `statsmodels`.

```bash
python scripts/run_all.py paper     # paper-relevant chain (13 steps; ~5 downloads of the quarter zip)
python scripts/run_all.py pipeline # full upstream chain (adds the 2015–2026 historical series, ~45 quarters)
```

Outputs land in `data/output/` (never overwriting the shipped `data/analysis/` files) and tables in `paper/tables/`. This step is **not required** for the canonical R replication above, which consumes the shipped extract.

### Step 5 (optional): Robustness Extension Battery (v1.2.0)

Beyond-manuscript robustness checks — **not** part of the paper's exhibits; every script gates on exact reproduction of the canonical results before estimating any variant. Full documentation and findings: [`output/robustness_ext/README.md`](output/robustness_ext/README.md).

```bash
Rscript code/06_polish_variants.R        # P1/P3/P5: UF FE, log/IHS income, schooling top-code, rating variants, θ bounding, S3 logit (~1–2 min)
Rscript code/07_design_inference.R       # P2: occupation vs PSU vs two-way vs survey-linearized SEs; Kish ESS; DEFF (needs R package survey; ~1 min)
python scripts/compute_robustness_ext.py # wild cluster bootstrap for S1/S3 occupation clusters (~1 min)
```

The two shipped extension inputs are regenerable deterministically: `scripts/build_exposure_variants.py` (`→ variants_scores.json`, 122/122 baseline gate) and `scripts/build_design_extract.py` (`→ individual_microdata_design.csv`, validated against the shipped extract; downloads `PNADC_012026.zip` unless `MICRODATA_ZIP`/`MICRODATA_TXT` point at a local copy).

**Headline findings:** all 23 variants (27 models incl. baselines) preserve sign and significance (weakest p = 8.4e-04); three quantified sensitivities — schooling top-code (S1 β −25.6%), income functional form (levels overstate the residual gradient ~16%), rating variant (S1 β 0.06–0.39; Spearman ρ 0.61–0.98); the 696 coverage-missing workers are immaterial (±2%); design-based SEs are ~10× smaller than occupation-clustered SEs (occupation clustering is the conservative, binding choice — θ varies only between occupations); wild cluster bootstrap rejects at the floor for S1 (t = 8.246) and S3 (t = −4.084), p ≤ 0.001.

---

## 6. Table & Figure to Program:Line Mapping

Every empirical exhibit in the manuscript is mechanically produced by the replication code:

| Paper Exhibit | Description | Generating Script | Generating Function / Block | Input Data | Output File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Table 1** | Descriptive statistics (computed cells, no literals) | `code/04_tables.R` | Lines 135–153 | `output/results.rds` (`desc_stats`) | `output/tables/tab_descritivas.tex` |
| **Table 2** | Education-Exposure Gradient (S1 & S2) | `code/04_tables.R` | Lines 178–211 | `output/results.rds` (S1, S2) | `output/tables/tab_gradiente.tex` |
| **Table 3** | Informality mediation (S3 & S3a) | `code/04_tables.R` | Lines 213–242 | `output/results.rds` (S3, S3a) | `output/tables/tab_s3.tex` |
| **Table 4** | Econometric robustness battery | `code/04_tables.R` | Lines 268–292 | `output/results.rds` (R1–R6) | `output/tables/tab_robustez.tex` |
| **Table A.1** | Group-level robustness (Appendix) | `code/04_tables.R` | Lines 294–331 | `output/results.rds` (R7) | `output/tables/tab_robustez_grupos.tex` |
| **Figure 1** | Education vs. AI Exposure Scatter & Slope ($\hat{\beta}_1 = 0{,}23$, line at covariate means) | `code/05_figures.R` | Lines 120–184 | `individual_microdata.csv`, `output/results.rds` (S1) | `output/figures/fig1_gradiente.pdf` |
| **Figure 2** | Conceptual mediation DAG (hypothesis, not estimated) | `paper/figures/fig_dag_mediacao.tex` | Hand-authored TikZ (`standalone` class) — no generating script; compile with `pdflatex fig_dag_mediacao.tex` | — (conceptual diagram) | `output/figures/fig_dag_mediacao.pdf` |
| **Figure 3** | Informality mediation (S3a vs. S3 lines at covariate means) | `code/05_figures.R` | Lines 189–227 | `individual_microdata.csv`, `output/results.rds` (S3, S3a) | `output/figures/fig2_mediacao.pdf` |

Figure numbering follows the compiled PDF: main-text Figures 1–3 are `fig1_gradiente`, `fig_dag_mediacao` and `fig2_mediacao`; the engine filename `fig2_…` sits one position earlier than its PDF number (Figure 3). `fig_dag_mediacao` (PDF Figure 2) is the only exhibit not generated by the R pipeline. `fig3_regional_slopes` (lines 232–276), `fig5_robustez_forest` (lines 280–345) and `tab_s4` (lines 244–266 of `04_tables.R`) are still generated for the slide deck but are no longer included in the manuscript (Table 4 / Table A.1 carry the same content). Appendix proofs A.1–A.3 are condensed in the PDF; `tab_maiores` is cited in §3 as descriptive text without a table.

---

## 7. License

- **Code License:** BSD 3-Clause License (see [`LICENSE.txt`](LICENSE.txt)).
- **Data Usage:** Creative Commons Attribution 4.0 International (CC-BY 4.0) with attribution to IBGE and Eloundou et al. (2024).
