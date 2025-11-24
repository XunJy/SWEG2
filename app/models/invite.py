from uuid import uuid4
from pydantic import BaseModel

from app.db.database import get_db_connection
from app.logs import log_action


class Invite(BaseModel):
    invite_id: str
    booking_id: str
    user_id: str
    status: str
    kind: str = "invite"  # invite or request


# --------------------
# CRUD
# --------------------

def create_invite(booking_id: str, user_id: str, status: str = "pending", kind: str = "invite") -> Invite:
    invite_id = str(uuid4())

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO invite (invite_id, booking_id, user_id, status, kind)
            VALUES (?, ?, ?, ?, ?)
            """,
            (invite_id, booking_id, user_id, status, kind),
        )
        conn.commit()

        log_action(user_id, f"Created {kind} {invite_id} for booking {booking_id}")

        return Invite(
            invite_id=invite_id,
            booking_id=booking_id,
            user_id=user_id,
            status=status,
            kind=kind,
        )


def get_invite_by_id(invite_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT invite_id, booking_id, user_id, status, kind FROM invite WHERE invite_id = ?",
            (invite_id,),
        )

        row = cursor.fetchone()
        return Invite(*row) if row else None


def get_all_invites():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id, booking_id, user_id, status, kind FROM invite")

        rows = cursor.fetchall()
        return [Invite(*row) for row in rows]


def get_invites_by_booking(booking_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT invite_id, booking_id, user_id, status, kind FROM invite WHERE booking_id = ?",
            (booking_id,),
        )

        rows = cursor.fetchall()
        return [Invite(*row) for row in rows]


def get_join_requests_for_booking(booking_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT invite_id, booking_id, user_id, status, kind
            FROM invite
            WHERE booking_id = ? AND kind = 'request'
            ORDER BY status ASC
            """,
            (booking_id,),
        )
        rows = cursor.fetchall()
        return [Invite(*row) for row in rows]


def get_invites_by_user(user_id: str) -> list[Invite]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT invite_id, booking_id, user_id, status, kind
            FROM invite
            WHERE user_id = ? AND kind = 'invite'
            """,
            (user_id,),
        )

        rows = cursor.fetchall()
        return [
            Invite(
                invite_id=row[0],
                booking_id=row[1],
                user_id=row[2],
                status=row[3],
                kind=row[4],
            )
            for row in rows
        ]


def user_already_linked(user_id: str, booking_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM user_booking WHERE user_id = ? AND booking_id = ?",
            (user_id, booking_id),
        )
        return cursor.fetchone() is not None


def existing_pending_request(user_id: str, booking_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM invite
            WHERE user_id = ? AND booking_id = ?
              AND kind = 'request' AND status = 'pending'
            """,
            (user_id, booking_id),
        )
        return cursor.fetchone() is not None


def create_join_request(booking_id: str, user_id: str) -> Invite:
    if user_already_linked(user_id, booking_id):
        raise ValueError("User already participating in this booking")

    if existing_pending_request(user_id, booking_id):
        raise ValueError("Request already pending")

    return create_invite(booking_id, user_id, status="pending", kind="request")


def update_invite_status(invite_id, new_status):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE invite
            SET status = ?
            WHERE invite_id = ?
            """,
            (new_status, invite_id),
        )
        conn.commit()

        updated = cursor.rowcount > 0

        if updated:
            log_action("system", f"Updated invite {invite_id} status to {new_status}")

        return updated


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
