# Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil

**Autor:** Marcelo Moura Freire  
**Padrão de Reprodutibilidade:** [AEA Data and Code Availability Standard (DCAS)](https://www.aeaweb.org/journals/data)  
**Licença:** BSD 3-Clause (Código) / CC-BY 4.0 (Documentos e Dados Derivados)  
**Slides Interativos (GitHub Pages):** [Visualizar Apresentação RevealJS](https://coach-sarmelo.github.io/exposicao-ia-trabalho-informal-brasil/01_exposicao_ia_brasil.html)

---

## 📄 Resumo Executivo / Abstract

### Português
Este projeto investiga como a dualidade entre **informalidade** e **capital humano** molda a exposição à Inteligência Artificial (IA) em uma grande economia em desenvolvimento. Combinando um modelo de designação ocupacional (*assignment model*) com fricções regulatórias e microdados da **PNAD Contínua do IBGE (2026Q1, $N = 227.629$ indivíduos representativos de 102,1 milhões de trabalhadores)**, harmonizados ao escore de exposição à IA do O\*NET-SOC via COD-ISCO, estabelecemos três resultados empíricos centrais:

1. **Gradiente Educacional Positivo ($\hat{\beta}_1 = 0{,}23$, $p < 0{,}001$):** Cada ano adicional de escolaridade associa-se a um aumento de 0,23 ponto (0,10 desvio-padrão) na exposição ocupacional à IA, robusto a controles mincerianos completos e rendimento habitual.
2. **Mediação Parcial da Informalidade:** Ocupações expostas apresentam 6,23 pontos percentuais a menos de informalidade. Apenas 37,2% dessa relação decorre da composição educacional; os 62,8% remanescentes refletem o canal direto de governança e capital organizacional do setor formal.
3. **Polarização Regional Interativa ($\hat{\beta}_2 = 0{,}28$, $p < 0{,}001$):** Em mercados de trabalho com maior maturidade formal (27 UFs leave-one-out), o prêmio de sorting educacional é estritamente mais acentuado, com limiar crítico de polarização estimado em $e^* = 11{,}14$ anos de estudo (conclusão do Ensino Médio).

---

## 📁 Estrutura do Repositório

```
exposicao-ia-trabalho-informal-brasil/
├── paper/                          # Artigo acadêmico completo em LaTeX
│   ├── main.tex                    # Fonte principal (17 páginas, padrão AEA)
│   ├── main.pdf                    # Manuscrito compilado pronto para submissão
│   ├── sections/                   # Seções modulares (00_resumo .. 06_conclusao, apendice)
│   ├── tables/                     # Tabelas em LaTeX geradas pela pipeline
│   ├── figures/                    # Gráficos vetoriais de alta resolução (PDF, SVG, PNG)
│   └── references.bib              # Bibliografia verificada
│
├── Slides/                         # Apresentação de seminário acadêmico
│   ├── 01_exposicao_ia_brasil.tex  # Fonte Beamer (16:9 widescreen)
│   └── 01_exposicao_ia_brasil.pdf  # Slide deck compilado (16 frames)
│
├── Quarto/                         # Apresentação interativa para a Web
│   ├── 01_exposicao_ia_brasil.qmd  # Código-fonte Quarto RevealJS
│   ├── 01_exposicao_ia_brasil.html # Deck HTML autocontido (recursos e SVGs embutidos)
│   └── theme-template.scss         # Tema institucional alinhado à paleta da pesquisa
│
├── Figures/                        # Figuras de publicação prontas para visualização
│   ├── fig1_gradiente.{pdf,svg,png}
│   ├── fig2_mediacao.{pdf,svg,png}
│   ├── fig3_regional_slopes.{pdf,svg,png}
│   └── fig5_robustez_forest.{pdf,svg,png}
│
├── replication_package/            # Pacote de replicação autônomo (AEA DCAS)
│   ├── README.md                   # Manifesto de replicação e mapeamento Tabela/Figura -> código
│   ├── DCAS_checklist.md           # Checklist de conformidade DCAS (100% PASS)
│   ├── LICENSE.txt                 # Licenças BSD 3-Clause e CC-BY 4.0
│   ├── code/                       # Scripts canônicos R (00_run_all.R .. 05_figures.R)
│   ├── data/                       # Microdados individuais, matrizes de crosswalk e painel UF
│   └── output/                     # Resultados serializados (results.rds) e tabelas/figuras
│
└── docs/                           # Mirror para publicação no GitHub Pages
```

---

## ⚡ Guia Rápido de Reprodução (Quickstart)

Toda a análise empírica, tabelas em LaTeX e figuras em formatos vetoriais são reproduzidas em **menos de 20 segundos** a partir dos microdados brutos:

### Pré-requisitos
- **R (versão $\ge 4.2.0$)** com os pacotes: `data.table`, `fixest`, `ggplot2`, `jsonlite`, `testthat`.

```r
install.packages(c("data.table", "fixest", "ggplot2", "jsonlite", "testthat"))
```

### Executar a Pipeline Canônica Completa
```bash
# Executa a pipeline de 5 etapas (Carga -> Limpeza -> Econometria -> Tabelas -> Figuras)
cd replication_package/code
Rscript 00_run_all.R
```

### Executar a Suíte de Verificação Econométrica
```bash
# Executa os 83 testes automatizados de exatidão numérica e identificação causal
Rscript test_econometrics.R
```

---

## 📊 Mapeamento de Tabelas e Figuras

| Item no Artigo | Descrição | Script Gerador | Arquivo de Saída |
|---|---|---|---|
| **Tabela 1** | Estatísticas Descritivas PNAD Contínua 2026Q1 | `code/04_tables.R:85` | `output/tables/tab_descritivas.tex` |
| **Tabela 2** | Top 10 e Bottom 10 Ocupações por Exposição | `code/04_tables.R:103` | `output/tables/tab_maiores.tex` |
| **Tabela 3** | Gradiente Educacional de IA (Modelos S1 e S2) | `code/04_tables.R:125` | `output/tables/tab_gradiente.tex` |
| **Tabela 4** | Mediação pela Informalidade (Modelos S3a e S3) | `code/04_tables.R:175` | `output/tables/tab_s3.tex` |
| **Tabela 5** | Heterogeneidade Regional LOO 27 UFs (Modelo S4) | `code/04_tables.R:206` | `output/tables/tab_s4.tex` |
| **Tabela 6** | Bateria de Robustez (R1–R6 e Limite de Oster) | `code/04_tables.R:230` | `output/tables/tab_robustez.tex` |
| **Tabela A.1** | Sensibilidade por Exclusão de Grandes Grupos COD | `code/04_tables.R:250` | `output/tables/tab_robustez_grupos.tex` |
| **Figura 1** | Gradiente Escolaridade vs. Exposição à IA | `code/05_figures.R:40` | `output/figures/fig1_gradiente.*` |
| **Figura 2** | Decomposição da Mediação da Informalidade | `code/05_figures.R:110` | `output/figures/fig2_mediacao.*` |
| **Figura 3** | Slopes Educacionais nas 5 Macro-Regiões | `code/05_figures.R:168` | `output/figures/fig3_regional_slopes.*` |
| **Figura 5** | Forest Plot de Estabilidade de Coeficientes | `code/05_figures.R:216` | `output/figures/fig5_robustez_forest.*` |

---

## 📖 Como Citar / Citation

```bibtex
@article{freire2026exposicao,
  author    = {Marcelo Moura Freire},
  title     = {Exposi{\c{c}}{\~a}o {\`a} Intelig{\^e}ncia Artificial em um Mercado de Trabalho Informal: Teoria e Evid{\^e}ncias para o Brasil},
  year      = {2026},
  publisher = {GitHub Repository},
  url       = {https://github.com/coach-sarmelo/exposicao-ia-trabalho-informal-brasil}
}
```

---

## ⚖️ Licença

- **Código-fonte:** [BSD 3-Clause License](LICENSE.txt)
- **Texto, Artigo e Figuras:** [Creative Commons Attribution 4.0 International (CC-BY 4.0)](LICENSE.txt)
