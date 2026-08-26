# Plan: Comprehensive Econometric & Empirical Specification Audit

**Project:** Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil  
**Author:** Marcelo Moura Freire (Universidade de Coimbra)  
**Standard:** AEA Data Editor Standard for Reproducibility / Econometric Best Practices  
**Date:** 2026-08-23  
**Status:** DRAFT -- In Planning Mode

---

## 1. Goal Description

Conduct a systematic, publication-grade econometric audit of the empirical specifications and findings in the research manuscript (*Exposição à IA no Mercado de Trabalho Brasileiro*). The audit will verify:
1. **Identification & Econometric Rigor:** Formal alignment between theoretical propositions (Propositions 1--3, Corollary 1) and empirical specifications (S1--S4).
2. **Standard Error Clustering & Weights:** Evaluation of Moulton (1986) clustering at the 122 occupation level and WLS PNAD sampling weights.
3. **Mediation Analysis (S3 & S3a):** Decomposition of educational mediation vs direct organizational capital effects, comparing LPM against WLS Logit.
4. **Regional Heterogeneity & Interaction (S4):** Leave-one-out formality index, cross-derivative dynamics ($\partial \theta / \partial \text{formal}_u$), and polarization threshold at $e^* \approx 11$ years.
5. **Full Numerical Chain-of-Verification (CoVe):** Automated cross-check of all point estimates, standard errors, sample sizes ($N = 227,629$), and percentages across text (`paper/sections/`), tables (`paper/tables/`), and raw data artifacts (`data/output/`).
6. **Robustness & Sensitivity Suite (R1--R7):** OLS vs WLS, Winsorization, Trimming, $\log(1+\theta)$, Oster (2019) bounding, and Wild Cluster Bootstrap.

---

## 2. Proposed Audit Modules & Methodology

### Module 1: Theoretical Derivation & Specification Mapping
- **Theoretical Model (`02_modelo.tex`):**
  - Verify sorting condition: $\text{argmax}_j [g(e)(1+\kappa_s\theta_j) - c\cdot\mathbb{1}[s=F]]$.
  - Verify proof of Proposition 1 ($d\theta^*(e)/de > 0$) in `apendice.tex`.
  - Verify proof of Proposition 2 ($de^*_j/d\theta_j < 0$) and Corollary 1 (Partial Mediation).
  - Verify proof of Proposition 3 ($d^2\theta/de\,dF > 0$) for regional depth.
- **Empirical Mapping (`04_estrategia_empirica.tex`):**
  - S1: $\theta_{j(i)} = \alpha + \beta_1 e_i + \mathbf{X}_i'\boldsymbol{\gamma} + \varepsilon_i$.
  - S2: $\theta_{j(i)} = \alpha + \beta_1 e_i + \beta_2 w_i + \mathbf{X}_i'\boldsymbol{\gamma} + \varepsilon_i$.
  - S3/S3a: $\text{informal}_i = \alpha + \delta_1 \theta_{j(i)} + \delta_2 e_i + \mathbf{X}_i'\boldsymbol{\gamma} + \varepsilon_i$.
  - S4: $\theta_{j(i)} = \alpha + \beta_1 e_i + \beta_2 (e_i \times \text{formal}_{u(i)}^{\text{LOO}}) + \beta_3 \text{formal}_{u(i)}^{\text{LOO}} + \mathbf{X}_i'\boldsymbol{\gamma} + \varepsilon_i$.

### Module 2: Numerical Parity Audit (Chain of Verification)
Check that every value stated in the paper text matches the generated JSON outputs and LaTeX tables:

| Claim in Text | Text Location | Paper Table | JSON Source | Ground Truth Value | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Sample size $N$ | Sec 4, 5, Resumo | All tables | `econometrics.json` | 227,629 | Pending |
| Occupation clusters | Sec 4, 5 | All tables | `econometrics.json` | 122 clusters | Pending |
| S1 Schooling ($\hat{\beta}_1$) | Sec 5.1 | `tab_gradiente.tex` | `econometrics.json:S1` | $0.2288 \approx 0.23$ (SE $0.0278 \approx 0.03$) | Pending |
| S1 $R^2$ | Sec 5.1 | `tab_gradiente.tex` | `econometrics.json:S1` | $0.2457 \approx 0.246$ | Pending |
| S2 Schooling ($\hat{\beta}_1$) | Sec 5.1 | `tab_gradiente.tex` | `econometrics.json:S2` | $0.2097 \approx 0.21$ (SE $0.0260 \approx 0.03$) | Pending |
| S2 Income ($\hat{\beta}_2$) | Sec 5.1 | `tab_gradiente.tex` | `econometrics.json:S2` | $4.27 \times 10^{-5} \rightarrow 0.043$ / R\$ 1k (SE $0.010$) | Pending |
| S3a Exposure ($\hat{\delta}_1$) | Sec 5.2 | `tab_s3.tex` | `econometrics.json:S3a` | $-6.2285 \approx -6.23$ (SE $0.9871 \approx 0.99$) | Pending |
| S3 Exposure ($\hat{\delta}_1$) | Sec 5.2 | `tab_s3.tex` | `econometrics.json:S3` | $-3.9068 \approx -3.91$ (SE $0.9565 \approx 0.96$) | Pending |
| S3 Schooling ($\hat{\delta}_2$) | Sec 5.2 | `tab_s3.tex` | `econometrics.json:S3` | $-2.6089 \approx -2.61$ (SE $0.2697 \approx 0.27$) | Pending |
| Mediation attenuation | Sec 5.2 | N/A | Calculated | $37.28\% \approx 37.2\%$ | Pending |
| S4 Interaction ($\hat{\beta}_2$) | Sec 5.3 | `tab_s4.tex` | `econometrics.json:S4` | $0.2786 \approx 0.28$ (SE $0.0649 \approx 0.06$) | Pending |
| S4 Formality ($\hat{\beta}_3$) | Sec 5.3 | `tab_s4.tex` | `econometrics.json:S4` | $-3.1042 \approx -3.10$ (SE $0.7671 \approx 0.77$) | Pending |
| Robustness OLS ($\hat{\beta}_1$) | Sec 5.4 | `tab_robustez.tex` | `robustness.json:R1` | $0.2111 \approx 0.21$ (SE $0.0266 \approx 0.03$) | Pending |
| Robustness Winsor 1% | Sec 5.4 | `tab_robustez.tex` | `robustness.json:R3` | $0.2288 \approx 0.23$ (SE $0.0278 \approx 0.03$) | Pending |
| Robustness Excl. p99 | Sec 5.4 | `tab_robustez.tex` | `robustness.json:R4` | $0.2173 \approx 0.22$, $N=225,478$ | Pending |
| Robustness $\log(1+\theta)$ | Sec 5.4 | `tab_robustez.tex` | `robustness.json:R5` | $0.0664 \approx 0.07$ (SE $0.0079 \approx 0.01$) | Pending |

### Module 3: Econometric Soundness & Diagnostic Checks
1. **Clustering Level:** Review whether clustering at the 122 occupation level is sufficient or whether two-way clustering (Occupation $\times$ UF) should be reported.
2. **LPM vs. Logit:** Compare S3 linear probability estimates with logistic regression estimates (`data/scripts/stats/logit.py`) to verify boundary condition robustness ($P \in [0,1]$).
3. **Oster (2019) Bounds:** Audit the stability parameter $\delta$ for unobservable selection on S1 $\rightarrow$ S2.
4. **Leave-One-Out Integrity:** Check that `_uf_formality_loo` correctly subtracts individual observation weights and avoids mechanical endogeneity.

---

## 3. Verification Plan

### Automated Execution
- Run `python data/scripts/run_all.py test` to verify all 137 unit and econometrics tests.
- Run dedicated audit script to verify text-table-JSON numeric consistency within $\epsilon < 0.01$.
- Re-compile manuscript with `latexmk -pdf` and verify that all tables and figures compile cleanly.

### Deliverable
- Comprehensive Audit Report saved to `quality_reports/audits/2026-08-23_empirical_specifications_audit.md` containing full findings, precision checks, and potential econometric enhancements.
