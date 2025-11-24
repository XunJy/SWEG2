import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, cancel_booking


@clear_contents
def show_my_bookings(app):
    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Bookings", font=("Arial", 18, "bold")).pack(pady=20)

    if not getattr(app, "user_id", None):
        ctk.CTkLabel(events_frame, text="Please log in to view your bookings.").pack(pady=20)
        return

    bookings_response = requests.get(f"http://127.0.0.1:8000/bookings/user/{app.user_id}")
    if bookings_response.status_code != 200:
        ctk.CTkLabel(events_frame, text="Unable to load bookings from the server.").pack(pady=20)
        return

    bookings = bookings_response.json()
    if not bookings:
        ctk.CTkLabel(events_frame, text="You have no bookings yet.").pack(pady=20)
        return

    for booking in bookings:
        booking_id = booking.get("booking_id")
        details = fetch_booking_details(booking_id)

        name = details.get("name")
        description = details.get("description") or ""
        start_time = details.get("start_time")
        end_time = details.get("end_time")
        room_number = details.get("room_number") or details.get("room_id")
        room_building = details.get("room_building")
        room_display = f"Room {room_number}" if room_number else "Room"
        if room_building:
            room_display = f"{room_display} - {room_building}"

        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=name, anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=description, wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

        info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        info_row.pack(fill="x", padx=10, pady=(5, 5))
        ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_row, text=f"Time: {start_time} - {end_time}", anchor="w").pack(anchor="w")

        button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            button_row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=booking_id: view_event_details(app, id, caller="bookings"),
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            button_row,
            text="Cancel Booking",
            width=120,
            height=28,
            fg_color="#cc3333",
            hover_color="#990000",
            command=lambda id=booking_id: cancel_booking(app, id),
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            button_row,
            text="Invite Users",
            width=120,
            height=28,
            fg_color="#6b6b6b",
            hover_color="#4a4a4a",
            command=lambda id=booking_id: invite_users(app, id),
        ).pack(side="right", padx=5)


def fetch_booking_details(booking_id):
    response = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}")
    if response.status_code != 200:
        return {"booking_id": booking_id}

    booking = response.json()
    room_id = booking.get("room_id")

    if room_id:
        room_response = requests.get(f"http://127.0.0.1:8000/rooms/{room_id}")
        if room_response.status_code == 200:
            room = room_response.json()
            booking["room_number"] = room.get("number")
            booking["room_building"] = room.get("building")

    return booking


def invite_users(app, booking_id):
    notification = ctk.CTkToplevel(app)
    notification.geometry("320x160")
    notification.title("Invite Users")
    ctk.CTkLabel(notification, text=f"Booking {booking_id}\nInvite flow coming soon.").pack(pady=20)
    ctk.CTkButton(notification, text="OK", command=notification.destroy).pack(pady=10)
    notification.focus_force()
    notification.attributes("-topmost", True)
    notification.after(1000, lambda: notification.attributes("-topmost", False))
