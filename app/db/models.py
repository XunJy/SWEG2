import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Generator, Iterable, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


class Role(str, Enum):
    organiser = "organiser"
    attendee = "attendee"
    admin = "admin"


@dataclass
class User:
    id: str
    full_name: str
    email: str
    role: Role
    created_at: datetime


@dataclass
class Room:
    id: str
    name: str
    building: Optional[str]
    capacity: int
    facilities: List[str]


@dataclass
class Booking:
    id: str
    organiser_id: str
    room_id: str
    start_time: datetime
    end_time: datetime
    title: str
    description: Optional[str]
    is_public: bool


@dataclass
class Registration:
    booking_id: str
    user_id: str
    is_organiser: bool
    registered_at: datetime


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    with get_connection() as conn:
        yield conn


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS room (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                building TEXT,
                capacity INTEGER NOT NULL,
                facilities TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS booking (
                id TEXT PRIMARY KEY,
                organiser_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                is_public INTEGER NOT NULL,
                FOREIGN KEY (organiser_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS registration (
                booking_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                is_organiser INTEGER NOT NULL,
                registered_at TEXT NOT NULL,
                PRIMARY KEY (booking_id, user_id),
                FOREIGN KEY (booking_id) REFERENCES booking(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
            )
            """
        )


def new_id() -> str:
    return str(uuid.uuid4())
