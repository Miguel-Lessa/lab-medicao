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

## Execucao completa (Linux e Windows)

Um comando cria o venv, instala dependencias e roda **coleta -> tratamento -> figuras -> dashboard**.

### Windows (PowerShell, na raiz do repo)

```powershell
cd C:\caminho\para\lab-medicao
.\laboratorio4\setup_and_run.ps1
```

### Linux (na raiz do repo)

Funciona em Ubuntu, Debian, Fedora, **Arch Linux** e demais distribuicoes.

**Pre-requisito (Arch Linux — apenas na primeira vez):**

```bash
sudo pacman -S python python-pip
```

No Arch, o pacote `python` ja inclui o modulo `venv`. Em outras distros, se `python3 -m venv` falhar, instale o pacote equivalente (ex.: `python3-venv` no Debian/Ubuntu).

**Executar o laboratorio completo:**

```bash
cd ~/caminho/para/lab-medicao
chmod +x laboratorio4/setup_and_run.sh
./laboratorio4/setup_and_run.sh
```

Acesse o dashboard em **http://localhost:8501**. Encerrar com `Ctrl+C`.

**Passo a passo manual no Linux:**

```bash
cd ~/caminho/para/lab-medicao
python -m venv .venv          # ou: python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r laboratorio4/requirements.txt
python laboratorio4/run_lab04.py
```

### macOS

Use os mesmos comandos da secao Linux acima (`python3` se `python` nao existir).

### Opcoes uteis

```bash
# Pular coleta (CSV brutos ja baixados)
./laboratorio4/setup_and_run.sh --skip-coleta

# So pipeline, sem abrir dashboard
./laboratorio4/setup_and_run.sh --skip-dashboard

# So dashboard (base ja tratada)
./laboratorio4/setup_and_run.sh --skip-coleta --skip-figuras
```

No Windows, troque `./laboratorio4/setup_and_run.sh` por `.\laboratorio4\setup_and_run.ps1`.

---

## Instalacao manual

No diretorio raiz do repositorio:

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r laboratorio4/requirements.txt
```

```bash
# Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r laboratorio4/requirements.txt
```

## Coleta dos dados

Por padrao, a coleta baixa os anos de 2020 a 2025.

```bash
python laboratorio4/scripts/coleta_ceap.py
```

Para escolher anos especificos:

```bash
python laboratorio4/scripts/coleta_ceap.py --anos 2020 2021 2022 2023 2024 2025
```

## Preparacao da base

```bash
python laboratorio4/scripts/prepara_dados.py
```

O arquivo tratado sera salvo em:

```text
laboratorio4/output/despesas_ceap_tratadas.csv
```

## Execucao do dashboard

Na raiz do repositorio, com o ambiente virtual ativo **ou** usando `python -m`:

```bash
# Linux / macOS
source .venv/bin/activate
python -m streamlit run laboratorio4/app/dashboard.py
```

```powershell
# Windows — ativar o venv
.\.venv\Scripts\Activate.ps1
python -m streamlit run laboratorio4/app/dashboard.py

# Windows — sem ativar
.\.venv\Scripts\python.exe -m streamlit run laboratorio4/app/dashboard.py
```

Se aparecer `streamlit is not recognized`, o comando `streamlit` nao esta no PATH;
use sempre `python -m streamlit` como acima.

**Primeira execucao:** se aparecer `Email:` no terminal, apenas pressione **Enter**
(deixe em branco). So depois o servidor sobe e o navegador pode abrir.

O Streamlit abrira o dashboard no navegador. Caso nao abra automaticamente,
acesse manualmente: **http://localhost:8501**

Para encerrar o dashboard: `Ctrl+C` no terminal.

**Caminho do script:** execute a partir da **raiz** (`lab-medicao`), nao de dentro de `laboratorio4/`.

Cada grafico possui botoes **Exportar PNG** e **Exportar HTML** logo abaixo da
visualizacao. O PNG exige o pacote `kaleido` (ja listado em `requirements.txt`).
Use os arquivos exportados no relatorio final e na entrega em PDF.

## Questoes de pesquisa

- RQ1: Quais tipos de despesa concentram mais gastos parlamentares?
- RQ2: Como os gastos variam por partido e UF?
- RQ3: Quais deputados e fornecedores concentram os maiores valores?

## Apresentacao em sala

Roteiro com fala sugerida para **cada grafico** do dashboard:

```text
laboratorio4/apresentacao.md
```

---

## Entrega final

A entrega da Sprint 03 contempla:

- dashboard interativo em Streamlit;
- base tratada em CSV;
- scripts reprodutiveis de coleta e tratamento;
- relatorio completo em `relatorios/relatorio_lab04_final.md` (com figuras em `relatorios/figuras/`).

Para regenerar as imagens do relatorio:

```bash
python laboratorio4/scripts/exportar_figuras_relatorio.py
```
