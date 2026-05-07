# RELATÓRIO FINAL — LABORATÓRIO 03

## Caracterizando a atividade de *code review* em repositórios populares do GitHub

---

**Disciplina:** Laboratório de Experimentação de Software  
**Autores:** *(preencher)*  
**Data:** 07 de maio de 2026 — Versão 2.0  
**Repositório:** [github.com/Miguel-Lessa/lab-medicao](https://github.com/Miguel-Lessa/lab-medicao)

---

## Resumo

Este estudo investiga, por meio de análise quantitativa observacional, quais variáveis de *Pull Requests* (PRs) se associam ao *feedback* final da revisão (`MERGED` ou `CLOSED`) e ao número de revisões recebidas. A amostra compreende **14.347 PRs** distribuídos por **182 repositórios** populares do GitHub. Os principais achados indicam que: (i) o **tempo de análise** é o preditor mais forte do desfecho, com PRs `CLOSED` apresentando mediana de 519,8 horas contra 40,7 horas dos `MERGED` (δ de Cliff = −0,437, efeito médio); (ii) o **tamanho** e as **interações** são os melhores preditores do esforço de revisão (ρ ≈ 0,30–0,34); e (iii) a **descrição** exerce influência apenas marginal em ambas as dimensões. Das oito hipóteses formuladas, três foram corroboradas, três refutadas e duas parcialmente corroboradas.

---

## 1. Contexto e Motivação

A prática de *code review* constitui elemento central dos processos colaborativos de desenvolvimento de software, especialmente no ecossistema *open source* hospedado no GitHub. Nesse modelo, toda contribuição é submetida por meio de um *Pull Request* (PR), o qual passa por inspeção de revisores antes de ser incorporado (`MERGED`) ou descartado (`CLOSED`).

Compreender quais fatores influenciam o resultado da revisão e o esforço demandado é relevante tanto para contribuidores, que desejam otimizar suas submissões, quanto para mantenedores, que buscam eficiência nos processos de integração. Este experimento é necessário para fornecer evidências empíricas que permitam separar duas dimensões frequentemente confundidas: **aceitação** do PR e **esforço** de revisão.

---

## 2. Objetivo e Hipóteses

### 2.1 Objetivo

Caracterizar empiricamente a atividade de *code review* nos 200 repositórios mais populares do GitHub, avaliando a relação entre métricas dos PRs, o *feedback* final e o número de revisões.

### 2.2 Hipóteses

| ID | Hipótese nula (H₀) | Hipótese alternativa (H₁) | Resultado |
|----|---------------------|---------------------------|-----------|
| H1 | Tamanho não diferencia `MERGED`/`CLOSED` | PRs maiores tendem a `CLOSED` | **Refutada** |
| H2 | Tempo não diferencia `MERGED`/`CLOSED` | Maior tempo associa-se a `CLOSED` | **Corroborada** |
| H3 | Descrição não diferencia `MERGED`/`CLOSED` | Descrição maior favorece `MERGED` | **Refutada** |
| H4 | Interações não diferenciam `MERGED`/`CLOSED` | Mais interações tendem a `CLOSED` | **Parcial** |
| H5 | Tamanho não se correlaciona com revisões | PRs maiores recebem mais revisões | **Corroborada** |
| H6 | Tempo não se correlaciona com revisões | Maior tempo implica mais revisões | **Parcial (fraca)** |
| H7 | Descrição não se correlaciona com revisões | Descrição maior reduz revisões | **Refutada** |
| H8 | Interações não se correlacionam com revisões | Mais interações implicam mais revisões | **Corroborada** |

---

## 3. Perguntas de Pesquisa

**Dimensão A — *Feedback* final (MERGED vs. CLOSED):**

- **RQ01:** Qual a relação entre o tamanho dos PRs e o *feedback* final?
- **RQ02:** Qual a relação entre o tempo de análise e o *feedback* final?
- **RQ03:** Qual a relação entre a descrição do PR e o *feedback* final?
- **RQ04:** Qual a relação entre as interações no PR e o *feedback* final?

**Dimensão B — Número de revisões:**

- **RQ05:** Qual a relação entre o tamanho e o número de revisões?
- **RQ06:** Qual a relação entre o tempo de análise e o número de revisões?
- **RQ07:** Qual a relação entre a descrição e o número de revisões?
- **RQ08:** Qual a relação entre as interações e o número de revisões?

---

## 4. Variáveis e Métricas

### 4.1 Métricas primárias

| Categoria | Métrica | Unidade | RQs |
|-----------|---------|---------|-----|
| Tamanho | `changed_files`, `additions`, `deletions`, `loc_total` | arquivos / linhas | RQ01, RQ05 |
| Tempo | `tempo_analise_horas` | horas | RQ02, RQ06 |
| Descrição | `descricao_tamanho_chars` | caracteres | RQ03, RQ07 |
| Interações | `num_participantes`, `total_comentarios` | pessoas / comentários | RQ04, RQ08 |

### 4.2 Variáveis dependentes

- **Dimensão A:** `status` (MERGED / CLOSED) — variável binária.
- **Dimensão B:** `numero_reviews` — variável numérica de contagem.

### 4.3 Definições

- **LOC total** = `additions` + `deletions`.
- **Tempo de análise** = `closedAt` (ou `mergedAt`) − `createdAt`, em horas.
- **Participantes** = `participants.totalCount` da API GraphQL (pessoas distintas).

---

## 5. Desenho Experimental

- **Tipo:** Estudo quantitativo, observacional e retrospectivo.
- **Unidades de análise:** Pull Requests individuais.
- **Amostra:** 200 repositórios mais populares do GitHub (por estrelas); 182 efetivamente analisados.
- **Critérios de inclusão:** PRs com `status ∈ {MERGED, CLOSED}`, pelo menos uma revisão, tempo de análise superior a uma hora.
- **Critérios de exclusão:** Forks, repositórios com menos de 100 PRs fechados.
- **Janela temporal:** *Snapshot* coletado em 30 de abril de 2026.
- **Tamanho final:** 14.347 PRs (9.728 MERGED, 4.619 CLOSED).

---

## 6. Ambiente e Materiais

| Material | Finalidade |
|----------|------------|
| GitHub REST API v3 | Busca dos 200 repositórios mais populares |
| GitHub GraphQL API v4 | Coleta de PRs, revisões, participantes e metadados |
| Python 3.12 | Scripts de coleta, enriquecimento e análise |
| pandas / numpy | Organização e sumarização tabular |
| scipy.stats | Mann-Whitney *U*, Spearman ρ, Pearson, ponto-bisserial |
| matplotlib / seaborn | Geração de gráficos |

---

## 7. Procedimento

1. Listar os 200 repositórios mais populares do GitHub por número de estrelas.
2. Validar elegibilidade: pelo menos 100 PRs em `MERGED + CLOSED`.
3. Coletar PRs via GraphQL (campos: *status*, datas, tamanho, descrição, comentários, revisões).
4. Aplicar filtros: `status ∈ {MERGED, CLOSED}`, `reviews ≥ 1`, `tempo > 1 hora`.
5. Enriquecer com `participants.totalCount` em segunda passagem GraphQL.
6. Persistir *dataset* em CSV.
7. Calcular estatísticas descritivas globais e por *status*.
8. Aplicar testes inferenciais e gerar gráficos.

---

## 8. Análise de Dados

### 8.1 Métodos estatísticos

- **Dimensão A (RQ01–RQ04):** Mann-Whitney *U* (comparação de dois grupos independentes), δ de Cliff (tamanho de efeito), ponto-bisserial de Pearson (complementar).
- **Dimensão B (RQ05–RQ08):** Spearman ρ (correlação monótona), Pearson em log(*x*+1) (verificação em escala expandida).
- **Intervalos de confiança:** 95%, via *bootstrap* com 1.000 reamostragens.
- **Correção de múltiplas comparações:** Holm *step-down* (α = 0,05) e Bonferroni (referência conservadora).

### 8.2 Justificativa

As distribuições apresentam forte assimetria com cauda longa (por exemplo, a média do tempo de análise é 2.069 h, contra mediana de 74 h). Essa característica justifica plenamente o uso de testes não paramétricos e da mediana como medida central.

---

## 9. Resultados

### 9.1 Estatísticas descritivas globais (*n* = 14.347)

| Métrica | Mediana | Média | Desvio padrão | p25 | p75 | p95 |
|---------|---------|-------|---------------|-----|-----|-----|
| Arquivos alterados | 2 | 9,6 | 101,7 | 1 | 5 | 23 |
| Linhas adicionadas | 22 | 1.137,0 | 34.259,3 | 3 | 121 | 1.237 |
| Linhas removidas | 3 | 199,2 | 2.808,9 | 1 | 21 | 318 |
| LOC total | 33 | 1.336,2 | 34.531,9 | 5 | 165 | 1.705 |
| Tempo de análise (h) | 74,3 | 2.068,9 | 6.814,7 | 13,3 | 651,7 | 11.818,0 |
| Descrição (caracteres) | 742 | 1.569,4 | 3.697,8 | 170 | 1.746 | 5.124 |
| Participantes | 3 | 3,2 | 4,7 | 2 | 3 | 6 |
| Comentários | 2 | 3,3 | 9,8 | 0 | 4 | 11 |
| Revisões | 1 | 3,4 | 11,6 | 1 | 3 | 10 |

> **Observação:** A razão média/mediana é extremamente elevada em várias métricas (ex.: 28× para tempo de análise), confirmando a assimetria das distribuições e a necessidade de estatísticas não paramétricas.

### 9.2 Resultados — Dimensão A (RQ01–RQ04)

*n*_MERGED = 9.728 | *n*_CLOSED = 4.619

| RQ | Métrica | Med. MERGED | Med. CLOSED | *p*-Holm | δ Cliff | Efeito |
|----|---------|-------------|-------------|----------|---------|--------|
| RQ01 | Arquivos alterados | 2,0 | 2,0 | < 0,001 | +0,106 | desprezível |
| RQ01 | Linhas adicionadas | 22,0 | 23,0 | 0,788 | +0,003 | desprezível |
| RQ01 | Linhas removidas | 4,0 | 2,0 | < 0,001 | +0,171 | pequeno |
| RQ01 | LOC total | 34,0 | 31,0 | 0,007 | +0,030 | desprezível |
| RQ02 | Tempo de análise (h) | **40,7** | **519,8** | < 0,001 | **−0,437** | **médio** |
| RQ03 | Descrição (chars) | 698 | 843 | < 0,001 | −0,043 | desprezível |
| RQ04 | Participantes | 3 | 3 | < 0,001 | −0,083 | desprezível |
| RQ04 | Comentários | 1 | 2 | < 0,001 | −0,155 | pequeno |

> **Convenção:** δ positivo indica `MERGED > CLOSED` na métrica; negativo, `MERGED < CLOSED`.

**Figura 1** — Tamanho do efeito (δ de Cliff) para todas as métricas da Dimensão A.
![Forest plot Cliff delta](../output/lab3s3/charts_v2/06_forest_cliff_delta.png)

> **Interpretação da Figura 1:** O gráfico ordena as oito métricas pelo seu δ de Cliff, evidenciando que o tempo de análise se destaca como a única variável com efeito médio (δ = −0,437), indicando que PRs `CLOSED` permanecem abertos substancialmente mais tempo. As demais métricas apresentam efeitos pequenos ou desprezíveis (|δ| < 0,2), o que demonstra que, isoladamente, tamanho, descrição e número de participantes têm pouca capacidade de discriminar o desfecho. Nota-se que as linhas pontilhadas verticais delimitam a faixa de efeito desprezível (|δ| < 0,147), auxiliando na identificação rápida das métricas relevantes.

**Figura 2** — Distribuição do tempo de análise por *status* (violino comparativo).
![Violin tempo](../output/lab3s3/charts_v2/01_violin_tempo_status.png)

> **Interpretação da Figura 2:** Os violinos revelam que a distribuição do tempo de análise em `MERGED` concentra-se em valores baixos (moda próxima de log(1+40) ≈ 3,7), enquanto em `CLOSED` a distribuição é mais larga e deslocada para cima. A linha tracejada interna (mediana) de `CLOSED` situa-se claramente acima da de `MERGED`, confirmando visualmente a diferença de 13× nas medianas. A forma bimodal do violino de `CLOSED` sugere a existência de dois perfis: PRs que são rapidamente rejeitados e PRs que permanecem indefinidamente abertos antes do fechamento.

**Figura 3** — Função de distribuição acumulada (ECDF) do tempo de análise por *status*.
![ECDF tempo](../output/lab3s3/charts_v2/04_ecdf_tempo_status.png)

> **Interpretação da Figura 3:** A ECDF permite observar que 50% dos PRs `MERGED` são concluídos em até 40,7 horas (≈1,7 dias), enquanto 50% dos `CLOSED` só atingem esse patamar por volta de 519,8 horas (≈21,7 dias). A separação entre as duas curvas é máxima na faixa de 40 a 500 horas, indicando que esse intervalo é o mais discriminante para prever o desfecho. Após 10.000 horas, as curvas convergem, pois os PRs extremamente longos existem em ambos os grupos, porém são mais frequentes em `CLOSED`.

**Figura 4** — Taxa de `MERGED` por decil de tempo de análise.
![Taxa merged decil](../output/lab3s3/charts_v2/08_taxa_merged_decil_tempo.png)

> **Interpretação da Figura 4:** A taxa de merge permanece elevada (≈80%) nos primeiros seis decis e cai abruptamente a partir do sétimo, atingindo apenas ≈25% no último decil (PRs mais lentos). Esse padrão confirma que o tempo não exerce efeito linear, mas sim um efeito de limiar: PRs que ultrapassam determinado período de latência possuem probabilidade significativamente menor de aceitação. A linha tracejada horizontal indica a média global (67,8%), servindo como referência para identificar os decis acima e abaixo do esperado.

### 9.3 Resultados — Dimensão B (RQ05–RQ08)

| RQ | Métrica | ρ Spearman | IC 95% | *p*-Holm | Interpretação |
|----|---------|-----------|--------|----------|---------------|
| RQ05 | Arquivos alterados | 0,270 | [0,254; 0,285] | < 0,001 | fraca positiva |
| RQ05 | Linhas adicionadas | **0,315** | [0,300; 0,329] | < 0,001 | **moderada positiva** |
| RQ05 | Linhas removidas | 0,183 | [0,168; 0,200] | < 0,001 | fraca positiva |
| RQ05 | LOC total | **0,302** | [0,287; 0,316] | < 0,001 | **moderada positiva** |
| RQ06 | Tempo de análise (h) | 0,110 | [0,094; 0,126] | < 0,001 | fraca positiva |
| RQ07 | Descrição (chars) | 0,185 | [0,169; 0,202] | < 0,001 | fraca positiva |
| RQ08 | Participantes | **0,342** | [0,327; 0,356] | < 0,001 | **moderada positiva** |
| RQ08 | Comentários | **0,330** | [0,315; 0,344] | < 0,001 | **moderada positiva** |

**Figura 5** — Spearman ρ com IC 95% para todas as métricas da Dimensão B.
![Forest Spearman](../output/lab3s3/charts_v2/07_forest_spearman_rho.png)

> **Interpretação da Figura 5:** O gráfico de floresta ordena as métricas pelo coeficiente de Spearman com o número de revisões. Quatro métricas ultrapassam o limiar de correlação moderada (ρ ≥ 0,30): número de participantes (0,342), total de comentários (0,330), linhas adicionadas (0,315) e LOC total (0,302). As barras de erro (IC 95%) são estreitas, refletindo a robustez estatística proporcionada pela amostra de 14.347 observações. Nota-se que o tempo de análise, apesar de ser o preditor mais forte do desfecho (Dimensão A), apresenta correlação fraca com o número de revisões (ρ = 0,110), reforçando a distinção entre as duas dimensões investigadas.

**Figura 6** — Dispersão LOC total × revisões (hexbin, escala log).
![Hexbin LOC](../output/lab3s3/charts_v2/09_hexbin_loc_reviews.png)

> **Interpretação da Figura 6:** O gráfico hexbin, em escala logarítmica, substitui o *scatter plot* tradicional para lidar com a sobreposição de 14.347 pontos. A concentração de PRs ocorre na região de baixo LOC e poucas revisões (canto inferior esquerdo, em tons escuros), confirmando que a maioria dos PRs é pequena e recebe entre 1 e 3 revisões. A tendência ascendente da nuvem indica que PRs maiores tendem a receber mais revisões, porém com alta variância — PRs de mesmo tamanho podem receber de 1 a centenas de revisões. Isso é consistente com ρ = 0,302: a relação é real, mas moderada e não determinística.

**Figura 7** — Dispersão comentários × revisões (hexbin, escala log).
![Hexbin comentarios](../output/lab3s3/charts_v2/10_hexbin_comentarios_reviews.png)

> **Interpretação da Figura 7:** A relação entre comentários e revisões mostra-se visualmente mais nítida do que a de LOC. A nuvem hexbin apresenta uma diagonal mais acentuada, o que é coerente com ρ = 0,330. Esse resultado era esperado, pois comentários e revisões são ambos indicadores de interação social no processo de *code review*: PRs que geram mais debate tendem a passar por mais ciclos de revisão. A concentração na base (0–1 comentário, 1 revisão) reflete a prevalência de PRs triviais que são aceitos sem discussão.

**Figura 8** — Distribuição de revisões por quartil de LOC total.
![Ridgeline reviews](../output/lab3s3/charts_v2/14_ridgeline_reviews_loc.png)

> **Interpretação da Figura 8:** O *boxenplot* segmenta os PRs em quartis de tamanho e mostra como a distribuição de revisões se desloca para cima à medida que o LOC total aumenta. A mediana de revisões sobe de Q1 para Q4, confirmando a correlação positiva. Além disso, a cauda superior (PRs com muitas revisões) é substancialmente mais longa em Q3 e Q4, indicando que PRs grandes não apenas recebem mais revisões em média, como também apresentam maior variabilidade no esforço de revisão exigido.

---

## 10. Discussão e Interpretação

### 10.1 Confronto questão a questão

**RQ01 — Tamanho × *feedback* final:** As medianas de LOC total são essencialmente idênticas entre os grupos (34 em `MERGED` vs. 31 em `CLOSED`), com δ de Cliff desprezível (+0,03). **Hipótese refutada.** O tamanho do PR, isoladamente, não prediz o desfecho.

**RQ02 — Tempo de análise × *feedback* final:** A mediana do tempo em `MERGED` (40,7 h) é aproximadamente **13 vezes menor** que em `CLOSED` (519,8 h). O δ de Cliff (−0,437) configura o efeito mais forte observado. **Hipótese corroborada.**

**RQ03 — Descrição × *feedback* final:** A mediana da descrição é maior em `CLOSED` (843 chars) do que em `MERGED` (698 chars), com efeito desprezível. **Hipótese refutada.** Descrições longas tendem a acompanhar PRs controversos.

**RQ04 — Interações × *feedback* final:** Comentários apresentam mediana maior em `CLOSED` (2 vs. 1), com efeito pequeno (δ = −0,155). Participantes não diferenciaram os grupos. **Hipótese parcialmente corroborada.**

**RQ05 — Tamanho × revisões:** LOC total apresenta ρ = 0,302 (moderada positiva). **Hipótese corroborada.** O tamanho não prediz o desfecho (RQ01), mas prediz o esforço de revisão.

**RQ06 — Tempo × revisões:** ρ = 0,110 (fraca positiva). **Hipótese corroborada com efeito fraco.** Um PR pode permanecer aberto sem novas revisões.

**RQ07 — Descrição × revisões:** ρ = 0,185 (fraca positiva, contrária à expectativa). **Hipótese refutada.** Descrições longas acompanham PRs complexos que demandam mais revisões.

**RQ08 — Interações × revisões:** ρ = 0,342 (participantes) e 0,330 (comentários), ambos moderada positiva. **Hipótese corroborada.**

### 10.2 Comparação cruzada (Dimensão A vs. Dimensão B)

| Categoria | δ Cliff (Dim. A) | ρ Spearman (Dim. B) | Leitura |
|-----------|-----------------|---------------------|---------|
| Tamanho (LOC) | +0,030 (desprezível) | +0,302 (moderada) | Não prediz desfecho; prediz esforço |
| Tempo | **−0,437 (médio)** | +0,110 (fraca) | Prediz desfecho mais que esforço |
| Descrição | −0,043 (desprezível) | +0,185 (fraca) | Pouca influência em ambas |
| Interações | −0,155 (pequeno) | +0,330 (moderada) | Mais comentários → `CLOSED` e mais revisões |

**Figura 9** — Cruzamento das duas dimensões: efeito no desfecho (δ) vs. efeito no esforço (ρ).
![Bubble chart](../output/lab3s3/charts_v2/12_bubble_delta_rho.png)

> **Interpretação da Figura 9:** Esta visualização inovadora posiciona cada métrica em um plano bidimensional, onde o eixo X representa o efeito sobre o desfecho (δ de Cliff) e o eixo Y o efeito sobre o esforço de revisão (ρ de Spearman). A leitura é imediata: o **tempo de análise** (canto inferior esquerdo) domina a Dimensão A, mas contribui pouco para a Dimensão B. Inversamente, **participantes** e **comentários** (parte superior central) são os melhores preditores do esforço, com impacto modesto no desfecho. As métricas de **tamanho** (LOC, adições) agrupam-se na região de alto ρ e δ próximo de zero, demonstrando que são preditoras de esforço, mas não de aceitação. A **descrição** permanece na zona de influência marginal em ambas as dimensões.

**Figura 10** — Matriz de correlação de Spearman entre todas as variáveis.
![Heatmap completo](../output/lab3s3/charts_v2/15_heatmap_completo.png)

> **Interpretação da Figura 10:** A matriz triangular revela dois blocos de alta correlação: (i) o bloco de tamanho, onde `additions`, `loc_total` e `changed_files` são altamente correlacionados entre si (ρ > 0,74), indicando redundância parcial entre essas métricas; e (ii) o bloco de interação, onde `participantes` e `comentários` apresentam ρ = 0,40. O tempo de análise, por sua vez, mostra correlação fraca com todas as demais variáveis (|ρ| < 0,10 com métricas de tamanho), reforçando sua natureza ortogonal às dimensões de escopo do PR. Essa independência é importante porque significa que a latência do PR captura informação complementar, não redundante, em relação às métricas de tamanho.

### 10.3 Limitações (ameaças à validade)

- ***Snapshot* temporal único** (30/04/2026): tendências do ecossistema podem mudar.
- **Viés de popularidade:** a amostragem dos 200 repositórios mais estrelados exclui projetos menores.
- **Heurística de 1 hora:** pode falhar em *bots* lentos ou PRs legítimos rápidos.
- **Subamostragem:** até 100 PRs validados por repositório para projetos de altíssimo volume.
- **Confundimento:** testes univariados não isolam efeitos cofundidos; análise multivariada é trabalho futuro.

### 10.4 Comparação com a literatura

- **Gousios, Pinzger e van Deursen (2014):** corroboramos parcialmente a importância do tempo; contestamos a centralidade da descrição.
- **Tsay, Dabbish e Herbsleb (2014):** corroboramos a importância dos fatores sociais (interações/comentários).
- **Yu *et al.* (2015):** corroboramos o efeito do tamanho sobre o esforço; contestamos a centralidade da descrição.
- **Kononenko, Baysal e Godfrey (2016):** complementamos o modelo misto (técnico + social) em escala agregada.

---

## 11. Conclusão e Recomendações

### 11.1 Decisões práticas

- **Para maximizar aceitação:** priorizar PRs que possam ser fechados rapidamente. A mediana de `MERGED` é 40,7 h contra 519,8 h dos `CLOSED`.
- **Para reduzir esforço de revisão:** manter PRs menores em LOC e reduzir ciclos de discussão.
- **Quanto à descrição:** boa prática, mas o ganho objetivo nas métricas agregadas é discreto.

### 11.2 Sugestões para trabalhos futuros

- Regressão logística para `status` e Binomial Negativa para `numero_reviews`.
- Segmentação por linguagem, domínio e maturidade do repositório.
- Inclusão de métricas de CI/CD (*checks*, presença de *bots*).
- Estudo longitudinal por repositório.

### 11.3 Resultado conclusivo

Em uma amostra de **14.347 PRs** distribuídos por **182 repositórios populares**, o **tempo de análise** mostrou-se o preditor mais forte do desfecho (δ = −0,44, efeito médio). Os melhores preditores do **esforço de revisão** são as **interações** (ρ ≈ 0,33) e o **tamanho** (ρ ≈ 0,30). O tamanho não prediz o desfecho, e a descrição apresenta influência apenas marginal em ambas as dimensões.

---

## 12. Reprodutibilidade

```bash
# 1. Coleta (≈90 min)
python scripts/coleta_graphql_PRs.py

# 2. Enriquecimento (≈25 min)
python scripts/enriquecer_participantes.py

# 3. Análise estatística
python scripts/analise_sprint3.py

# 4. Gráficos aprimorados
python scripts/graficos_aprimorados.py
```

**Dados:** `output/lab3s2/pull_requests_com_reviews.csv`  
**Resultados:** `output/lab3s3/`  
**Gráficos:** `output/lab3s3/charts_v2/`

---

## 13. Painel Resumo

**Figura 11** — Dashboard consolidado dos achados do estudo.
![Dashboard resumo](../output/lab3s3/charts_v2/13_dashboard_resumo.png)

> **Interpretação da Figura 11:** O painel superior esquerdo evidencia o balanceamento razoável entre os grupos (67,8% MERGED, 32,2% CLOSED), garantindo que as comparações não são enviesadas por desproporção amostral. O painel superior direito destaca o achado mais forte do estudo: a mediana de tempo em `CLOSED` (520 h) é 12,8× maior que em `MERGED` (41 h). Os painéis inferiores sintetizam, respectivamente, o *ranking* de efeitos da Dimensão A (onde o tempo domina) e da Dimensão B (onde interações e tamanho lideram).

**Figura 12** — Distribuições comparativas por status para todas as métricas.
![Painel violin](../output/lab3s3/charts_v2/16_painel_violin_status.png)

> **Interpretação da Figura 12:** O painel de oito violinos permite uma comparação visual rápida de todas as métricas simultaneamente. Nota-se que a maioria das métricas apresenta distribuições muito similares entre `MERGED` e `CLOSED` (violinos quase idênticos), exceto pelo tempo de análise, onde a diferença é evidente. Essa homogeneidade nas demais variáveis é consistente com os efeitos desprezíveis reportados na Tabela da Dimensão A, e reforça que o tempo de análise é a variável com maior poder discriminante.

**Figura 13** — Medianas MERGED vs. CLOSED para métricas selecionadas.
![Medianas IC](../output/lab3s3/charts_v2/11_mediana_ic_barras.png)

> **Interpretação da Figura 13:** A comparação direta das medianas em escala logarítmica destaca a discrepância do tempo de análise e a similaridade das demais métricas entre os dois grupos. Enquanto o tempo apresenta diferença visual evidente (barras de alturas muito distintas), LOC total, comentários e descrição mostram barras de magnitude comparável, confirmando que essas variáveis não são bons discriminantes do desfecho final.

---

## Referências

- GOUSIOS, G.; PINZGER, M.; VAN DEURSEN, A. An Exploratory Study of the Pull-based Software Development Model. In: *ICSE*, 2014. DOI: 10.1145/2568225.2568260.
- TSAY, J.; DABBISH, L.; HERBSLEB, J. Influence of Social and Technical Factors for Evaluating Contribution in GitHub. In: *ICSE*, 2014. DOI: 10.1145/2568225.2568315.
- YU, Y.; WANG, H.; FILKOV, V.; DEVANBU, P.; VASILESCU, B. Wait for It: Determinants of Pull Request Evaluation Latency on GitHub. In: *MSR*, 2015. DOI: 10.1109/MSR.2015.42.
- KONONENKO, O.; BAYSAL, O.; GODFREY, M. W. Code Review Quality: How Developers See It. In: *ICSE*, 2016. DOI: 10.1145/2884781.2884840.
