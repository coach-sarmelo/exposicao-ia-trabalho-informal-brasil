# CLAUDE.md -- Academic & Empirical Research with Claude Code

**Project:** Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil  
**Author:** Marcelo Moura Freire  
**Repository:** https://github.com/coach-sarmelo/claude-code-my-workflow  
**Branch:** main  
**Standard:** AEA Data Editor Standard for Reproducibility (Social Science Data Editors DCAS / `template_README`)

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- run test suites (`pytest`), execute data pipelines, and verify compiled paper/figures at the end of every task
- **Single source of truth** -- Python data pipeline (`data/scripts/run_all.py`) generates authoritative datasets in `data/output/`; LaTeX paper (`paper/`) and figures derive directly from them
- **Quality gates** -- strict standards (80 Commit / 90 PR / 95 Excellence); nothing ships unverified
- **[LEARN] tags & Knowledge** -- when corrected, record patterns to [MEMORY.md](MEMORY.md) or use `/learn`

Cross-session context lives in [MEMORY.md](MEMORY.md); past plans, specs, and session logs are in [quality_reports/](quality_reports/).

---

## Folder Structure

```
claude-code-my-workflow/
├── AGENTS.md / GEMINI.md / CLAUDE.md # Core AI instructions
├── .agents/ / .claude/               # 18 agents, 52 skills, 33 rules, 7 hooks
├── data/                             # Data pipeline & microdata processing
│   ├── external/                     # Benchmark datasets (O*NET-SOC, ISCO crosswalks) + SOURCES.md
│   ├── output/                       # Authoritative JSON & CSV datasets
│   ├── scripts/                      # 13-step Python pipeline (run_all.py)
│   └── tests/                        # 137 unit and econometric tests (pytest)
├── paper/                            # LaTeX research paper
│   ├── main.tex                      # Primary paper source
│   ├── sections/                     # Modular section files (00_resumo .. 06_conclusao, apendice)
│   ├── tables/                       # Generated regression & summary tables
│   ├── figures/                      # Publication-ready vector plots (PDF + PNG)
│   └── references.bib                # Verified bibliography
├── Figures/                          # Mirror of publication figures for slides/reports
├── quality_reports/                  # Plans, session logs, merge reports, decision records
└── templates/                        # Templates for session logs, specs, and reports
```

---

## Commands (Git Bash / PowerShell)

```bash
# Run complete data pipeline
python data/scripts/run_all.py

# Run econometric & pipeline test suite
pytest -q

# Compile LaTeX paper (fresh 3-pass / latexmk)
cd paper && latexmk -pdf -interaction=nonstopmode main.tex

# Quality scoring
python scripts/quality_score.py paper/main.tex

# Workflow integrity & surface checks
bash scripts/check-surface-sync.sh
bash scripts/check-palette-sync.sh
```

---

## Quality Thresholds (Advisory & Gate)

| Score | Checkpoint | Meaning |
|-------|------------|---------|
| 80 | Commit | Methodologically sound, tests passing, verified numbers |
| 90 | PR / Showcase | Ready for public portfolio presentation (LinkedIn / GitHub) |
| 95 | Excellence | Publication-grade academic & visual polish |

Enforced by git pre-commit hook (`.githooks/pre-commit` installed via `bash scripts/install-hooks.sh`).
