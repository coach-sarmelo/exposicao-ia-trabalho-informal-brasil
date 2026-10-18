# Exposição à Inteligência Artificial em um Mercado de Trabalho Informal: Teoria e Evidências para o Brasil

**Marcelo Moura Freire** · Economista · [LinkedIn](https://www.linkedin.com/in/marcelomfreire) · [Email](mailto:marcelo.moura.freire@gmail.com)

[![Dashboard Interativo](https://img.shields.io/badge/🚀%20Dashboard-Interativo-0072B2?style=for-the-badge)](https://coach-sarmelo.github.io/exposicao-ia-trabalho-informal-brasil/)
[![Artigo Completo](https://img.shields.io/badge/📄%20Artigo%20Completo-(PDF)-D55E00?style=for-the-badge)](https://coach-sarmelo.github.io/exposicao-ia-trabalho-informal-brasil/paper.pdf)
[![CI](https://github.com/coach-sarmelo/exposicao-ia-trabalho-informal-brasil/actions/workflows/ci.yml/badge.svg)](https://github.com/coach-sarmelo/exposicao-ia-trabalho-informal-brasil/actions/workflows/ci.yml)

> Acesso rápido: [🚀 Dashboard Interativo](https://coach-sarmelo.github.io/exposicao-ia-trabalho-informal-brasil/) · [📄 Artigo Completo (PDF)](./docs/paper.pdf)

---

## Sumário Executivo

Este estudo investiga a penetração e os efeitos distributivos da Inteligência Artificial generativa no mercado de trabalho brasileiro, conectando a teoria de exposição ocupacional a microdados representativos nacionais:

- **Amostra Ampla e Representativa:** Avaliação empírica com mais de 228 mil observações individuais da PNAD Contínua (IBGE, 2026Q1), ponderadas pelos pesos amostrais oficiais e com inferência robusta clusterizada por ocupação.
- **Índice de Exposição Ocupacional:** Mapeamento de escores de tarefas de IA (O*NET/Eloundou et al., 2024 via COD/CBO) em escala contínua (0–10) para 122 subgrupos ocupacionais, revelando forte assimetria entre setores de alta complexidade cognitiva e atividades manuais/operacionais.
- **Decomposição da Mediação da Informalidade:** O emprego informal reduz substancialmente a exposição líquida às tecnologias de IA. A decomposição econométrica demonstra que **37,2%** desse diferencial opera via canal educacional, enquanto **62,8%** decorre diretamente da estrutura e organização do posto informal.
- **Robustez Econométrica e Bounding:** Coeficiente de seleção em não-observáveis de Oster de $\delta = 1,93$ para anular o efeito estimado (superando com folga a referência canônica $\delta = 1$), comprovando resiliência frente a variáveis omitidas e estabilidade em especificações logit e de desenho amostral complexo.

---

## Instruções de Replicação

Execute a replicação completa dos dados, modelos, tabelas e figuras em apenas 3 comandos:

```bash
git clone https://github.com/coach-sarmelo/exposicao-ia-trabalho-informal-brasil.git
cd exposicao-ia-trabalho-informal-brasil
Rscript code/00_run_all.R
```

*Os microdados derivados e insumos encontram-se incluídos no repositório. O checklist completo de conformidade com os padrões de reprodução está disponível em [`DCAS_checklist.md`](DCAS_checklist.md).*

---

## Licença

Distribuído sob a licença [BSD 3-Clause](LICENSE.txt).
