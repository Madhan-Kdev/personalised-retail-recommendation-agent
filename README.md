# Personalized Retail Recommendation Agent

A full-stack retail recommendation application that combines classical recommendation models, neural collaborative filtering, explainable recommendations, conversational shopping assistance, and governance checks.

## Features

- User-based and item-based collaborative filtering
- TF-IDF content recommendations and SVD matrix factorization
- PyTorch NeuMF neural collaborative filtering
- Context-aware hybrid ranking with session and seasonal signals
- Customer personas, recommendation explanations, and shopping chat
- Fairness auditing, human review queue, and audit logging
- React storefront and FastAPI REST API

## Architecture

```text
browser
  |
  v
React + Vite frontend (http://localhost:5173)
  |
  | HTTP requests to http://127.0.0.1:8000/api
  v
FastAPI backend (http://127.0.0.1:8000)
  |
  +-- Recommendation models
  +-- SQLite data and telemetry
  +-- Governance and audit services
```

The frontend API client is configured in `frontend/src/services/api.js`. It connects to the backend at `http://127.0.0.1:8000/api`.

## Prerequisites

- Windows PowerShell
- Python 3.10 or later (Python 3.12 recommended)
- Node.js 18 or later, including npm

## First-time setup

Run these commands once from the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd frontend
npm install
cd ..
```

If PowerShell prevents activation, open it with an execution policy for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Start the complete application

Use the included launcher to start the backend and frontend together:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-app.ps1
```

The launcher verifies the Python virtual environment and required packages, then starts both services in the background.

Open these addresses after running the command:

| Service | Address |
| --- | --- |
| Storefront | http://localhost:5173 |
| Backend API | http://127.0.0.1:8000 |
| Interactive API documentation | http://127.0.0.1:8000/docs |

## Start services manually

Open two PowerShell terminals in the project root.

### Backend

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

## Deploy to Streamlit Community Cloud

Streamlit Community Cloud runs one Streamlit application, so this repository includes `streamlit_app.py`. It uses the same database, recommendation models, explanations, and conversational agent as the FastAPI backend; it does not start the React or FastAPI development servers.

1. Create a GitHub repository and push this project to it. The Git steps are below.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Select **Create app** and select your repository and branch.
4. Set **Main file path** to `streamlit_app.py`.
5. Select **Deploy**.

Streamlit Community Cloud installs packages from the root `requirements.txt` automatically. The initial launch can take longer because the recommendation models are trained when the app starts.

### Run the Streamlit app locally

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## Publish the project to GitHub

Run these commands from the project root after creating an empty GitHub repository. Replace `YOUR-ACCOUNT` and `YOUR-REPOSITORY` with your GitHub account and repository name.

```powershell
git init
git add .
git commit -m "Prepare Streamlit deployment"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

Do not commit the `venv`, `frontend/node_modules`, generated SQLite database, or secrets. The included `.gitignore` excludes them.

## Stop the application

If you started services manually, use `Ctrl+C` in each terminal.

If you used `start-app.ps1`, stop the services listening on the application ports:

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ }
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastapi'`

The virtual environment is missing backend packages. Install them with:

```powershell
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### `ImportError: DLL load failed while importing _C`

PyTorch is incomplete or incompatible in the virtual environment. Reinstall it from a short folder path because PyTorch contains deeply nested files and Windows can reach its path-length limit when the project is stored in a long path.

```powershell
New-Item -ItemType Junction -Path E:\v -Target "$PWD\venv"
E:\v\Scripts\python.exe -m pip install --force-reinstall --no-deps torch
```

Then start the backend again. `E:\v` is a junction to the same `venv`; it does not create a second environment.

### Frontend reports API or network errors

Confirm the backend is running at `http://127.0.0.1:8000/docs`, then restart the frontend. The frontend expects the backend on port `8000`.

## Tests

Run the backend verification suite from the project root:

```powershell
.\venv\Scripts\python.exe backend\test_suite.py
```

## Project layout

```text
backend/                 FastAPI application, data layer, ML models, and governance services
frontend/                React and Vite storefront
start-app.ps1            One-command launcher for backend and frontend
run_demo.bat             Legacy Windows launcher
backend/requirements.txt Python dependencies
```
