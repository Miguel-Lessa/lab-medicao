# Laboratório 03 — Sprint 02 — Relatório Inicial com Hipóteses

> Versão preliminar, redigida ao final da Sprint 02 e contendo as
> hipóteses informais que guiarão a análise da Sprint 03.

---

## 1. Introdução

### 1.1 Contextualização

A prática de *code review* constitui um dos pilares dos processos
ágeis de desenvolvimento de software, em particular no ecossistema
*open source* hospedado no GitHub. Cada contribuição submetida sob a
forma de *Pull Request* (PR) passa pela inspeção de um ou mais
colaboradores antes de ser integrada à *branch* principal. Em muitos
projetos, ferramentas de análise estática e *pipelines* de CI realizam
ainda uma triagem automatizada antes da revisão humana.

### 1.2 Problema-foco

Caracterizar, sob a perspectiva de quem submete contribuições, **quais
variáveis dos PRs influenciam** (i) o *feedback* final da revisão
(`MERGED` ou `CLOSED`) e (ii) o número de revisões realizadas, tomando
como amostra os PRs submetidos aos **200 repositórios mais populares
do GitHub**.

### 1.3 Questões de pesquisa

**Dimensão A — *Feedback* final do PR**

- RQ01: relação entre o tamanho dos PRs e o *feedback* final;
- RQ02: relação entre o tempo de análise e o *feedback* final;
- RQ03: relação entre a descrição e o *feedback* final;
- RQ04: relação entre as interações e o *feedback* final.

**Dimensão B — Número de revisões**

- RQ05: relação entre o tamanho e o número de revisões;
- RQ06: relação entre o tempo de análise e o número de revisões;
- RQ07: relação entre a descrição e o número de revisões;
- RQ08: relação entre as interações e o número de revisões.

### 1.4 Hipóteses informais

| ID | Direção esperada |
|---|---|
| H1 (RQ01) | PRs maiores (mais arquivos ou mais linhas) tendem a ser **rejeitados** com maior frequência (`CLOSED`). |
| H2 (RQ02) | Tempo de análise muito alto associa-se a `CLOSED` (abandono); `MERGED` tende a ocorrer em prazos moderados. |
| H3 (RQ03) | Descrições mais longas e detalhadas favorecem `MERGED`. |
| H4 (RQ04) | Mais participantes ou comentários sinalizam **mais discussão** — efeito potencialmente misto, com tendência ao `CLOSED` em PRs grandes. |
| H5 (RQ05) | PRs maiores demandam **mais revisões** (correlação positiva). |
| H6 (RQ06) | Tempos maiores correlacionam-se positivamente com mais revisões. |
| H7 (RQ07) | Descrições mais longas reduzem o esforço de revisão e, portanto, levam a **menos** revisões. |
| H8 (RQ08) | Mais interações implicam **mais** revisões (correlação positiva forte). |

### 1.5 Objetivos

- **Objetivo principal**: caracterizar empiricamente a atividade de
  *code review* nos 200 repositórios mais populares do GitHub.
- **Objetivos específicos**:
  1. construir um *dataset* aderente aos filtros do enunciado;
  2. calcular as estatísticas descritivas das métricas;
  3. aplicar testes estatísticos adequados a cada questão de pesquisa;
  4. confrontar as hipóteses H1–H8 com os resultados;
  5. discutir as ameaças à validade.

---

## 2. Metodologia (versão da Sprint 02)

### 2.1 Coleta

A coleta foi estruturada em duas etapas, materializadas nos seguintes
*scripts*:

- **Coleta principal** via GraphQL:
  [`scripts/coleta_graphql_PRs.py`](../scripts/coleta_graphql_PRs.py).
- **Enriquecimento** com `num_participantes`:
  [`scripts/enriquecer_participantes.py`](../scripts/enriquecer_participantes.py).
- A versão REST inicial,
  [`scripts/coleta_sprint1_PRs.py`](../scripts/coleta_sprint1_PRs.py),
  é mantida como referência (mostrou-se aproximadamente cinquenta vezes
  mais lenta em testes preliminares).

Etapas detalhadas:

1. Listagem dos 200 repositórios mais populares por meio do *endpoint*
   `GET /search/repositories?sort=stars&order=desc`.
2. Para cada repositório, recuperar `pullRequests.totalCount` em
   GraphQL com filtro `states: [MERGED, CLOSED]`. Repositórios com
   **menos de 100 PRs fechados** são descartados.
3. Coleta paginada via GraphQL (até 100 PRs por *query*, com no máximo
   seis páginas), recuperando em uma única requisição todos os campos
   relevantes: `additions`, `deletions`, `changedFiles`, `body`,
   `state`, `createdAt`, `closedAt`, `mergedAt`, `comments.totalCount`
   e `reviews.totalCount`.
4. Aplicação dos filtros em memória:
   - `state ∈ {MERGED, CLOSED}`;
   - `reviews.totalCount ≥ 1`;
   - `(mergedAt | closedAt) − createdAt > 1 hora`.
5. Em uma segunda passagem, *queries* GraphQL com *aliases* (até 30 PRs
   por requisição) acrescentam o campo `participants.totalCount`. Essa
   estratégia foi adotada porque a inclusão desse campo na coleta
   principal extrapolaria o orçamento de complexidade da API do
   GitHub.

### 2.2 Métricas e unidades

- **Tamanho**: `changed_files` (arquivos), `additions` / `deletions` /
  `loc_total` (linhas).
- **Tempo de análise**: `tempo_analise_horas` (horas) e
  `tempo_analise_dias` (dias).
- **Descrição**: `descricao_tamanho_chars` (caracteres do *markdown*).
- **Interações**: `num_participantes` (via `participants.totalCount` —
  contagem única de autor, comentadores e revisores) e
  `total_comentarios` (via `comments.totalCount` — apenas comentários
  da *issue*, sem somar revisões, para evitar circularidade com
  `numero_reviews`).
- **Revisão**: `numero_reviews` (via `reviews.totalCount`).
- ***Status***: `MERGED` ou `CLOSED`.

### 2.3 Decisões e materiais

- API: GitHub REST v3 (busca de repositórios) + GraphQL v4 (PRs e
  participantes), autenticadas com *Personal Access Token* armazenado
  em `.env`.
- Bibliotecas Python: `requests`, `python-dotenv`, `pandas`, `numpy`,
  `scipy`, `matplotlib`, `seaborn`.
- Tratamento de *rate limit* (`X-RateLimit-Remaining=0` provoca espera
  até `X-RateLimit-Reset`) e *retry* exponencial em erros transientes
  da família 5xx.

### 2.4 Estrutura prevista para a Sprint 03

- **Estatística descritiva** por métrica (*n*, média, mediana, IQR,
  percentis 25/75/95, mínimo, máximo).
- **RQ01–RQ04 (*status* binário)**: Mann-Whitney *U* + delta de Cliff
  + correlação ponto-bisserial. Justificativa: distribuições
  assimétricas com cauda longa invalidam a aplicação de testes
  paramétricos.
- **RQ05–RQ08 (`numero_reviews` numérico)**: Spearman ρ + Pearson em
  log(*x* + 1) como verificação adicional.
- **Intervalos de confiança de 95%** via *bootstrap* com 1.000
  reamostragens.
- **Correção** Holm step-down e Bonferroni para os oito testes.

---

## 3. Estado do *dataset*

O *dataset* final encontra-se em
`output/lab3s2/pull_requests_com_reviews.csv`:

- **14.347 PRs** após todos os filtros.
- **182 repositórios** efetivamente analisados (dos 200 candidatos, 18
  foram descartados por não atingirem o mínimo de 100 PRs
  `MERGED + CLOSED` ou por inacessibilidade temporária da API).
- Distribuição: 9.728 PRs `MERGED` e 4.619 `CLOSED`.
- Todos os PRs satisfazem `numero_reviews ≥ 1`,
  `tempo_analise_horas > 1` e possuem `num_participantes` válido.

Versões anteriores foram conservadas para fins de auditoria:

- `pull_requests_com_reviews_v1_buggy.csv`: primeira coleta (REST), com
  defeito em `numero_reviews` (valor sempre igual a 1, decorrente de
  uso incorreto do *header* `X-Total-Count`).
- `pull_requests_com_reviews_sem_participantes.csv`: *dataset* GraphQL
  antes do enriquecimento de `num_participantes`.

---

## 4. Riscos e ameaças à validade (preliminares)

- ***Snapshot* temporal**: PRs em aberto recentes podem influenciar as
  estatísticas e tendências mudam ao longo do tempo.
- **Viés de popularidade**: o conjunto dos 200 repositórios mais
  estrelados não representa todo o ecossistema do GitHub.
- **Heurística de uma hora**: pode não excluir todos os *bots*; *bots*
  podem ainda aparecer como `autora` legítima de PRs (por exemplo,
  *dependabot*).
- **Limite de paginação** (seis páginas de cem PRs, totalizando até
  600 PRs por repositório): há subamostragem em projetos com altíssimo
  volume de PRs. Ainda assim, mantêm-se até 100 PRs validados por
  repositório após filtros — suficiente para a análise agregada
  exigida no enunciado.
