# Relatorio LAB05 - GraphQL vs REST

## Hipoteses

- RQ1 H0: o tempo medio do GraphQL e igual ao tempo medio do REST.

- RQ1 H1 unicaudal: o tempo medio do GraphQL e menor que o tempo medio do REST.

- RQ2 H0: o tamanho medio do GraphQL e igual ao tamanho medio do REST.

- RQ2 H1 unicaudal: o tamanho medio do GraphQL e menor que o tamanho medio do REST.

- Nivel de significancia: 0.05.

## Metodologia

A variavel independente e a tecnologia de API, com tratamentos REST e GraphQL. As variaveis dependentes sao tempo_ms e tamanho_bytes. O objeto experimental e a requisicao de dados de um jogador existente. O desenho e pareado: cada ID sorteado e submetido aos dois tratamentos na mesma iteracao. A coleta oficial planeja 1000 iteracoes por tratamento, totalizando 2000 registros planejados.

## Estatisticas Descritivas

```text
           tempo_ms                                          tamanho_bytes                                  
              count    mean  median     std     min      max         count     mean median     std  min  max
tecnologia                                                                                                  
GraphQL        1000  1.0388  0.9906  0.1968  0.7729   2.5807          1000   54.214   54.0  1.9570   50   59
REST           1000  0.8015  0.7564  0.4633  0.6173  14.9072          1000  326.236  326.0  2.7936  320  333
```

## RQ1
- Metrica: tempo_ms
- Mediana REST: 0.7564
- Mediana GraphQL: 0.9907
- Diferenca das medianas (REST - GraphQL): -0.2343
- Reducao percentual: -30.97%
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

## Ameacas a Validade

- Interna: cache, ordem de execucao, carga do computador e aquecimento do runtime podem afetar tempos.

- Externa: a base e ficticia e em memoria, portanto os resultados nao generalizam diretamente para APIs reais com banco externo.

- Construcao: tempo de resposta e tamanho de payload capturam apenas parte dos custos de adocao de GraphQL ou REST.

- Conclusao: amostras com muitas falhas ou baixa variabilidade reduzem o poder dos testes estatisticos.
