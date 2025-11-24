import customtkinter as ctk
from UI.components.clear_contents import clear_contents
from UI.components.theme import apply_calendar_theme, apply_datepicker_theme  
from UI.pages.bookings_page import show_my_bookings

# https://stackoverflow.com/questions/26902034/how-to-center-a-tkinter-widget-in-a-sticky-frame
@clear_contents
def select_time_slot(app, caller, date, slot_text, room_id=None):
    back_button = ctk.CTkButton(app, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E",
    )
    if caller == "timeslots":
        back_button.configure(
        command=lambda: back_button_to_booking_date(app, room_id, date)
    )
    else:
        back_button.configure(command=lambda: back_button_to_booking_room(app, date, slot_text))
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

    app.submit_button = ctk.CTkButton(form_frame, text="Submit", command=lambda: submit_booking(app))
    app.submit_button.grid(
        row=2, column=0, columnspan=2, pady=20
    )

def back_button_to_booking_room(app, room_id, date):
    from UI.pages.booking_by_room import show_booking_room, on_calendar_selected, show_time_slots_for_date

    show_booking_room(app)
    app.room_select.set(room_id)
    app.calander.place(relx=0.5, rely=0.5, anchor="e")
    app.calander.config(state="normal") 
    app.calander.selection_set(date=date)
    app.calander.bind("<<CalendarSelected>>", lambda ev, cal=app.calander: on_calendar_selected(ev, cal))
    apply_calendar_theme(app)
    if hasattr(app, 'time_slots_frame') and app.time_slots_frame is not None:
        app.time_slots_frame.destroy()     
    app.time_slots_frame = ctk.CTkFrame(app, width=200, height=300)
    app.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")
    show_time_slots_for_date(app, room_id, date)

def back_button_to_booking_date(app, date, time_slot):
    from UI.pages.booking_by_date import show_booking_date
    show_booking_date(app)
    app.date_picker.set_date(date)
    hour, minute = map(int, time_slot.split(" - ")[0].split(":"))
    ampm = "AM"
    apply_datepicker_theme(app)
    

def submit_booking(app):
    # TODO Awaiting Backend Implemnentation to store booking and handle race conditions
    success = True
    notification_screen = ctk.CTkToplevel(app)
    notification_screen.geometry("300x150")
    notification_screen.title("University Room Booking System - Notification")
    button = ctk.CTkButton(notification_screen, text="OK", command=notification_screen.destroy)
    if app.title_entry.get() == "":
        ctk.CTkLabel(notification_screen, text="Booking Failed! Title is required.").pack(pady=20)
    elif app.description_entry.get() == "":
        ctk.CTkLabel(notification_screen, text="Booking Failed! Description is required.").pack(pady=20)
    elif not success:
        ctk.CTkLabel(notification_screen, text="Booking Failed!").pack(pady=20)
    else:
        ctk.CTkLabel(notification_screen, text="Booking Successful!").pack(pady=20)
        button.configure(command=lambda: handle_close_booking(app, success, notification_screen))
    button.pack(pady=10)
    notification_screen.focus_force()
    notification_screen.attributes("-topmost", True)
    notification_screen.after(1000, lambda: notification_screen.attributes("-topmost", False))

def handle_close_booking(app, success, notification_screen):
    notification_screen.destroy()
    if success:
        show_my_bookings(app)