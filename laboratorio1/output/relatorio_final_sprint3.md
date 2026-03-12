# Laboratorio 1 - Relatorio Final (Sprint 3)

**Disciplina:** Laboratorio de Experimentacao de Software
**Data de geracao:** 2026-03-12 20:38:16 UTC
**Amostra:** 905 repositorios mais estrelados do GitHub (com linguagem de programacao definida)

---

## 1. Introducao e Hipoteses Informais

Este relatorio apresenta a analise final dos **905 repositorios mais populares do GitHub** (por numero de estrelas), considerando apenas projetos de software que possuem linguagem de programacao primaria definida. O objetivo e investigar caracteristicas comuns desses sistemas populares, respondendo as seguintes questoes de pesquisa:

**Hipoteses informais (formuladas antes da analise):**

| # | Questao | Hipotese |
|---|---|---|
| H1 | RQ01 - Sistemas populares sao maduros/antigos? | Repositorios populares tendem a ter mais tempo de existencia, pois a popularidade e construida ao longo dos anos. Espera-se mediana acima de 5 anos. |
| H2 | RQ02 - Recebem muita contribuicao externa? | Repositorios populares, por atrairem comunidades grandes, devem ter um volume expressivo de PRs aceitas. Espera-se mediana elevada (centenas a milhares). |
| H3 | RQ03 - Lancam releases com frequencia? | Repositorios populares tendem a manter um ciclo de releases, mas muitos projetos modernos usam CD contínuo sem releases formais. Espera-se uma distribuicao bastante variada. |
| H4 | RQ04 - Sao atualizados com frequencia? | Repositorios populares devem estar ativos. Espera-se que a maioria tenha sido atualizada nos ultimos dias ou semanas. |
| H5 | RQ05 - Sao escritos nas linguagens mais populares? | Linguagens como Python, JavaScript, TypeScript, Go, Java e C++ devem dominar o top 1000. |
| H6 | RQ06 - Possuem alto percentual de issues fechadas? | Repositorios populares contam com equipes ativas que mantem issues sob controle. Espera-se mediana acima de 70%. |
| H7 | RQ07 - Linguagens mais populares recebem mais contribuicao, mais releases e sao mais ativas? | Linguagens com ecossistemas maduros (ex.: TypeScript, Go, Rust) devem mostrar metricas superiores de contribuicao e atividade. |

---

## 2. Metodologia

### 2.1 Coleta de dados
- **Fonte:** API GraphQL do GitHub.
- **Criterio de selecao:** `search(query: "stars:>0 sort:stars-desc", type: REPOSITORY)` com paginacao de 100 repositorios por requisicao.
- **Filtro de linguagem:** apenas repositorios com `primaryLanguage` definida (projetos de software).
- **Metricas coletadas por repositorio:**
  - **Idade:** calculada a partir de `createdAt` (em dias e anos).
  - **PRs aceitas:** `pullRequests(states: MERGED).totalCount`.
  - **Total de releases:** `releases.totalCount`.
  - **Tempo sem push:** diferenca entre data de coleta e `pushedAt` (em dias).
  - **Linguagem primaria:** `primaryLanguage.name`.
  - **Razao de issues fechadas:** `issues(states: CLOSED).totalCount / issues.totalCount`.

### 2.2 Analise estatistica
- **Medida de tendencia central:** mediana (robusta a outliers, adequada para distribuicoes assimetricas).
- **Estatisticas descritivas:** media, desvio padrao, quartis (Q1, Q3), IQR, min e max.
- **Correlacao:** coeficiente de Spearman (nao-parametrico, adequado para relacoes monotonicas).
- **Visualizacoes:** histogramas com KDE, boxplots, graficos de barras, heatmaps e scatter plots.

---

## 3. Resultados

### RQ01 - Sistemas populares sao maduros/antigos?

**Metrica:** idade do repositorio em anos.

| Estatistica | Valor |
|---|---:|
| Mediana | 8.16 anos |
| Media | 8.1 anos |
| Desvio Padrao | 4.18 anos |
| Minimo | 0.11 anos |
| Q1 (25%) | 4.78 anos |
| Q3 (75%) | 11.43 anos |
| Maximo | 17.92 anos |
| IQR | 6.65 anos |

![Distribuicao da Idade](charts/rq01_idade.png)

![Idade por Linguagem](charts/rq01_idade_por_linguagem.png)

**Analise:** A mediana de **8.16 anos** confirma que repositorios populares sao, em geral, sistemas maduros. O intervalo interquartil [4.78, 11.43] mostra que 50% dos repositorios tem entre 4.78 e 11.43 anos. Isso suporta a hipotese H1: popularidade no GitHub esta fortemente associada a maturidade e tempo de existencia, refletindo o efeito cumulativo de exposicao, adocao e contribuicoes ao longo dos anos.

---

### RQ02 - Sistemas populares recebem muita contribuicao externa?

**Metrica:** total de pull requests aceitas (merged).

| Estatistica | Valor |
|---|---:|
| Mediana | 889 PRs |
| Media | 4,244 PRs |
| Desvio Padrao | 9,885 |
| Minimo | 0 |
| Q1 (25%) | 220 |
| Q3 (75%) | 3,598 |
| Maximo | 87,666 |
| IQR | 3,378 |

![Distribuicao de PRs Aceitas](charts/rq02_prs_aceitas.png)

**Analise:** A mediana de **889 PRs aceitas** demonstra que repositorios populares recebem um volume significativo de contribuicoes externas. A grande diferenca entre mediana e media (4,244) indica uma distribuicao com cauda longa a direita: alguns repositorios sao verdadeiros "imãs" de contribuicoes, enquanto a maioria tem volume moderado. H2 e parcialmente confirmada — ha contribuicao expressiva, mas com grande variabilidade.

---

### RQ03 - Sistemas populares lancam releases com frequencia?

**Metrica:** total de releases.

| Estatistica | Valor |
|---|---:|
| Mediana | 53 releases |
| Media | 133 releases |
| Desvio Padrao | 206 |
| Minimo | 0 |
| Q1 (25%) | 2 |
| Q3 (75%) | 156 |
| Maximo | 1,000 |
| IQR | 154 |
| Repos sem nenhuma release | 210 (23.2%) |

![Distribuicao de Releases](charts/rq03_releases.png)

**Analise:** A mediana de **53 releases** mostra que muitos repositorios populares utilizam o mecanismo de releases do GitHub, mas **23.2%** dos repositorios nao possuem nenhuma release formal. Isso reflete uma tendencia moderna de deploy continuo (CD), onde releases formais sao substituidas por commits diretamente na branch principal. H3 e parcialmente confirmada — existe atividade de releases, mas o padrao varia enormemente entre projetos.

---

### RQ04 - Sistemas populares sao atualizados com frequencia?

**Metrica:** dias desde o ultimo push.

| Estatistica | Valor |
|---|---:|
| Mediana | 1 dias |
| Media | 96 dias |
| Desvio Padrao | 238 |
| Minimo | -1 |
| Q1 (25%) | 0 |
| Q3 (75%) | 24 |
| Maximo | 2,291 |
| IQR | 24 |
| Push nos ultimos 7 dias | 610 |
| Push nos ultimos 30 dias | 696 |
| Push no ultimo ano | 801 |

![Tempo sem Push](charts/rq04_atualizacao.png)

**Analise:** A mediana de **1 dias** desde o ultimo push confirma fortemente H4: repositorios populares sao extremamente ativos. 610 repositorios receberam push na ultima semana e 696 no ultimo mes. Isso demonstra que a popularidade esta diretamente associada a manutencao ativa e constante. A metrica `pushedAt` e mais precisa que `updatedAt`, pois reflete apenas pushes de codigo reais, excluindo atividades como comentarios em issues ou bots.

---

### RQ05 - Sistemas populares sao escritos nas linguagens mais populares?

**Metrica:** linguagem primaria.

| Estatistica | Valor |
|---|---|
| Total de linguagens distintas | 20 |
| Concentracao top 5 | 67.18% |
| Concentracao top 10 | 84.86% |

**Top 5 linguagens:**

| Linguagem | Repositorios | % |
|---|---:|---:|
| Python | 203 | 22.4% |
| TypeScript | 162 | 17.9% |
| JavaScript | 112 | 12.4% |
| Go | 76 | 8.4% |
| Rust | 55 | 6.1% |

![Linguagens - Barras](charts/rq05_linguagens_barras.png)

![Linguagens - Pizza](charts/rq05_linguagens_pizza.png)

**Analise:** O top 5 concentra **67.18%** e o top 10 concentra **84.86%** dos repositorios. H5 e confirmada: linguagens amplamente utilizadas na industria (Python, JavaScript/TypeScript, Go, Java, C++) dominam os repositorios mais populares. Existe uma forte correlacao entre a popularidade geral de uma linguagem e sua representacao entre os projetos mais estrelados do GitHub.

---

### RQ06 - Sistemas populares possuem alto percentual de issues fechadas?

**Metrica:** razao issues fechadas / total de issues (%).

| Estatistica | Valor |
|---|---:|
| Mediana | 87.7% |
| Media | 79.1% |
| Desvio Padrao | 23.7% |
| Minimo | 0.0% |
| Q1 (25%) | 70.5% |
| Q3 (75%) | 96.1% |
| Maximo | 100.0% |
| Repos >= 90% issues fechadas | 405 |
| Repos >= 70% issues fechadas | 685 |
| Repos < 50% issues fechadas | 107 |

![Issues Fechadas](charts/rq06_issues_fechadas.png)

**Analise:** A mediana de **87.7%** de issues fechadas indica que repositorios populares, de fato, mantem um alto nivel de resolucao de demandas. 685 repositorios (75.7%) fecham pelo menos 70% de suas issues, confirmando H6. Isso reflete comunidades ativas e equipes de manutencao comprometidas com a saude do projeto.

---

## 4. Bonus - RQ07: Analise por Linguagem

**Questao:** Sistemas escritos em linguagens mais populares recebem mais contribuicao externa, lancam mais releases e sao atualizados com mais frequencia?

| Linguagem | Repos | Mediana PRs | Media PRs | Mediana Releases | Media Releases | Mediana Dias sem Push | Media Dias sem Push |
|---|---:|---:|---:|---:|---:|---:|---:|
| Python | 203 | 620 | 4,025 | 23 | 92 | 2 | 121 |
| TypeScript | 162 | 2,526 | 5,000 | 158 | 254 | 0 | 35 |
| JavaScript | 112 | 590 | 2,192 | 38 | 111 | 6 | 147 |
| Go | 76 | 1,509 | 6,092 | 131 | 181 | 0 | 49 |
| Rust | 55 | 2,348 | 5,395 | 74 | 144 | 0 | 12 |
| C++ | 46 | 983 | 7,953 | 64 | 164 | 0 | 43 |
| Java | 46 | 614 | 4,074 | 42 | 72 | 2 | 126 |
| C | 23 | 124 | 1,585 | 39 | 63 | 1 | 113 |
| Jupyter Notebook | 23 | 88 | 212 | 0 | 0 | 7 | 136 |
| Shell | 22 | 466 | 877 | 18 | 64 | 4 | 120 |
| Outras | 137 | 642 | 4,344 | 24 | 90 | 3 | 145 |

![Boxplots por Linguagem](charts/rq07_boxplots_por_linguagem.png)

![Medianas por Linguagem](charts/rq07_medianas_barras.png)

![Heatmap de Medianas](charts/rq07_heatmap.png)

**Analise:** A segmentacao por linguagem revela diferencas significativas entre ecossistemas:

- **Contribuicao externa (PRs):** Linguagens com ecossistemas de pacotes maduros e forte cultura de open-source tendem a receber mais PRs.
- **Releases:** A pratica de releases formais varia entre ecossistemas. Linguagens compiladas e com gestao de pacotes centralizada (ex.: Rust/crates, Go/modules) tendem a ter mais releases formais.
- **Atividade recente:** A maioria das linguagens populares mostra repositorios atualizados muito recentemente, confirmando que a popularidade no GitHub esta associada a atividade constante independente da linguagem.

H7 e parcialmente confirmada: linguagens populares de fato concentram mais atividade, mas as diferencas entre elas revelam que o ecossistema e a cultura da comunidade importam tanto quanto a popularidade da linguagem.

---

## 5. Analise de Correlacoes

![Correlacao de Spearman](charts/correlacao_spearman.png)

![Estrelas vs PRs](charts/scatter_stars_vs_prs.png)

A matriz de correlacao de Spearman permite identificar relacoes entre as metricas coletadas. Correlacoes positivas fortes indicam que as metricas crescem juntas, enquanto valores proximos de zero indicam independencia.

---

## 6. Discussao Final: Hipoteses x Resultados

| Hipotese | Resultado | Veredito |
|---|---|---|
| H1 - Repos populares sao maduros | Mediana de 8.16 anos de idade | **Confirmada** - maturidade e um fator chave |
| H2 - Recebem muita contribuicao | Mediana de 889 PRs aceitas | **Parcialmente confirmada** - volume alto, porem com grande variancia |
| H3 - Lancam releases com frequencia | Mediana de 53 releases; 23.2% sem releases | **Parcialmente confirmada** - muitos usam CD sem releases formais |
| H4 - Sao atualizados com frequencia | Mediana de 1 dias desde ultimo push; 696 com push no ultimo mes | **Fortemente confirmada** |
| H5 - Escritos em linguagens populares | Top 5 linguagens = 67.18% da amostra | **Confirmada** |
| H6 - Alto percentual de issues fechadas | Mediana de 87.7% | **Confirmada** |
| H7 - Linguagens populares = mais atividade | Diferencas observadas entre ecossistemas | **Parcialmente confirmada** |

---

## 7. Ameacas a Validade

- **Validade de construcao:** `pushedAt` do GitHub reflete o ultimo push de codigo ao repositorio, sendo mais precisa que `updatedAt` para medir atividade de desenvolvimento. Ainda assim, pushes automatizados por bots/CI podem influenciar o valor.
- **Validade externa:** a amostra se limita aos 1000 mais estrelados. Resultados nao sao generalizaveis para todo o ecossistema GitHub.
- **Viés de sobrevivencia:** repositorios abandonados que ja foram populares podem ter sido excluidos se perderam estrelas ao longo do tempo.
- **Linguagem primaria:** o GitHub classifica automaticamente a linguagem primaria com base no volume de codigo. Projetos poliglotas podem ser classificados de forma nao intuitiva.
- **Releases:** nem todos os projetos usam o mecanismo de releases do GitHub (alguns usam tags, changelogs ou deploy continuo).

---

## 8. Arquivos Gerados

- Dados brutos: `output/top_1000_repos.csv`
- Relatorio Sprint 2: `output/relatorio_sprint2.md`
- **Relatorio Final (este): `output/relatorio_final_sprint3.md`**
- Graficos: `output/charts/` (9 imagens PNG)
