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

## Testes

```powershell
npm test
python -m pytest tests_py
```

As tarefas opcionais da especificacao tambem foram implementadas: os testes de
propriedade cobrem P1-P13 e executam no minimo 100 exemplos cada.
