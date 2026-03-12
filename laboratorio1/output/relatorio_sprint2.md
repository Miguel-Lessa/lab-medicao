# Laboratorio 1 - Sprint 2

## 1. Introducao e hipoteses informais

Este documento apresenta a primeira versao do relatorio para os 1.000 repositorios mais estrelados do GitHub.

Hipoteses informais (antes da analise):
- H1 (RQ01): repositorios populares tendem a ser mais antigos e maduros.
- H2 (RQ02): repositorios populares recebem volume alto de contribuicao externa (PRs aceitas).
- H3 (RQ03): repositorios populares fazem releases com frequencia moderada/alta.
- H4 (RQ04): repositorios populares costumam ter atualizacoes recentes.
- H5 (RQ05): linguagens populares (JavaScript, TypeScript, Python, Java, Go, C++) devem aparecer com mais frequencia.
- H6 (RQ06): repositorios populares devem ter percentual alto de issues fechadas.
- H7 (RQ07 - bonus): repositorios de linguagens mais populares devem concentrar mais contribuicoes, mais releases e menor tempo sem atualizacao.

Data/hora da coleta (UTC): 2026-03-12 19:43:02
Tamanho da amostra: 1000 repositorios.

## 2. Metodologia

- Fonte de dados: API GraphQL do GitHub.
- Criterio de selecao: `search(query: "stars:>0 sort:stars-desc", type: REPOSITORY)` com paginacao.
- Pagina: 100 repositorios por requisicao; 10 paginas para coletar 1000 itens.
- Metricas de RQ02, RQ03 e RQ06 coletadas em lotes de 20 repositorios por query GraphQL.
- Cada repositorio foi coletado com:
  - idade (dias/anos) via `createdAt`.
  - PRs aceitas via `pullRequests(states: MERGED).totalCount`.
  - releases via `releases.totalCount`.
  - tempo sem atualizacao via diferenca entre coleta e `pushedAt`.
  - linguagem primaria via `primaryLanguage.name`.
  - razao de issues fechadas via `issues(states: CLOSED).totalCount / issues.totalCount`.

## 3. Resultados por RQ (medianas)

- RQ01 (idade): mediana de **8.16 anos**.
- RQ02 (PRs aceitas): mediana de **889.0 PRs**.
- RQ03 (releases): mediana de **53.0 releases**.
- RQ04 (tempo ate ultimo push): mediana de **1.0 dias**.
- RQ05 (linguagem primaria): distribuicao das linguagens no top 1000:

| Linguagem | Quantidade |
|---|---:|
| Python | 203 |
| TypeScript | 162 |
| JavaScript | 112 |
| Go | 76 |
| Rust | 55 |
| C++ | 46 |
| Java | 46 |
| C | 23 |
| Jupyter Notebook | 23 |
| Shell | 22 |
| HTML | 18 |
| Ruby | 12 |
| C# | 11 |
| Kotlin | 10 |
| CSS | 8 |

- RQ06 (percentual de issues fechadas): mediana de **87.69%**.

## 4. Bonus - RQ07 (analise por linguagem)

| Linguagem | Repos | Mediana PRs aceitas | Mediana releases | Mediana dias sem push |
|---|---:|---:|---:|---:|
| Python | 203 | 620.0 | 23.0 | 2.0 |
| TypeScript | 162 | 2526.5 | 157.5 | 0.0 |
| JavaScript | 112 | 590.5 | 38.0 | 6.0 |
| Go | 76 | 1509.0 | 131.0 | 0.0 |
| Rust | 55 | 2348.0 | 74.0 | 0.0 |
| C++ | 46 | 983.0 | 63.5 | 0.0 |
| Java | 46 | 614.0 | 42.0 | 1.5 |
| C | 23 | 124.0 | 39.0 | 1.0 |
| Jupyter Notebook | 23 | 88.0 | 0.0 | 7.0 |
| Shell | 22 | 466.5 | 17.5 | 3.5 |
| HTML | 18 | 310.0 | 0.0 | 8.5 |
| Ruby | 12 | 4771.5 | 14.5 | 1.0 |
| C# | 11 | 5186.0 | 120.0 | 0.0 |
| Kotlin | 10 | 399.5 | 53.5 | 2.0 |
| CSS | 8 | 440.0 | 13.0 | 206.0 |

## 5. Discussao inicial (hipoteses x resultados)

- RQ01: a mediana de idade indica o nivel de maturidade dos sistemas populares.
- RQ02: a mediana de PRs aceitas mostra se a contribuicao externa tende a ser alta.
- RQ03: a mediana de releases mostra o ritmo de empacotamento/publicacao.
- RQ04: dias sem update refletem atividade recente de manutencao.
- RQ05: a distribuicao por linguagem permite verificar se o top 1000 acompanha linguagens populares.
- RQ06: a mediana de fechamento de issues indica eficiencia geral no tratamento de demandas.
- RQ07: a comparacao por linguagem ajuda a identificar diferencas de dinamica entre ecossistemas.

## 6. Arquivos gerados

- CSV com dados brutos: `output/top_1000_repos.csv`
- Este relatorio: `output/relatorio_sprint2.md`
