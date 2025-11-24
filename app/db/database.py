import os
import sqlite3
from contextlib import contextmanager
from secrets import token_urlsafe
import uuid

import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

#-------------------------
# DATABASE INITIALISATION
#-------------------------

# Context manager for database connection secure creation and closing
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit() # Commit changes automatically after block ends
    except sqlite3.Error as DBInitError:
        print("Error in connecting to DB: ", DBInitError)
    finally:
        conn.close()

def init_db():
    """Initialise all database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        #--------------
        # PRIMARY TABLES
        #--------------

        # Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                user_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL CHECK (LENGTH(password) > 8),
                recovery_code TEXT,
                admin INTEGER NOT NULL CHECK (admin IN (0,1))
            );
        """)

        # Rooms
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room (
                room_id TEXT PRIMARY KEY,
                number TEXT NOT NULL,
                building TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'available',
                open_time TEXT,
                close_time TEXT
            );
        """)

        # Backfill new columns for existing deployments
        existing_room_columns = {row[1] for row in cursor.execute("PRAGMA table_info(room)").fetchall()}
        if "status" not in existing_room_columns:
            cursor.execute("ALTER TABLE room ADD COLUMN status TEXT NOT NULL DEFAULT 'available'")
        if "open_time" not in existing_room_columns:
            cursor.execute("ALTER TABLE room ADD COLUMN open_time TEXT")
        if "close_time" not in existing_room_columns:
            cursor.execute("ALTER TABLE room ADD COLUMN close_time TEXT")

        # Bookings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking (
                booking_id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                public BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (room_id) REFERENCES room(room_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        # Invites (also used for join requests via the "kind" column)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invite (
                invite_id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending','accepted', 'declined')),
                kind TEXT NOT NULL DEFAULT 'invite' CHECK (kind IN ('invite','request')),
                FOREIGN KEY (booking_id) REFERENCES booking(booking_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (user_id) REFERENCES user(user_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        # Backfill new invite "kind" column for existing deployments
        existing_invite_columns = {row[1] for row in cursor.execute("PRAGMA table_info(invite)").fetchall()}
        if "kind" not in existing_invite_columns:
            cursor.execute("ALTER TABLE invite ADD COLUMN kind TEXT NOT NULL DEFAULT 'invite'")
        
        # Facilities (in rooms)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facility (
                facility_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        """)

        #--------------
        # JOINING TABLES
        #--------------

        # Users - Bookings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_booking (
                user_id TEXT NOT NULL,
                booking_id TEXT NOT NULL,
                organiser INTEGER NOT NULL CHECK (organiser IN (0,1)),
                PRIMARY KEY (user_id, booking_id),
                FOREIGN KEY (user_id) REFERENCES user(user_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)
        
        # Trigger ensuring attendee is inserted into user_booking when an invite is updated to accepted
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS add_participant_after_invite_accept
            AFTER UPDATE ON invite
            FOR EACH ROW
            WHEN NEW.status = 'accepted'
            BEGIN
                INSERT OR IGNORE INTO user_booking (user_id, booking_id, organiser)
                VALUES (NEW.user_id, NEW.booking_id, 0);
            END;
        """)
        
        # Rooms - Facilities
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_facility (
                room_id TEXT NOT NULL,
                facility_id TEXT NOT NULL,
                PRIMARY KEY (room_id, facility_id),
                FOREIGN KEY (room_id) REFERENCES room(room_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (facility_id) REFERENCES facility(facility_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        # Seed an initial admin account if none exists
        cursor.execute("SELECT 1 FROM user WHERE admin = 1 LIMIT 1")
        existing_admin = cursor.fetchone()
        if not existing_admin:
            admin_id = str(uuid.uuid4())
            hashed_password = bcrypt.hashpw("Admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                """
                INSERT OR IGNORE INTO user (user_id, first_name, last_name, email, password, recovery_code, admin)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    admin_id,
                    "System",
                    "Administrator",
                    "Admin",
                    hashed_password,
                    token_urlsafe(16),
                ),
            )

