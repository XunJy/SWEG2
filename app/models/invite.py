from uuid import uuid4
from ..logs import log_action
from ..db.database import get_db_connection
from pydantic import BaseModel

DB_PATH = 'database.db' 

#TODO: make the logs show the current user id for logs

#----------------
# INVITE CLASS
#----------------
class Invite(BaseModel):
    invite_id: str
    booking_id: str
    user_id: str
    status: str
    message: str | None = None
    inviter_id: str | None = None

#--------------------
# CRUD
#--------------------

# CREATE
def create_invite(booking_id: str, user_id: str, inviter_id: str | None = None, status: str = 'pending', message: str | None = None) -> Invite:
    invite_id = str(uuid4())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO invite (invite_id, booking_id, user_id, status, message, inviter_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (invite_id, booking_id, user_id, status, message, inviter_id))
        conn.commit() 

        log_action(inviter_id or user_id, f"Created invite {invite_id} for booking {booking_id}")
        
        return Invite(
            invite_id=invite_id,
            booking_id=booking_id,
            user_id=user_id,
            status=status,
            message=message,
            inviter_id=inviter_id,
        )

# READ
def get_invite_by_id(invite_id):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id, booking_id, user_id, status, message, inviter_id FROM invite WHERE invite_id = ?", (invite_id,))
        
        row = cursor.fetchone()
        return Invite(*row) if row else None


def get_all_invites():
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id, booking_id, user_id, status, message, inviter_id FROM invite")
        
        rows = cursor.fetchall()
        return [Invite(*row) for row in rows]


def get_invites_by_booking(booking_id):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id, booking_id, user_id, status, message, inviter_id FROM invite WHERE booking_id = ?", (booking_id,))
    
        rows = cursor.fetchall()
        return [Invite(*row) for row in rows]


def get_invites_by_user(user_id: str) -> list[Invite]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invite_id, booking_id, user_id, status, message, inviter_id
            FROM invite
            WHERE user_id = ?
        """, (user_id,))
        
        rows = cursor.fetchall()
        # Return list of Invite objects using keyword arguments
        return [
            Invite(
                invite_id=row[0],
                booking_id=row[1],
                user_id=row[2],
                status=row[3],
                message=row[4],
                inviter_id=row[5],
            ) for row in rows
        ]



# UPDATE
def update_invite_status(invite_id, new_status):
    from app.models.booking import read_booking
    from app.models.user_booking import create_user_booking

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT booking_id, user_id
            FROM invite
            WHERE invite_id = ?
        """, (invite_id,))
        invite_row = cursor.fetchone()

        if not invite_row:
            return False

        booking_id, user_id = invite_row

        if new_status == "accepted":
            booking = read_booking(booking_id)
            if not booking:
                return False

            attendee_count = booking.get("attendee_count") or 0
            capacity = booking.get("room_capacity") or 0
            if capacity and attendee_count >= capacity:
                raise ValueError("Booking is at full capacity.")

            create_user_booking(user_id, booking_id, organiser=False)

        cursor.execute("""
            UPDATE invite
            SET status = ?
            WHERE invite_id = ?
        """, (new_status, invite_id))
        conn.commit()

        updated = cursor.rowcount > 0

        if updated:
            log_action("system", f"Updated invite {invite_id} status to {new_status}")

        return updated


# DELETE
def delete_invite(invite_id):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invite WHERE invite_id = ?", (invite_id,))
        conn.commit()
        
        deleted = cursor.rowcount > 0
        
        if deleted:
            log_action("system", f"Deleted invite {invite_id}")
            
        return deleted


def delete_invites_by_booking(booking_id):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invite WHERE booking_id = ?", (booking_id,))
        conn.commit()
        
        count = cursor.rowcount
        
        if count > 0:
            log_action("system", f"Deleted {count} invites for booking {booking_id}")
            
        return count
