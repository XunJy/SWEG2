import datetime

import customtkinter as ctk
import requests
import tkcalendar

from UI.components.clear_contents import clear_contents
from UI.components.theme import apply_calendar_theme
from UI.pages.booking_submit import select_time_slot


@clear_contents
def show_booking_room(app):
    ctk.CTkLabel(app, text="Room Booking", font=("Arial", 18, "bold")).pack(pady=20)
    ctk.CTkLabel(app, text="Please select a room:").pack(pady=(0, 10))

    rooms = fetch_rooms()
    app.room_lookup = {
        f"Room {room['number']} ({room['building']})": {
            **room,
            "display_name": f"Room {room['number']} ({room['building']})",
        }
        for room in rooms
    }

    app.room_select = ctk.CTkOptionMenu(
        app,
        values=["Select a room"] + list(app.room_lookup.keys()),
        width=200,
        command=lambda value: on_room_selected(app, value),
    )
    app.room_select.pack(pady=(0, 20))
    app.room_select.set("Select a room")

    app.calander = tkcalendar.Calendar(
        app, selectmode="day", mindate=datetime.date.today(), font=("Arial", 14)
    )
    app.calander.selection_set(date=datetime.date.today())
    app.calander.config(state="disabled")

    app.time_slots_frame = None


def fetch_rooms():
    try:
        response = requests.get("http://127.0.0.1:8000/rooms")
        if response.status_code == 200:
            return response.json()
    except Exception:
        return []
    return []


def on_room_selected(app, value):
    room = app.room_lookup.get(value)
    app.selected_room = room

    if not room:
        if hasattr(app, "time_slots_frame") and app.time_slots_frame is not None:
            app.time_slots_frame.destroy()
            app.time_slots_frame = None
        app.calander.config(state="disabled")
        return

    app.calander.place(relx=0.5, rely=0.5, anchor="e")
    app.calander.config(state="normal")
    app.calander.bind(
        "<<CalendarSelected>>",
        lambda ev, cal=app.calander: on_calendar_selected(app, ev, cal),
    )
    apply_calendar_theme(app)

    if hasattr(app, "time_slots_frame") and app.time_slots_frame is not None:
        app.time_slots_frame.destroy()
    app.time_slots_frame = ctk.CTkFrame(app, width=200, height=300)
    app.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")
    show_time_slots_for_date(app, room, datetime.date.today())


def on_calendar_selected(app, event, cal_widget):
    selected_date = cal_widget.selection_get()
    selected_room = getattr(app, "selected_room", None)
    show_time_slots_for_date(app, selected_room, selected_date)


def show_time_slots_for_date(app, room, date):
    if not room:
        return

    if not hasattr(app, "time_slots_frame") or app.time_slots_frame is None:
        app.time_slots_frame = ctk.CTkFrame(app, width=200, height=300)
        app.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")

    for child in app.time_slots_frame.winfo_children():
        child.destroy()

    header = ctk.CTkLabel(app.time_slots_frame, text=f"Slots for {date.isoformat()}")
    header.pack(pady=(8, 6))

    availability = requests.get(
        f"http://127.0.0.1:8000/rooms/{room['room_id']}/availability/day",
        params={"date": date.isoformat()},
    )

    if availability.status_code != 200:
        ctk.CTkLabel(app.time_slots_frame, text="Failed to load availability.").pack(pady=10)
        return

    slots = availability.json().get("availability", [])
    if not slots:
        ctk.CTkLabel(app.time_slots_frame, text="No slots available.").pack(pady=10)
        return

    for entry in slots:
        slot = entry.get("slot", "")
        available = entry.get("available", False)
        slot_parts = slot.split(" - ") if " - " in slot else [slot]
        start_str = f"{date.isoformat()} {slot_parts[0]}"
        end_str = f"{date.isoformat()} {slot_parts[1]}" if len(slot_parts) > 1 else ""

        btn = ctk.CTkButton(
            app.time_slots_frame,
            text=slot,
            width=160,
            height=30,
            state="normal" if available else "disabled",
            command=lambda s=slot, st=start_str, et=end_str: select_time_slot(
                app, "timeslots", date, s, room, st, et
            ),
        )
        btn.pack(padx=10, pady=4)
