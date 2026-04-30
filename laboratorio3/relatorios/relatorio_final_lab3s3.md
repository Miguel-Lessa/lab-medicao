# Laboratório 03 — Relatório Final (Sprint 03)

> Caracterizando a atividade de *code review* em repositórios populares do GitHub.

---

## 1. Introdução

### 1.1 Contextualização

A prática de *code review* tornou-se elemento central dos processos ágeis
de desenvolvimento de software, em particular no ecossistema *open source*
hospedado no GitHub. Nesse modelo, a integração de qualquer contribuição
à *branch* principal de um projeto exige a abertura de um *Pull Request*
(PR), o qual é submetido à inspeção de um ou mais revisores antes de ser
incorporado (status `MERGED`) ou descartado (status `CLOSED`). Em muitos
projetos, ferramentas de análise estática e pipelines de integração
contínua (CI) realizam ainda uma triagem automatizada antes da revisão
humana, o que torna a atividade de revisão um fenômeno híbrido entre o
técnico e o social.

### 1.2 Problema-foco

Este experimento investiga, sob a perspectiva de quem submete contribuições,
**quais variáveis dos PRs influenciam**:

1. o *feedback* final da revisão (`MERGED` versus `CLOSED`); e
2. o número de revisões realizadas até o fechamento do PR.

A análise utiliza uma amostra de PRs submetidos aos **200 repositórios mais
populares do GitHub** (ordenados pelo número de estrelas).

### 1.3 Questões de pesquisa

| Dimensão | RQ | Pergunta |
|---|---|---|
| A — *Feedback* final | RQ01 | Qual a relação entre o **tamanho** dos PRs e o *feedback* final? |
| A | RQ02 | Qual a relação entre o **tempo de análise** e o *feedback* final? |
| A | RQ03 | Qual a relação entre a **descrição** e o *feedback* final? |
| A | RQ04 | Qual a relação entre as **interações** e o *feedback* final? |
| B — Número de revisões | RQ05 | Tamanho versus número de revisões? |
| B | RQ06 | Tempo de análise versus número de revisões? |
| B | RQ07 | Descrição versus número de revisões? |
| B | RQ08 | Interações versus número de revisões? |

### 1.4 Hipóteses

| ID | Hipótese (direção esperada) | Justificativa informal |
|---|---|---|
| H1 (RQ01) | PRs maiores tendem a ser `CLOSED`. | Mais código implica maior risco de regressão e maior probabilidade de rejeição. |
| H2 (RQ02) | Tempo muito alto associa-se a `CLOSED`. | PRs longos sem progresso costumam ser abandonados. |
| H3 (RQ03) | Descrição mais extensa favorece `MERGED`. | Boa descrição reduz a incerteza do revisor. |
| H4 (RQ04) | Mais interações tendem a `CLOSED` em PRs grandes. | Discussão prolongada sinaliza controvérsia ou retrabalho. |
| H5 (RQ05) | PRs maiores demandam mais revisões. | Mais código implica mais ciclos de *review*. |
| H6 (RQ06) | Tempo maior implica mais revisões. | Mais tempo absorve mais ciclos de revisão. |
| H7 (RQ07) | Descrição maior implica menos revisões. | Clareza inicial reduz idas e vindas. |
| H8 (RQ08) | Mais interações implicam mais revisões. | Discussão evolui ao longo dos ciclos de *review*. |

### 1.5 Objetivos

- **Objetivo principal**: caracterizar empiricamente a atividade de
  *code review* nos 200 repositórios mais populares do GitHub.
- **Objetivos específicos**:
  1. construir um *dataset* aderente aos filtros definidos no enunciado;
  2. calcular estatísticas descritivas globais e por *status*;
  3. aplicar testes inferenciais adequados a cada questão de pesquisa;
  4. confrontar as hipóteses formuladas com a evidência empírica;
  5. discutir as ameaças à validade do estudo.

---

## 2. Metodologia

### 2.1 Passo a passo do experimento

1. **Listagem dos 200 repositórios** mais populares por meio do *endpoint*
   REST `GET /search/repositories?sort=stars&order=desc`.
2. **Validação de elegibilidade**: para cada repositório, verifica-se via
   *GraphQL* o campo `pullRequests.totalCount` com filtro
   `states: [MERGED, CLOSED]`. Repositórios com **menos de 100 PRs
   fechados** são descartados.
3. **Coleta principal** dos PRs fechados via *GitHub GraphQL API v4*
   (uma única requisição traz até 100 PRs com todos os campos
   necessários, drasticamente mais eficiente do que a alternativa REST).
4. **Aplicação dos filtros** definidos no enunciado:
   - `state ∈ {MERGED, CLOSED}`;
   - `reviews.totalCount ≥ 1`;
   - `(mergedAt | closedAt) − createdAt > 1 hora` (descarta PRs
     processados por *bots* ou pipelines de CI).
5. **Enriquecimento** com `participants.totalCount` em segunda passagem,
   utilizando *queries* GraphQL com *aliases* (até 30 PRs por requisição),
   estratégia adotada para contornar o orçamento de complexidade do
   GitHub, que impede a inclusão desse campo na coleta principal.
6. **Persistência** do *dataset* em CSV.
7. **Análise estatística**: descritivas, testes não paramétricos, geração
   de gráficos.
8. **Sumarização** dos valores medianos globais para responder cada
   questão de pesquisa.

### 2.2 Decisões de projeto

- **Mediana** como estatística central, dada a forte assimetria das
  distribuições (cauda longa). A título de ilustração, o tempo de análise
  apresenta mediana de 74,3 horas e média de 2.068,9 horas — cerca de
  28 vezes maior.
- **Mann-Whitney *U*** acompanhado do **delta de Cliff** para as RQs da
  Dimensão A (variável dependente binária). O ponto-bisserial de Pearson
  é reportado como métrica complementar.
- **Coeficiente de Spearman (ρ)** para as RQs da Dimensão B (variável
  dependente numérica), por preservar relações monótonas e ser robusto a
  *outliers*. O Pearson em escala log(*x* + 1) é reportado como verificação
  adicional em distribuições de cauda pesada.
- **α = 0,05**, com correção **Holm step-down** e Bonferroni aplicadas
  sobre o conjunto de oito *p*-valores (uma por RQ × métrica).
- **Intervalos de confiança de 95%** estimados via *bootstrap* com 1.000
  reamostragens, tanto para medianas quanto para o coeficiente ρ.
- **Filtro de uma hora** preservado conforme o enunciado, para excluir
  revisões executadas por *bots* ou ferramentas de CI/CD.

### 2.3 Materiais utilizados

- **Fontes de dados**: *GitHub REST API v3* (busca de repositórios) e
  *GitHub GraphQL API v4* (PRs, revisões e participantes).
- **Linguagem**: Python 3.12.
- **Bibliotecas**: `requests`, `python-dotenv`, `pandas`, `numpy`,
  `scipy.stats`, `matplotlib`, `seaborn`.
- **Código-fonte**:
  - [`scripts/coleta_graphql_PRs.py`](../scripts/coleta_graphql_PRs.py) — coleta principal;
  - [`scripts/enriquecer_participantes.py`](../scripts/enriquecer_participantes.py) — enriquecimento;
  - [`scripts/analise_sprint3.py`](../scripts/analise_sprint3.py) — análise estatística;
  - [`scripts/coleta_sprint1_PRs.py`](../scripts/coleta_sprint1_PRs.py) — versão REST inicial (mantida para fins de auditoria).

### 2.4 Métodos utilizados

- **Estatística descritiva**: *n*, média, mediana, desvio-padrão, IQR,
  percentis 25, 75 e 95, mínimo e máximo.
- **Inferência não paramétrica**: Mann-Whitney *U*, delta de Cliff,
  ponto-bisserial de Pearson, Spearman ρ, Pearson em escala log.
- ***Bootstrap*** com 1.000 reamostragens para intervalos de confiança.
- **Correção de múltiplas comparações**: Holm step-down (preferida) e
  Bonferroni (reportada como referência conservadora).

### 2.5 Métricas e suas unidades

| Categoria | Métrica | Unidade |
|---|---|---|
| Tamanho | `changed_files` | arquivos |
| Tamanho | `additions`, `deletions`, `loc_total` | linhas de código |
| Tempo de análise | `tempo_analise_horas` / `tempo_analise_dias` | horas / dias |
| Descrição | `descricao_tamanho_chars` | caracteres (corpo em *markdown*) |
| Interações | `num_participantes` | pessoas distintas |
| Interações | `total_comentarios` | comentários na *issue* |
| Revisão | `numero_reviews` | revisões submetidas |
| *Status* | `status` | `MERGED` / `CLOSED` |

### 2.6 *Dataset* final

- **14.347 PRs** após todos os filtros do enunciado.
- **182 repositórios** efetivamente analisados (dos 200 candidatos,
  18 foram descartados por não atingirem o mínimo de 100 PRs
  `MERGED + CLOSED` ou por inacessibilidade temporária da API).
- Distribuição por *status*: 9.728 (67,8%) `MERGED` e 4.619 (32,2%) `CLOSED`.
- *Snapshot* coletado em 30 de abril de 2026.

---

## 3. Visualização dos resultados

### 3.1 Tabelas geradas

- Descritivas globais: [`output/lab3s3/descritivas_globais.csv`](../output/lab3s3/descritivas_globais.csv).
- Descritivas por *status*: [`output/lab3s3/descritivas_por_status.csv`](../output/lab3s3/descritivas_por_status.csv).
- RQ01–RQ04 (Mann-Whitney + Cliff + ponto-bisserial):
  [`output/lab3s3/comparacao_status_mannwhitney.csv`](../output/lab3s3/comparacao_status_mannwhitney.csv).
- RQ05–RQ08 (Spearman + Pearson em log):
  [`output/lab3s3/correlacoes_spearman.csv`](../output/lab3s3/correlacoes_spearman.csv).
- Resumo executivo: [`output/lab3s3/resumo_rqs.md`](../output/lab3s3/resumo_rqs.md).

### 3.2 Gráficos gerados

A pasta [`output/lab3s3/charts/`](../output/lab3s3/charts/) contém 25 figuras:

- **Oito boxplots** (`boxplot_<métrica>_status.png`) comparando `MERGED`
  versus `CLOSED` para cada métrica preditora — base visual das RQs da
  Dimensão A.
- **Oito gráficos de dispersão** em escala log-log
  (`scatter_<métrica>_x_reviews.png`) com o coeficiente ρ de Spearman no
  título — base visual das RQs da Dimensão B.
- **Oito gráficos de violino** (`violin_<métrica>.png`) em escala log
  para inspeção das distribuições.
- **Um *heatmap*** consolidando as correlações de Spearman entre as
  preditoras e o número de revisões (`heatmap_spearman_reviews.png`).

### 3.3 Estatísticas descritivas globais (*n* = 14.347)

| Métrica | Mediana | p25 | p75 | p95 | Máximo |
|---|--:|--:|--:|--:|--:|
| Arquivos alterados | 2 | 1 | 5 | 23 | 7.264 |
| Linhas adicionadas | 22 | 3 | 121 | 1.237 | 2.901.110 |
| Linhas removidas | 3 | 1 | 21 | 318 | 141.843 |
| LOC total | 33 | 5 | 165 | 1.705 | 2.901.110 |
| Tempo de análise (h) | 74,3 | 13,3 | 651,7 | 11.818,0 | 92.293,6 |
| Descrição (caracteres) | 742 | 170 | 1.746 | 5.124 | 82.171 |
| Número de participantes | 3 | 2 | 3 | 6 | 277 |
| Total de comentários | 2 | 0 | 4 | 11 | 589 |
| Número de revisões | 1 | 1 | 3 | 10 | 905 |

### 3.4 Resultados — Dimensão A (RQ01–RQ04)

*n*<sub>MERGED</sub> = 9.728 e *n*<sub>CLOSED</sub> = 4.619.
Teste: Mann-Whitney *U*. Tamanho de efeito: delta de Cliff
(|δ| < 0,147 desprezível; < 0,33 pequeno; < 0,474 médio; ≥ 0,474 grande).

| RQ | Métrica | Mediana MERGED | Mediana CLOSED | *p*-valor | *p*-Holm | δ de Cliff | Efeito |
|---|---|--:|--:|--:|--:|--:|---|
| RQ01 | Arquivos alterados | 2,0 | 2,0 | < 0,001 | < 0,001 | +0,106 | desprezível |
| RQ01 | Linhas adicionadas | 22,0 | 23,0 | 0,788 | 0,788 | +0,003 | desprezível |
| RQ01 | Linhas removidas | 4,0 | 2,0 | < 0,001 | < 0,001 | +0,171 | pequeno |
| RQ01 | LOC total | 34,0 | 31,0 | 0,003 | 0,007 | +0,030 | desprezível |
| RQ02 | Tempo de análise (h) | **40,7** | **519,8** | < 0,001 | < 0,001 | **−0,437** | **médio** |
| RQ03 | Descrição (caracteres) | 698 | 843 | < 0,001 | < 0,001 | −0,043 | desprezível |
| RQ04 | Número de participantes | 3 | 3 | < 0,001 | < 0,001 | −0,083 | desprezível |
| RQ04 | Total de comentários | 1 | 2 | < 0,001 | < 0,001 | −0,155 | pequeno |

> Convenção: δ positivo indica `MERGED > CLOSED` na métrica; negativo,
> `MERGED < CLOSED`.

### 3.5 Resultados — Dimensão B (RQ05–RQ08)

Coeficiente ρ de Spearman com IC 95% por *bootstrap*. Todos os
*p*-valores são inferiores a 10⁻⁶.

| RQ | Métrica | ρ | IC 95% | *p*-Holm | Pearson em log | Interpretação |
|---|---|--:|---|--:|--:|---|
| RQ05 | Arquivos alterados | 0,270 | [0,254; 0,285] | < 0,001 | 0,295 | fraca positiva |
| RQ05 | Linhas adicionadas | **0,315** | [0,300; 0,329] | < 0,001 | 0,346 | **moderada positiva** |
| RQ05 | Linhas removidas | 0,183 | [0,168; 0,200] | < 0,001 | 0,213 | fraca positiva |
| RQ05 | LOC total | **0,302** | [0,287; 0,316] | < 0,001 | 0,330 | **moderada positiva** |
| RQ06 | Tempo de análise (h) | 0,110 | [0,094; 0,126] | < 0,001 | 0,119 | fraca positiva |
| RQ07 | Descrição (caracteres) | 0,185 | [0,169; 0,202] | < 0,001 | 0,168 | fraca positiva |
| RQ08 | Número de participantes | **0,342** | [0,327; 0,356] | < 0,001 | 0,330 | **moderada positiva** |
| RQ08 | Total de comentários | **0,330** | [0,315; 0,344] | < 0,001 | 0,381 | **moderada positiva** |

---

## 4. Discussão dos resultados

### 4.1 Confronto questão a questão

**RQ01 — Tamanho × *feedback* final (H1)**

As medianas das métricas de tamanho são essencialmente idênticas entre
os grupos (LOC = 34 em `MERGED` versus 31 em `CLOSED`), e o delta de
Cliff varia entre desprezível (+0,03 para LOC total) e pequeno (+0,17
para *deletions*). **Veredito: hipótese refutada.** A direção do
sinal, quando presente, é inclusive contrária à esperada: PRs `MERGED`
removem ligeiramente mais linhas. Uma interpretação plausível é que
PRs muito grandes raramente passam pela triagem inicial necessária à
inclusão na amostra (ao menos uma revisão e tempo superior a uma hora).

**RQ02 — Tempo de análise × *feedback* final (H2)**

A mediana do tempo de análise dos PRs `MERGED` é de **40,7 horas**,
enquanto a dos `CLOSED` é de **519,8 horas** — aproximadamente 13 vezes
maior. O delta de Cliff (−0,437) caracteriza um **efeito médio**, o
mais forte observado na Dimensão A. **Veredito: hipótese corroborada.**
O tempo de análise é, com larga vantagem, o melhor preditor do desfecho
do PR neste estudo.

**RQ03 — Descrição × *feedback* final (H3)**

A mediana da descrição é maior nos PRs `CLOSED` (843 caracteres) do que
nos `MERGED` (698), com δ = −0,043 (desprezível). **Veredito: hipótese
refutada.** O sinal é contrário ao esperado, possivelmente porque
descrições muito extensas acompanham PRs controversos ou complexos, que
demandam justificativas detalhadas mas não necessariamente são aceitos.

**RQ04 — Interações × *feedback* final (H4)**

O número de participantes apresenta medianas idênticas (3 em ambos os
grupos) e efeito desprezível. Já o total de comentários é maior em
`CLOSED` (mediana 2 versus 1 em `MERGED`), com δ = −0,155 (pequeno).
**Veredito: hipótese parcialmente corroborada.** PRs que geram debate
prolongado tendem a terminar em `CLOSED`, conforme previsto.

**RQ05 — Tamanho × número de revisões (H5)**

Os coeficientes de Spearman variam de 0,18 (deletions) a 0,32 (additions).
LOC total apresenta ρ = 0,302 — uma **correlação moderada positiva**.
**Veredito: hipótese corroborada.** Importante destacar que o tamanho
não prediz o desfecho do PR (RQ01) mas prediz o **esforço de revisão**.

**RQ06 — Tempo de análise × número de revisões (H6)**

ρ = 0,110 (correlação fraca positiva). **Veredito: hipótese corroborada
com efeito fraco.** Embora estatisticamente significativo, o efeito é
modesto, sugerindo que tempo elevado nem sempre é proporcional a número
de ciclos: um PR pode permanecer aberto por longos períodos sem novas
revisões.

**RQ07 — Descrição × número de revisões (H7)**

ρ = 0,185 (fraca **positiva**, contrária à expectativa de que descrições
longas reduziriam o número de revisões). **Veredito: hipótese refutada.**
O sinal sugere efeito confundidor: descrições longas tipicamente
acompanham PRs grandes ou complexos, que por sua vez demandam mais
ciclos de revisão.

**RQ08 — Interações × número de revisões (H8)**

Coeficientes de 0,342 (participantes) e 0,330 (comentários), ambos
**moderada positiva**. **Veredito: hipótese corroborada.** Ao lado de
RQ05, configura o sinal mais forte da Dimensão B.

### 4.2 *Insights*

- **Distribuições assimétricas**: a média do tempo de análise (2.069 h)
  excede a mediana (74 h) por um fator de aproximadamente 28×. Esse
  padrão se repete em todas as métricas e justifica plenamente o uso
  de estatísticas não paramétricas.
- **Independência entre desfecho e esforço**: PRs grandes não são
  rejeitados com mais frequência (RQ01), mas exigem mais revisões
  (RQ05). Trata-se de um achado relevante para a engenharia de software,
  pois separa duas dimensões frequentemente conflundidas no discurso
  comum sobre *code review*.
- **Tempo é o sinal dominante da Dimensão A**: PRs `CLOSED` levam, em
  mediana, cerca de 13 vezes mais tempo do que `MERGED` para serem
  fechados.
- **Interações são bom *proxy* de esforço**: o número de participantes
  e o total de comentários apresentam ρ ≈ 0,33 com o número de revisões,
  consistente com um modelo em que cada novo ciclo de revisão tende a
  trazer participantes e comentários adicionais.
- **Efeito surpreendentemente modesto da descrição**: a descrição não
  discrimina o desfecho (RQ03 desprezível) e tem efeito apenas fraco
  sobre o número de revisões (RQ07).

### 4.3 Comparação cruzada (Dimensão A *vs.* Dimensão B)

A tabela abaixo confronta o efeito de cada categoria de preditor sobre
as duas dimensões:

| Categoria preditora | RQ Dimensão A (Cliff δ) | RQ Dimensão B (ρ) | Leitura |
|---|---|---|---|
| Tamanho (LOC total) | +0,030 (desprezível) | +0,302 (moderada) | Não prediz desfecho; prediz esforço. |
| Tempo de análise | **−0,437 (médio)** | +0,110 (fraca) | Prediz desfecho mais do que esforço. |
| Descrição | −0,043 (desprezível) | +0,185 (fraca) | Pouca influência em ambas as dimensões. |
| Interações (comentários) | −0,155 (pequeno) | +0,330 (moderada) | Mais comentários → `CLOSED` e mais revisões. |

### 4.4 Estatísticas reportadas

Para todos os testes apresentados, registram-se:

- *n* total e por grupo;
- mediana com intervalo de confiança de 95% via *bootstrap* (1.000
  reamostragens);
- *p*-valor bruto, *p*-valor ajustado por Holm e *p*-valor ajustado por
  Bonferroni;
- tamanho de efeito (delta de Cliff para a Dimensão A; magnitude do ρ
  com IC 95% para a Dimensão B);
- interpretação qualitativa segundo as convenções de Romano et al.
  (Cliff) e Cohen (ρ).

Após a correção de Holm, **todos os testes da Dimensão A são
significativos** ao nível de 5%, à exceção de RQ01 com `additions`
(*p* = 0,788). Na Dimensão B, **todos os oito testes são
significativos** após a correção.

---

## 5. Conclusão

### 5.1 Tomada de decisão

À luz dos resultados obtidos, recomenda-se aos contribuidores de
projetos *open source* populares:

- **Para maximizar a chance de aceitação (`MERGED`)**: priorizar PRs
  que possam ser fechados rapidamente. PRs `MERGED` apresentam mediana
  de 40,7 horas até o fechamento, contra 519,8 horas dos `CLOSED`. O
  tamanho do PR, isoladamente, possui pouco poder discriminativo do
  desfecho.
- **Para reduzir o esforço de revisão**: manter PRs **menores em LOC**
  e procurar **acertar na primeira submissão**, evitando ciclos
  prolongados de discussão. Esses são os preditores mais fortes do
  número de revisões.
- **Quanto à descrição**: há evidência apenas marginal de que
  descrições mais elaboradas afetem o desfecho ou o esforço. Trata-se
  de boa prática, mas o ganho objetivo nas métricas agregadas é
  discreto.

### 5.2 Sugestões para trabalhos futuros

- **Ampliação da amostra** para além dos 200 repositórios mais
  populares, com segmentação por linguagem ou domínio (web, móvel,
  infraestrutura, *machine learning*).
- **Inclusão de métricas de CI/CD**, como sucesso ou falha de *checks*
  automatizados, que provavelmente medeiam parte dos efeitos
  observados.
- **Modelagem multivariada** para isolar efeitos de variáveis
  cofundidas (regressão logística para `status`; regressão de Poisson
  ou Binomial Negativa para `numero_reviews`).
- **Estudo longitudinal** por repositório, capturando efeitos de
  mantenedores específicos ou de mudanças de política ao longo do
  tempo.
- **Refinamento de `num_participantes`** por meio de pipeline que
  liste explicitamente os comentadores de *issues*, de modo a
  triangular o valor reportado pela API.

### 5.3 Resultado conclusivo sucinto

Em uma amostra de **14.347 PRs distribuídos por 182 repositórios
populares**, o **tempo de análise** mostrou-se o preditor mais forte do
desfecho do PR (delta de Cliff = −0,44, efeito médio): PRs `MERGED`
fecham, em mediana, 13 vezes mais rápido do que `CLOSED`. Quanto ao
**número de revisões**, os melhores preditores são as **interações**
(ρ ≈ 0,33) e o **tamanho** (ρ ≈ 0,30 em LOC). O tamanho **não prediz o
desfecho** (efeito desprezível) e a descrição apresenta influência
apenas marginal em ambas as dimensões. Das oito hipóteses formuladas,
**três foram corroboradas** (H2, H5, H8), **três foram refutadas**
(H1, H3, H7) e **duas foram parcialmente corroboradas com efeito
fraco** (H4, H6).

### 5.4 *Plus* — Confronto com a literatura

- **Gousios, Pinzger e van Deursen (2014, *MSR*)** —
  *“An exploratory study of the pull-based software development model”*.
  Os autores reportam que PRs pequenos são integrados com maior rapidez
  e que a descrição exerce efeito positivo sobre a aceitação. Nossos
  achados **corroboram parcialmente** o primeiro ponto via RQ02 (PRs
  `MERGED` apresentam tempo significativamente menor) mas **contestam**
  a centralidade da descrição (RQ03 com efeito desprezível).

- **Tsay, Dabbish e Herbsleb (2014, *ICSE*)** —
  *“Influence of social and technical factors for evaluating contribution
  in GitHub”*. Demonstram que fatores **sociais** (discussão, contexto
  do autor) são tão influentes quanto os técnicos. Nossos resultados de
  **RQ04 (comentários)** e **RQ08 (interações)** **corroboram** a
  importância do canal social: PRs com mais comentários tendem a
  `CLOSED` e demandam mais revisões.

- **Yu, Wang, Yin e Wang (2015, *ICSME*)** —
  *“Wait for it: determinants of pull request evaluation latency”*.
  Os autores apontam tamanho, descrição e atividade do projeto como
  determinantes do tempo de avaliação. Nossos achados **corroboram** o
  efeito do tamanho sobre o esforço (RQ05, ρ moderada), mas
  **contestam** a centralidade da descrição (RQ07, efeito apenas
  fraco).

- **Kononenko, Baysal e Godfrey (2016, *ICSE*)** —
  *“Code review quality: how developers see it”*. Defendem que
  características técnicas e sociais combinadas determinam a qualidade
  e o desfecho da revisão. Nossos achados **corroboram** esse modelo
  misto, identificando dois preditores robustos: técnico (tempo, em
  RQ02) e social (interações, em RQ04 e RQ08).

---

## 6. Ameaças à validade

- ***Snapshot* temporal único** (30/04/2026): PRs muito recentes podem
  ainda evoluir, e tendências do ecossistema mudam ao longo do tempo.
- **Viés de popularidade**: a amostragem dos 200 repositórios mais
  estrelados exclui projetos de menor visibilidade, nos quais a
  dinâmica de revisão pode ser substancialmente distinta.
- **Heurística de uma hora**: o filtro de uma hora captura a maior
  parte de revisões automáticas, mas pode falhar em casos de *bots*
  lentos ou em PRs legítimos fechados rapidamente.
- **Limite de paginação** (seis páginas de cem PRs por repositório):
  para repositórios com altíssimo volume de PRs, há subamostragem dos
  mais antigos. Mantêm-se, ainda assim, até 100 PRs validados por
  repositório, suficientes para a sumarização agregada exigida.
- **Confundimento entre variáveis**: tamanho, descrição e número de
  revisões provavelmente cofundem-se. Os testes univariados aqui
  aplicados não isolam efeitos. Uma análise multivariada é parte das
  sugestões para trabalhos futuros (Seção 5.2).
- **Definição de `num_participantes`**: utiliza-se o
  `participants.totalCount` do GraphQL, que conta participantes únicos
  da *issue*/PR (autor + comentadores + revisores), conforme definição
  da própria API do GitHub.
