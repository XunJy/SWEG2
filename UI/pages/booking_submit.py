import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.components.theme import apply_calendar_theme
from UI.pages.bookings_page import show_my_bookings


# https://stackoverflow.com/questions/26902034/how-to-center-a-tkinter-widget-in-a-sticky-frame
@clear_contents
def select_time_slot(app, caller, date, slot_text, room, start_time, end_time):
    app.pending_booking = {
        "room": room,
        "date": date,
        "slot_text": slot_text,
        "start_time": start_time,
        "end_time": end_time,
        "source": caller,
    }

    back_button = ctk.CTkButton(
        app,
        text="Back",
        width=60,
        height=28,
        fg_color="#0078D7",
        hover_color="#005A9E",
    )

    if caller == "timeslots":
        back_button.configure(command=lambda: back_button_to_booking_room(app))
    else:
        back_button.configure(command=lambda: back_button_to_booking_date(app))
    back_button.pack(padx=55, pady=(10, 10), anchor="w")

    form_frame = ctk.CTkFrame(app, fg_color="transparent")
    form_frame.pack(pady=10)

    form_frame.grid_columnconfigure(0, weight=1)
    form_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(form_frame, text="Booking Title:").grid(
        row=0, column=0, padx=10, pady=5, sticky="e"
    )
    app.title_entry = ctk.CTkEntry(form_frame, width=250)
    app.title_entry.grid(
        row=0, column=1, padx=10, pady=5, sticky="w"
    )

    ctk.CTkLabel(form_frame, text="Booking Description:").grid(
        row=1, column=0, padx=10, pady=5, sticky="e"
    )
    app.description_entry = ctk.CTkEntry(form_frame, width=250)
    app.description_entry.grid(
        row=1, column=1, padx=10, pady=5, sticky="w"
    )

    previous_public_value = app.public_var.get() if hasattr(app, "public_var") else False
    app.public_var = ctk.BooleanVar(value=previous_public_value)
    ctk.CTkCheckBox(
        form_frame,
        text="Make this a public event",
        variable=app.public_var,
    ).grid(row=2, column=0, columnspan=2, pady=(5, 10))

    slot_summary = ctk.CTkLabel(
        form_frame,
        text=f"Room: {room.get('number', room.get('room_id'))} | {slot_text}",
        font=("Arial", 12, "bold"),
    )
    slot_summary.grid(row=3, column=0, columnspan=2, pady=(0, 10))

    app.submit_button = ctk.CTkButton(
        form_frame, text="Submit", command=lambda: submit_booking(app)
    )
    app.submit_button.grid(
        row=4, column=0, columnspan=2, pady=20
    )


def back_button_to_booking_room(app):
    from UI.pages.booking_by_room import (
        on_calendar_selected,
        show_booking_room,
        show_time_slots_for_date,
    )

    pending = getattr(app, "pending_booking", {})
    room = pending.get("room")
    date = pending.get("date")

    show_booking_room(app)
    if room:
        display = room.get("display_name") or room.get("number") or room.get("room_id")
        app.room_select.set(display)
        app.selected_room = room
        app.calander.place(relx=0.5, rely=0.5, anchor="e")
        app.calander.config(state="normal")
        if date:
            app.calander.selection_set(date=date)
        app.calander.bind(
            "<<CalendarSelected>>",
            lambda ev, cal=app.calander: on_calendar_selected(app, ev, cal),
        )
        apply_calendar_theme(app)
        if hasattr(app, "time_slots_frame") and app.time_slots_frame is not None:
            app.time_slots_frame.destroy()
        app.time_slots_frame = ctk.CTkFrame(app, width=200, height=300)
        app.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")
        show_time_slots_for_date(app, room, date)


def back_button_to_booking_date(app):
    from datetime import datetime

    from UI.pages.booking_by_date import search_rooms, show_booking_date

    pending = getattr(app, "pending_booking", {})
    start_time = pending.get("start_time")

    show_booking_date(app)
    if not start_time:
        return

    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    app.date_picker.set_date(start_dt.date())
    app.hour_spin.set(start_dt.strftime("%I"))
    app.minute_spin.set(start_dt.strftime("%M"))
    app.ampm_var.set("PM" if start_dt.hour >= 12 else "AM")
    search_rooms(app)


def submit_booking(app):
    pending = getattr(app, "pending_booking", None)

    notification_screen = ctk.CTkToplevel(app)
    notification_screen.geometry("320x180")
    notification_screen.title("University Room Booking System - Notification")

    button = ctk.CTkButton(notification_screen, text="OK", command=notification_screen.destroy)

    if pending is None:
        ctk.CTkLabel(notification_screen, text="No booking slot selected.").pack(pady=20)
        button.pack(pady=10)
        return

    if not getattr(app, "user_id", None):
        ctk.CTkLabel(notification_screen, text="Please log in before booking.").pack(pady=20)
        button.pack(pady=10)
        return

    title = app.title_entry.get().strip()
    description = app.description_entry.get().strip()

    if title == "":
        ctk.CTkLabel(notification_screen, text="Booking Failed! Title is required.").pack(pady=20)
    elif description == "":
        ctk.CTkLabel(notification_screen, text="Booking Failed! Description is required.").pack(pady=20)
    else:
        payload = {
            "room_id": pending["room"].get("room_id"),
            "name": title,
            "description": description,
            "start_time": pending["start_time"],
            "end_time": pending["end_time"],
            "public": bool(app.public_var.get()),
        }

        response = requests.post("http://127.0.0.1:8000/bookings", json=payload)

        if response.status_code != 200:
            detail = response.json().get("detail", "Booking Failed!")
            ctk.CTkLabel(notification_screen, text=f"Booking Failed: {detail}").pack(pady=20)
        else:
            booking_id = response.json().get("booking_id")
            link_success = link_booking_to_user(app, booking_id)
            message = "Booking Successful!"
            if not link_success:
                message = "Booking saved but failed to link to user."
            ctk.CTkLabel(notification_screen, text=message).pack(pady=20)
            button.configure(command=lambda: handle_close_booking(app, notification_screen))

    button.pack(pady=10)
    notification_screen.focus_force()
    notification_screen.attributes("-topmost", True)
    notification_screen.after(1000, lambda: notification_screen.attributes("-topmost", False))


def link_booking_to_user(app, booking_id):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/user-bookings",
            json={"user_id": app.user_id, "booking_id": booking_id, "organiser": True},
        )
        return response.status_code == 200
    except Exception:
        return False


def handle_close_booking(app, notification_screen):
    notification_screen.destroy()
    show_my_bookings(app)
