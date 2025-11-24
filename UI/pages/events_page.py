import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.pages.bookings_page import fetch_booking_details


@clear_contents
def show_events(app):
    from UI.pages.event_details_page import view_event_details

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="Available Events", font=("Arial", 18, "bold")).pack(pady=20)

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
    ctk.CTkLabel(app, text="My Events", font=("Arial", 18, "bold")).pack(pady=20)

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
