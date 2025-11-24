import uuid

from app.db.database import get_db_connection
from app.logs import log_action
from app.models.user import is_admin


# -------------------------
# ROOM CRUD OPERATIONS
# -------------------------


def create_room(user_id, number, building, capacity, status="available", open_time=None, close_time=None):
    """Create a room with all its attributes (privileged action)."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        if not is_admin(user_id):
            raise PermissionError("Access denied: system admin privileges required.")

        room_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO room (room_id, number, building, capacity, status, open_time, close_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (room_id, number, building, capacity, status, open_time, close_time),
        )

        log_action(
            user_id,
            f"Created room {room_id} ({number}, {building}, capacity {capacity}, status {status})",
        )
        return room_id


def read_rooms():
    """Fetch all rooms with metadata."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT room_id, number, building, capacity, status, open_time, close_time FROM room"
        )
        rows = cursor.fetchall()

    return [
        {
            "room_id": row[0],
            "number": row[1],
            "building": row[2],
            "capacity": row[3],
            "status": row[4],
            "open_time": row[5],
            "close_time": row[6],
        }
        for row in rows
    ]


def read_room(room_id):
    """Fetch a specific room by ID."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT room_id, number, building, capacity, status, open_time, close_time FROM room WHERE room_id = ?",
            (room_id,),
        )
        row = cursor.fetchone()

    if not row:
        return None

    return {
        "room_id": row[0],
        "number": row[1],
        "building": row[2],
        "capacity": row[3],
        "status": row[4],
        "open_time": row[5],
        "close_time": row[6],
    }


def update_room(
    user_id,
    room_id,
    number=None,
    building=None,
    capacity=None,
    status=None,
    open_time=None,
    close_time=None,
):
    """Update one or more room attributes (system admin only)."""

    if not is_admin(user_id):
        raise PermissionError("Access denied: admin privileges required.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM room WHERE room_id = ?", (room_id,))
        if not cursor.fetchone():
            raise ValueError("Room not found.")

        updates = []
        params = []

        if number is not None:
            updates.append("number = ?")
            params.append(number)
        if building is not None:
            updates.append("building = ?")
            params.append(building)
        if capacity is not None:
            updates.append("capacity = ?")
            params.append(capacity)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if open_time is not None:
            updates.append("open_time = ?")
            params.append(open_time)
        if close_time is not None:
            updates.append("close_time = ?")
            params.append(close_time)

        if not updates:
            return

        query = f"UPDATE room SET {', '.join(updates)} WHERE room_id = ?"
        params.append(room_id)
        cursor.execute(query, params)
        log_action(user_id, f"Updated room {room_id}: {', '.join(updates)}")


def delete_room(user_id, room_id):
    """Delete a room (system admin only)."""

    with get_db_connection() as conn:
        cursor = conn.cursor()

        if not is_admin(user_id):
            raise PermissionError("Access denied: admin privileges required.")

        cursor.execute("DELETE FROM room WHERE room_id = ?", (room_id,))
        log_action(user_id, f"Deleted room {room_id}")
