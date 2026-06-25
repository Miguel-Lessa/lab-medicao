# Laboratorio 05 - GraphQL vs REST

Experimento controlado que compara uma API REST e uma API GraphQL usando uma
base ficticia de estatisticas de futebol. O objetivo e medir tempo de resposta
e tamanho do payload para responder:

- RQ1: respostas GraphQL sao mais rapidas que respostas REST?
- RQ2: respostas GraphQL possuem tamanho menor que respostas REST?

## Estrutura

```text
laboratorio5/
  src/                 servidor Node.js Express + Apollo
  lab05/               medicao, analise e dashboard em Python
  scripts/             wrappers de execucao
  app/                 wrapper do dashboard
  tests/               testes Node.js com fast-check
  tests_py/            testes Python com hypothesis
  output/              results.csv e figuras geradas
  relatorios/          relatorio final
```

## Instalacao

```powershell
cd laboratorio5
npm install
python -m pip install -r requirements.txt
```

## Execucao

Em um terminal:

```powershell
npm start
```

Em outro terminal:

```powershell
python scripts/experiment.py
python scripts/analyze.py
python app/dashboard.py
```

Para abrir o dashboard interativo usado na apresentacao:

```powershell
streamlit run app/interactive_dashboard.py
```

Depois acesse `http://localhost:8501`.

## Dashboard sem Docker no Linux

Se o arquivo `output/results.csv` ja existir, nao precisa subir a API para abrir
o dashboard. Basta instalar as dependencias Python e executar o Streamlit:

```bash
cd laboratorio5
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app/interactive_dashboard.py
```

Depois acesse:

```text
http://localhost:8501
```

Para regenerar os dados do experimento sem Docker, use dois terminais.

Terminal 1, para iniciar a API:

```bash
cd laboratorio5
npm install
npm start
```

Terminal 2, para coletar os dados, atualizar o relatorio, gerar as figuras e
abrir o dashboard:

```bash
cd laboratorio5
source .venv/bin/activate
python scripts/experiment.py
python scripts/analyze.py
python app/dashboard.py
streamlit run app/interactive_dashboard.py
```

## Execucao em ambiente controlado com Docker

Para reduzir variacoes do ambiente local, a coleta oficial pode ser regenerada em
um container Docker com Node.js 20 e Python 3 instalados na mesma imagem:

```powershell
docker compose up --build
```

O container sobe a API REST/GraphQL, aguarda o endpoint REST responder, executa a
validacao, coleta 1000 pares de requisicoes, gera o relatorio e recria as figuras
em `output/figures`. Os diretorios `output/` e `relatorios/` ficam montados como
volumes para preservar os artefatos gerados no host.

Para abrir o dashboard interativo em Docker:

```powershell
docker compose --profile dashboard up dashboard --build
```

Depois acesse `http://localhost:8501`.

## Testes

```powershell
npm test
python -m pytest tests_py
```

As tarefas opcionais da especificacao tambem foram implementadas: os testes de
propriedade cobrem P1-P13 e executam no minimo 100 exemplos cada.
