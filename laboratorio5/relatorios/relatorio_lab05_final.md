# Relatorio LAB05 - GraphQL vs REST

## Introducao

Este experimento controlado compara uma API REST e uma API GraphQL que expoem a mesma base ficticia de estatisticas de futebol. A motivacao e avaliar, de forma quantitativa, se a flexibilidade do GraphQL traz beneficios mensuraveis sobre uma API REST equivalente em duas dimensoes: tempo de resposta e tamanho do payload retornado.

## Hipoteses

- RQ1 H0: o tempo medio do GraphQL e igual ao tempo medio do REST.

- RQ1 H1 unicaudal: o tempo medio do GraphQL e menor que o tempo medio do REST.

- RQ2 H0: o tamanho medio do GraphQL e igual ao tamanho medio do REST.

- RQ2 H1 unicaudal: o tamanho medio do GraphQL e menor que o tamanho medio do REST.

- Nivel de significancia: 0.05.

## Metodologia

A variavel independente e a tecnologia de API, com tratamentos REST e GraphQL. As variaveis dependentes sao tempo_ms e tamanho_bytes. O objeto experimental e a requisicao de dados de um jogador existente. O desenho e pareado: cada ID sorteado e submetido aos dois tratamentos na mesma iteracao. A coleta oficial planeja 1000 iteracoes por tratamento, totalizando 2000 registros planejados.

## Ambiente de Execucao

Para aumentar a reprodutibilidade, o experimento foi preparado para execucao em ambiente controlado com Docker. A configuracao adicionada usa a imagem base `node:20-bookworm`, instala Python 3 e as dependencias pinadas de `requirements.txt`, sobe a API na porta 4000, aguarda a disponibilidade do endpoint REST e entao executa a validacao, a coleta oficial, a analise estatistica e a geracao das figuras. A execucao recomendada e `docker compose up --build`, preservando `output/` e `relatorios/` como volumes. As metricas atuais foram regeneradas por esse fluxo, com 2000 registros validos e 0 falhas. Esse procedimento reduz diferencas de versao entre maquinas e torna mais claro o ambiente usado para gerar as metricas.

## Estatisticas Descritivas

```text
           tempo_ms                                          tamanho_bytes                                  
              count    mean  median     std     min      max         count     mean median     std  min  max
tecnologia                                                                                                  
GraphQL        1000  1.7641  1.5131  1.1198  0.8339  19.2746          1000   54.272   54.0  2.0000   50   59
REST           1000  1.2227  1.0699  0.6051  0.6342   9.0806          1000  326.236  326.0  2.8111  320  333
```

## RQ1
- Metrica: tempo_ms
- Mediana REST: 1.0699
- Mediana GraphQL: 1.5131
- Diferenca das medianas (REST - GraphQL): -0.4432
- Reducao percentual: -41.43%
- Valor-p: 1.000000
- Decisao: nao rejeitar a hipotese nula ao nivel de 0,05.

## RQ2
- Metrica: tamanho_bytes
- Mediana REST: 326.0000
- Mediana GraphQL: 54.0000
- Diferenca das medianas (REST - GraphQL): 272.0000
- Reducao percentual: 83.44%
- Valor-p: 0.000000
- Decisao: rejeitar a hipotese nula ao nivel de 0,05.

## Discussao Final

Os resultados nao sustentam a hipotese de que GraphQL foi mais rapido neste cenario: a mediana de tempo do GraphQL ficou maior que a do REST e, por isso, a hipotese nula de RQ1 nao foi rejeitada. Para RQ2, os resultados indicam uma vantagem clara do GraphQL em tamanho de resposta, pois a consulta selecionou apenas os campos `nome` e `gols`, enquanto o endpoint REST retornou o objeto completo do jogador. Assim, a principal evidencia observada neste experimento e que GraphQL reduziu substancialmente o payload, mas nao melhorou o tempo de resposta no ambiente medido.

## Ameacas a Validade

- Interna: cache, ordem de execucao, carga do computador e aquecimento do runtime podem afetar tempos.

- Externa: a base e ficticia e em memoria, portanto os resultados nao generalizam diretamente para APIs reais com banco externo.

- Construcao: tempo de resposta e tamanho de payload capturam apenas parte dos custos de adocao de GraphQL ou REST.

- Conclusao: amostras com muitas falhas ou baixa variabilidade reduzem o poder dos testes estatisticos.
