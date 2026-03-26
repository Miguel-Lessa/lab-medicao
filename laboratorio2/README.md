# Laboratorio 2 - Sprint 01 (Java + CK)

## Objetivo da Sprint 01

Entregar:

1. Lista dos 1.000 repositorios Java mais populares.
2. Script de automacao de clone + coleta de metricas CK.
3. CSV com resultado das medicoes de 1 repositorio.

## Estrutura

- `scripts/coleta_sprint1_java.py`: coleta top-1000 Java no GitHub.
- `scripts/coleta_ck_sprint1.py`: clona 1 repositorio e executa CK.
- `output/top_1000_java_repos.csv`: lista de repositorios Java.
- `output/ck_resultado_1_repo.csv`: sumarizacao de CBO/DIT/LCOM para 1 repositorio.

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

## Instalacao

No diretorio `laboratorio2`:

```powershell
pip install -r requirements.txt
```

## Execucao da Sprint 01

1. Coletar top-1000 repositorios Java:

```powershell
python scripts/coleta_sprint1_java.py
```

2. Executar CK em 1 repositorio da lista e gerar CSV final:

```powershell
python scripts/coleta_ck_sprint1.py
```

Observacao: o script do CK baixa automaticamente o JAR em `tools/ck.jar` caso ele nao exista.
