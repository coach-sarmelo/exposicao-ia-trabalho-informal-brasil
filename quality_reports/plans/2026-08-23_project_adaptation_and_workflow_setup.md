# Implementation Plan: Academic Workflow Adaptation & Project Setup (Updated)

**Project:** Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil  
**Author:** Marcelo Moura Freire (Universidade de Coimbra)  
**Target Standard:** AEA Data Editor Standard for Reproducibility (Social Science Data Editors DCAS / `template_README`) & AEA-RCT style  
**Shell Environment:** Git Bash (GNU Bash 5.3) on Windows 11  
**Date:** 2026-08-23  
**Status:** APPROVED FOR EXECUTION

---

## 1. Context & Objectives

Adapt the academic workflow (forked from `pedrohcgs/claude-code-my-workflow`) for **Marcelo Moura Freire's** empirical economics portfolio project:
- **Scope:** Rigorous empirical and theoretical study on AI exposure in Brazil's informal labor market.
- **Goal:** Stand out in the job market as a recent economics graduate by demonstrating senior-level microeconometrics, data science, and AEA Data Editor replication compliance.
- **Environment:** Antigravity (Gemini 3.7) + Git Bash as default terminal + TeX Live 2026 + Python 3.14 + R 4.6.

---

## 2. Shell & Scripts Verification Status

All native `.sh` and `.py` scripts have been verified in Git Bash:
- `scripts/validate-setup.sh`: **PASS (11/11 checks)** (XeLaTeX, Quarto, Git, Python 3.14, R 4.6, GitHub CLI, Hooks).
- `scripts/check-palette-sync.sh`: **PASS** (11/11 palette colors in sync).
- `scripts/install-hooks.sh`: **PASS** (`core.hooksPath -> .githooks` installed).
- `scripts/check-model-versions.sh`: **PASS** (model versions match).
- `scripts/check-skill-integrity.py`: **PASS** (all 52 skills valid).
- `scripts/quality_score.py`: **PASS** (`paper/main.tex` scored 100/100).
- `scripts/check-surface-sync.sh`: **DRIFT DETECTED** on rule count (disk has 33 rules, docs state 32). Resolved during configuration update.

---

## 3. Standardized Folder Architecture (AEA Compliant)

```
claude-code-my-workflow/
├── AGENTS.md / GEMINI.md / CLAUDE.md # Pair-programming & project instructions
├── MEMORY.md                         # Persistent cross-session knowledge & [LEARN] log
├── README.md                         # AEA Data Editor compliant Replication README (template_README)
├── .agents/                          # Skills, subagents, rules, hooks
├── data/                             # Data & replication module
│   ├── external/                     # Third-party benchmark data (O*NET-SOC, ISCO crosswalks) + SOURCES.md
│   ├── output/                       # Authoritative processed data (JSONs, individual_microdata.csv)
│   ├── scripts/                      # 13-step Python ETL, econometrics, table & figure generators
│   │   ├── reference/                # COD structure, PNAD layout, UF codes
│   │   └── stats/                    # Econometric estimators (WLS logit, clustered SEs)
│   └── tests/                        # 137 unit and econometric specification tests (pytest)
├── paper/                            # LaTeX Research Paper
│   ├── main.tex                      # Article root
│   ├── sections/                     # 00_resumo .. 06_conclusao, apendice
│   ├── tables/                       # Booktabs tables generated from data/output/
│   ├── figures/                      # Publication-ready vector figures (PDF + PNG, 300+ DPI)
│   └── references.bib                # Centralized BibTeX references
├── Figures/                          # Mirror of publication figures for slides/reports/README
├── quality_reports/                  # Plans, specs, session logs, reproducible audit reports
└── templates/                        # Templates for session logs, decision records, specs
```

---

## 4. Execution Steps

### Step 1: Asset Migration & Workspace Cleanup
1. Copy figure files (`fig1_gradiente.*`, `fig2_mediacao.*`, `fig3_regional_slopes.*`, `fig5_robustez_forest.*`) to `paper/figures/`.
2. Remove empty stray directories (`data/data/output/` and `data/paper/tables/`).
3. Add `pytest.ini` with `pythonpath = data` at root.

### Step 2: Update Configuration Files & Fix Surface Counts
1. Update `AGENTS.md` and `CLAUDE.md` with:
   - Project: *Exposição à IA em um Mercado de Trabalho Informal (Brasil)*
   - Author: *Marcelo Moura Freire (Universidade de Coimbra)*
   - Authoritative pipeline: `data/scripts/run_all.py` -> `data/output/` -> `paper/tables/` + `paper/figures/` -> `paper/main.tex`.
   - Update rule counts (33 rules) to satisfy `check-surface-sync.sh`.
2. Create `GEMINI.md` customized for Antigravity with Gemini 3.7.
3. Update `.agents/rules/model-routing.md`.

### Step 3: AEA Data Editor Standard Replication README
1. Draft `README.md` following [Social Science Data Editors `template_README`](https://social-science-data-editors.github.io/template_README/):
   - Data Availability Statement (PNAD Contínua microdata, O*NET-SOC ratings, ISCO crosswalks).
   - Computational Requirements (Python 3.14, TeX Live 2026, packages).
   - Step-by-step Execution Instructions (`bash scripts/run_all.sh` / `python scripts/run_all.py`).
   - Table and Figure to Script mapping table.

### Step 4: Verification Gate
1. Run `pytest` across all 137 tests -> confirm 100% pass rate.
2. Run `latexmk -pdf -interaction=nonstopmode main.tex` in `paper/` -> confirm clean build.
3. Run `bash scripts/check-surface-sync.sh` -> confirm 0 drift errors.
4. Record session log in `quality_reports/session_logs/`.
