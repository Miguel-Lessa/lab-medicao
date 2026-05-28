# Lab04S03 - Dashboard Interativo com Dados Abertos Governamentais

> **Relatorio completo (template do laboratorio + figuras):** veja
> [`relatorios/relatorio_lab04_final.md`](relatorios/relatorio_lab04_final.md)

---

# Versao resumida (legado)

## 1. Introducao

Business Intelligence apoia a tomada de decisao ao transformar dados brutos em
visualizacoes claras, exploraveis e atualizadas. Neste laboratorio, o objetivo foi
construir um dashboard interativo utilizando dados publicos governamentais,
permitindo analisar despesas parlamentares de forma transparente e reprodutivel.

Como alternativa ao uso de uma ferramenta proprietaria de BI, a entrega foi
implementada em Python com Streamlit e Plotly. Essa escolha permite que a coleta,
o tratamento e a visualizacao dos dados sejam versionados junto com o restante do
projeto.

## 2. Metodologia e Descricao da Base

A base utilizada foi a Cota para Exercicio da Atividade Parlamentar (CEAP),
disponibilizada pela Camara dos Deputados no portal de Dados Abertos. Os arquivos
sao publicados por ano e contem registros de despesas ressarcidas a deputados
federais.

O recorte definido para a Sprint 03 contempla os anos de 2020 a 2025. Os dados
foram coletados em formato CSV compactado, extraidos localmente e tratados com
Python. O tratamento padroniza nomes de colunas, converte datas, transforma
valores monetarios em numeros decimais e cria campos auxiliares de ano, mes,
ano-mes e data de referencia. As visualizacoes temporais usam o ano e mes de
competencia da CEAP, pois a data de emissao do documento pode ser anterior ou
posterior ao periodo de ressarcimento.

Os principais campos analisados foram:

| Campo | Descricao |
|---|---|
| deputado | Nome do parlamentar |
| partido | Sigla partidaria |
| uf | Unidade federativa do parlamentar |
| tipo_despesa | Categoria da despesa declarada |
| fornecedor | Empresa ou pessoa fornecedora |
| data_referencia | Primeiro dia do mes de competencia da despesa |
| data_emissao | Data de emissao do documento |
| valor_liquido | Valor efetivamente considerado na analise |
| ano | Ano da despesa |
| mes | Mes da despesa |

## 3. Resultados

### Caracterizacao do Dataset

A primeira pagina do dashboard apresenta uma visao geral da base, incluindo total
de registros, valor total, quantidade de deputados, partidos, UFs e fornecedores.
Tambem sao exibidos graficos de valor por tipo de despesa e evolucao mensal dos
gastos.

No recorte de competencia 2020-2025, a base tratada possui 1.271.817 registros,
R$ 1.389.844.978,70 em valor liquido, 927 nomes parlamentares ou estruturas
parlamentares, 27 partidos, 28 UFs/categorias territoriais e 67.783
fornecedores distintos.

Essa caracterizacao permite entender a cobertura do dataset antes da analise das
questoes de pesquisa. Ela tambem evidencia quais categorias concentram maior
volume financeiro e como as despesas se distribuem ao longo do periodo analisado.

### RQ1: Quais tipos de despesa concentram mais gastos parlamentares?

A primeira questao de pesquisa e respondida por graficos de ranking, participacao
percentual e evolucao mensal dos principais tipos de despesa. O objetivo e
identificar quais categorias representam maior impacto financeiro dentro da CEAP.

Essa analise ajuda a diferenciar categorias recorrentes e de baixo valor agregado
de categorias que concentram grande parte dos recursos. O uso de graficos
interativos permite filtrar por ano, partido, UF e parlamentar.

Na base analisada, as maiores categorias por valor liquido foram divulgacao da
atividade parlamentar, passagem aerea, locacao ou fretamento de veiculos,
manutencao de escritorio de apoio e combustiveis/lubrificantes.

### RQ2: Como os gastos variam por partido e UF?

A segunda questao compara os valores por partido e unidade federativa. O dashboard
apresenta barras por partido, barras por UF e uma matriz partido x tipo de
despesa.

Essa visualizacao permite observar diferencas de composicao de gastos entre
grupos politicos e regioes. A matriz tambem facilita identificar se determinados
tipos de despesa aparecem de forma mais concentrada em alguns partidos.

Os maiores valores agregados por partido aparecem em PL, PT, Uniao, PP e PSD. Por
UF, os maiores totais aparecem em SP, MG, RJ, BA e RS.

### RQ3: Quais deputados e fornecedores concentram os maiores valores?

A terceira questao apresenta rankings de deputados e fornecedores por valor
liquidado. Tambem ha uma tabela detalhada, ordenada por valor, para inspecao dos
registros individuais.

Essa parte do dashboard e importante para transparencia e auditoria exploratoria,
pois permite localizar rapidamente os maiores concentradores de despesa dentro do
recorte analisado.

## 4. Discussao

O dashboard produzido atende ao objetivo do laboratorio por apresentar uma base
publica em formato interativo e autoexplicativo. A organizacao por abas separa a
caracterizacao do dataset das questoes de pesquisa, mantendo a narrativa dos dados
clara.

Uma limitacao importante e que a analise considera os valores registrados na CEAP
sem inferir irregularidades. Gastos maiores podem decorrer de fatores legitimos,
como tamanho da UF, intensidade da atividade parlamentar, deslocamentos e regras
administrativas. Portanto, os resultados devem ser interpretados como indicadores
descritivos.

Como melhoria futura, o dashboard poderia cruzar os dados da CEAP com informacoes
adicionais da Camara, como legislatura, presenca em eventos, autoria de
proposicoes e votacoes. Isso permitiria analises mais completas sobre relacao
entre atividade parlamentar e uso da cota.
