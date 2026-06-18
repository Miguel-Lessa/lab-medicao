# Requirements Document

## Introduction

Este documento descreve os requisitos de um experimento controlado de Engenharia de Software (LAB05 - Laboratório de Experimentação de Software) cujo objetivo é avaliar quantitativamente os benefícios da adoção de uma API GraphQL em comparação a uma API REST. O experimento adota o tema de estatísticas de futebol, no qual uma base de dados fictícia contém Ligas, Times e Jogadores com um grande conjunto de atributos estatísticos, de forma que o payload REST seja propositalmente pesado e evidencie a economia de tráfego do GraphQL.

O experimento responde a duas questões de pesquisa:

- **RQ1:** As respostas às consultas GraphQL são mais rápidas que as respostas às consultas REST?
- **RQ2:** As respostas às consultas GraphQL possuem tamanho menor que as respostas REST?

O trabalho é entregue em três sprints:

- **Sprint 1:** Desenho do experimento e preparação do ambiente (API e script de medição).
- **Sprint 2:** Execução das medições, análise dos dados e relatório final.
- **Sprint 3:** Dashboard de visualização dos resultados com Pandas, Matplotlib e Seaborn.

Este documento cobre os elementos de desenho experimental exigidos pelo enunciado: hipóteses nula e alternativa, variáveis dependentes, variáveis independentes, tratamentos, objetos experimentais, tipo de desenho experimental, número de medições e ameaças à validade, além do requisito de dashboard/visualização.

## Glossary

- **Experimento**: Estudo empírico controlado que compara as tecnologias REST e GraphQL sob condições reprodutíveis.
- **API_REST**: Servidor que expõe o endpoint `GET /rest/players/:id` e retorna o jogador com todas as suas estatísticas.
- **API_GraphQL**: Servidor que expõe o endpoint `POST /graphql` e retorna apenas os campos solicitados na consulta.
- **Servidor_API**: Aplicação Node.js que hospeda simultaneamente a API_REST (Express) e a API_GraphQL (Apollo Server) na porta 4000.
- **Base_De_Dados**: Conjunto de dados fictício em memória, composto por Ligas, Times e Jogadores com atributos estatísticos.
- **Jogador**: Entidade da Base_De_Dados que contém identificador, nome e um grande conjunto de estatísticas (gols, assistências, cartões amarelos, cartões vermelhos, passes certos, desarmes, km percorridos, finalizações no gol, entre outros).
- **Script_De_Medicao**: Programa Python (`scripts/experiment.py`) que executa as requisições, mede tempo e tamanho e grava os resultados.
- **Tratamento**: Tecnologia de API aplicada em cada medição (REST ou GraphQL).
- **Objeto_Experimental**: Requisição de dados de um Jogador específico submetida a um Tratamento.
- **Variavel_Dependente**: Métrica observada e medida no Experimento (tempo de resposta e tamanho da resposta).
- **Variavel_Independente**: Fator manipulado no Experimento (a tecnologia de API).
- **Arquivo_De_Resultados**: Arquivo `results.csv` que armazena os registros das medições.
- **Tempo_Ms**: Tempo de resposta de uma requisição, medido em milissegundos.
- **Tamanho_Bytes**: Tamanho do corpo da resposta de uma requisição, medido em bytes.
- **Dashboard**: Aplicação de visualização que apresenta gráficos e estatísticas dos resultados do Experimento.
- **Hipotese_Nula**: Afirmação de que não há diferença entre os Tratamentos para uma dada Variavel_Dependente.
- **Hipotese_Alternativa**: Afirmação de que existe diferença entre os Tratamentos para uma dada Variavel_Dependente.

## Requirements

### Requirement 1: Definição do desenho experimental

**User Story:** Como pesquisador do laboratório, quero que o desenho experimental esteja formalmente definido, para que o Experimento seja reprodutível e cientificamente válido.

#### Acceptance Criteria

1. THE Experimento SHALL definir como Variavel_Independente a tecnologia de API, com exatamente dois valores possíveis e mutuamente exclusivos: REST e GraphQL.
2. THE Experimento SHALL definir como Variaveis_Dependentes o Tempo_Ms, medido em milissegundos, e o Tamanho_Bytes da resposta, medido em bytes.
3. THE Experimento SHALL definir exatamente dois Tratamentos: requisição via API_REST e requisição via API_GraphQL.
4. THE Experimento SHALL definir o Objeto_Experimental como a requisição dos dados de um Jogador identificado por um ID que corresponde a um Jogador existente na Base_De_Dados.
5. THE Experimento SHALL adotar desenho experimental pareado, no qual cada ID de Jogador sorteado aleatoriamente é submetido aos dois Tratamentos dentro da mesma iteração, utilizando o mesmo ID em ambos os Tratamentos.
6. THE Experimento SHALL planejar exatamente 1000 iterações de medição por Tratamento, totalizando exatamente 2000 registros (1000 para o Tratamento REST e 1000 para o Tratamento GraphQL).

### Requirement 2: Formulação das hipóteses

**User Story:** Como pesquisador do laboratório, quero que as hipóteses estatísticas estejam declaradas, para que as questões de pesquisa possam ser testadas formalmente.

#### Acceptance Criteria

1. THE Experimento SHALL declarar, para a RQ1, a Hipotese_Nula de que o Tempo_Ms médio das respostas GraphQL é igual ao Tempo_Ms médio das respostas REST.
2. THE Experimento SHALL declarar, para a RQ1, a Hipotese_Alternativa, de natureza unicaudal, de que o Tempo_Ms médio das respostas GraphQL é menor que o Tempo_Ms médio das respostas REST.
3. THE Experimento SHALL declarar, para a RQ2, a Hipotese_Nula de que o Tamanho_Bytes médio das respostas GraphQL é igual ao Tamanho_Bytes médio das respostas REST.
4. THE Experimento SHALL declarar, para a RQ2, a Hipotese_Alternativa, de natureza unicaudal, de que o Tamanho_Bytes médio das respostas GraphQL é menor que o Tamanho_Bytes médio das respostas REST.
5. THE Experimento SHALL declarar um nível de significância de 0,05 para o teste das hipóteses, rejeitando a Hipotese_Nula da RQ1 e da RQ2 quando o valor-p obtido for menor que 0,05.

### Requirement 3: Base de dados fictícia de futebol

**User Story:** Como responsável pela preparação do ambiente, quero uma base de dados em memória com dados de futebol, para que as APIs tenham conteúdo suficiente para evidenciar a diferença de payload entre as tecnologias.

#### Acceptance Criteria

1. THE Base_De_Dados SHALL conter coleções em memória, sem dependência de banco de dados externo, com ao menos duas Ligas, ao menos cinco Times e ao menos cinquenta Jogadores.
2. THE Base_De_Dados SHALL associar cada Time a uma Liga existente e cada Jogador a um Time existente, sem Times ou Jogadores órfãos.
3. THE Base_De_Dados SHALL atribuir a cada Jogador um identificador único, do tipo inteiro e não nulo.
4. THE Base_De_Dados SHALL atribuir aos Jogadores identificadores formando um conjunto contíguo de 1 a N, onde N é a quantidade total de Jogadores, para permitir o sorteio aleatório de identificadores.
5. THE Base_De_Dados SHALL atribuir a cada Jogador ao menos dez atributos estatísticos, incluindo gols, assistências, cartões amarelos, cartões vermelhos, passes certos, desarmes, quilômetros percorridos e finalizações no gol.
6. THE Base_De_Dados SHALL atribuir a cada atributo estatístico de cada Jogador um valor numérico não negativo.
7. THE Base_De_Dados SHALL conter ao menos cinquenta Jogadores para permitir o sorteio aleatório de identificadores durante as medições.

### Requirement 4: API REST

**User Story:** Como cliente do experimento, quero uma API REST que retorne todos os dados de um jogador, para que o Tratamento REST represente o cenário de payload completo.

#### Acceptance Criteria

1. WHEN o Servidor_API recebe uma requisição `GET /rest/players/:id` com um identificador correspondente a um Jogador existente na Base_De_Dados, THE API_REST SHALL retornar o Jogador correspondente contendo seu identificador, nome e todos os seus atributos estatísticos definidos na Base_De_Dados (ao menos dez atributos, incluindo gols, assistências, cartões amarelos, cartões vermelhos, passes certos, desarmes, quilômetros percorridos e finalizações no gol).
2. WHEN o Servidor_API recebe uma requisição `GET /rest/players/:id` com um identificador correspondente a um Jogador existente na Base_De_Dados, THE API_REST SHALL responder com código de status HTTP 200.
3. IF o identificador informado está em formato válido mas não corresponde a nenhum Jogador da Base_De_Dados, THEN THE API_REST SHALL responder com código de status HTTP 404, sem incluir dados de Jogador no corpo, e com uma mensagem de erro indicando que o Jogador não foi encontrado.
4. IF o identificador informado não está em formato válido para identificação de um Jogador da Base_De_Dados, THEN THE API_REST SHALL responder com código de status HTTP 400, sem incluir dados de Jogador no corpo, e com uma mensagem de erro indicando que o identificador é inválido.
5. THE API_REST SHALL retornar o corpo de todas as respostas no formato JSON.

### Requirement 5: API GraphQL

**User Story:** Como cliente do experimento, quero uma API GraphQL que retorne apenas os campos solicitados, para que o Tratamento GraphQL represente o cenário de payload otimizado.

#### Acceptance Criteria

1. WHEN o Servidor_API recebe uma consulta `POST /graphql` válida solicitando um Jogador por um identificador existente, THE API_GraphQL SHALL retornar, no formato JSON, exclusivamente os campos especificados na consulta, sem incluir atributos não solicitados.
2. WHEN a consulta GraphQL solicita apenas os campos nome e gols de um Jogador existente, THE API_GraphQL SHALL retornar no corpo da resposta exclusivamente esses dois campos, sem incluir nenhum outro atributo do Jogador.
3. IF a consulta GraphQL referencia um identificador que não corresponde a nenhum Jogador da Base_De_Dados, THEN THE API_GraphQL SHALL retornar uma resposta JSON com o campo de dados do Jogador nulo e um campo de erro indicando que o Jogador não foi encontrado.
4. THE API_GraphQL SHALL expor um schema que descreva as entidades Liga, Time e Jogador, incluindo, para a entidade Jogador, o identificador, o nome e ao menos dez atributos estatísticos.
5. THE API_GraphQL SHALL expor no schema uma consulta que permita obter um Jogador a partir de seu identificador.

### Requirement 6: Servidor de API unificado

**User Story:** Como responsável pela preparação do ambiente, quero um único servidor que hospede ambas as APIs, para que as medições ocorram sob as mesmas condições de execução.

#### Acceptance Criteria

1. THE Servidor_API SHALL hospedar a API_REST e a API_GraphQL em um único processo, expondo os endpoints `GET /rest/players/:id` e `POST /graphql` acessíveis na porta 4000.
2. THE Servidor_API SHALL utilizar Node.js com Express para a API_REST e Apollo Server para a API_GraphQL.
3. THE Servidor_API SHALL habilitar CORS, aceitando requisições dos métodos GET e POST originadas do Script_De_Medicao e incluindo os cabeçalhos CORS correspondentes nas respostas.
4. WHEN o Servidor_API conclui sua inicialização, THE Servidor_API SHALL registrar no console, em até 30 segundos, a confirmação de que está disponível na porta 4000.
5. IF a porta 4000 já está em uso no momento da inicialização, THEN THE Servidor_API SHALL registrar uma mensagem de erro descritiva e encerrar a execução.

### Requirement 7: Script de medição

**User Story:** Como pesquisador do laboratório, quero um script que execute as requisições e colete as métricas, para que os dados do Experimento sejam gerados de forma automatizada e consistente.

#### Acceptance Criteria

1. THE Script_De_Medicao SHALL executar exatamente 1000 iterações de medição de forma sequencial.
2. WHEN uma iteração é iniciada, THE Script_De_Medicao SHALL sortear um identificador de Jogador de forma aleatória com distribuição uniforme entre todos os identificadores existentes na Base_De_Dados.
3. WHEN uma iteração é executada, THE Script_De_Medicao SHALL realizar uma requisição à API_REST e registrar o Tempo_Ms, medido como o intervalo entre o envio da requisição e o recebimento completo do corpo da resposta, e o Tamanho_Bytes, medido como o número de bytes do corpo da resposta.
4. WHEN uma iteração é executada, THE Script_De_Medicao SHALL realizar uma consulta à API_GraphQL solicitando apenas os campos nome e gols e registrar o Tempo_Ms, medido como o intervalo entre o envio da requisição e o recebimento completo do corpo da resposta, e o Tamanho_Bytes, medido como o número de bytes do corpo da resposta.
5. WHEN uma iteração é executada, THE Script_De_Medicao SHALL aplicar o mesmo identificador de Jogador a ambos os Tratamentos na mesma iteração.
6. IF uma requisição não recebe resposta completa dentro de 30000 ms, THEN THE Script_De_Medicao SHALL considerar a requisição como falha por expiração de tempo limite.
7. IF uma requisição falha durante uma iteração por erro de conexão, por expiração de tempo limite ou por resposta com código de status HTTP igual ou superior a 400 ou contendo campo de erro, THEN THE Script_De_Medicao SHALL registrar a ocorrência da falha indicando o identificador de Jogador e o Tratamento, descartar a medição correspondente e prosseguir para a próxima iteração.

### Requirement 8: Armazenamento dos resultados

**User Story:** Como pesquisador do laboratório, quero que as medições sejam gravadas em arquivo, para que os dados possam ser analisados posteriormente.

#### Acceptance Criteria

1. THE Script_De_Medicao SHALL gravar os resultados no Arquivo_De_Resultados `results.csv` no formato CSV, com uma única linha de cabeçalho antes dos registros.
2. THE Arquivo_De_Resultados SHALL conter, nesta ordem, as colunas tecnologia (valores permitidos "REST" ou "GraphQL"), tempo_ms (valor numérico em milissegundos) e tamanho_bytes (valor inteiro em bytes).
3. WHEN uma medição de um Tratamento é concluída com sucesso, THE Script_De_Medicao SHALL adicionar um registro ao Arquivo_De_Resultados com o valor de tecnologia correspondente ao Tratamento e com tempo_ms e tamanho_bytes preenchidos com os valores medidos.
4. WHEN a execução completa de 1000 iterações termina, THE Arquivo_De_Resultados SHALL conter entre 1800 e 2000 registros de medição bem-sucedida, sem contar a linha de cabeçalho.
5. IF a gravação de um registro no Arquivo_De_Resultados falha, THEN THE Script_De_Medicao SHALL registrar a ocorrência da falha, preservar os registros já gravados e prosseguir a execução.

### Requirement 9: Verificação do ambiente e validação prévia

**User Story:** Como pesquisador do laboratório, quero validar o ambiente antes da execução oficial, para que erros sejam detectados antes da coleta definitiva.

#### Acceptance Criteria

1. WHEN o Servidor_API é iniciado para verificação, THE Servidor_API SHALL responder a uma requisição de teste à API_REST com código de status HTTP 200 e a uma consulta de teste à API_GraphQL com uma resposta sem campo de erro.
2. WHERE o Script_De_Medicao é executado em modo de validação, THE Script_De_Medicao SHALL executar exatamente 10 iterações de medição antes da execução oficial.
3. WHEN a execução de validação com 10 iterações termina, THE Script_De_Medicao SHALL gerar o Arquivo_De_Resultados contendo as colunas tecnologia, tempo_ms e tamanho_bytes e aproximadamente 20 registros (10 iterações por dois Tratamentos).
4. WHEN a execução de validação termina sem nenhuma falha de requisição registrada, THE Script_De_Medicao SHALL habilitar a execução da coleta oficial de 1000 iterações.
5. IF a execução de validação registra ao menos uma falha de requisição, THEN THE Script_De_Medicao SHALL interromper o fluxo antes da coleta oficial e exibir uma mensagem de erro descritiva.

### Requirement 10: Análise dos dados e relatório final

**User Story:** Como pesquisador do laboratório, quero analisar os dados coletados e produzir um relatório, para que as questões de pesquisa sejam respondidas com base nas evidências.

#### Acceptance Criteria

1. THE Experimento SHALL calcular, para cada Tratamento e considerando apenas registros válidos, estatísticas descritivas de Tempo_Ms e Tamanho_Bytes, incluindo contagem, média, mediana, desvio padrão, mínimo e máximo.
2. THE Experimento SHALL comparar o Tempo_Ms entre os Tratamentos para responder à RQ1, reportando a diferença entre as medianas, a redução percentual e a decisão de rejeitar ou não rejeitar a Hipotese_Nula da RQ1 ao nível de significância de 0,05.
3. THE Experimento SHALL comparar o Tamanho_Bytes entre os Tratamentos para responder à RQ2, reportando a diferença entre as medianas, a redução percentual e a decisão de rejeitar ou não rejeitar a Hipotese_Nula da RQ2 ao nível de significância de 0,05.
4. THE Experimento SHALL documentar as ameaças à validade do Experimento, incluindo ameaças à validade interna, externa, de construção e de conclusão.
5. THE Experimento SHALL produzir um relatório final que apresente as hipóteses, a metodologia, os resultados e, para a RQ1 e a RQ2, a decisão explícita de rejeitar ou não rejeitar cada Hipotese_Nula.
6. IF não há registros válidos suficientes para a análise de uma das questões de pesquisa, THEN THE Experimento SHALL documentar no relatório a ausência de dados suficientes para responder àquela questão.

### Requirement 11: Dashboard de visualização

**User Story:** Como pesquisador do laboratório, quero um dashboard com gráficos dos resultados, para que as diferenças entre as tecnologias sejam comunicadas de forma visual.

#### Acceptance Criteria

1. WHEN o Dashboard é iniciado e o Arquivo_De_Resultados está disponível, THE Dashboard SHALL ler os registros das colunas tecnologia, tempo_ms e tamanho_bytes do Arquivo_De_Resultados utilizando Pandas.
2. THE Dashboard SHALL apresentar uma visualização comparativa do Tempo_Ms entre os Tratamentos REST e GraphQL utilizando Matplotlib e Seaborn, exibindo ambos os Tratamentos no mesmo gráfico.
3. THE Dashboard SHALL apresentar uma visualização comparativa do Tamanho_Bytes entre os Tratamentos REST e GraphQL utilizando Matplotlib e Seaborn, exibindo ambos os Tratamentos no mesmo gráfico.
4. THE Dashboard SHALL exibir, para cada Tratamento, as estatísticas descritivas de Tempo_Ms e de Tamanho_Bytes incluindo média, mediana e desvio padrão.
5. IF o Arquivo_De_Resultados não está disponível ou não pode ser lido, THEN THE Dashboard SHALL exibir uma mensagem informando que os dados de resultados não foram encontrados e SHALL não renderizar os gráficos comparativos.
6. IF o Arquivo_De_Resultados está disponível mas não contém nenhum registro de medição, THEN THE Dashboard SHALL exibir uma mensagem informando que não há dados suficientes para gerar as visualizações e SHALL não renderizar os gráficos comparativos.
