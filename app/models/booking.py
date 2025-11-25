from datetime import datetime, timedelta
from uuid import uuid4
from app.db.database import get_db_connection
from app.logs import log_action


def parse_datetime(value: str) -> datetime:
    """Parse a datetime string that may use multiple formats.

    The UI currently sends "%Y-%m-%d %H:%M:%S", but existing data or future
    clients could include ISO 8601 "T" separators or omit seconds. Normalising
    to datetime objects ensures availability checks aren't thrown off by string
    ordering quirks.
    """

    # Fast path for already-parsed datetimes
    if isinstance(value, datetime):
        return value

    value = str(value).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    # Try the flexible ISO parser as a last resort (handles timezone offsets)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Invalid datetime format: {value}")

#-------------
# BOOKING CRUD
#-------------

# CREATE
def create_booking(room_id, start_time, end_time, name, description=None, public=False, user_id="system"):
    booking_id = str(uuid4())
    public_flag = 1 if public else 0 # Pydantic to SQLite conversion

    # Normalise incoming times to a consistent format for reliable comparisons
    start_dt = parse_datetime(start_time)
    end_dt = parse_datetime(end_time)
    if end_dt <= start_dt:
        raise ValueError("End time must be after start time.")

    normalized_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    normalized_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check for overlapping bookings
        cursor.execute(
            """
            SELECT booking_id
            FROM booking
            WHERE room_id = ?
            AND start_time < ?
            AND end_time > ?
        """,
            (room_id, normalized_end, normalized_start),
        )
        overlap = cursor.fetchone()

        # Raise error if overlapping booking exists
        if overlap:
            raise ValueError(f"Room {room_id} is already booked during this time.")

        # Insert the booking
        cursor.execute(
            """
            INSERT INTO booking (booking_id, room_id, start_time, end_time, name, description, public)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (booking_id, room_id, normalized_start, normalized_end, name, description, public_flag),
        )

    visibility = "public" if public else "private" # For logging public/private as a string
    log_action(
        user_id,
        f"Created {visibility} booking {booking_id} in room {room_id} from {normalized_start} to {normalized_end}",
    )

    return {
        "booking_id": booking_id,
        "room_id": room_id,
        "name": name,
        "description": description,
        "start_time": normalized_start,
        "end_time": normalized_end,
        "public": public
    }


# READ public bookings that a user is not already attending
def get_public_bookings(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM booking b
            WHERE b.public = 1
            AND b.booking_id NOT IN (
                SELECT booking_id FROM user_booking WHERE user_id = ?
            )
        """, (user_id,))
        rows = cursor.fetchall()

    return [
        {
            "booking_id": row[0],
            "room_id": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "name": row[4],
            "description": row[5],
            "public": bool(row[6])
        }
        for row in rows
    ]

# Read a booking by its id
def read_booking(booking_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, b.room_id, b.start_time, b.end_time, b.name, b.description, b.public,
                   r.number, r.building, r.capacity
            FROM booking b
            JOIN room r ON b.room_id = r.room_id
            WHERE b.booking_id = ?
        """, (booking_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "booking_id": row[0],
        "room_id": row[1],
        "start_time": row[2],
        "end_time": row[3],
        "name": row[4],
        "description": row[5],
        "public": bool(row[6]),
        "room_number": row[7],
        "room_building": row[8],
        "room_capacity": row[9],
    }


# READ bookings by room_id - not updated
# def read_booking_by_room(room_id):
#     with get_db_connection() as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT b.booking_id, b.name, b.description, b.start_time, b.end_time,
#                 r.room_id, r.number, r.building, r.capacity
#             FROM booking b
#             JOIN room r ON b.room_id = r.room_id
#             WHERE b.room_id = ?
#         """, (room_id,))
#         rows = cursor.fetchall()

#     if not rows:
#         return []

#     bookings = []
#     for row in rows:
#         booking_id, name, description, start_time, end_time, room_id, number, building, capacity = row
#         room = Room(number, building, capacity)
#         bookings.append(Booking(booking_id, room, name, description, start_time, end_time))

#     return bookings

# READ bookings by user
def read_bookings_by_user(user_id):
    """
    Returns a list of Booking objects for a given user from the user_booking table.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT booking_id, room_id, start_time, end_time, name, description, public
            FROM booking
            JOIN user_booking USING (booking_id)
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

    return [
        {
            "booking_id": r[0],
            "room_id": r[1],
            "start_time": r[2],
            "end_time": r[3],
            "name": r[4],
            "description": r[5],
            "public": bool(r[6])
        }
        for r in rows
    ]

# Retrieve all bookings
def read_all_bookings():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT booking_id, room_id, start_time, end_time, name, description, public
            FROM booking
        """)
        rows = cursor.fetchall()

    return [
        {
            "booking_id": row[0],
            "room_id": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "name": row[4],
            "description": row[5],
            "public": bool(row[6])
        }
        for row in rows
    ]

# Return whether a room is free during a given time slot (check if a booking exists then)
def get_conflicting_bookings(room_id, start_time, end_time):
    request_start = parse_datetime(start_time)
    request_end = parse_datetime(end_time)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT start_time, end_time FROM booking WHERE room_id = ?",
            (room_id,),
        )
        for existing_start, existing_end in cursor.fetchall():
            try:
                existing_start_dt = parse_datetime(existing_start)
                existing_end_dt = parse_datetime(existing_end)
            except ValueError:
                # Skip malformed rows rather than blocking all availability
                continue

            if existing_start_dt < request_end and existing_end_dt > request_start:
                return True

    return False
    
# Generates suggested booking slots on a given day
def generate_time_slots_for_day(date_str: str, start_hour=9, end_hour=17):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    slots = []

    current = date.replace(hour=start_hour, minute=0, second=0)
    end_time = date.replace(hour=end_hour, minute=0, second=0)

    while current < end_time:
        slot_start = current.strftime("%Y-%m-%d %H:%M:%S")
        current += timedelta(hours=1)
        slot_end = current.strftime("%Y-%m-%d %H:%M:%S")

        slots.append((slot_start, slot_end))

    return slots

# UPDATE
    # Users can only update the name and description of a booking - changing time requires creating a new booking
def update_booking_name(booking_id, new_name, user_id="system"):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE booking
            SET name = ?
            WHERE booking_id = ?
        """, (new_name, booking_id))

    log_action(user_id, f"Renamed booking {booking_id} to '{new_name}'")
    return True

def update_booking_description(booking_id, new_description, user_id="system"):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE booking
            SET description = ?
            WHERE booking_id = ?
        """, (new_description, booking_id))

    log_action(user_id, f"Renamed booking {booking_id} to '{new_description}'")
    return True

# DELETE
def delete_booking(booking_id, user_id="system"):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM booking
            WHERE booking_id = ?
        """, (booking_id,))

    log_action(user_id, f"Deleted booking {booking_id}")
    return cursor.rowcount > 0

