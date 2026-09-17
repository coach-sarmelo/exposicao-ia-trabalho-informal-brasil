# Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil

**Artigo (PDF):** [Ler online (PDF)](replication_package/paper/main.pdf) · [Download v1.1](https://github.com/coach-sarmelo/exposicao-ia-trabalho-informal-brasil/releases/download/v1.1/Exposicao_IA_Trabalho_Informal_Brasil.pdf)  
**Autor:** Marcelo Moura Freire  
**Padrão de Reprodutibilidade:** [AEA Data and Code Availability Standard (DCAS)](https://www.aeaweb.org/journals/data)  
**Licença:** BSD 3-Clause (Código) / CC-BY 4.0 (Documentos e Dados Derivados)  
**Painel Interativo / Dashboard (GitHub Pages):** [Acessar Dashboard](https://coach-sarmelo.github.io/exposicao-ia-trabalho-informal-brasil/)  

---

## 📄 Resumo Executivo / Abstract

### Português
Este projeto investiga como a dualidade entre **informalidade** e **capital humano** molda a exposição à Inteligência Artificial (IA) em uma grande economia em desenvolvimento. Combinando um modelo de designação ocupacional (*assignment model*) com fricções regulatórias e microdados da **PNAD Contínua do IBGE (2026Q1, $N = 227.629$ indivíduos representativos de 102,1 milhões de trabalhadores)**, harmonizados ao escore de exposição à IA do O\*NET-SOC via COD-ISCO, estabelecemos três resultados empíricos centrais:

1. **Gradiente Educacional Positivo ($\hat{\beta}_1 = 0{,}23$, $p < 0{,}001$):** Cada ano adicional de escolaridade associa-se a um aumento de 0,23 ponto (0,10 desvio-padrão) na exposição ocupacional à IA, robusto a controles mincerianos completos e rendimento habitual.
2. **Mediação Parcial da Informalidade:** Ocupações expostas apresentam 6,23 pontos percentuais a menos de informalidade. Apenas 37,2% dessa relação decorre da composição educacional; os 62,8% remanescentes refletem o canal direto de governança e capital organizacional do setor formal.
3. **Polarização Regional Interativa ($\hat{\beta}_2 = 0{,}28$, $p < 0{,}001$):** Em mercados de trabalho com maior maturidade formal (27 UFs leave-one-out), o prêmio de sorting educacional é estritamente mais acentuado, com limiar crítico de polarização estimado em $e^* = 11{,}14$ anos de estudo (conclusão do Ensino Médio).

---

## 📁 Estrutura do Repositório

O repositório público é estruturado de forma minimalista e autocontida, abrigando exclusivamente o pacote de replicação certificado e o painel interativo:

```
exposicao-ia-trabalho-informal-brasil/
├── replication_package/            # Pacote de replicação autônomo (AEA DCAS)
│   ├── README.md                   # Manifesto detalhado de dados, código e mapeamento de tabelas/figuras
│   ├── DCAS_checklist.md           # Checklist de conformidade com os padrões da AEA (100% PASS)
│   ├── LICENSE.txt                 # Licenças BSD 3-Clause (código) e CC-BY 4.0 (dados e texto)
│   ├── CITATION.cff                # Metadados de citação acadêmica
│   ├── renv.lock                   # Snapshot do ambiente computacional R (versões exatas de pacotes)
│   ├── code/                       # Pipeline econométrico canônico em R (Rscript code/00_run_all.R)
│   ├── data/                       # Microdados derivados (PNAD Contínua), ratings O*NET e crosswalks
│   ├── output/                     # Tabelas em LaTeX, figuras vetoriais e estimativas (results.rds)
│   ├── paper/                      # Manuscrito completo em LaTeX, fontes, seções e PDF compilado
│   └── scripts/                    # Pipeline em Python para extração de microdados e cross-validação
│
└── docs/                           # Dashboard analítico e portal de disseminação (GitHub Pages)
    ├── index.html                  # Dashboard executivo autocontido (Quarto Dashboard interativo)
    ├── paper.pdf                   # Cópia do artigo para visualização direta via GitHub Pages
    └── .nojekyll                   # Instrução para publicação estática sem processamento Jekyll
```

---

## ⚡ Guia Rápido de Reprodução (Quickstart)

A pipeline reproduz integralmente todas as análises empíricas, tabelas em LaTeX e figuras vetoriais a partir dos dados do pacote em menos de 45 segundos:

### Pré-requisitos
- **R (versão $\ge 4.2.0$)** com os pacotes: `data.table`, `fixest`, `ggplot2`, `jsonlite`, `testthat`, `svglite`.

```r
install.packages(c("data.table", "fixest", "ggplot2", "jsonlite", "testthat", "svglite"))
```

### Executar a Pipeline Canônica Completa
```bash
# Navegar até o diretório do código no pacote de replicação
cd replication_package/code

# Executar a pipeline completa (Carga -> Limpeza -> Econometria -> Tabelas -> Figuras)
Rscript 00_run_all.R
```

### Executar a Suíte de Verificação Econométrica
```bash
# Executa a bateria de testes automatizados de exatidão numérica e identificação causal
Rscript test_econometrics.R
```

---

## 📊 Mapeamento de Tabelas e Figuras

| Item no Artigo | Descrição | Script Gerador | Arquivo de Saída |
|---|---|---|---|
| **Tabela 1** | Estatísticas Descritivas PNAD Contínua 2026Q1 | `code/04_tables.R:85` | `replication_package/output/tables/tab_descritivas.tex` |
| **Tabela 2** | Top 10 e Bottom 10 Ocupações por Exposição | `code/04_tables.R:103` | `replication_package/output/tables/tab_maiores.tex` |
| **Tabela 3** | Gradiente Educacional de IA (Modelos S1 e S2) | `code/04_tables.R:125` | `replication_package/output/tables/tab_gradiente.tex` |
| **Tabela 4** | Mediação pela Informalidade (Modelos S3a e S3) | `code/04_tables.R:175` | `replication_package/output/tables/tab_s3.tex` |
| **Tabela 5** | Heterogeneidade Regional LOO 27 UFs (Modelo S4) | `code/04_tables.R:206` | `replication_package/output/tables/tab_s4.tex` |
| **Tabela 6** | Bateria de Robustez (R1–R6 e Limite de Oster) | `code/04_tables.R:230` | `replication_package/output/tables/tab_robustez.tex` |
| **Tabela A.1** | Sensibilidade por Exclusão de Grandes Grupos COD | `code/04_tables.R:250` | `replication_package/output/tables/tab_robustez_grupos.tex` |
| **Figura 1** | Gradiente Escolaridade vs. Exposição à IA | `code/05_figures.R:40` | `replication_package/output/figures/fig1_gradiente.*` |
| **Figura 2** | Decomposição da Mediação da Informalidade | `code/05_figures.R:110` | `replication_package/output/figures/fig2_mediacao.*` |
| **Figura 3** | Diagrama Causal de Mediação (DAG) | `code/05_figures.R` | `replication_package/output/figures/fig_dag_mediacao.*` |
| **Figura 4** | Slopes Educacionais nas 5 Macro-Regiões | `code/05_figures.R:168` | `replication_package/output/figures/fig3_regional_slopes.*` |
| **Figura 5** | Forest Plot de Estabilidade de Coeficientes | `code/05_figures.R:216` | `replication_package/output/figures/fig5_robustez_forest.*` |

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
- **Texto, Artigo e Dados Derivados:** [Creative Commons Attribution 4.0 International (CC-BY 4.0)](LICENSE.txt)
