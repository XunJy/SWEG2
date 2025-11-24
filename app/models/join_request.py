from uuid import uuid4

from pydantic import BaseModel

from app.db.database import get_db_connection
from app.logs import log_action
from app.models.booking import read_booking
from app.models.user_booking import create_user_booking


class JoinRequest(BaseModel):
    request_id: str
    booking_id: str
    user_id: str
    status: str


def create_join_request(booking_id: str, user_id: str) -> JoinRequest:
    booking = read_booking(booking_id)
    if not booking:
        raise ValueError("Booking not found")

    if not booking.get("public"):
        raise ValueError("Only public bookings accept join requests")

    attendee_count = booking.get("attendee_count") or 0
    capacity = booking.get("room_capacity") or 0
    if capacity and attendee_count >= capacity:
        raise ValueError("Booking is at full capacity")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT organiser FROM user_booking WHERE booking_id = ? AND user_id = ?",
            (booking_id, user_id),
        )
        existing_membership = cursor.fetchone()
        if existing_membership:
            raise ValueError("User already joined this booking")

        cursor.execute(
            "SELECT request_id FROM join_request WHERE booking_id = ? AND user_id = ? AND status = 'pending'",
            (booking_id, user_id),
        )
        if cursor.fetchone():
            raise ValueError("A pending request already exists")

        request_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO join_request (request_id, booking_id, user_id, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (request_id, booking_id, user_id),
        )

    log_action(user_id, f"Requested to join booking {booking_id}")
    return JoinRequest(request_id=request_id, booking_id=booking_id, user_id=user_id, status="pending")


def get_join_requests_for_booking(booking_id: str) -> list[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT jr.request_id, jr.user_id, jr.status, u.first_name, u.last_name, u.email, u.admin
            FROM join_request jr
            JOIN user u ON jr.user_id = u.user_id
            WHERE jr.booking_id = ?
        """,
            (booking_id,),
        )
        rows = cursor.fetchall()

    requests = []
    for row in rows:
        requests.append(
            {
                "request_id": row[0],
                "user_id": row[1],
                "status": row[2],
                "first_name": row[3],
                "last_name": row[4],
                "email": row[5],
                "admin": bool(row[6]),
            }
        )

    return requests


def update_join_request_status(request_id: str, new_status: str) -> bool:
    if new_status not in {"accepted", "declined"}:
        raise ValueError("Invalid status")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT booking_id, user_id FROM join_request WHERE request_id = ?",
            (request_id,),
        )
        request_row = cursor.fetchone()
        if not request_row:
            return False

        booking_id, user_id = request_row

        booking = read_booking(booking_id)
        if not booking:
            return False

        attendee_count = booking.get("attendee_count") or 0
        capacity = booking.get("room_capacity") or 0
        if new_status == "accepted" and capacity and attendee_count >= capacity:
            raise ValueError("Booking is at full capacity")

        cursor.execute(
            """
            UPDATE join_request
            SET status = ?
            WHERE request_id = ?
        """,
            (new_status, request_id),
        )

        if new_status == "accepted":
            create_user_booking(user_id, booking_id, organiser=False)

    log_action(user_id, f"Join request {request_id} → {new_status}")
    return True
