@echo off
title REETA Desktop Platform

echo ==================================================
echo Starting REETA Backend (FastAPI)...
echo ==================================================
start "REETA Backend" cmd /c "set PYTHONIOENCODING=utf-8 && venv\Scripts\activate && python -m uvicorn api.server:app --host 127.0.0.1 --port 8000"

echo ==================================================
echo Starting REETA Frontend (Electron + React)...
echo ==================================================
cd ui
start "REETA Frontend" cmd /c "npm run electron:dev"

echo Both systems have been launched in background windows.
pause
