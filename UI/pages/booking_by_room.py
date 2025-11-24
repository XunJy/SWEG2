import customtkinter as ctk
import tkcalendar
import datetime
from UI.components.clear_contents import clear_contents
from UI.pages.booking_submit import select_time_slot
from UI.components.theme import apply_calendar_theme

@clear_contents
def show_booking_room(app):
    ctk.CTkLabel(app, text="Room Booking", font=("Arial", 18, "bold")).pack(pady=20)
    ctk.CTkLabel(app, text="Please select a room:").pack(pady=(0,10))
    # TODO: Populate with available rooms from backend
    app.room_select = ctk.CTkOptionMenu(
        app,
        values=["Select a room"] + app.rooms,
        width=200,
        command=lambda value: on_room_selected(app, value)
    )
    app.room_select.pack(pady=(0,20))
    app.room_select.set("Select a room")

    app.calander = tkcalendar.Calendar(app, selectmode='day', mindate=datetime.date.today(), font=("Arial", 14))
    app.calander.selection_set(date=datetime.date.today())
    app.calander.config(state="disabled")

def on_room_selected(app, value):
    if value != "Select a room":
        app.calander.place(relx=0.5, rely=0.5, anchor="e")
        app.calander.config(state="normal") 
        app.calander.bind("<<CalendarSelected>>", lambda ev, cal=app.calander: on_calendar_selected(app, ev, cal))
        apply_calendar_theme(app)
        if hasattr(app, 'time_slots_frame') and app.time_slots_frame is not None:
            app.time_slots_frame.destroy()     
        app.time_slots_frame = ctk.CTkFrame(app, width=200, height=300)
        app.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")
        show_time_slots_for_date(app, value, datetime.date.today())

def on_calendar_selected(app, event, cal_widget):
    try:
        selected_date = cal_widget.selection_get()
        selected_room = app.room_select.get()
    except Exception:
        selected_date = datetime.date.today()
    show_time_slots_for_date(app, selected_room, selected_date)


def show_time_slots_for_date(app, room,  date):
    if not hasattr(app, 'time_slots_frame') or app.time_slots_frame is None:
        app.time_slots_frame = ctk.CTkFrame(app, width=200, height=300)
        app.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")

    for child in app.time_slots_frame.winfo_children():
        child.destroy()

    header = ctk.CTkLabel(app.time_slots_frame, text=f"Slots for {date.isoformat()}")
    header.pack(pady=(8, 6))

    # Hard Coded Room Availability TODO: Wait for backend implementation
    slots = [f"{h:02d}:00 - {h+1:02d}:00" for h in range(9, 17)]

    for slot in slots:
        btn = ctk.CTkButton(app.time_slots_frame, text=slot, width=160, height=30,
                            command=lambda s=slot, d=date: select_time_slot(app, "timeslots",d, s, room_id=room))
        btn.pack(padx=10, pady=4)
