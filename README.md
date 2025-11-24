## 📌 Updates (2025-11-24—Admin_v1)
1. Added a new `admin` attribute to the User class to distinguish between regular users and administrators.

2. Updated the login logic to check the user's `admin` attribute and redirect them to either the regular user interface or the administrator interface accordingly.

3. Added a **Logout** button at the bottom of the function menu for both administrators and regular users.

4. Created an initial administrator page  **admin_page.py** that shares the same left-side navigation menu as regular users, but currently includes only the Logout option.
5. Created an initial administrator account for test.  
   - **Username:** Admin  
   - **Password:** Admin  
   This account can be used to access the administrator interface during development.
6. You may also turn any existing user into an administrator by modifying the `admin` field in the `user` table of the database.
## 📌 Updates (2025-11-24)

1. Connected most static pages to the backend.
2. Forwarded `user_id` during login in preparation for the upcoming user invitation feature.
3. Improved the sidebar slide-out animation.
4. Fixed a bug in both by-date and by-room booking where incorrect room availability logic caused available rooms not to display properly.
5. Added a “Make this a public event” button to both booking methods.
6. Updated the Location label on the My Booking page to display the room name instead.
7. Added an “Invite Users” button to each booking entry on the My Booking page (feature not yet fully implemented).
8. Modified Room-related components to prepare for upcoming admin functionality.

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