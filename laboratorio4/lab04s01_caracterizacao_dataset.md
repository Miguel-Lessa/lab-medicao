# Lab04S01 - Caracterizacao do Dataset

## Contexto

Esta caracterizacao foi produzida para a Sprint 01 do Laboratorio 04, cujo objetivo e apresentar o dataset utilizado no trabalho de TIS 6 por meio de visualizacoes adequadas em uma ferramenta de BI. A base analisada esta no banco PostgreSQL `youtube_research`, executado em Docker no container `youtube-research-postgres-1`.

O dataset representa uma coleta de dados do YouTube voltada a conteudos relacionados a linguagens de programacao. Nesta etapa da coleta, os dados disponiveis caracterizam principalmente consultas realizadas, canais encontrados e playlists classificadas por linguagem.

## Conexao com a Base

- Servidor: `localhost:55432`
- Banco: `youtube_research`
- Usuario: `yt`
- Senha: `ytsecret`
- SGBD: PostgreSQL 16

## Tabelas Consideradas

As tabelas mais relevantes para a caracterizacao inicial sao:

- `language`: linguagens de programacao monitoradas.
- `search_query`: consultas utilizadas para descoberta de conteudos.
- `search_run`: execucoes das buscas na API do YouTube.
- `channel`: canais encontrados durante a coleta.
- `playlist`: playlists encontradas, classificadas e filtradas.

As tabelas `video`, `video_comment`, `video_stats_snapshot`, `playlist_stats_snapshot`, `video_comment_classification` e `video_engagement_classification` existem no banco, mas ainda nao possuem registros nesta etapa.

## Visao Geral do Dataset

| Metrica | Valor |
|---|---:|
| Linguagens cadastradas | 10 |
| Consultas de busca | 1.460 |
| Execucoes de busca | 2.880 |
| Canais coletados | 8.039 |
| Playlists coletadas | 9.328 |
| Videos coletados | 0 |
| Comentarios coletados | 0 |
| Snapshots de estatisticas de videos | 0 |
| Snapshots de estatisticas de playlists | 0 |

Esses valores indicam que a base esta concentrada na etapa de descoberta e classificacao de playlists/canais. As analises de engajamento, comentarios e metricas de videos dependem de uma etapa posterior de hidratacao/coleta.

## Distribuicao por Linguagem

| Linguagem | Playlists | Canais |
|---|---:|---:|
| TypeScript | 5.489 | 4.862 |
| Python | 3.839 | 3.262 |
| JavaScript | 0 | 0 |
| Java | 0 | 0 |
| C# | 0 | 0 |
| C++ | 0 | 0 |
| PHP | 0 | 0 |
| Shell | 0 | 0 |
| C | 0 | 0 |
| Go | 0 | 0 |

O dataset efetivamente coletado, ate o momento, esta concentrado em duas linguagens: TypeScript e Python. Portanto, a caracterizacao no dashboard deve deixar claro que as demais linguagens fazem parte do escopo planejado da coleta, mas ainda nao possuem playlists associadas.

## Status de Filtragem das Playlists

| Status do Filtro | Playlists | Percentual |
|---|---:|---:|
| passed | 6.766 | 72,53% |
| rejected_whitelist | 2.557 | 27,41% |
| rejected_blacklist | 5 | 0,05% |

A maior parte das playlists foi aprovada pelo filtro automatico. Uma parcela relevante foi rejeitada por nao atender aos criterios de whitelist, o que indica que o processo de filtragem tem impacto importante na composicao final do dataset.

## Status por Linguagem

| Linguagem | Status do Filtro | Playlists |
|---|---|---:|
| Python | passed | 3.189 |
| Python | rejected_whitelist | 645 |
| Python | rejected_blacklist | 5 |
| TypeScript | passed | 3.577 |
| TypeScript | rejected_whitelist | 1.912 |

Python possui maior proporcao de playlists aprovadas em relacao ao total coletado para a linguagem. TypeScript possui maior volume bruto de playlists, mas tambem apresenta maior quantidade de rejeicoes por whitelist.

## Periodo dos Dados

| Campo | Menor Data | Maior Data |
|---|---|---|
| Publicacao das playlists | 2019-12-20 | 2025-12-31 |
| Descoberta das playlists | 2026-05-18 | 2026-05-21 |
| Inicio das buscas | 2026-05-18 | 2026-05-21 |
| Fim das buscas | 2026-05-18 | 2026-05-21 |

As playlists encontradas foram publicadas entre 2019 e 2025. A coleta registrada no banco ocorreu em dois dias: 18/05/2026 e 21/05/2026.

## Playlists por Ano de Publicacao

| Ano | Playlists |
|---:|---:|
| 2019 | 109 |
| 2020 | 3.993 |
| 2021 | 1.433 |
| 2022 | 1.314 |
| 2023 | 1.408 |
| 2024 | 660 |
| 2025 | 411 |

O maior volume de playlists publicadas esta em 2020. A partir de 2021, o volume anual se mantem menor e relativamente mais distribuido, com reducao em 2024 e 2025.

## Processo de Coleta

| Status da Busca | Execucoes | Itens Retornados | Custo de Quota | Media de Itens por Execucao |
|---|---:|---:|---:|---:|
| ok | 1.800 | 79.309 | 180.000 | 44,06 |
| error | 1.080 | 0 | 0 | 0,00 |

O processo de coleta possui 1.800 execucoes bem-sucedidas e 1.080 execucoes com erro. Para a apresentacao, e importante mostrar esse dado porque ele explica por que algumas linguagens cadastradas ainda nao possuem playlists coletadas.

## Consultas e Execucoes por Linguagem

| Linguagem | Consultas | Execucoes | Itens Retornados | Custo de Quota |
|---|---:|---:|---:|---:|
| TypeScript | 296 | 1.367 | 60.129 | 136.700 |
| Python | 204 | 553 | 19.180 | 43.300 |
| PHP | 204 | 204 | 0 | 0 |
| JavaScript | 204 | 204 | 0 | 0 |
| Java | 204 | 204 | 0 | 0 |
| Go | 80 | 80 | 0 | 0 |
| C# | 72 | 72 | 0 | 0 |
| C++ | 68 | 68 | 0 | 0 |
| Shell | 68 | 68 | 0 | 0 |
| C | 60 | 60 | 0 | 0 |

TypeScript e Python concentram os itens retornados pela coleta. As outras linguagens possuem consultas e execucoes registradas, mas sem retorno de itens nesta etapa.

## Top 10 Canais por Quantidade de Playlists

| Canal | Playlists | Linguagens |
|---|---:|---:|
| Hans Schenker | 57 | 2 |
| Testers Talk | 31 | 2 |
| Net Ninja | 22 | 2 |
| WsCube Tech | 18 | 2 |
| Codevolution | 16 | 2 |
| Fernando Herrera | 13 | 1 |
| Neso Academy | 12 | 1 |
| Turtle Code | 11 | 1 |
| SDET- QA | 10 | 2 |
| Code-yug | 9 | 1 |

Esses canais aparecem como os maiores fornecedores de playlists dentro da amostra atual. Como alguns canais aparecem em mais de uma linguagem, eles podem representar conteudos transversais.

## Completude dos Dados

| Campo | Total | Preenchidos | Ausentes |
|---|---:|---:|---:|
| channel.subscriber_count | 8.039 | 0 | 8.039 |
| channel.country | 8.039 | 0 | 8.039 |
| channel.title | 8.039 | 8.039 | 0 |
| playlist.item_count | 9.328 | 0 | 9.328 |
| playlist.title | 9.328 | 9.328 | 0 |
| playlist.published_at | 9.328 | 9.328 | 0 |

Campos de identificacao textual, como titulos de canais e playlists, estao preenchidos. Campos de enriquecimento, como pais do canal, quantidade de inscritos e quantidade de itens da playlist, ainda estao ausentes. Essa limitacao deve ser explicitada no dashboard.

## Graficos Recomendados para o Power BI

### Pagina 1: Visao Geral

Use cartoes para:

- Total de playlists.
- Total de canais.
- Total de linguagens.
- Total de execucoes de busca.
- Total de playlists aprovadas.

Use graficos:

- Barras horizontais: playlists por linguagem.
- Barras empilhadas: playlists aprovadas/rejeitadas por linguagem.
- Rosca ou barra 100% empilhada: distribuicao dos status de filtro.

### Pagina 2: Coleta e Periodo

Use graficos:

- Colunas: playlists por ano de publicacao.
- Colunas por dia: playlists descobertas por dia de coleta.
- Barras: execucoes de busca por status.
- Tabela: consultas, execucoes e itens retornados por linguagem.

### Pagina 3: Qualidade e Cobertura

Use graficos:

- Tabela: completude dos campos principais.
- Barras: preenchidos versus ausentes por campo.
- Tabela: top 10 canais por quantidade de playlists.

## Tutorial Resumido para Montar no Power BI

1. Abra o Power BI Desktop.
2. Clique em `Obter dados`.
3. Escolha `Banco de dados PostgreSQL`.
4. Informe o servidor `localhost:55432`.
5. Informe o banco `youtube_research`.
6. Escolha o modo `Importar`.
7. Use as credenciais:
   - Usuario: `yt`
   - Senha: `ytsecret`
8. Carregue as tabelas `language`, `playlist`, `channel`, `search_query` e `search_run`.
9. Crie os relacionamentos:
   - `language.id` com `playlist.language_id`
   - `language.id` com `search_query.language_id`
   - `search_query.id` com `search_run.query_id`
   - `channel.channel_id` com `playlist.owner_channel_id`
10. Crie as medidas DAX basicas:

```DAX
Total Playlists = COUNTROWS(playlist)
Total Canais = COUNTROWS(channel)
Total Linguagens = COUNTROWS(language)
Total Execucoes = COUNTROWS(search_run)
Playlists Aprovadas = CALCULATE(COUNTROWS(playlist), playlist[filter_status] = "passed")
Percentual Aprovadas = DIVIDE([Playlists Aprovadas], [Total Playlists])
Itens Retornados = SUM(search_run[items_returned])
Custo de Quota = SUM(search_run[quota_cost])
```

11. Monte as paginas conforme os graficos recomendados.
12. Exporte o dashboard em PDF para entrega final da Sprint.

## Texto Curto para Apresentacao

O dataset analisado contem 9.328 playlists e 8.039 canais do YouTube, coletados a partir de 1.460 consultas relacionadas a linguagens de programacao. Ate o momento, os dados coletados estao concentrados em TypeScript e Python. TypeScript possui maior volume bruto de playlists, enquanto Python apresenta maior proporcao de playlists aprovadas pelo filtro automatico. A coleta possui registros entre 18/05/2026 e 21/05/2026, e as playlists encontradas foram publicadas entre 2019 e 2025. Como videos, comentarios e metricas de engajamento ainda nao estao preenchidos no banco, a Sprint 01 caracteriza principalmente a cobertura inicial da coleta, a distribuicao por linguagem, a qualidade dos dados e o status de filtragem.
