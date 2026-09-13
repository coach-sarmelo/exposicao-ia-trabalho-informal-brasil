# Replication Package: Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil

**Author:** Marcelo Moura Freire  
**Standard:** [Social Science Data Editors Data and Code Availability Standard (DCAS)](https://datacodestandard.org/) / AEA Data Editor Template  
**Date:** 2026-08-23  
**Deposit Target:** openICPSR / Zenodo / Dataverse  

---

## 1. Overview & Paper Citation

This replication package contains the complete data, code, microeconometric analysis pipeline, test suite, and generated artifacts for the research paper:

> **Freire, Marcelo Moura (2026).** *Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil.*

The paper investigates the distribution of artificial intelligence (LLM) exposure across formal and informal employment in Brazil using microdata from the IBGE Continuous National Household Sample Survey (PNAD Contínua) linked to O*NET-SOC occupational exposure ratings (Eloundou et al., 2024).

---

## 2. Data Availability and Provenance Statements

### Statement of Rights
The author certifies that he has legitimate access to all data used in this study and the right to distribute the replication materials. All primary and secondary data are public, open-access, and reproducible.

### Summary of Data Sources

| Data Name | Source / Citation | Access / URL | License | Provided in Package? |
| :--- | :--- | :--- | :--- | :--- |
| **PNAD Contínua Microdata (2026Q1)** | IBGE (Instituto Brasileiro de Geografia e Estatística) | [ftp.ibge.gov.br](https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/) | Public Open Data (Decreto 8.777/2016) | Yes (`data/analysis/individual_microdata.csv`) |
| **AI Exposure Ratings** | Eloundou, Manning, Mishkin, & Rock (2024). *Science*, 384(6702). | [github.com/openai/GPTs-are-GPTs](https://github.com/openai/GPTs-are-GPTs) | MIT License | Yes (`data/external/occ_level.csv`) |
| **BLS OEWS Employment** | U.S. Bureau of Labor Statistics (May 2021) | [bls.gov/oes/](https://www.bls.gov/oes/) | U.S. Public Domain | Yes (`data/external/national_May2021_dl.csv`) |
| **ISCO-08 x SOC 2010 Crosswalk** | BLS / SOC Policy Committee | BLS Crosswalk Archive | U.S. Public Domain | Yes (`data/external/isco08_to_soc2010.csv`) |
| **SOC 2010 x SOC 2018 Crosswalk** | BLS / OMB / SOCPC | BLS Crosswalk Archive | U.S. Public Domain | Yes (`data/external/soc2010_to_soc2018.csv`) |
| **COD Structure & Metadata** | IBGE Classificação de Ocupações | IBGE Documentação Técnica | Public Domain | Yes (`data/reference/cod_estrutura.json`) |

For full metadata and checksums, see [`data/external/SOURCES.md`](data/external/SOURCES.md).

---

## 3. Dataset Manifest

| File Path | Format | Obs / Rows | Key Variables | Description |
| :--- | :--- | :--- | :--- | :--- |
| `data/analysis/individual_microdata.csv` | CSV | 227,629 | `uf, occupation, weight, income, sex, race, informal, age, years_of_study` | Individual worker microdata from PNAD Contínua 2026Q1 with sampling weights. |
| `data/analysis/scores.json` | JSON | 122 groups | `code, name, exposure, soc_codes, onet_soc_codes` | AI occupational task exposure scores ($\theta_j$, 0–10 scale). |
| `data/analysis/regional_panel.json` | JSON | 27 UFs | `uf, formality_rate, mean_exposure, gradient` | State-level panel of formality depth and educational slopes. |
| `data/analysis/econometrics.json` | JSON | 5 models | `beta, se, p_value, r_squared, n, n_clusters` | Authoritative econometric estimation outputs for S1–S4. |
| `data/analysis/robustness.json` | JSON | 7 checks | `beta, se, r_squared, delta_for_zero` | Sensitivity checks (R1–R7) and Oster (2019) bounding estimates. |

---

## 4. Computational Requirements

### Software & Stack
- **Operating System:** Windows 10/11, macOS, or Linux
- **R:** Version 4.0+ (tested on R 4.6.1)
  - Required packages: `here`, `data.table`, `fixest`, `ggplot2`, `svglite`, `jsonlite`, `testthat`
- **LaTeX Distribution (for compiling manuscript):** TeX Live 2026 / MacTeX / MikTeX (`pdflatex` / `xelatex` with `latexmk`)

### Resource Requirements
- **Memory (RAM):** ~4 GB minimum, 8 GB recommended
- **Storage:** ~100 MB disk space
- **Runtime:** Master execution pipeline (`00_run_all.R`) runs in under **45 seconds** on a standard multi-core laptop.

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

---

## 6. Table & Figure to Program:Line Mapping

Every empirical exhibit in the manuscript is mechanically produced by the replication code:

| Paper Exhibit | Description | Generating Script | Generating Function / Block | Input Data | Output File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Table 1** | Descriptive statistics by formality status | `code/04_tables.R` | Lines 45–60 | `individual_microdata.csv` | `output/tables/tab_descritivas.tex` |
| **Table 2** | Highest & lowest exposure occupations | `code/04_tables.R` | Lines 63–95 | `scores.json`, `individual_microdata.csv` | `output/tables/tab_maiores.tex` |
| **Table 3** | Education-Exposure Gradient (S1 & S2) | `code/04_tables.R` | Lines 98–122 | `output/results.rds` (S1, S2) | `output/tables/tab_gradiente.tex` |
| **Table 4** | Informality mediation (S3 & S3a) | `code/04_tables.R` | Lines 125–149 | `output/results.rds` (S3, S3a) | `output/tables/tab_s3.tex` |
| **Table 5** | Regional formality interaction (S4) | `code/04_tables.R` | Lines 152–175 | `output/results.rds` (S4) | `output/tables/tab_s4.tex` |
| **Table 6** | Econometric robustness battery | `code/04_tables.R` | Lines 178–215 | `output/results.rds` (R1–R6) | `output/tables/tab_robustez.tex` |
| **Table A.1** | Group-level robustness (Appendix) | `code/04_tables.R` | Lines 218–265 | `output/results.rds` (R7) | `output/tables/tab_robustez_grupos.tex` |
| **Figure 1** | Education vs. AI Exposure Scatter & Slope ($\hat{\beta}_1 = 0{,}23$) | `code/05_figures.R` | Lines 88–118 | `individual_microdata.csv`, `scores.json` | `output/figures/fig1_gradiente.pdf` |
| **Figure 2** | Informality mediation (Gross S3a vs. Net S3) | `code/05_figures.R` | Lines 120–150 | `individual_microdata.csv`, `scores.json` | `output/figures/fig2_mediacao.pdf` |
| **Figure 3** | Regional slopes across 5 macro-regions | `code/05_figures.R` | Lines 152–195 | `individual_microdata.csv`, `scores.json` | `output/figures/fig3_regional_slopes.pdf` |
| **Figure 5** | Robustness forest plot across variations | `code/05_figures.R` | Lines 198–275 | `output/results.rds` | `output/figures/fig5_robustez_forest.pdf` |

---

## 7. License

- **Code License:** BSD 3-Clause License (see [`LICENSE.txt`](LICENSE.txt)).
- **Data Usage:** Creative Commons Attribution 4.0 International (CC-BY 4.0) with attribution to IBGE and Eloundou et al. (2024).
