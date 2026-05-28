# Laboratorio 04 - Sprint 03

Dashboard interativo em Python para analise de dados publicos governamentais.

## Tema

O trabalho utiliza a base publica da Cota para Exercicio da Atividade Parlamentar
(CEAP), disponibilizada pela Camara dos Deputados. A base contem despesas
ressarcidas a deputados federais, com informacoes como parlamentar, partido, UF,
tipo de despesa, fornecedor, data e valor.

Fonte oficial:

- Portal: https://dadosabertos.camara.leg.br/
- Arquivos CEAP: http://www.camara.leg.br/cotas/Ano-2024.csv.zip

## Estrutura

```text
laboratorio4/
  app/
    dashboard.py
  data/
    raw/
  output/
    despesas_ceap_tratadas.csv
  scripts/
    coleta_ceap.py
    prepara_dados.py
  relatorio_lab04s03.md
  requirements.txt
```

## Instalacao

No diretorio raiz do repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r laboratorio4/requirements.txt
```

## Coleta dos dados

Por padrao, a coleta baixa os anos de 2020 a 2025.

```powershell
python laboratorio4/scripts/coleta_ceap.py
```

Para escolher anos especificos:

```powershell
python laboratorio4/scripts/coleta_ceap.py --anos 2020 2021 2022 2023 2024 2025
```

## Preparacao da base

```powershell
python laboratorio4/scripts/prepara_dados.py
```

O arquivo tratado sera salvo em:

```text
laboratorio4/output/despesas_ceap_tratadas.csv
```

## Execucao do dashboard

```powershell
streamlit run laboratorio4/app/dashboard.py
```

O Streamlit abrira o dashboard no navegador. Caso nao abra automaticamente,
acesse a URL indicada no terminal, normalmente `http://localhost:8501`.

Cada grafico possui botoes **Exportar PNG** e **Exportar HTML** logo abaixo da
visualizacao. O PNG exige o pacote `kaleido` (ja listado em `requirements.txt`).
Use os arquivos exportados no relatorio final e na entrega em PDF.

## Questoes de pesquisa

- RQ1: Quais tipos de despesa concentram mais gastos parlamentares?
- RQ2: Como os gastos variam por partido e UF?
- RQ3: Quais deputados e fornecedores concentram os maiores valores?

## Entrega final

A entrega da Sprint 03 contempla:

- dashboard interativo em Streamlit;
- base tratada em CSV;
- scripts reprodutiveis de coleta e tratamento;
- relatorio completo em `relatorios/relatorio_lab04_final.md` (com figuras em `relatorios/figuras/`).

Para regenerar as imagens do relatorio:

```powershell
python laboratorio4/scripts/exportar_figuras_relatorio.py
```
