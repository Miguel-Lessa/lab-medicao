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

Data/hora da coleta (UTC): 2026-03-05 21:40:29
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
  - tempo sem atualizacao via diferenca entre coleta e `updatedAt`.
  - linguagem primaria via `primaryLanguage.name`.
  - razao de issues fechadas via `issues(states: CLOSED).totalCount / issues.totalCount`.

## 3. Resultados por RQ (medianas)

- RQ01 (idade): mediana de **8.38 anos**.
- RQ02 (PRs aceitas): mediana de **739.0 PRs**.
- RQ03 (releases): mediana de **40.5 releases**.
- RQ04 (tempo ate ultima atualizacao): mediana de **0.0 dias**.
- RQ05 (linguagem primaria): distribuicao das linguagens no top 1000:

| Linguagem | Quantidade |
|---|---:|
| Python | 200 |
| TypeScript | 160 |
| JavaScript | 115 |
| Unknown | 95 |
| Go | 77 |
| Rust | 54 |
| Java | 47 |
| C++ | 46 |
| C | 25 |
| Jupyter Notebook | 23 |
| Shell | 21 |
| HTML | 18 |
| Ruby | 12 |
| C# | 11 |
| Kotlin | 10 |

- RQ06 (percentual de issues fechadas): mediana de **86.75%**.

## 4. Bonus - RQ07 (analise por linguagem)

| Linguagem | Repos | Mediana PRs aceitas | Mediana releases | Mediana dias sem update |
|---|---:|---:|---:|---:|
| Python | 200 | 631.0 | 23.5 | 0.0 |
| TypeScript | 160 | 2583.5 | 158.0 | 0.0 |
| JavaScript | 115 | 576.0 | 40.0 | 0.0 |
| Unknown | 95 | 129.0 | 0.0 | 0.0 |
| Go | 77 | 1690.0 | 132.0 | 0.0 |
| Rust | 54 | 2370.5 | 76.0 | 0.0 |
| Java | 47 | 605.0 | 42.0 | 0.0 |
| C++ | 46 | 982.0 | 63.5 | 0.0 |
| C | 25 | 145.0 | 39.0 | 0.0 |
| Jupyter Notebook | 23 | 88.0 | 0.0 | 0.0 |
| Shell | 21 | 494.0 | 27.0 | 0.0 |
| HTML | 18 | 310.0 | 0.0 | 0.0 |
| Ruby | 12 | 4770.0 | 14.5 | 0.0 |
| C# | 11 | 5176.0 | 119.0 | 0.0 |
| Kotlin | 10 | 399.5 | 53.5 | 0.0 |

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
