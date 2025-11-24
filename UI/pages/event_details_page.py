import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents


@clear_contents
def view_event_details(app, id, caller, booking_id=None, invite=None):
    from UI.pages.events_page import show_events
    from UI.pages.invites_page import show_invites

    back_button = ctk.CTkButton(
        app,
        text="Back",
        width=60,
        height=28,
        fg_color="#0078D7",
        hover_color="#005A9E",
    )

    invite_message = invite.get("message") if invite else None
    inviter_name = invite.get("inviter_name") if invite else None

    if caller == "events":
        back_button.configure(command=lambda: show_events(app))
        booking = fetch_booking(booking_id or id)
    elif caller == "invites":
        back_button.configure(command=lambda: show_invites(app))
        booking = fetch_booking(booking_id)
    elif caller == "bookings":
        from UI.pages.bookings_page import show_my_bookings

        back_button.configure(command=lambda: show_my_bookings(app))
        booking = fetch_booking(id)
    else:
        booking = None
    back_button.pack(padx=55, pady=(10, 10), anchor="w")

    attendees = get_booking_users(booking.get("booking_id") if booking else None) if booking else []
    capacity = booking.get("room_capacity") if booking else None
    attendee_count = booking.get("attendee_count") or len(attendees)

    if booking is None:
        ctk.CTkLabel(app, text="Event not found").pack(pady=(10, 20))
        ctk.CTkButton(app, text="Back to Events", width=100, height=28, command=lambda: show_events(app)).pack(pady=(10, 10))
    else:
        ctk.CTkLabel(app, text=booking["name"], font=("Arial", 16, "bold")).pack(pady=(10, 10))
        ctk.CTkLabel(app, text=booking.get("description", ""), wraplength=450).pack(pady=(0, 10))

        room_number = booking.get("room_number") or booking.get("room_id")
        room_building = booking.get("room_building")
        room_display = f"Room {room_number}" if room_number else "Room"
        if room_building:
            room_display = f"{room_display} - {room_building}"

        ctk.CTkLabel(app, text=f"Room: {room_display}").pack(pady=(0, 5))
        ctk.CTkLabel(app, text=f"Start Time: {booking.get('start_time')}").pack(pady=(0, 5))
        ctk.CTkLabel(app, text=f"End Time: {booking.get('end_time')}").pack(pady=(0, 10))

        if capacity:
            ctk.CTkLabel(app, text=f"Attendees: {attendee_count}/{capacity}").pack(pady=(0, 8))
        if attendees:
            attendee_list = ctk.CTkFrame(app)
            attendee_list.pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkLabel(attendee_list, text="Participants:", font=("Arial", 13, "bold")).pack(anchor="w", padx=4, pady=(4, 2))
            for user in attendees:
                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", "User")
                role_suffix = " (Organiser)" if user.get("organiser") else ""
                ctk.CTkLabel(
                    attendee_list,
                    text=f"• {full_name}{role_suffix}",
                    anchor="w",
                ).pack(anchor="w", padx=8)

        if inviter_name:
            ctk.CTkLabel(app, text=f"Invited by: {inviter_name}").pack(pady=(0, 5))
        if invite_message:
            ctk.CTkLabel(app, text="Message:").pack(pady=(0, 2))
            ctk.CTkLabel(app, text=invite_message, wraplength=450, justify="left").pack(pady=(0, 10))

        if caller == "invites":
            ctk.CTkButton(
                app,
                text="Accept",
                width=100,
                height=28,
                fg_color="#33cc33",
                hover_color="#00cc00",
                command=lambda invite_id=id: accept_invite(app, invite_id),
            ).pack(padx=10, pady=(10, 10), anchor="e")
            ctk.CTkButton(
                app,
                text="Decline",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda invite_id=id: decline_invite(app, invite_id),
            ).pack(padx=10, pady=(10, 10), anchor="e")

        if caller == "bookings":
            ctk.CTkButton(
                app,
                text="Cancel Booking",
                width=120,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda booking_id=booking.get("booking_id"): cancel_booking(app, booking_id),
            ).pack(padx=10, pady=(10, 10), anchor="e")


def fetch_booking(booking_id):
    if not booking_id:
        return None
    response = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}")
    if response.status_code != 200:
        return None

    booking = response.json()
    room_id = booking.get("room_id")

    if room_id:
        room_response = requests.get(f"http://127.0.0.1:8000/rooms/{room_id}")
        if room_response.status_code == 200:
            room = room_response.json()
            booking["room_number"] = room.get("number")
            booking["room_building"] = room.get("building")

    return booking


def get_booking_users(booking_id):
    if not booking_id:
        return []
    try:
        response = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}/users")
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    users = []
    for item in response.json():
        user = item.get("user", {})
        user["organiser"] = item.get("organiser", False)
        users.append(user)
    return users


def accept_invite(app, id):
    response = requests.put(f"http://127.0.0.1:8000/invites/{id}/status/accept")
    if response.status_code != 200:
        error_screen = ctk.CTkToplevel(app)
        error_screen.geometry("300x150")
        error_screen.title("Invite Acceptance Failed")
        ctk.CTkLabel(error_screen, text="Unable to accept invite.").pack(pady=20)
        ctk.CTkButton(error_screen, text="OK", command=error_screen.destroy).pack(pady=20)
        error_screen.focus_force()
        error_screen.attributes("-topmost", True)
        error_screen.after(1000, lambda: error_screen.attributes("-topmost", False))
        return

    success_screen = ctk.CTkToplevel(app)
    success_screen.geometry("300x150")
    success_screen.title("University Room Booking System - Invite Accepted")
    ctk.CTkLabel(success_screen, text="Invite Accepted Successfully!").pack(pady=20)
    ctk.CTkButton(success_screen, text="OK", command=lambda: close_accept_and_decline_screen(app, success_screen)).pack(pady=20)
    success_screen.focus_force()
    success_screen.attributes("-topmost", True)
    success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))


def close_accept_and_decline_screen(app, screen):
    from UI.pages.invites_page import show_invites

    screen.destroy()
    show_invites(app)


def decline_invite(app, id):
    response = requests.put(f"http://127.0.0.1:8000/invites/{id}/status/decline")
    if response.status_code != 200:
        error_screen = ctk.CTkToplevel(app)
        error_screen.geometry("300x150")
        error_screen.title("Invite Decline Failed")
        ctk.CTkLabel(error_screen, text="Unable to decline invite.").pack(pady=20)
        ctk.CTkButton(error_screen, text="OK", command=error_screen.destroy).pack(pady=20)
        error_screen.focus_force()
        error_screen.attributes("-topmost", True)
        error_screen.after(1000, lambda: error_screen.attributes("-topmost", False))
        return

    success_screen = ctk.CTkToplevel(app)
    success_screen.geometry("300x150")
    success_screen.title("University Room Booking System - Invite Declined")
    ctk.CTkLabel(success_screen, text="Invite Declined!").pack(pady=20)
    ctk.CTkButton(success_screen, text="OK", command=lambda: close_accept_and_decline_screen(app, success_screen)).pack(pady=20)
    success_screen.focus_force()
    success_screen.attributes("-topmost", True)
    success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))


def cancel_booking(app, id):
    request = requests.delete(f"http://127.0.0.1:8000/bookings/{id}")
    if request.status_code != 200:
        error_screen = ctk.CTkToplevel(app)
        error_screen.geometry("300x150")
        error_screen.title("University Room Booking System - Booking Cancellation Failed")
        ctk.CTkLabel(error_screen, text="Booking Cancellation Failed!").pack(pady=20)
        ctk.CTkButton(error_screen, text="OK", command=error_screen.destroy).pack(pady=20)
        error_screen.focus_force()
        error_screen.attributes("-topmost", True)
        error_screen.after(1000, lambda: error_screen.attributes("-topmost", False))
    else:
        success_screen = ctk.CTkToplevel(app)
        success_screen.geometry("300x150")
        success_screen.title("University Room Booking System - Booking Cancelled")
        ctk.CTkLabel(success_screen, text="Booking Cancelled Successfully!").pack(pady=20)
        ctk.CTkButton(success_screen, text="OK", command=lambda: close_cancel_booking_screen(app, success_screen)).pack(pady=20)
        success_screen.focus_force()
        success_screen.attributes("-topmost", True)
        success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))


def close_cancel_booking_screen(app, screen):
    from UI.pages.bookings_page import show_my_bookings

    screen.destroy()
    show_my_bookings(app)
