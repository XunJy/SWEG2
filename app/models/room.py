import uuid
from app.db.database import get_db_connection
from app.models.user import is_admin
from app.logs import log_action
    
#-------------------------
# ROOM CRUD OPERATIONS
#-------------------------

DB_PATH = 'database.db' 

#CREATE
def create_room(user_id, number, building, capacity):
    """Create a room with all its attributes (privileged action)."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if not is_admin(user_id):
            raise PermissionError("Access denied: system admin privileges required.")
        
        room_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO room (room_id, number, building, capacity)
            VALUES (?, ?, ?, ?)
        """, (room_id, number, building, capacity))
        
        log_action(user_id, f"Created room {room_id} ({number}, {building}, capacity {capacity})")
        return room_id

#READ
def read_rooms():
    """Fetch all rooms."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM room")
        return cursor.fetchall()

def read_room(room_id):
    """Fetch a specific room by ID."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM room WHERE room_id = ?", (room_id,))
        return cursor.fetchone()

#UPDATE
def update_room(user_id, room_id, number=None, building=None, capacity=None):
    """Update one or more room attributes (system admin only)."""
    
    if not is_admin(user_id):
        raise PermissionError("Access denied: admin privileges required.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM room WHERE room_id = ?", (room_id,))
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

        if not updates:
            return  # nothing to update

        query = f"UPDATE room SET {', '.join(updates)} WHERE room_id = ?"
        params.append(room_id)
        cursor.execute(query, params)

#DELETE
def delete_room(user_id, room_id):
    """Delete a room (system admin only)."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if not is_admin(user_id):
            raise PermissionError("Access denied: admin privileges required.")
        
        cursor.execute("DELETE FROM room WHERE room_id = ?", (room_id,))