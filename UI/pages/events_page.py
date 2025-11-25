import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents


@clear_contents
def show_events(app):
    from UI.pages.event_details_page import view_event_details

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    header = ctk.CTkFrame(app, fg_color=app.cget("fg_color"))
    header.pack(fill="x", pady=10)

    ctk.CTkLabel(header, text="Available Events", font=("Arial", 18, "bold"), anchor="w").pack(
        side="left", padx=(20, 10), pady=(10, 0)
    )
    ctk.CTkButton(
        header,
        text="Refresh",
        width=90,
        height=28,
        fg_color="#6b6b6b",
        hover_color="#4a4a4a",
        command=lambda: show_events(app),
    ).pack(side="right", padx=(0, 20), pady=(10, 0))

    if not getattr(app, "user_id", None):
        ctk.CTkLabel(events_frame, text="Please log in to view available events.").pack(pady=20)
        return

    response = requests.get(
        "http://127.0.0.1:8000/bookings/public", params={"user_id": app.user_id}
    )
    if response.status_code != 200:
        ctk.CTkLabel(events_frame, text="Unable to load events from the server.").pack(pady=20)
        return

    events = response.json()
    if not events:
        ctk.CTkLabel(events_frame, text="No public events available right now.").pack(pady=20)
        return

    for event in events:
        details = fetch_booking_details(event.get("booking_id"))
        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=details.get("name"), anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=details.get("description", ""), wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

        row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        row.pack(fill="x", padx=10, pady=(0, 10))

        room_number = details.get("room_number") or details.get("room_id")
        room_building = details.get("room_building")
        room_display = f"Room {room_number}" if room_number else "Room"
        if room_building:
            room_display = f"{room_display} - {room_building}"

        ctk.CTkLabel(row, text=f"Room: {room_display}", anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            row,
            text=f"Time: {details.get('start_time')} - {details.get('end_time')}",
            anchor="w",
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            row,
            text="Apply",
            width=90,
            height=28,
            fg_color="#33cc33",
            hover_color="#00cc00",
            command=lambda id=details.get("booking_id"): apply_for_event(app, id),
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=details.get("booking_id"): view_event_details(app, id, caller="events"),
        ).pack(side="right")


@clear_contents
def show_my_events(app):
    from UI.pages.event_details_page import view_event_details

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    header = ctk.CTkFrame(app, fg_color=app.cget("fg_color"))
    header.pack(fill="x", pady=10)

    ctk.CTkLabel(header, text="My Events", font=("Arial", 18, "bold"), anchor="w").pack(
        side="left", padx=(20, 10), pady=(10, 0)
    )
    ctk.CTkButton(
        header,
        text="Refresh",
        width=90,
        height=28,
        fg_color="#6b6b6b",
        hover_color="#4a4a4a",
        command=lambda: show_my_events(app),
    ).pack(side="right", padx=(0, 20), pady=(10, 0))

    if not getattr(app, "user_id", None):
        ctk.CTkLabel(events_frame, text="Please log in to view your events.").pack(pady=20)
        return

    response = requests.get(f"http://127.0.0.1:8000/bookings/user/{app.user_id}")
    if response.status_code != 200:
        ctk.CTkLabel(events_frame, text="Unable to load your events.").pack(pady=20)
        return

    events = response.json()
    if not events:
        ctk.CTkLabel(events_frame, text="You have no events yet.").pack(pady=20)
        return

    for event in events:
        details = fetch_booking_details(event.get("booking_id"))
        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=details.get("name"), anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=details.get("description", ""), wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
        row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        row.pack(fill="x", padx=10, pady=(0, 10))

        room_number = details.get("room_number") or details.get("room_id")
        room_building = details.get("room_building")
        room_display = f"Room {room_number}" if room_number else "Room"
        if room_building:
            room_display = f"{room_display} - {room_building}"

        ctk.CTkLabel(row, text=f"Room: {room_display}", anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            row,
            text=f"Time: {details.get('start_time')} - {details.get('end_time')}",
            anchor="w",
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=details.get("booking_id"): view_event_details(app, id, caller="events"),
        ).pack(side="right")


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


def apply_for_event(app, booking_id):
    response = requests.post(
        "http://127.0.0.1:8000/user-bookings",
        json={"user_id": app.user_id, "booking_id": booking_id, "organiser": False},
    )

    status_screen = ctk.CTkToplevel(app)
    status_screen.geometry("320x170")
    status_screen.title("University Room Booking System - Apply to Event")

    if response.status_code == 200:
        message = "Successfully applied to the event."
        ctk.CTkLabel(status_screen, text=message).pack(pady=20)
    else:
        detail = response.json().get("detail", "Failed to apply to the event")
        ctk.CTkLabel(status_screen, text=f"Error: {detail}").pack(pady=20)

    ctk.CTkButton(
        status_screen,
        text="OK",
        command=lambda: close_apply_screen(app, status_screen),
    ).pack(pady=20)
    status_screen.focus_force()
    status_screen.attributes("-topmost", True)
    status_screen.after(1000, lambda: status_screen.attributes("-topmost", False))


def close_apply_screen(app, screen):
    screen.destroy()
    show_events(app)
