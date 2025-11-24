"""Terminal client for the room booking service.

Run with:
    python -m UI.cli --help
"""

from datetime import datetime
from typing import Optional

import requests
import typer

API_BASE = "http://127.0.0.1:8000"
app = typer.Typer(add_completion=False)


def _handle_response(response: requests.Response):
    if response.ok:
        typer.echo(response.json())
    else:
        typer.echo(f"Error {response.status_code}: {response.text}")


@app.command()
def create_user(
    full_name: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    role: str = typer.Option("attendee", prompt=True, help="attendee, organiser, or admin"),
):
    """Create a new user account."""

    payload = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
    }
    resp = requests.post(f"{API_BASE}/users", json=payload)
    _handle_response(resp)


@app.command()
def login(email: str = typer.Option(..., prompt=True), password: str = typer.Option(..., prompt=True, hide_input=True)):
    """Validate credentials and show the matching user."""

    resp = requests.post(f"{API_BASE}/login", json={"email": email, "password": password})
    _handle_response(resp)


@app.command()
def create_room(
    name: str = typer.Option(..., prompt=True),
    building: Optional[str] = typer.Option(None, prompt="Building (blank to skip)", show_default=False),
    capacity: int = typer.Option(..., prompt=True),
    facilities: Optional[str] = typer.Option("", help="Comma separated list of facilities"),
):
    """Create a room that can be booked."""

    payload = {
        "name": name,
        "building": building or None,
        "capacity": capacity,
        "facilities": [f.strip() for f in facilities.split(",") if f.strip()],
    }
    resp = requests.post(f"{API_BASE}/rooms", json=payload)
    _handle_response(resp)


@app.command("rooms")
def list_rooms():
    """List available rooms."""

    resp = requests.get(f"{API_BASE}/rooms")
    _handle_response(resp)


@app.command()
def create_booking(
    organiser_id: str = typer.Option(..., prompt=True),
    room_id: str = typer.Option(..., prompt=True),
    title: str = typer.Option(..., prompt=True),
    start: str = typer.Option(..., prompt="Start time (YYYY-MM-DD HH:MM)"),
    end: str = typer.Option(..., prompt="End time (YYYY-MM-DD HH:MM)"),
    description: Optional[str] = typer.Option(None, prompt=False),
    public: bool = typer.Option(True, help="Is the booking public?"),
):
    """Create a booking as an organiser."""

    payload = {
        "organiser_id": organiser_id,
        "room_id": room_id,
        "title": title,
        "start_time": datetime.fromisoformat(start).isoformat(),
        "end_time": datetime.fromisoformat(end).isoformat(),
        "description": description,
        "is_public": public,
    }
    resp = requests.post(f"{API_BASE}/bookings", json=payload)
    _handle_response(resp)


@app.command("bookings")
def list_bookings():
    """List all bookings with attendee counts."""

    resp = requests.get(f"{API_BASE}/bookings")
    _handle_response(resp)


@app.command()
def register(booking_id: str = typer.Option(..., prompt=True), user_id: str = typer.Option(..., prompt=True)):
    """Register the given user for the selected booking."""

    resp = requests.post(f"{API_BASE}/bookings/{booking_id}/register", params={"user_id": user_id})
    _handle_response(resp)


if __name__ == "__main__":
    app()
