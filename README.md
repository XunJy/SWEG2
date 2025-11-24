# Room Booking System

A Python-based prototype for managing room bookings with organiser/attendee roles. It includes a FastAPI server backed by SQLite/SQLModel, a simple terminal client, and automated tests covering the core user journey.

## Running the server

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API locally:

```bash
uvicorn app.api.server:app --reload
```

Interactive documentation is available at http://127.0.0.1:8000/docs once the server is running.

## Terminal client

A small Typer-based CLI is provided to exercise the API:

```bash
python -m UI.cli --help
```

Example flow (with the server running):

```bash
python -m UI.cli create-user
python -m UI.cli create-room
python -m UI.cli create-booking
python -m UI.cli bookings
python -m UI.cli register
```

## Testing

Run the automated integration test suite:

```bash
pytest
```

The tests reset the SQLite database for isolation and validate user creation, booking creation, and attendee registration with capacity limits.
