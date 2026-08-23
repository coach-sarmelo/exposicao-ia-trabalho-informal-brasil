# Replication Package: Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil

**Author:** Marcelo Moura Freire  
**Standard Compliance:** [Social Science Data Editors Data and Code Availability Standard (DCAS)](https://social-science-data-editors.github.io/template_README/) / AEA Data Editor Guidelines  
**Date:** 2026-08-23  

---

## 1. Overview

This replication package contains the complete data, code, microeconometric analysis pipeline, test suite, and LaTeX manuscript for the research paper:

> **Freire, Marcelo Moura (2026).** *Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil.* 

The paper examines the empirical and theoretical distribution of artificial intelligence (LLM) task exposure across formal and informal employment in Brazil using microdata from the IBGE Continuous National Household Sample Survey (PNAD Contínua) linked to O*NET-SOC occupational exposure ratings (Eloundou et al., 2024).

---

## 2. Data Availability and Provenance Statements

### Statement of Rights
The author certifies that he has legitimate access to all data used in this study and the right to distribute the replication materials. All primary and secondary data are public, open-access, and reproducible.

### Summary of Data Sources

| Data Name | Source / Citation | Access / URL | License | Location in Repo |
| :--- | :--- | :--- | :--- | :--- |
| **PNAD Contínua Microdata** | IBGE (Instituto Brasileiro de Geografia e Estatística) | [ftp.ibge.gov.br](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/) | Public Open Data (Decreto 8.777/2016) | Fetched via `data/scripts/fetch_ibge_microdata.py` |
| **AI Exposure Ratings** | Eloundou, Manning, Mishkin, & Rock (2024). *Science*, 384(6702). | [github.com/openai/GPTs-are-GPTs](https://github.com/openai/GPTs-are-GPTs) | MIT License | `data/external/occ_level.csv` |
| **BLS OEWS Employment** | U.S. Bureau of Labor Statistics (May 2021) | [bls.gov/oes/](https://www.bls.gov/oes/) | U.S. Public Domain | `data/external/national_May2021_dl.csv` |
| **ISCO-08 x SOC 2010 Crosswalk** | BLS / SOC Policy Committee | BLS Crosswalk Archive | U.S. Public Domain | `data/external/isco08_to_soc2010.csv` |
| **SOC 2010 x SOC 2018 Crosswalk** | BLS / OMB / SOCPC | BLS Crosswalk Archive | U.S. Public Domain | `data/external/soc2010_to_soc2018.csv` |
| **Brazilian Territorial Grids (UF)** | IBGE Malhas Territoriais | [servicodados.ibge.gov.br](https://servicodados.ibge.gov.br/api/v3/malhas/) | Public Open Data | Fetched dynamically |

For detailed provenance, checksums, and version notes for every benchmark dataset, see [`data/external/SOURCES.md`](data/external/SOURCES.md).

---

## 3. Dataset List & Manifest

| File | Format | Observations | Key Variables | Description |
| :--- | :--- | :--- | :--- | :--- |
| `data/output/individual_microdata.csv` | CSV | 227,629 | `UF, V2009, VD3005, VD4009, VD4016, exposure` | Individual-level microdata with Mincer controls and assigned AI exposure score |
| `data/output/scores.json` | JSON | 122 groups | `cod_code, cod_title, exposure, soc_matches` | COD-level occupation AI exposure scores (0–10 scale) |
| `data/output/regional_panel.json` | JSON | 27 UFs | `uf, formality_rate, mean_exposure, gradient` | State-level panel of formality depth and educational gradients |
| `data/output/econometrics.json` | JSON | Multiple specs | `beta, se, p_value, r2, n` | Econometric estimation results for specifications S1–S4 |
| `data/output/robustness.json` | JSON | 5 specs | `beta, se, p_value, spec_name` | Sensitivity analysis and robustness check outputs |

---

## 4. Computational Requirements

### Software & Stack
- **Operating System:** Windows 11, macOS, or Linux
- **Shell:** Bash (Git Bash on Windows)
- **Python:** Version 3.10+ (tested on Python 3.14.7)
  - Core packages: `numpy`, `scipy`, `pandas`, `statsmodels`, `matplotlib`, `pytest`
- **LaTeX Distribution:** TeX Live 2026 (or MacTeX / MikTeX)
  - Engine: `pdflatex` or `xelatex` with `latexmk`
  - Packages: `booktabs`, `natbib`, `amsmath`, `graphicx`, `microtype`, `icomma`

### Resource Requirements
- **Memory (RAM):** ~4 GB minimum, 8 GB recommended
- **Storage:** ~150 MB disk space
- **Runtime:** Complete replication (data processing + econometrics + figures + LaTeX compilation) executes in under **45 seconds** on standard hardware.

---

## 5. Step-by-Step Instructions to Replicators

### Step 1: Environment Setup
Clone the repository and install dependencies:
```bash
# Python dependencies (for cross-validation suite):
pip install -r requirements.txt

# R dependencies (canonical analysis engine):
Rscript -e "install.packages(c('here', 'data.table', 'fixest', 'ggplot2', 'svglite', 'jsonlite', 'testthat'), repos='https://cloud.r-project.org')"
```

### Step 2: Execute Complete Data & Econometrics Pipeline
Run the canonical R replication pipeline:
```bash
Rscript scripts/R/00_run_all.R
```
This executes:
1. `scripts/R/01_load.R` — reads 227k PNAD Contínua microdata records and benchmark JSONs.
2. `scripts/R/02_clean.R` — cleans Mincerian covariates and derives leave-one-out regional formality.
3. `scripts/R/03_analyze.R` — estimates S1–S4, R1–R7, and Oster bounds via `fixest::feols()`.
4. `scripts/R/04_tables.R` — generates all 7 LaTeX tables in `paper/tables/`.
5. `scripts/R/05_figures.R` — exports dual vector (`.pdf`, `.svg`) and `.png` figures in `paper/figures/` and `Figures/`.

*(Optional dual-engine Python pipeline: `python data/scripts/run_all.py`)*

### Step 3: Run Automated Verification Suites
```bash
# R econometric test suite:
Rscript scripts/R/test_econometrics.R

# Python econometric & cross-validation test suite:
pytest -q
```

### Step 4: Compile the Manuscript & Presentation Decks
```bash
# Compile LaTeX Paper (PDF):
cd paper && latexmk -pdf -interaction=nonstopmode main.tex && cd ..

# Compile Beamer Presentation Deck (PDF):
cd Slides && xelatex -interaction=nonstopmode 01_exposicao_ia_brasil.tex && bibtex 01_exposicao_ia_brasil && xelatex -interaction=nonstopmode 01_exposicao_ia_brasil.tex && cd ..

# Render Quarto RevealJS Presentation (HTML):
quarto render Quarto/01_exposicao_ia_brasil.qmd
```

---

## 6. Table & Figure Replication Mapping

Every empirical claim, table, and figure in the paper is mechanically linked to a generating script:

| Paper Exhibit | Description | Generating Script | Authoritative Input Artifact | Output File |
| :--- | :--- | :--- | :--- | :--- |
| **Table 1** | Descriptive statistics by formality status | `data/scripts/build_paper_tables.py` | `data/output/statistics.json` | `paper/tables/tab_descritivas.tex` |
| **Table 2** | Highest & lowest exposure occupations | `data/scripts/build_paper_tables.py` | `data/output/scores.json` | `paper/tables/tab_maiores.tex` |
| **Table 3** | Education-Exposure Gradient (S1 & S2) | `data/scripts/build_paper_tables.py` | `data/output/econometrics.json` | `paper/tables/tab_gradiente.tex` |
| **Table 4** | Informality, exposure & schooling mediation (S3 & S3a) | `data/scripts/build_paper_tables.py` | `data/output/econometrics.json` | `paper/tables/tab_s3.tex` |
| **Table 5** | Regional formality depth interaction (S4) | `data/scripts/build_paper_tables.py` | `data/output/econometrics.json` | `paper/tables/tab_s4.tex` |
| **Table 6** | Econometric robustness battery | `data/scripts/build_paper_tables.py` | `data/output/robustness.json` | `paper/tables/tab_robustez.tex` |
| **Table A.1** | Group-level robustness (Appendix) | `data/scripts/build_paper_tables.py` | `data/output/robustness.json` | `paper/tables/tab_robustez_grupos.tex` |
| **Figure 1** | Education vs. AI Exposure Scatter & Slope ($\hat{\beta}_1 = 0.23$) | `data/scripts/generate_paper_figures.py` | `data/output/regional_panel.json` | `paper/figures/fig1_gradiente.pdf` |
| **Figure 2** | Informality mediation (Gross S3a vs. Partial S3) | `data/scripts/generate_paper_figures.py` | `data/output/econometrics.json` | `paper/figures/fig2_mediacao.pdf` |
| **Figure 3** | Regional slopes across 5 macro-regions | `data/scripts/generate_paper_figures.py` | `data/output/regional_panel.json` | `paper/figures/fig3_regional_slopes.pdf` |
| **Figure 5** | Robustness forest plot across variations | `data/scripts/generate_paper_figures.py` | `data/output/robustness.json` | `paper/figures/fig5_robustez_forest.pdf` |

---

## 7. Quality & Verification Gates

This project enforces strict verification gates:
- **Pre-commit Gate:** `.githooks/pre-commit` verifies that all unit tests pass, surface-counts match, and paper scores $\ge 80/100$ before any commit is saved.
- **Audit Reproducibility:** Run `python scripts/quality_score.py paper/main.tex` to audit manuscript formatting and quality.
