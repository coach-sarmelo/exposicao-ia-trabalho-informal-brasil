# Plan: Implementing Methodological Enhancements from Methods Referee Review

**Project:** Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil  
**Author:** Marcelo Moura Freire (Universidade de Coimbra)  
**Standard:** Publication-Grade Academic Rigor (95+ Excellence Gate)  
**Date:** 2026-08-23  
**Status:** DRAFT -- In Planning Mode

---

## 1. Goal Description

Implement the 5 targeted methodological enhancements recommended by the `methods-referee` subagent to elevate the manuscript's econometric rigor and theoretical framing:
1. **Section 2 (`paper/sections/02_modelo.tex`):** Add competitive task price / hedonic wage schedule market-clearing context (Rosen 1986, Costinot & Vogel 2010) supporting interior sorting across all $j \in \{1, \dots, J\}$.
2. **Section 5.1 & 5.4 (`paper/sections/05_resultados.tex`):** Explicitly cite the Oster (2019) bound parameter ($\delta = 1.64 > 1, \beta^*(\delta=1) = 0.082$ for $R_{\max} = 1.3 R^2$).
3. **Section 5.2 (`paper/sections/05_resultados.tex`):** Provide balanced attribution for the $62.8\%$ mediation residual as the direct occupational task channel (organizational governance, scale, and complementary capital).
4. **Section 5.2 (`paper/sections/05_resultados.tex`):** Add footnote on WLS Logit average marginal effects (AME) confirming robustness of the Linear Probability Model.
5. **Section 5.4 (`paper/sections/05_resultados.tex`):** Document the 27-UF Wild Cluster Bootstrap ($p < 0.001, 1000$ draws) on specification S4.

---

## 2. Proposed Text Edits

### File 1: `paper/sections/02_modelo.tex`
- Add hedonic task compensation and market-clearing citation in Section 2.2 before equation \eqref{eq:salarios}.

### File 2: `paper/sections/05_resultados.tex`
- Update Section 5.1 with explicit Oster (2019) bounds.
- Update Section 5.2 with mediation attribution nuance and WLS Logit footnote.
- Update Section 5.4 with Wild Cluster Bootstrap precision and p-value.

---

## 3. Verification Plan
- Compile paper via `cd paper && latexmk -pdf -g main.tex` to ensure zero compilation errors.
- Run `python scripts/quality_score.py paper/main.tex` to verify quality score $\ge 95$.
- Run `bash scripts/check-surface-sync.sh` to confirm surface integrity.
