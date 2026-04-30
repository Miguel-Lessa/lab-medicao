# Resumo das RQs - Lab 03

- Total de PRs: **14347**
- MERGED: **9728** | CLOSED: **4619**
- Repositorios distintos: **182**
- alpha = 0.05 (Holm step-down aplicado)

## Dimensao A - Feedback final (MERGED vs CLOSED)

| RQ | Metrica | Mediana MERGED | Mediana CLOSED | p-valor | p-Holm | Cliff delta | Efeito |
|----|---------|---------------:|---------------:|--------:|-------:|------------:|--------|
| RQ01 | Arquivos alterados | 2.0 | 2.0 | 0 | 0 | 0.1063 | desprezivel |
| RQ01 | Linhas adicionadas | 22.0 | 23.0 | 0.788 | 0.788 | 0.0028 | desprezivel |
| RQ01 | Linhas removidas | 4.0 | 2.0 | 0 | 0 | 0.1711 | pequeno |
| RQ01 | LOC total (add+del) | 34.0 | 31.0 | 0.00348 | 0.00696 | 0.0301 | desprezivel |
| RQ02 | Tempo de analise (h) | 40.7326 | 519.8089 | 0 | 0 | -0.4367 | medio |
| RQ03 | Tamanho da descricao (chars) | 698.0 | 843.0 | 3e-05 | 9e-05 | -0.0431 | desprezivel |
| RQ04 | Numero de participantes | 3.0 | 3.0 | 0 | 0 | -0.0827 | desprezivel |
| RQ04 | Total de comentarios | 1.0 | 2.0 | 0 | 0 | -0.1547 | pequeno |

## Dimensao B - Numero de revisoes

| RQ | Metrica | n | Spearman rho | p-valor | p-Holm | IC95 rho | Interpretacao |
|----|---------|--:|-------------:|--------:|-------:|----------|---------------|
| RQ05 | Arquivos alterados | 14347 | 0.27 | 0 | 0 | [0.254, 0.2846] | fraca positiva |
| RQ05 | Linhas adicionadas | 14347 | 0.3146 | 0 | 0 | [0.3002, 0.3294] | moderada positiva |
| RQ05 | Linhas removidas | 14347 | 0.1833 | 0 | 0 | [0.1676, 0.1998] | fraca positiva |
| RQ05 | LOC total (add+del) | 14347 | 0.3018 | 0 | 0 | [0.2868, 0.3163] | moderada positiva |
| RQ06 | Tempo de analise (h) | 14347 | 0.1103 | 0 | 0 | [0.0941, 0.1264] | fraca positiva |
| RQ07 | Tamanho da descricao (chars) | 14347 | 0.1852 | 0 | 0 | [0.1688, 0.2019] | fraca positiva |
| RQ08 | Numero de participantes | 14347 | 0.3415 | 0 | 0 | [0.3266, 0.3557] | moderada positiva |
| RQ08 | Total de comentarios | 14347 | 0.3296 | 0 | 0 | [0.3149, 0.3439] | moderada positiva |