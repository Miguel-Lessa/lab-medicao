# Laboratorio 2 — Qualidade de Sistemas Java (CK)

## Pre-requisitos

- Python 3.12+
- Java (JRE/JDK 8+)
- Git

## Configuracao

1. Copie `.env.example` para `.env`:

```powershell
Copy-Item .env.example .env
```

2. Edite `.env` e preencha:

```env
GITHUB_TOKEN=ghp_seu_token_aqui
```

3. Instale dependencias:

```powershell
pip install -r requirements.txt
```

## Estrutura

```
laboratorio2/
  scripts/
    coleta_sprint1_java.py    # Sprint 01: coleta top-1000 Java
    coleta_ck_sprint1.py      # Sprint 01: CK em 1 repositorio
    enriquecer_repos.py       # Sprint 02: adiciona releases e tamanho via API
    coleta_ck_todos.py        # Sprint 02: CK em todos os repos (paralelo)
    analise_sprint2.py        # Sprint 02: analise estatistica + relatorio
  output/
    top_1000_java_repos.csv
    top_1000_java_repos_enriquecido.csv
    ck_resultado_1_repo.csv
    ck_resultado_todos.csv
    relatorio_final_sprint2.md
    charts/*.png
  tools/                       # ck.jar (baixado automaticamente)
  repos/                       # clones temporarios (gitignored)
  tmp/                         # saidas temporarias do CK (gitignored)
```

## Sprint 01

1. Coletar top-1000 repositorios Java:

```powershell
python scripts/coleta_sprint1_java.py
```

2. Executar CK em 1 repositorio (validacao):

```powershell
python scripts/coleta_ck_sprint1.py
```

## Sprint 02

1. Enriquecer CSV com releases e tamanho (via API, sem clone):

```powershell
python scripts/enriquecer_repos.py
```

2. Executar CK em todos os repositorios (4 workers paralelos):

```powershell
python scripts/coleta_ck_todos.py
```

Opcoes:
- `--workers 8` para usar 8 workers
- `--ck-jar caminho/ck.jar` para informar JAR customizado

3. Gerar analise, graficos e relatorio:

```powershell
python scripts/analise_sprint2.py
```
