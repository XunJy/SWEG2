# P2 - Room Booking System - Group 4
## Table of Contents
TBD

## 1 - Running the System
### 1.1 - Setup 
The server and UI require various packages including flask, uvicorn, and customtkinter (A full list of these packages can be found in the requirements.txtx), to run the system, install it on a local machine using the command:
```bash
pip install -r requirements.txt
```
### 1.2 - Running the server
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
### 1.3 - Running the UI Client
Please Ensure the Server is running before connecting the client
From Root Directory, Run the main UI as a package module as so:
```bash
python -m UI.main_ui
```

### 1.4 - Running the Unit Tests
TBD

Anything else anyone feels needs added to this ReadMe feel free to