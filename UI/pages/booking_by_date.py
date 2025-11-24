import datetime
import tkinter as tk

import customtkinter as ctk
import requests
import tkcalendar

from UI.components.clear_contents import clear_contents
from UI.components.theme import apply_datepicker_theme
from UI.pages.booking_submit import select_time_slot


@clear_contents
def show_booking_date(app):
    ctk.CTkLabel(app, text="Room Booking", font=("Arial", 18, "bold")).pack(pady=20)
    ctk.CTkLabel(app, text="Please select a date:").pack(pady=(0, 10))

    app.date_picker = tkcalendar.DateEntry(app, width=15, height=15)
    apply_datepicker_theme(app)
    app.date_picker.pack(pady=(0, 20))
    ctk.CTkLabel(app, text="Select Time:", font=("Arial", 14)).pack(pady=(10, 5))

    time_frame = ctk.CTkFrame(app, fg_color="transparent")
    time_frame.pack(pady=5)

    app.hour_spin = ctk.CTkComboBox(time_frame, values=[f"{h}" for h in range(1, 13)], width=60)
    app.hour_spin.set("12")
    app.hour_spin.pack(side="left", padx=(0, 5))

    ctk.CTkLabel(time_frame, text=":", font=("Arial", 14)).pack(side="left")

    app.minute_spin = ctk.CTkComboBox(time_frame, values=[f"{m:02d}" for m in range(0, 60, 15)], width=70)
    app.minute_spin.set("00")
    app.minute_spin.pack(side="left", padx=(5, 0))

    app.ampm_var = ctk.StringVar(value="AM")
    ampm_menu = ctk.CTkOptionMenu(time_frame, values=["AM", "PM"], variable=app.ampm_var, width=70)
    ampm_menu.pack(side="left", padx=(10, 0))

    ctk.CTkButton(app, text="Search", command=lambda: search_rooms(app)).pack(pady=(10, 10))

    ctk.CTkLabel(app, text="Select a Room:", font=("Arial", 14)).pack(pady=(10, 5))
    app.rooms_frame = ctk.CTkScrollableFrame(app, width=450, height=300)
    app.rooms_frame.pack(pady=10)

    search_rooms(app)


def search_rooms(app):
    if not hasattr(app, "rooms_frame"):
        return

    for child in app.rooms_frame.winfo_children():
        child.destroy()

    try:
        date = app.date_picker.get_date()
        hour = int(app.hour_spin.get() or 0)
        minute = int(app.minute_spin.get() or 0)
    except Exception:
        ctk.CTkLabel(app.rooms_frame, text="Invalid time selection.").pack(pady=10)
        return

    ampm = app.ampm_var.get()
    if ampm == "PM" and hour != 12:
        hour += 12
    if ampm == "AM" and hour == 12:
        hour = 0

    start_dt = datetime.datetime.combine(date, datetime.time(hour, minute))
    end_dt = start_dt + datetime.timedelta(hours=1)

    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    slot_text = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"

    response = requests.get(
        "http://127.0.0.1:8000/rooms/available",
        params={"start_time": start_str, "end_time": end_str},
    )

    if response.status_code != 200:
        ctk.CTkLabel(app.rooms_frame, text="Unable to load rooms from the server.").pack(pady=10)
        return

    rooms = response.json()
    if not rooms:
        ctk.CTkLabel(app.rooms_frame, text="No available rooms for the selected time.").pack(pady=10)
        return

    for room in rooms:
        room["display_name"] = f"Room {room['number']} ({room['building']})"
        frame = ctk.CTkFrame(app.rooms_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text=f"Room {room['number']} - {room['building']} (Capacity: {room['capacity']})",
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkButton(
            frame,
            text="Book This Room",
            width=160,
            command=lambda r=room: select_time_slot(app, "date", date, slot_text, r, start_str, end_str),
        ).pack(pady=(0, 10), anchor="e")
