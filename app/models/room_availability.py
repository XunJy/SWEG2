from datetime import datetime, timedelta
from room import Room
from database import get_db_connection

DB_PATH = 'database.db' 

#-------------------------
# ROOM AVAILABILITY
#-------------------------
    
def get_available_rooms_at(date, start_time_str, duration_minutes=30):
    """
    Returns a list of Room objects that are available at a specific date and start time.
    
    Parameters:
    - date: string "YYYY-MM-DD"
    - start_time_str: string "HH:MM"
    - duration_minutes: length of desired booking (default 30)
    """
    desired_start = datetime.fromisoformat(f"{date}T{start_time_str}")
    desired_end = desired_start + timedelta(minutes=duration_minutes)

    available_rooms = []
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Fetch all rooms
        cursor.execute("SELECT room_id, number, building, capacity FROM room")
        rooms = [Room(*row) for row in cursor.fetchall()]

        for room in rooms:
            # Fetch bookings for this room on the given date
            cursor.execute("""
                SELECT start_time, end_time 
                FROM booking 
                WHERE room_id = ? AND date(start_time) = ?
            """, (room.room_id, date))
            
            booked_times = [(datetime.fromisoformat(start), datetime.fromisoformat(end))
                            for start, end in cursor.fetchall()]

            # Check if desired slot overlaps any existing booking
            overlap = any(desired_start < booked_end and booked_start < desired_end for booked_start, booked_end in booked_times)
            if not overlap:
                available_rooms.append(room)
        
    return available_rooms

# Example usage:
# rooms = get_available_rooms_at("2025-11-20", "10:00", duration_minutes=30)
# for room in rooms:
#     print(room)

#Check a specific room availability
def is_room_available(room_id, date, start_time_str, duration_minutes=30):
    desired_start = datetime.fromisoformat(f"{date}T{start_time_str}")
    desired_end = desired_start + timedelta(minutes=duration_minutes)
        
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Fetch bookings for this room on the given date
        cursor.execute("""
                SELECT start_time, end_time 
                FROM booking 
                WHERE room_id = ? AND date(start_time) = ?
            """, (room_id, date))
            
        booked_times = [(datetime.fromisoformat(start), datetime.fromisoformat(end))
                            for start, end in cursor.fetchall()]

            # Check if desired slot overlaps any existing booking
        overlap = any(desired_start < booked_end and booked_start < desired_end for booked_start, booked_end in booked_times)
    
    return not overlap
    
# Example usage:
# available = is_room_available(1, "2025-11-20", "10:00", duration_minutes=30)
# print("Room available:", available)