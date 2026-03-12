# Lab Medicao

Projeto de coleta e analise de repositorios populares do GitHub (Lab 1), com geracao de:

- CSV com os dados coletados
- relatorio em Markdown
- graficos
- relatorio final em PDF

## Estrutura Organizada

```text
lab-medicao/
├── laboratorio1/
│   ├── requirements.txt
│   ├── .env.example
│   ├── scripts/
│   │   ├── coleta_sprint2.py
│   │   ├── analise_sprint3.py
│   │   ├── gerar_pdf_relatorio.py
│   │   └── run_pipeline.py
│   └── output/
└── README.md
```

## Pre-requisitos

- Git
- Python 3.12+
- PowerShell (Windows) ou terminal bash/zsh (Linux/macOS)

## 1. Criar token do GitHub (API)

1. Acesse [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
1. Clique em `Generate new token`.
1. Para este projeto (repositorios publicos), pode usar token sem permissoes extras.
1. Copie o token gerado (ele aparece apenas uma vez).

## 2. Clonar o projeto

```bash
git clone https://github.com/Miguel-Lessa/lab-medicao.git
cd lab-medicao
```

## 3. Criar um novo ambiente virtual (venv)

No diretorio raiz do projeto:

```bash
python -m venv .venv
```

Ativacao:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
source .venv/bin/activate
```

## 4. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r laboratorio1/requirements.txt
```

## 5. Configurar variavel do token

Crie o arquivo `laboratorio1/.env` com base no exemplo:

```bash
cp laboratorio1/.env.example laboratorio1/.env
```

No Windows PowerShell, se nao tiver `cp`:

```powershell
Copy-Item laboratorio1/.env.example laboratorio1/.env
```

Edite `laboratorio1/.env` e informe:

```env
GITHUB_TOKEN=ghp_seu_token_aqui
```

## 6. Ordem correta de execucao

Execute nesta ordem:

1. Coleta dos dados:

```bash
python laboratorio1/scripts/coleta_sprint2.py
```

2. Analise + graficos + relatorio final em Markdown:

```bash
python laboratorio1/scripts/analise_sprint3.py
```

3. Geracao do PDF final (opcional, depende dos passos anteriores):

```bash
python laboratorio1/scripts/gerar_pdf_relatorio.py
```

Opcional: executar tudo de uma vez:

```bash
python laboratorio1/scripts/run_pipeline.py
```

Sem PDF:

```bash
python laboratorio1/scripts/run_pipeline.py --sem-pdf
```

## Saidas geradas

Arquivos gerados em `laboratorio1/output/`:

- `top_1000_repos.csv`
- `relatorio_sprint2.md`
- `relatorio_final_sprint3.md`
- `relatorio_final_completo.pdf`
- `charts/*.png`

## Boas praticas

- Nunca versionar `.env` nem `venv`.
- Sempre ativar o venv antes de rodar scripts.
- Regenerar `output/` quando precisar de dados atualizados.
