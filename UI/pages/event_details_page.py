import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents


@clear_contents
def view_event_details(app, id, caller, booking_id=None):
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

        if caller == "invites":
            ctk.CTkButton(
                app,
                text="Accept",
                width=100,
                height=28,
                fg_color="#33cc33",
                hover_color="#00cc00",
                command=lambda invite_id=id: accept_invite(app, invite_id, booking.get("booking_id")),
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


def accept_invite(app, invite_id, booking_id=None):
    response = requests.put(f"http://127.0.0.1:8000/invites/{invite_id}/status/accept")
    success_screen = ctk.CTkToplevel(app)
    success_screen.geometry("320x170")
    success_screen.title("University Room Booking System - Invite Accepted")

    if response.status_code == 200:
        ctk.CTkLabel(success_screen, text="Invite accepted successfully!").pack(pady=20)
    else:
        detail = response.json().get("detail", "Failed to accept invite")
        ctk.CTkLabel(success_screen, text=f"Error: {detail}").pack(pady=20)

    ctk.CTkButton(
        success_screen,
        text="OK",
        command=lambda: close_accept_and_decline_screen(app, success_screen),
    ).pack(pady=20)
    success_screen.focus_force()
    success_screen.attributes("-topmost", True)
    success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))


def close_accept_and_decline_screen(app, screen):
    from UI.pages.invites_page import show_invites

    screen.destroy()
    show_invites(app)


def decline_invite(app, invite_id):
    response = requests.put(f"http://127.0.0.1:8000/invites/{invite_id}/status/decline")
    success_screen = ctk.CTkToplevel(app)
    success_screen.geometry("320x170")
    success_screen.title("University Room Booking System - Invite Declined")

    if response.status_code == 200:
        ctk.CTkLabel(success_screen, text="Invite declined.").pack(pady=20)
    else:
        detail = response.json().get("detail", "Failed to decline invite")
        ctk.CTkLabel(success_screen, text=f"Error: {detail}").pack(pady=20)

    ctk.CTkButton(
        success_screen,
        text="OK",
        command=lambda: close_accept_and_decline_screen(app, success_screen),
    ).pack(pady=20)
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
