from app.logs import log_action
from app.models.user import UserRead
from app.db.database import get_db_connection
from app.models.invite import update_invite_status
from pydantic import BaseModel

#-------------------------
# USER-BOOKING MODELS
#-------------------------
class UserBookingCreate(BaseModel):
    user_id: str
    booking_id: str
    organiser: bool = False

class UserBookingUpdate(BaseModel):
    organiser: bool

#-------------------------
# USER-BOOKING CRUD
#-------------------------
DB_PATH = 'database.db' 
# CREATE

def create_user_booking(user_id, booking_id, organiser=False):
    """Create a link between a user and a booking."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                INSERT INTO user_booking (user_id, booking_id, organiser)
                VALUES (?, ?, ?)
            """, (user_id, booking_id, int(organiser)))

        log_action("CREATE_USER_BOOKING",
                    f"User {user_id} linked to booking {booking_id} (organiser={organiser})")


# READ
def get_users_for_booking(booking_id):
    """Return a list of (UserRead, organiser) linked to a booking."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.first_name, u.last_name, u.email,
                   u.admin,
                   ub.organiser
            FROM user_booking ub
            JOIN user u ON ub.user_id = u.user_id
            WHERE ub.booking_id = ?
        """, (booking_id,))

        rows = cursor.fetchall()

        users = []
        for row in rows:
            user = UserRead(
                user_id=row[0],
                first_name=row[1],
                last_name=row[2],
                email=row[3],
                admin=bool(row[4])
            )
            organiser = bool(row[5])
            users.append((user, organiser))

        return users


def get_bookings_for_user(user_id):
    """Return a list of booking IDs linked to a user."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT booking_id, organiser
            FROM user_booking
            WHERE user_id = ?
        """, (user_id,))

        rows = cursor.fetchall()

        return [(booking_id, bool(organiser)) for booking_id, organiser in rows]

# UPDATE
def update_user_booking(user_id, booking_id, organiser):
    """Update the organiser flag for a user-booking link."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
                UPDATE user_booking
                SET organiser = ?
                WHERE user_id = ? AND booking_id = ?
            """, (int(organiser), user_id, booking_id))

        log_action(
                user_id,  
                f"Updated organiser status for booking {booking_id} → {organiser}" 
            )


# DELETE
def delete_user_booking(user_id, booking_id):
    """Delete a user–booking link, change invtie status to declined """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
                DELETE FROM user_booking
                WHERE user_id = ? AND booking_id = ?
            """, (user_id, booking_id))
            
        update_invite_status(
                user_id, 
                booking_id, 
                'declined'
            )
        log_action(
                user_id,  
                f"Left booking {booking_id}"  
            )
