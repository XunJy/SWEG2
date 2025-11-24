import os
import threading
import time
from datetime import datetime, timedelta

import pytest
import requests
import uvicorn

from app.db.models import DB_PATH, init_db
from app.api.server import app


@pytest.fixture(scope="session")
def api_server():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    config = uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="error")
    server = uvicorn.Server(config=config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for the server to start accepting connections
    timeout = time.time() + 10
    while not server.started and time.time() < timeout:
        time.sleep(0.1)

    yield "http://127.0.0.1:8001"

    server.should_exit = True
    thread.join(timeout=5)


def test_booking_flow(api_server):
    base = api_server

    organiser = requests.post(
        f"{base}/users",
        json={
            "full_name": "Olivia Organiser",
            "email": "org@example.com",
            "password": "secretpass",
            "role": "organiser",
        },
    ).json()

    attendee = requests.post(
        f"{base}/users",
        json={
            "full_name": "Andy Attendee",
            "email": "andy@example.com",
            "password": "secretpass",
            "role": "attendee",
        },
    ).json()

    extra_attendee = requests.post(
        f"{base}/users",
        json={
            "full_name": "Alex Extra",
            "email": "alex@example.com",
            "password": "secretpass",
            "role": "attendee",
        },
    ).json()

    room = requests.post(
        f"{base}/rooms",
        json={
            "name": "Room 101",
            "building": "Engineering",
            "capacity": 2,
            "facilities": ["Projector", "Whiteboard"],
        },
    ).json()

    start = datetime.utcnow().replace(microsecond=0)
    end = start + timedelta(hours=1)

    booking = requests.post(
        f"{base}/bookings",
        json={
            "organiser_id": organiser["id"],
            "room_id": room["id"],
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "title": "Sprint Planning",
            "description": "Planning the next iteration",
            "is_public": True,
        },
    ).json()

    assert booking["attendee_count"] == 1

    reg_resp = requests.post(
        f"{base}/bookings/{booking['id']}/register",
        params={"user_id": attendee["id"]},
    )
    assert reg_resp.status_code == 201

    booking_after = requests.get(f"{base}/bookings/{booking['id']}").json()
    assert booking_after["attendee_count"] == 2

    full_resp = requests.post(
        f"{base}/bookings/{booking['id']}/register",
        params={"user_id": extra_attendee["id"]},
    )
    assert full_resp.status_code == 400
    assert "full capacity" in full_resp.json()["detail"]
