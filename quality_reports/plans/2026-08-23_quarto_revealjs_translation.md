# Plan: Port Beamer Research Presentation Deck to Quarto RevealJS

**Date:** 2026-08-23  
**Target File:** `Quarto/01_exposicao_ia_brasil.qmd`  
**Source of Truth:** `Slides/01_exposicao_ia_brasil.tex`  
**Standard:** 95+ Excellence Gate / Content Invariants INV-1 through INV-12  

---

## 1. Objectives & Quality Requirements
- Translate all 16 frames from `Slides/01_exposicao_ia_brasil.tex` into a 1:1 matching Quarto RevealJS presentation `Quarto/01_exposicao_ia_brasil.qmd`.
- Enforce strict mathematical and notation parity (INV-2), single bibliography (INV-5), and web-compatible images (PNG/SVG, INV-4).
- Use `Quarto/theme-template.scss` custom classes (`.keybox`, `.methodbox`, `.highlightbox`, `.emorygold`, `.emoryblue`, etc.) with responsive two-column grid layouts (`:::: {.columns}`).
- Render with Quarto CLI (`quarto render Quarto/01_exposicao_ia_brasil.qmd`) with 0 errors and 0 warnings.
- Run complete verification test suite (`pytest -q`, palette/surface checks) and update project logs.

---

## 2. Slide Structure & Mapping Matrix

| Beamer Frame | Quarto Slide | Layout / Components | Key Elements / Invariants |
|---|---|---|---|
| Frame 1: Title | Title Slide | RevealJS Title Header | Title, Subtitle, Author, Date |
| Frame 2: Motivação | `## Motivação: A Dualidade do Mercado de Trabalho Brasileiro` | 2 columns (`.column width="60%"`, `.column width="40%"`) | Context bullets, Questão Central box, Mecanismo Proposto box |
| Frame 3: Perguntas | `## Três Perguntas de Pesquisa` | Numbered list with sub-bullets | 1. Gradiente, 2. Mediação, 3. Polarização Espacial |
| Frame 4: Transição 1 | `# Modelo Teórico de Alocação e Arbitragem` | Section slide (h1 full-bleed) | Dark accent transition |
| Frame 5: Modelo Teórico | `## Modelo de Designação Ocupacional (Assignment Model)` | 2 columns (`.column width="50%"`, `.column width="50%"`) | Primitive production function $y_{js}(e)$, Supermodularidade box, Cost structure |
| Frame 6: Previsões Teóricas | `## Arbitragem Formal-Informal e Previsões Teóricas` | 2 columns | Equilibrium threshold $e^*_j$, Proposição 1 box, Corolário 1 box |
| Frame 7: Transição 2 | `# Dados Microeconômicos e Estratégia Empírica` | Section slide (h1) | Dark accent transition |
| Frame 8: Microdados | `## Microdados da PNAD Contínua e Construção do Escore $\theta_j$` | 2 columns (`width="55%"`, `width="45%"`) | Sample stats ($N = 227.629$), Harmonization, Moulton correction box, Mincerian controls box |
| Frame 9: Especificações | `## Especificações Econométricas Estimadas` | Stacked list with display equations | S1 Baseline, S2 Wage control, S3a/S3 Mediation, S4 LOO Interaction |
| Frame 10: Transição 3 | `# Resultados Empíricos e Mecanismos` | Section slide (h1) | Dark accent transition |
| Frame 11: Resultado 1 | `## Resultado 1: Gradiente Escolaridade--Exposição ($\hat{\beta}_1 = 0{,}23$)` | 2 columns | Estimation bullets, Oster (2019) $\delta=1{,}64$ box, `../paper/figures/fig1_gradiente.png` |
| Frame 12: Resultado 2 | `## Resultado 2: Mediação Parcial da Informalidade (Corolário 1)` | 2 columns | S3a vs S3 decomposition, 37.2% vs 62.8% channel box, `../paper/figures/fig2_mediacao.png` |
| Frame 13: Resultado 3 | `## Resultado 3: Polarização Espacial e Formalidade Regional (S4)` | 2 columns | S4 LOO estimates, Marginal derivative, $e^* = 11{,}14$ threshold box, `../paper/figures/fig3_regional_slopes.png` |
| Frame 14: Robustez | `## Bateria de Robustez Econométrica (R1--R7)` | 2 columns | R1--R7 summary bullets, Wild Cluster Bootstrap box, `../paper/figures/fig5_robustez_forest.png` |
| Frame 15: Conclusões | `## Conclusões e Implicações de Política Pública` | 2 columns | Main findings, Policy recommendations box |
| Frame 16: Referências | `## Referências Selecionadas` | RevealJS References block | Citations mapped to `../Bibliography_base.bib` |

---

## 3. Implementation Steps

1. **Step 1: Environment & Theme Inspection**
   - Verify `Quarto/theme-template.scss` classes and create any necessary styling overrides.
2. **Step 2: Generate `Quarto/01_exposicao_ia_brasil.qmd`**
   - Write cleanly structured Markdown + RevealJS syntax.
   - Reference high-res figures in `../paper/figures/` (or `../Figures/`).
   - Use `[@eloundou2024gpts]` and `[@ulyssea2018firms]` citations.
3. **Step 3: Quarto Build & Verification**
   - Run `quarto render Quarto/01_exposicao_ia_brasil.qmd`.
   - Validate HTML output and check for rendering defects.
4. **Step 4: Repository Sync & Quality Checks**
   - Run `pytest -q` to verify econometric test suite passes.
   - Update rule mapping table in `.agents/rules/beamer-quarto-sync.md`.
5. **Step 5: Session Logging & Checkpoint Update**
   - Write session log and update checkpoint for Action 2.
