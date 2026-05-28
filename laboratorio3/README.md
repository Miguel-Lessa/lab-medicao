# Laboratório 03 — Caracterizando *code review* no GitHub

Coleta e análise estatística da atividade de *code review* (Pull
Requests) nos **200 repositórios mais populares do GitHub**, sob a
perspectiva de quem submete contribuições.

## Pré-requisitos

- Python 3.12+
- *Personal Access Token* (PAT) do GitHub com permissão básica de
  leitura

## Configuração

1. Copie o token para `.env` (existe um exemplo herdado do `laboratorio2`):

   ```powershell
   Copy-Item ..\laboratorio2\.env .\.env
   ```

   Ou crie manualmente:

   ```env
   GITHUB_TOKEN=ghp_seu_token_aqui
   ```

2. Instale as dependências:

   ```powershell
   pip install -r requirements.txt
   ```

## Filtros aplicados (definidos no enunciado)

- 200 repositórios mais populares (por número de estrelas);
- repositório precisa ter pelo menos **100 PRs fechados**
  (`MERGED + CLOSED`);
- PRs com *status* `MERGED` ou `CLOSED`;
- PRs com pelo menos uma revisão;
- PRs cujo intervalo entre criação e fechamento (*merge*/*close*)
  seja **maior que uma hora** (descarta revisões automáticas de
  *bots*/CI).

## Estrutura do projeto

```
laboratorio3/
  scripts/
    coleta_graphql_PRs.py        # Sprint 01/02: coleta principal via GraphQL
    enriquecer_participantes.py  # Sprint 02: adiciona num_participantes
    coleta_sprint1_PRs.py        # Versão REST inicial (referência)
    analise_sprint3.py           # Sprint 03: análise estatística + gráficos
  output/
    lab3s2/
      top_200_repos.csv
      pull_requests_com_reviews.csv
      pull_requests_com_reviews_sem_participantes.csv  # backup pré-enriquecimento
      pull_requests_com_reviews_v1_buggy.csv           # auditoria
      coleta.log
      enrich.log
    lab3s3/
      descritivas_globais.csv
      descritivas_por_status.csv
      comparacao_status_mannwhitney.csv  # RQ01–RQ04
      correlacoes_spearman.csv           # RQ05–RQ08
      resumo_rqs.md
      charts/*.png                       # 25 figuras
  relatorios/
    relatorio_inicial_lab3s2.md
    relatorio_final_lab3s3.md
  README.md
  requirements.txt
```

## Sprint 01 + 02 — Coleta

A coleta foi estruturada em duas etapas (GraphQL para velocidade, com
enriquecimento posterior para o campo mais custoso):

```powershell
# 1. Coleta principal: top-200 repositórios e PRs com filtros (~90 min)
python scripts/coleta_graphql_PRs.py

# 2. Enriquecimento com num_participantes (~25 min)
python scripts/enriquecer_participantes.py
```

Saídas:

- `output/lab3s2/top_200_repos.csv`
- `output/lab3s2/pull_requests_com_reviews.csv` (versão final, com
  `num_participantes`)

## Sprint 03 — Análise estatística

```powershell
python scripts/analise_sprint3.py
```

Saídas em `output/lab3s3/`:

- `descritivas_globais.csv` — estatísticas descritivas globais;
- `descritivas_por_status.csv` — estatísticas por *status*;
- `comparacao_status_mannwhitney.csv` — RQ01–RQ04 (Mann-Whitney *U*,
  delta de Cliff, ponto-bisserial);
- `correlacoes_spearman.csv` — RQ05–RQ08 (Spearman ρ, Pearson em log,
  IC 95% por *bootstrap*);
- `resumo_rqs.md` — resumo executivo;
- `charts/*.png` — 25 figuras (8 *boxplots*, 8 *scatter* log-log,
  8 violinos, 1 *heatmap*).

## Métricas coletadas por PR

| Categoria | Métrica | Unidade |
|---|---|---|
| Tamanho | `changed_files` | arquivos |
| Tamanho | `additions`, `deletions`, `loc_total` | linhas |
| Tempo de análise | `tempo_analise_horas`, `tempo_analise_dias` | horas / dias |
| Descrição | `descricao_tamanho_chars` | caracteres |
| Interações | `num_participantes` | pessoas distintas |
| Interações | `total_comentarios` | comentários |
| Revisão | `numero_reviews` | revisões |
| *Status* | `status` | `MERGED` / `CLOSED` |

## Questões de pesquisa

**Dimensão A — *Feedback* final (*status* do PR):**

- RQ01: tamanho × *status*
- RQ02: tempo de análise × *status*
- RQ03: descrição × *status*
- RQ04: interações × *status*

**Dimensão B — Número de revisões:**

- RQ05: tamanho × `numero_reviews`
- RQ06: tempo de análise × `numero_reviews`
- RQ07: descrição × `numero_reviews`
- RQ08: interações × `numero_reviews`

## Estatística empregada

- Mediana, IQR, percentis 25/75/95 (distribuições assimétricas).
- **Mann-Whitney *U*** + **delta de Cliff** + ponto-bisserial para
  RQ01–RQ04.
- **Spearman ρ** + Pearson em log(*x* + 1) para RQ05–RQ08.
- Intervalos de confiança de 95% via *bootstrap* (1.000 reamostragens).
- Correção **Holm step-down** e Bonferroni para múltiplas
  comparações (α = 0,05).

## *Dataset* final

- 14.347 PRs analisados;
- 182 repositórios efetivos (de 200 candidatos);
- 9.728 `MERGED` e 4.619 `CLOSED`;
- *Snapshot* coletado em 30 de abril de 2026.

Para resultados, hipóteses, vereditos e discussão, consulte o
[relatório final](relatorios/relatorio_final_lab3s3.md).
