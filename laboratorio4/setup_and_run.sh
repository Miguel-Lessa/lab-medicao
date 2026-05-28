#!/usr/bin/env bash
# Executa o Laboratorio 04 completo no Linux/macOS (cria venv, instala deps, roda pipeline).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Erro: python3 ou python nao encontrado no PATH."
  exit 1
fi

echo "==> Repositorio: $ROOT"
echo "==> Python: $($PY --version)"

if [ ! -d ".venv" ]; then
  echo "==> Criando ambiente virtual .venv"
  "$PY" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Instalando dependencias"
pip install --upgrade pip
pip install -r laboratorio4/requirements.txt

echo "==> Executando pipeline do Laboratorio 04"
python laboratorio4/run_lab04.py "$@"
