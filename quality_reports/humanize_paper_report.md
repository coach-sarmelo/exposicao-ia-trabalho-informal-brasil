# Humanize Audit Report: Academic Manuscript

**Target Files:** `paper/main.tex` and modular section files in `paper/sections/` (00_resumo to 06_conclusao, apendice)  
**Total Word Count:** 4,640 words  
**Total Findings:** 27 (5 HIGH, 11 MED, 11 LOW)  
**HIGH Rate:** 1.08 per 1,000 words  
**Action Recommendation:** **Cosmetic cleanup & Strip targeted tells** (Prose is methodologically rigorous with 0 hedging stacking; strip triadic structuring, formulaic table lead-ins, and promotional clauses).

---

## 1. Per-Category Breakdown

| Category | HIGH | MED | LOW | Total |
|---|---:|---:|---:|---:|
| 1. Boilerplate transitions | 1 | 2 | 0 | 3 |
| 2. AI-cliché lexicon | 1 | 3 | 0 | 4 |
| 3. Em-dash & punctuation | 0 | 2 | 0 | 2 |
| 4. Symmetric paragraph shapes | 0 | 4 | 0 | 4 |
| 5. Tricolon abuse | 0 | 1 | 3 | 4 |
| 6. Hedging stacking | 0 | 0 | 0 | 0 |
| 7. "Not only X but also Y" frames | 0 | 1 | 1 | 2 |
| 8. Formulaic openers | 0 | 0 | 6 | 6 |
| 9. Hyphenation excess | 0 | 0 | 0 | 0 |
| 10. Sycophancy / Self-important framing | 3 | 0 | 1 | 4 |
| **Total** | **5** | **13** | **11** | **29*** |

*\*Note: Some compound findings bridge adjacent categories (e.g., symmetric structuring + tricolons).*

---

## 2. Itemized Findings Table

| File & Line | Category | Severity | Current Text | Suggested Human Revision |
|---:|---|---|---|---|
| `01_introducao.tex:4` | 5. Tricolon abuse | LOW | `"predominantemente manual, presencial e informal de suas atividades"` | `"predominantemente manual e informal de suas atividades"` (evitar trio de adjetivos mecânico) |
| `01_introducao.tex:10` | 4. Symmetric shapes | MED | `"Três resultados empíricos emergem. Primeiro, [...] Segundo, [...] Terceiro, [...]"` | Integrar os resultados em narrativa fluida contínua sem a fórmula `"Três X: 1, 2, 3"` |
| `01_introducao.tex:14` | 4. Symmetric shapes | MED | `"O artigo conecta três literaturas principais. A primeira [...] A segunda [...] A terceira [...]"` | Conectar diretamente ao debate substantivo (`"Dialogo com a literatura de exposição... incorporando a escolha contratual de Ulyssea (2018)..."`) |
| `01_introducao.tex:16` | 10. Sycophancy | HIGH | `"A contribuição do trabalho é tripla: (i) apresenta a primeira mensuração em nível de microdados [...]"` | `"O artigo contribui em três frentes:"` ou parágrafo corrido; substituir `"primeira mensuração"` por `"mensuração pioneira em microdados para o contexto brasileiro"` |
| `01_introducao.tex:18` | 3. Punctuation | MED | `"A Seção~\ref{sec:modelo} apresenta...; a Seção~\ref{sec:dados}...; a Seção~\ref{sec:estrategia}...; e a Seção~\ref{sec:conclusao} conclui."` | Dividir em duas frases independentes para eliminar a pilha de 4 pontos-e-vírgulas sequenciais |
| `02_modelo.tex:17` | 3. Punctuation | MED | `"--- integração a fluxos de trabalho estruturados, segurança da informação e governança de dados ---"` | Reduzir travessões e tricolon: `"(processos estruturados, segurança e governança de dados)"` |
| `02_modelo.tex:17` | 7. Not only/but also | LOW | `"não por erguer uma barreira física de acesso à ferramenta, mas por limitar a rentabilidade econômica"` | `"ao limitar o retorno econômico da integração corporativa, e não por barrar o acesso à ferramenta"` |
| `02_modelo.tex:40` | 2. AI-cliché lexicon | MED | `"O arcabouço assenta-se em três hipóteses estruturais:"` | `"O modelo baseia-se em três hipóteses estruturais:"` (substituir o clichê `"arcabouço"`) |
| `02_modelo.tex:82` | 1. Boilerplate | MED | `"Consequentemente, a composição educacional responde por parcela substantiva"` | `"Assim, a composição educacional explica parcela substantiva"` (remover conector formulaico) |
| `02_modelo.tex:93` | 10. Sycophancy | HIGH | `"A modelagem proposta resolve uma tensão analítica fundamental na literatura recente sobre inteligência artificial"` | `"O modelo formaliza por que a difusão de ferramentas generativas não anula o papel..."` (eliminar auto-elogio `"resolve tensão fundamental"`) |
| `02_modelo.tex:93` | 2. AI-cliché lexicon | HIGH | `"aplicativos generativos na era digital não anula o papel da informalidade"` | Substituir `"na era digital"` por `"de IA generativa"` e `"papel da informalidade"` por `"a função amortecedora da informalidade"` |
| `03_dados.tex:6` | 4. Symmetric shapes | MED | `"Uso três fontes de dados. Primeira: [...] Segunda: [...] Terceira: [...]"` | `"A análise combina três fontes de dados: microdados da PNAD Contínua (2026Q1), o índice de \citet{eloundou2024gpts} e os cruzamentos ISCO-08--SOC."` |
| `03_dados.tex:25` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:descritivas} resume as características descritivas da amostra"` | `"A amostra de indivíduos ocupados em 2026Q1 apresenta exposição média de 2{,}86 (Tabela~\ref{tab:descritivas})."` |
| `03_dados.tex:40` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:maiores} detalha as dez maiores ocupações do país, evidenciando o contraste estrutural:"` | `"O contraste estrutural é visível nas dez maiores ocupações do país (Tabela~\ref{tab:maiores}):"` |
| `03_dados.tex:60` | 2. AI-cliché lexicon | MED | `"Três limitações merecem explicitação transparente no corpo do texto. Primeira: [...] Segunda: [...] Terceira: [...]"` | `"Três limitações metodológicas devem ser consideradas: primeiro, [...] segundo, [...] terceiro, [...]"` (remover `"explicitação transparente no corpo do texto"`) |
| `05_resultados.tex:6` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:gradiente} reporta as estimativas das especificações S1 e S2 no nível do indivíduo"` | `"As estimativas baseline (Tabela~\ref{tab:gradiente}, coluna 1) indicam um gradiente educacional positivo e significante:"` |
| `05_resultados.tex:33` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:s3} avalia a Proposição~\ref{prop:formalidade} e o Corolário~\ref{cor:mediacao}."` | `"Em consonância com a Proposição~\ref{prop:formalidade}, a exposição à IA associa-se negativamente à probabilidade de informalidade (Tabela~\ref{tab:s3})."` |
| `05_resultados.tex:49` | 5. Tricolon abuse | LOW | `"--- englobando infraestrutura de governança corporativa, escala de dados e capital físico complementar que demandam contratos formais estruturados."` | `", decorrente de requisitos organizacionais e de capital complementar próprios de firmas formais."` |
| `05_resultados.tex:60` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:s4} testa a Proposição~\ref{prop:regiao} interagindo a escolaridade individual com a taxa de formalidade"` | `"A interação entre escolaridade individual e formalidade média da UF confirma a heterogeneidade espacial prevista (Tabela~\ref{tab:s4}):"` |
| `05_resultados.tex:76` | 10. Sycophancy | LOW | `"Esse resultado revela uma importante dinâmica de polarização ocupacional no espaço geográfico:"` | `"Esse resultado aponta para uma dinâmica de polarização ocupacional no espaço geográfico:"` (remover `"importante"`) |
| `05_resultados.tex:88` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:robustez} submete a especificação baseline (S1) a uma bateria de checagens de sensibilidade."` | `"O gradiente estimado permanece inalterado sob checagens adicionais de sensibilidade (Tabela~\ref{tab:robustez})."` |
| `06_conclusao.tex:4` | 2. AI-cliché lexicon | MED | `"Este artigo investigou quem está exposto à inteligência artificial [...] e desenvolveu um arcabouço teórico"` | `"Este trabalho avalia a exposição ocupacional à inteligência artificial no Brasil e propõe um modelo de tarefas..."` (substituir `"arcabouço"`) |
| `06_conclusao.tex:4` | 1. Boilerplate | MED | `"Por outro lado, as ocupações que concentram a maioria dos trabalhadores brasileiros"` | `"Em contrapartida, as ocupações com maior contingente de ocupados"` (eliminar `"Por outro lado"` isolado) |
| `06_conclusao.tex:6` | 7. Not only/but also | MED | `"não por vedar o acesso a ferramentas pontuais, mas por limitar a capacidade de extração de ganhos"` | `"ao restringir a apropriação dos ganhos corporativos de escala que justificam o custo de formalização."` (evitar repetição verbatim de `02_modelo.tex`) |
| `06_conclusao.tex:8` | 10. Sycophancy | HIGH | `"Para a formulação de políticas públicas, os resultados redefinem as prioridades de adaptação tecnológica."` | `"Em termos de políticas públicas, os achados qualificam as prioridades de capacitação e transição tecnológica."` (remover tom hiperbólico `"redefinem"`) |
| `06_conclusao.tex:8` | 1. Boilerplate | HIGH | `"Nesse sentido, iniciativas de formação técnica e continuada --- articuladas a instituições consolidadas"` | `"Iniciativas de formação técnica e continuada..."` (eliminar o conector clássico de LLM `"Nesse sentido,"`) |
| `apendice.tex:71` | 8. Formulaic openers | LOW | `"A Tabela~\ref{tab:robustezgrupos} apresenta os testes de sensibilidade excluindo cada um dos 9 grandes grupos"` | `"A exclusão sequencial de cada grande grupo ocupacional preserva a estabilidade do coeficiente (Tabela~\ref{tab:robustezgrupos})."` |

---

## 3. Top 3 Most Concentrated Paragraphs

1. **`paper/sections/06_conclusao.tex` ¶ linhas 4–8 (Conclusão & Políticas Públicas):** 5 achados (2 HIGH, 2 MED, 1 LOW). O parágrafo de políticas públicas concentra auto-afirmações hiperbólicas (`"redefinem as prioridades"`), conector de transição de IA (`"Nesse sentido,"`) e repetição da fórmula de contraste negativo (`"não por X, mas por Y"`).
2. **`paper/sections/01_introducao.tex` ¶ linhas 10–16 (Sequência triádica da Introdução):** 4 achados (1 HIGH, 2 MED, 1 LOW). Três parágrafos consecutivos com template simétrico idêntico (`"Três resultados..."`, `"Três literaturas..."`, `"Contribuição tripla..."`), finalizando com a alegação de `"primeira mensuração"`.
3. **`paper/sections/02_modelo.tex` ¶ linha 93 (Discussão Teórica):** 2 achados (2 HIGH). Presença de clichês marcantes de IA (`"na era digital"`, `"papel da informalidade"`) e auto-declaração promocional (`"resolve uma tensão analítica fundamental"`).
