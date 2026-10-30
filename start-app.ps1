<#
Starts the FastAPI backend and Vite frontend for local development.

Run from the project root:
  .\start-app.ps1
#>

$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$python = Join-Path $projectRoot 'venv\Scripts\python.exe'
$frontend = Join-Path $projectRoot 'frontend'

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Create it with: python -m venv venv"
}

if (-not (Test-Path (Join-Path $frontend 'node_modules'))) {
    throw "Frontend dependencies are missing. Run: cd frontend; npm install"
}

& $python -c "import fastapi, torch, sklearn, pandas, uvicorn" 
if ($LASTEXITCODE -ne 0) {
    throw "Backend dependencies are missing. Run: .\venv\Scripts\python.exe -m pip install -r backend\requirements.txt"
}

Write-Host 'Starting backend at http://127.0.0.1:8000 ...'
Start-Process -FilePath $python -ArgumentList '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload' -WorkingDirectory $projectRoot -WindowStyle Hidden

Write-Host 'Starting frontend at http://localhost:5173 ...'
Start-Process -FilePath 'npm.cmd' -ArgumentList 'run', 'dev', '--', '--host', '127.0.0.1' -WorkingDirectory $frontend -WindowStyle Hidden

Write-Host ''
Write-Host 'Both services were started.'
Write-Host 'Frontend: http://localhost:5173'
Write-Host 'API docs: http://127.0.0.1:8000/docs'
