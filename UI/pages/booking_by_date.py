import customtkinter as ctk
import tkinter as tk
import tkcalendar
import datetime
from UI.components.clear_contents import clear_contents
from UI.pages.booking_submit import select_time_slot
from UI.components.theme import apply_datepicker_theme

# Reimplemented https://pythonguides.com/create-date-time-picker-using-python-tkinter in customtkinter
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

    hour_var = tk.StringVar(value="12")
    minute_var = tk.StringVar(value="00")
    ampm_var = ctk.StringVar(value="AM")

    app.hour_spin = ctk.CTkComboBox(time_frame, values=[f"{h}" for h in range(1, 13)])

    app.hour_spin.pack(side="left", padx=(0, 5))

    ctk.CTkLabel(time_frame, text=":", font=("Arial", 14)).pack(side="left")

    app.minute_spin = ctk.CTkComboBox(time_frame, values=[f"{m:02d}" for m in range(0, 60, 15)])
    app.minute_spin.pack(side="left", padx=(5, 0))

    ampm_menu = ctk.CTkOptionMenu(time_frame, values=["AM", "PM"], variable=ampm_var, width=70)
    ampm_menu.pack(side="left", padx=(10, 0))

    ctk.CTkButton(app, text="Search")

    ctk.CTkLabel(app, text="Select a Room:", font=("Arial", 14)).pack(pady=(20, 5))

    rooms_frame = ctk.CTkScrollableFrame(app, width=450, height=300)
    rooms_frame.pack(pady=10)

    def handle_room_click(selected_room):

        date = app.date_picker.get_date()

        hour = int(hour_var.get())
        minute = int(minute_var.get())
        ampm = ampm_var.get()

        if ampm == "PM" and hour != 12:
            hour += 12
        if ampm == "AM" and hour == 12:
            hour = 0

        slot_text = f"{hour:02d}:{minute:02d}"
        select_time_slot(app, "date", date, slot_text, selected_room)


    for room in app.rooms:
        frame = ctk.CTkFrame(rooms_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=room, anchor="w").pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkButton(
            frame,
            text="Book This Room",
            width=160,
            command=lambda r=room: handle_room_click(r)
        ).pack(pady=(0, 10), anchor="e")
