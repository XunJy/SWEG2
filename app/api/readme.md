# app/api/readme.md

## Purpose
Instructions to run the FastAPI server from this repository.

## Prerequisites
- Python 3.8+
- pip

(Recommended) create and activate a virtual environment:
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate

## Install
If the project includes requirements:
```bash
pip install -r requirements.txt
```
Or install minimal dependencies:
```bash
pip install fastapi uvicorn
```

## Run (development)
From the repository root run:
```bash
uvicorn app.api.server:app --reload
```
- `app.api.server:app` — Python import path to the ASGI application.
- `--reload` — automatically reloads on code changes (development only).

Default bind: http://127.0.0.1:8000

To change host/port:
```bash
uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8080
```