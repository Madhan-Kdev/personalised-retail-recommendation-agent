@echo off
title Personalized Retail Recommendation Agent - Launcher
echo ==============================================================================
echo       PERSONALIZED RETAIL RECOMMENDATION AGENT (AI/ML + GenAI Studio)
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python environment and dependencies...
python -c "import torch, sklearn, fastapi, uvicorn; print('PyTorch & Core ML libraries ready.')" 2>nul
if %errorlevel% neq 0 (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
)

echo.
echo [2/3] Starting FastAPI Backend Server on http://127.0.0.1:8000 ...
start "Retail Recommendation Backend (FastAPI)" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 >nul

echo.
echo [3/3] Starting Vite Frontend on http://localhost:5173 ...
start "Retail Recommendation Frontend (React)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ==============================================================================
echo Both Backend and Frontend services have been launched!
echo.
echo - Frontend UI:  http://localhost:5173
echo - API Docs:     http://127.0.0.1:8000/docs
echo - Test Suite:   python backend/test_suite.py
echo ==============================================================================
echo.
pause
