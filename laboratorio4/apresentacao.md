# Apresentação em sala — Lab 04 | Dashboard CEAP

Roteiro para demonstrar o dashboard Streamlit ao professor e à turma.  
**Tempo sugerido:** 5–7 minutos + perguntas.

**Como abrir antes da aula:**

```bash
cd /caminho/para/lab-medicao
source .venv/bin/activate
python -m streamlit run laboratorio4/app/dashboard.py
```

URL: **http://localhost:8501**

---

## Abertura (30 segundos)

> “Nosso trabalho analisa a **CEAP** — Cota para Exercício da Atividade Parlamentar — da Câmara dos Deputados, com dados abertos de **2020 a 2025**.  
> Montamos um **pipeline reprodutível** em Python: coleta, tratamento e este **dashboard** com Plotly/Streamlit.  
> O foco são **três perguntas**: onde concentram os gastos, como variam por partido e UF, e quem são os maiores valores por deputado e fornecedor.  
> A análise é **descritiva** — mostramos padrões nos dados, sem afirmar irregularidade.”

**Números-chave (decorar):**

| Indicador | Valor |
|-----------|------:|
| Lançamentos | 1.271.817 |
| Valor líquido total | R$ 1,39 bilhão |
| Período | 2020–2025 |
| Top 2 categorias | Divulgação (~34%) + passagens (~18%) |

---

## Aba 1 — Dataset (caracterização)

*“Antes das perguntas de pesquisa, caracterizamos a base.”*

### Gráfico 1 — Valor líquido total por ano

**O que é:** barras com a soma anual do valor líquido (competência da despesa).

**O que dizer:** “O volume **cresce** de cerca de R$ 176 milhões em 2020 para ~R$ 264 milhões em 2024. Isso mostra que estamos analisando um período de **alta movimentação** da cota.”

---

### Gráfico 2 — Quantidade de lançamentos por ano

**O que é:** número de registros (notas/linhas) por ano.

**O que dizer:** “Não é só valor que sobe: há entre **166 mil e 237 mil lançamentos** por ano — base grande e estável para análise.”

---

### Gráfico 3 — Deputados distintos por ano

**O que é:** quantos nomes distintos aparecem cada ano (inclui trocas e estruturas como liderança).

**O que dizer:** “Entre **554 e 800** nomes por ano — o total acumulado de 927 no período inclui mandatos e cadastros diferentes.”

---

### Gráfico 4 — Evolução mensal do valor liquidado

**O que é:** linha do tempo mês a mês da soma de gastos.

**O que dizer:** “Vemos **sazonalidade** e picos pontuais; dá para discutir em trabalhos futuros com eventos do calendário legislativo.”

---

### Gráfico 5 — Distribuição dos valores por lançamento

**O que é:** histograma dos valores de cada nota (eixo limitado ao P99 para leitura).

**O que dizer:** “A **mediana** por lançamento é ~R$ 259, mas a **média** é ~R$ 1.131 — muitos lançamentos pequenos e poucos muito grandes. Distribuição **assimétrica**.”

---

### Gráfico 6 — Valor total por tipo de despesa (top 15)

**O que é:** ranking horizontal das categorias que mais pesam no total.

**O que dizer:** “Antecipa a RQ1: **divulgação**, **passagens**, **veículos** e **escritório** dominam antes mesmo do Pareto.”

**KPIs no topo da aba:** citar registros, valor total, partidos, UFs — “caracterização completa do dataset, como pede o enunciado.”

---

## Aba 2 — RQ1: Tipos de despesa

*“Quais tipos concentram mais gastos?”*

### Gráfico 7 — Diagrama de Pareto

**O que é:** barras = valor por tipo; linha = % acumulado.

**O que dizer:** “**Poucas rubricas explicam quase tudo.** Quando a linha passa de 80%, são só alguns tipos — padrão de concentração clássico. Top 5 categorias ≈ **86%** do total.”

---

### Gráfico 8 — Pizza (top 7 + Outros)

**O que é:** participação percentual com fatia “Outros” fechando 100%.

**O que dizer:** “Complementa o Pareto de forma visual para o público — divulgação sozinha é ~**um terço** do gasto.”

---

### Gráfico 9 — Ranking dos tipos (top 12)

**O que é:** barras horizontais ordenadas por valor.

**O que dizer:** “Mesma informação do Pareto, em formato de ranking direto — útil para citar valores no relatório.”

---

### Gráfico 10 — Evolução mensal dos top 5 tipos

**O que é:** cinco linhas, uma por principal categoria, ao longo dos meses.

**O que dizer:** “Mostra se a concentração é **estável** ou se alguma rubrica cresceu mais no fim do período — passagens vs. divulgação, por exemplo.”

---

## Aba 3 — RQ2: Partido e UF

*“Como os gastos variam entre partidos e estados?”*

**Destaque metodológico (importante para o professor):**

> “Comparamos **soma total** e **mediana por deputado**. Soma favorece partido grande; mediana compara o parlamentar típico.”

---

### Gráfico 11 — Soma total por partido

**O que é:** volume bruto por sigla (top 20).

**O que dizer:** “**PL, PT e União** lideram — mas isso reflete **tamanho da bancada**, não necessariamente que cada deputado gaste mais.”

---

### Gráfico 12 — Mediana do gasto por deputado, por partido

**O que é:** para cada partido, mediana da soma individual de cada deputado.

**O que dizer:** “Aqui a história **muda**: **PRD e PCdoB** sobem no ranking; PL não lidera. É a métrica **mais justa** para comparar legendas.”

---

### Gráfico 13 — Soma total por UF

**O que é:** gasto agregado por estado do parlamentar.

**O que dizer:** “**SP, MG e RJ** lideram — estados com mais deputados e maior volume absoluto.”

---

### Gráfico 14 — Mediana por deputado, por UF

**O que é:** mediana da soma por deputado dentro de cada UF.

**O que dizer:** “**BA** e estados menores podem aparecer no topo — comparar só por soma estadual **engana**.”

---

### Gráfico 15 — Boxplot por partido

**O que é:** caixas com dispersão do gasto de cada deputado nos 10 partidos com maior mediana.

**O que dizer:** “Dois partidos com mediana parecida podem ter **desigualdade interna** diferente — uns poucos deputados puxam o total para cima (outliers).”

---

### Gráfico 16 — Heatmap (% por partido)

**O que é:** cada linha é um partido; cores = % do gasto daquele partido em cada tipo (linha soma 100%).

**O que dizer:** “Não é ‘quem gasta mais’, e sim **com o que gasta**: perfil de divulgação vs. passagem vs. escritório **muda por legenda**.”

**Filtros laterais:** demonstrar filtrar um **ano** ou **partido** — “dashboard interativo e autoexplicativo.”

---

## Aba 4 — RQ3: Deputados e fornecedores

*“Quem concentra os maiores valores?”*

### Gráfico 17 — Top deputados

**O que é:** ranking dos 15 parlamentares com maior soma no período (opção de excluir lideranças no filtro).

**O que dizer:** “Valores na faixa de **~R$ 3,3 a 3,5 milhões em 6 anos** — mandato longo e deslocamento explicam parte disso. **Não é ranking de culpa**, é transparência.”

---

### Gráfico 18 — Top fornecedores

**O que é:** quem mais recebeu recursos da CEAP no agregado.

**O que dizer:** “**TAM, GOL e AZUL** dominam — fecha o ciclo com a RQ1: o dinheiro vai para **passagens aéreas**. Coerente e esperado.”

**Tabela top 500:** “Permite auditar lançamentos individuais; exportamos CSV pelo próprio dashboard.”

---

## Encerramento (30 segundos)

> “Resumindo: a CEAP entre 2020 e 2025 concentra-se em **poucas categorias**; comparar partidos exige **mediana por deputado**; fornecedores aéreos captam a maior fatia.  
> Entregamos **dashboard**, **scripts reprodutíveis**, **relatório** e figuras exportáveis.  
> Limitação: análise **descritiva**, sem cruzar mandato, distância da capital ou presença parlamentar — sugestão para trabalho futuro.”

---

## Perguntas que o professor pode fazer

| Pergunta | Resposta curta |
|----------|----------------|
| Por que não Power BI? | Trabalho alternativo; Python versiona coleta + dashboard no Git. |
| Por que mediana e não média? | Média sofre com outliers; mediana representa o deputado “do meio”. |
| Por que não subiram os CSV no Git? | ~205 MB gerados; reproduz com `coleta` + `prepara`. |
| Gasto alto = irregularidade? | Não; CEAP cobre deslocamento, divulgação e escritório. |
| Fonte dos dados? | [dadosabertos.camara.leg.br](https://dadosabertos.camara.leg.br/) — arquivos `Ano-YYYY.csv.zip`. |

---

## Checklist antes de apresentar

- [ ] `despesas_ceap_tratadas.csv` gerado (`prepara_dados.py`)
- [ ] Dashboard abre em `localhost:8501`
- [ ] Internet estável (se for rodar coleta ao vivo — **não recomendado** em sala)
- [ ] Filtros laterais testados (ano, partido)
- [ ] Relatório PDF e este roteiro à mão

---

## Mapa rápido: aba → RQ do enunciado

| Aba do dashboard | Entrega Lab04 |
|------------------|---------------|
| Dataset | Caracterização (Sprint 01 + enunciado) |
| RQ1 | Pergunta 1 + métricas de concentração |
| RQ2 | Pergunta 2 + comparação partido/UF |
| RQ3 | Pergunta 3 + transparência |

*Boa apresentação.*
