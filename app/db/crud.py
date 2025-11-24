import json
from datetime import datetime
from typing import Iterable, List, Optional

import bcrypt
import sqlite3

from .models import Booking, Registration, Role, Room, User, get_connection, new_id


# -------------------------
# Utilities
# -------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(hashed: str, plain: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"],
        role=Role(row["role"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def row_to_room(row: sqlite3.Row) -> Room:
    return Room(
        id=row["id"],
        name=row["name"],
        building=row["building"],
        capacity=row["capacity"],
        facilities=json.loads(row["facilities"]),
    )


def row_to_booking(row: sqlite3.Row) -> Booking:
    return Booking(
        id=row["id"],
        organiser_id=row["organiser_id"],
        room_id=row["room_id"],
        start_time=datetime.fromisoformat(row["start_time"]),
        end_time=datetime.fromisoformat(row["end_time"]),
        title=row["title"],
        description=row["description"],
        is_public=bool(row["is_public"]),
    )


def row_to_registration(row: sqlite3.Row) -> Registration:
    return Registration(
        booking_id=row["booking_id"],
        user_id=row["user_id"],
        is_organiser=bool(row["is_organiser"]),
        registered_at=datetime.fromisoformat(row["registered_at"]),
    )


# -------------------------
# User operations
# -------------------------

def create_user(*, full_name: str, email: str, password: str, role: Role) -> User:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user WHERE email = ?", (email,))
        if cursor.fetchone():
            raise ValueError("Email already exists")

        user_id = new_id()
        now = datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT INTO user(id, full_name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, full_name, email, hash_password(password), role.value, now),
        )
        cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        return row_to_user(cursor.fetchone())


def authenticate(*, email: str, password: str) -> Optional[User]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and verify_password(row["password_hash"], password):
            return row_to_user(row)
    return None


def list_users() -> List[User]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user ORDER BY created_at")
        return [row_to_user(r) for r in cursor.fetchall()]


def get_user(user_id: str) -> Optional[User]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return row_to_user(row) if row else None


# -------------------------
# Room operations
# -------------------------

def create_room(
    *, name: str, building: Optional[str], capacity: int, facilities: Iterable[str]
) -> Room:
    if capacity <= 0:
        raise ValueError("Capacity must be positive")

    with get_connection() as conn:
        cursor = conn.cursor()
        room_id = new_id()
        cursor.execute(
            """
            INSERT INTO room(id, name, building, capacity, facilities)
            VALUES (?, ?, ?, ?, ?)
            """,
            (room_id, name, building, capacity, json.dumps(list(facilities))),
        )
        cursor.execute("SELECT * FROM room WHERE id = ?", (room_id,))
        return row_to_room(cursor.fetchone())


def list_rooms() -> List[Room]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM room ORDER BY name")
        return [row_to_room(r) for r in cursor.fetchall()]


def get_room(room_id: str) -> Optional[Room]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM room WHERE id = ?", (room_id,))
        row = cursor.fetchone()
        return row_to_room(row) if row else None


# -------------------------
# Booking operations
# -------------------------

def _ensure_organiser(user_id: str) -> User:
    organiser = get_user(user_id)
    if organiser is None:
        raise ValueError("Organiser not found")
    if organiser.role not in {Role.organiser, Role.admin}:
        raise PermissionError("Only organisers can create bookings")
    return organiser


def _ensure_valid_slot(start_time: datetime, end_time: datetime) -> None:
    if end_time <= start_time:
        raise ValueError("End time must be after start time")


def _room_has_conflict(room_id: str, start_time: datetime, end_time: datetime) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM booking
            WHERE room_id = ?
              AND start_time < ?
              AND end_time   > ?
            LIMIT 1
            """,
            (room_id, end_time.isoformat(), start_time.isoformat()),
        )
        return cursor.fetchone() is not None


def create_booking(
    *,
    organiser_id: str,
    room_id: str,
    start_time: datetime,
    end_time: datetime,
    title: str,
    description: Optional[str],
    is_public: bool,
) -> Booking:
    organiser = _ensure_organiser(organiser_id)
    room = get_room(room_id)
    if room is None:
        raise ValueError("Room not found")

    _ensure_valid_slot(start_time, end_time)
    if _room_has_conflict(room_id, start_time, end_time):
        raise ValueError("Room already booked for this timeslot")

    booking_id = new_id()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO booking(id, organiser_id, room_id, start_time, end_time, title, description, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                booking_id,
                organiser.id,
                room_id,
                start_time.isoformat(),
                end_time.isoformat(),
                title,
                description,
                int(is_public),
            ),
        )
        cursor.execute(
            """
            INSERT INTO registration(booking_id, user_id, is_organiser, registered_at)
            VALUES (?, ?, 1, ?)
            """,
            (booking_id, organiser.id, datetime.utcnow().isoformat()),
        )
        cursor.execute("SELECT * FROM booking WHERE id = ?", (booking_id,))
        booking_row = cursor.fetchone()
    return row_to_booking(booking_row)


def list_bookings() -> List[Booking]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM booking ORDER BY start_time")
        return [row_to_booking(r) for r in cursor.fetchall()]


def get_booking(booking_id: str) -> Optional[Booking]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM booking WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        return row_to_booking(row) if row else None


def registrations_for_booking(booking_id: str) -> List[Registration]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registration WHERE booking_id = ?", (booking_id,))
        return [row_to_registration(r) for r in cursor.fetchall()]


def register_for_booking(*, booking_id: str, user_id: str) -> Registration:
    booking = get_booking(booking_id)
    if booking is None:
        raise ValueError("Booking not found")

    user = get_user(user_id)
    if user is None:
        raise ValueError("User not found")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM registration WHERE booking_id = ? AND user_id = ?",
            (booking_id, user_id),
        )
        if cursor.fetchone():
            raise ValueError("User already registered for this booking")

        room = get_room(booking.room_id)
        if room is None:
            raise ValueError("Room not found")

        cursor.execute(
            "SELECT COUNT(*) FROM registration WHERE booking_id = ?",
            (booking_id,),
        )
        attendee_count = cursor.fetchone()[0]
        if attendee_count >= room.capacity:
            raise ValueError("Room is at full capacity")

        cursor.execute(
            """
            INSERT INTO registration(booking_id, user_id, is_organiser, registered_at)
            VALUES (?, ?, 0, ?)
            """,
            (booking_id, user_id, datetime.utcnow().isoformat()),
        )
        cursor.execute(
            "SELECT * FROM registration WHERE booking_id = ? AND user_id = ?",
            (booking_id, user_id),
        )
        return row_to_registration(cursor.fetchone())
