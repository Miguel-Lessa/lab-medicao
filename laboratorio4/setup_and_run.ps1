# Executa o Laboratorio 04 completo no Windows (cria venv, instala deps, roda pipeline).
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$Py = Get-Command python -ErrorAction SilentlyContinue
if (-not $Py) {
    $Py = Get-Command py -ErrorAction SilentlyContinue
    if ($Py) {
        $PythonExe = "py -3"
    } else {
        throw "Python nao encontrado. Instale Python 3.10+ e tente novamente."
    }
} else {
    $PythonExe = "python"
}

Write-Host "==> Repositorio: $RepoRoot"
& $PythonExe --version

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "==> Criando ambiente virtual .venv"
    & $PythonExe -m venv .venv
}

Write-Host "==> Instalando dependencias"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r laboratorio4/requirements.txt

Write-Host "==> Executando pipeline do Laboratorio 04"
& $VenvPython laboratorio4/run_lab04.py @args
