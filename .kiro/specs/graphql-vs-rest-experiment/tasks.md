# Implementation Plan: GraphQL vs REST Experiment (LAB05)

## Overview

O plano converte o desenho do experimento em passos incrementais de código. A camada de servidor é implementada em **Node.js** (Express + Apollo Server, testes de propriedade com `fast-check`); a camada de medição, análise e dashboard é implementada em **Python** (testes de propriedade com `hypothesis` + `pytest`). Cada tarefa constrói sobre as anteriores e termina conectando os componentes, sem código órfão. As propriedades de corretude do design (P1–P13) são implementadas como sub-tarefas de teste, cada uma referenciando a propriedade e os requisitos que valida.

## Tasks

- [x] 1. Configurar estrutura do projeto e dependências
  - [x] 1.1 Inicializar o projeto Node.js do servidor unificado
    - Criar `package.json` e a estrutura `src/` (`database`, `restApi`, `graphqlApi`, `server`)
    - Instalar dependências: `express`, `@apollo/server`, `graphql`, `cors`
    - Instalar dependências de teste: `fast-check` e o runner (`jest` ou `vitest`)
    - _Requirements: 6.1, 6.2_

  - [x] 1.2 Inicializar o projeto Python de medição, análise e dashboard
    - Criar `requirements.txt`/`pyproject` e a estrutura `scripts/`
    - Instalar dependências: `requests` (ou `httpx`), `pandas`, `scipy`, `numpy`, `matplotlib`, `seaborn`
    - Instalar dependências de teste: `hypothesis` e `pytest`
    - _Requirements: 7.1, 11.1_

- [x] 2. Implementar a base de dados em memória
  - [x] 2.1 Implementar `buildDatabase`, `getPlayerById` e `getPlayerCount`
    - Gerar >= 2 Ligas, >= 5 Times e >= 50 Jogadores, com IDs de Jogador contíguos de 1..N
    - Atribuir a cada Jogador >= 10 atributos estatísticos numéricos e não negativos
    - Garantir integridade referencial (Time -> Liga existente, Jogador -> Time existente)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x]* 2.2 Escrever teste de propriedade da integridade estrutural da base
    - **Property 1: Integridade estrutural da base de dados**
    - **Validates: Requirements 3.1, 3.2, 3.4, 3.7**
    - Usar `fast-check`, mínimo de 100 iterações

  - [x]* 2.3 Escrever teste de propriedade dos atributos estatísticos dos Jogadores
    - **Property 2: Atributos estatísticos dos Jogadores**
    - **Validates: Requirements 3.5, 3.6, 3.3**
    - Usar `fast-check`, mínimo de 100 iterações

- [x] 3. Implementar a API REST
  - [x] 3.1 Implementar o handler `GET /rest/players/:id`
    - Retornar 200 + Jogador completo (id, nome, todos os atributos) em JSON para ID existente
    - Retornar 404 + mensagem de erro (sem dados de Jogador) para ID inteiro fora de [1, N]
    - Retornar 400 + mensagem de erro (sem dados de Jogador) para ID em formato inválido
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x]* 3.2 Escrever teste de propriedade do retorno completo do REST
    - **Property 3: REST retorna o Jogador completo para identificador existente**
    - **Validates: Requirements 4.1, 4.2**
    - Usar `fast-check`, mínimo de 100 iterações

  - [x]* 3.3 Escrever teste de propriedade de erro do REST
    - **Property 4: REST sinaliza erro sem dados de Jogador para identificadores não atendíveis**
    - **Validates: Requirements 4.3, 4.4**
    - Usar `fast-check`, mínimo de 100 iterações

  - [x]* 3.4 Escrever teste de exemplo do formato JSON das respostas
    - Verificar `Content-Type: application/json` em respostas de sucesso e de erro
    - _Requirements: 4.5_

- [x] 4. Implementar a API GraphQL
  - [x] 4.1 Implementar o schema e os resolvers (`player`, `league`, `team`)
    - Schema descreve Liga, Time e Jogador com >= 10 atributos e consulta `player(id)`
    - Resolver `player` retorna apenas os campos solicitados; ID inexistente -> `player` nulo + `errors`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x]* 4.2 Escrever teste de propriedade da seleção de campos do GraphQL
    - **Property 5: GraphQL retorna exclusivamente os campos solicitados**
    - **Validates: Requirements 5.1, 5.2**
    - Usar `fast-check`, mínimo de 100 iterações

  - [x]* 4.3 Escrever teste de propriedade do Jogador inexistente no GraphQL
    - **Property 6: GraphQL retorna Jogador nulo e erro para identificador inexistente**
    - **Validates: Requirements 5.3**
    - Usar `fast-check`, mínimo de 100 iterações

  - [x]* 4.4 Escrever testes de exemplo e introspecção do schema
    - Caso dedicado: consulta `player { nome gols }` retorna exatamente esses dois campos
    - Introspecção: entidades Liga/Time/Jogador, >= 10 atributos e consulta `player(id)`
    - _Requirements: 5.2, 5.4, 5.5_

- [x] 5. Implementar o servidor unificado
  - [x] 5.1 Implementar `startServer` montando REST + GraphQL na porta 4000
    - Montar Express + Apollo no mesmo processo; habilitar CORS para GET e POST
    - Registrar log de disponibilidade na porta 4000; tratar `EADDRINUSE` com erro descritivo + saída
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x]* 5.2 Escrever testes de integração e smoke do servidor
    - Health check: `GET /rest/players/:id` (200) e `POST /graphql` (sem `errors`)
    - Verificar cabeçalhos CORS para GET/POST, log de disponibilidade e tratamento de porta ocupada
    - _Requirements: 9.1, 6.1, 6.3, 6.4, 6.5_

- [x] 6. Checkpoint - Garantir que os testes do servidor passam
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implementar o script de medição (Python)
  - [x] 7.1 Implementar `measure_request` e `is_failure`
    - `measure_request`: medir `tempo_ms` (envio -> corpo completo) e `tamanho_bytes`, timeout de 30000 ms
    - `is_failure`: erro de conexão, timeout, status >= 400 ou corpo com campo de erro
    - _Requirements: 7.3, 7.4, 7.6, 7.7_

  - [x]* 7.2 Escrever teste de propriedade da classificação de falha
    - **Property 9: Classificação de falha de requisição**
    - **Validates: Requirements 7.7, 7.6**
    - Usar `hypothesis`, mínimo de 100 iterações

  - [x] 7.3 Implementar `run_experiment` com iteração pareada
    - Sortear `id = randint(1, N)` por iteração e aplicar o mesmo ID a REST e GraphQL
    - GraphQL solicita apenas `nome` e `gols`; descartar medições falhas e prosseguir
    - _Requirements: 7.1, 7.2, 7.5, 1.5_

  - [x]* 7.4 Escrever teste de propriedade do pareamento de identificador
    - **Property 7: Iteração pareada usa o mesmo identificador em ambos os tratamentos**
    - **Validates: Requirements 1.5, 7.5**
    - Usar `hypothesis`, mínimo de 100 iterações

  - [x]* 7.5 Escrever teste de propriedade do domínio do identificador sorteado
    - **Property 8: Identificador sorteado pertence ao domínio válido**
    - **Validates: Requirements 7.2**
    - Usar `hypothesis`, mínimo de 100 iterações

- [x] 8. Implementar o armazenamento de resultados
  - [x] 8.1 Implementar `ResultsWriter` e `load_results`
    - Escrever cabeçalho único e registros nas colunas `tecnologia`, `tempo_ms`, `tamanho_bytes` (nesta ordem)
    - Em falha de gravação de um registro, registrar a ocorrência, preservar os já gravados e prosseguir
    - `load_results` lê o CSV com Pandas
    - _Requirements: 8.1, 8.2, 8.3, 8.5, 11.1_

  - [x]* 8.2 Escrever teste de propriedade do round-trip do arquivo de resultados
    - **Property 10: Round-trip do arquivo de resultados**
    - **Validates: Requirements 8.1, 8.2, 8.3**
    - Usar `hypothesis`, mínimo de 100 iterações

  - [x]* 8.3 Escrever testes de exemplo das contagens de execução
    - 1000 iterações oficiais geram entre 1800 e 2000 registros válidos (taxa de falha mockada)
    - _Requirements: 8.4, 7.1_

- [x] 9. Implementar a verificação do ambiente e validação prévia
  - [x] 9.1 Implementar o modo de validação do script
    - Executar 10 iterações gerando ~20 registros; sem falhas -> habilita a coleta oficial
    - Com >= 1 falha -> interromper antes da coleta oficial com mensagem descritiva
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x]* 9.2 Escrever teste de propriedade da habilitação da coleta oficial
    - **Property 13: Habilitação da coleta oficial após a validação**
    - **Validates: Requirements 9.4, 9.5**
    - Usar `hypothesis`, mínimo de 100 iterações

- [x] 10. Checkpoint - Garantir que medição e validação passam
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implementar a análise estatística e o relatório
  - [x] 11.1 Implementar `descriptive_stats`, `compare_treatments` e a regra `reject_null`
    - Estatísticas por tratamento: count, média, mediana, desvio padrão, min, max
    - Comparar tempo (RQ1) e tamanho (RQ2): diferença de medianas, redução percentual, teste unicaudal e decisão
    - Rejeitar H0 se, e somente se, valor-p < 0,05
    - _Requirements: 10.1, 10.2, 10.3, 2.5_

  - [x]* 11.2 Escrever teste de propriedade da corretude das estatísticas descritivas
    - **Property 11: Corretude das estatísticas descritivas**
    - **Validates: Requirements 10.1, 10.2, 10.3**
    - Usar `hypothesis`, mínimo de 100 iterações

  - [x]* 11.3 Escrever teste de propriedade da decisão das hipóteses
    - **Property 12: Decisão das hipóteses pelo nível de significância**
    - **Validates: Requirements 2.5**
    - Usar `hypothesis`, mínimo de 100 iterações

  - [x] 11.4 Implementar `generate_report`
    - Apresentar hipóteses, metodologia, resultados e a decisão explícita de H0 para RQ1 e RQ2
    - Documentar ameaças à validade (interna, externa, de construção, de conclusão) e a ausência de dados quando aplicável
    - Documentar o desenho experimental (variáveis, tratamentos, objeto, pareamento, 2000 registros planejados)
    - _Requirements: 10.4, 10.5, 10.6, 2.1, 2.2, 2.3, 2.4, 1.1, 1.2, 1.3, 1.4, 1.6_

- [x] 12. Implementar o dashboard de visualização
  - [x] 12.1 Implementar `render_dashboard`
    - Ler `results.csv` com Pandas; gráfico comparativo de `tempo_ms` e de `tamanho_bytes` (ambos os tratamentos no mesmo gráfico) com Matplotlib/Seaborn
    - Exibir tabela de estatísticas (média, mediana, desvio padrão) por tratamento
    - CSV ausente/ilegível -> mensagem de erro sem gráficos; CSV vazio -> mensagem "sem dados suficientes" sem gráficos
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

  - [x]* 12.2 Escrever testes de integração do dashboard
    - Verificar ambos os tratamentos no mesmo gráfico (tempo e tamanho), a tabela de estatísticas e as mensagens de CSV ausente/vazio
    - _Requirements: 11.2, 11.3, 11.4, 11.5, 11.6_

- [x] 13. Checkpoint final - Garantir que todos os testes passam
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tarefas marcadas com `*` são opcionais (testes) e podem ser puladas para um MVP mais rápido.
- Cada tarefa referencia requisitos específicos para rastreabilidade.
- Os checkpoints garantem validação incremental.
- Testes de propriedade (P1–P13) usam `fast-check` (Node.js) e `hypothesis` (Python), com mínimo de 100 iterações cada e anotação `Feature: graphql-vs-rest-experiment, Property {n}`.
- Testes unitários e de integração validam exemplos, contagens, formatos e wiring de infraestrutura.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "7.1", "8.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "3.1", "4.1", "7.2", "7.3", "8.2", "8.3"] },
    { "id": 3, "tasks": ["3.2", "3.3", "3.4", "4.2", "4.3", "4.4", "5.1", "7.4", "7.5", "9.1", "11.1"] },
    { "id": 4, "tasks": ["5.2", "9.2", "11.2", "11.3", "11.4", "12.1"] },
    { "id": 5, "tasks": ["12.2"] }
  ]
}
```

