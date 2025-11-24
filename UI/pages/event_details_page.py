import customtkinter as ctk
import requests
from UI.components.clear_contents import clear_contents


@clear_contents
def view_event_details(app, id, caller):
    from UI.pages.events_page import show_events
    from UI.pages.invites_page import show_invites
    back_button = ctk.CTkButton(app, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E",
    )
    if caller == "events":
        back_button.configure(command=lambda: show_events(app))
        event = requests.get(f"http://127.0.0.1:8000/events/{id}").json()
    elif caller == "invites":
        back_button.configure(command=lambda: show_invites(app))
        event = requests.get(f"http://127.0.0.1:8000/invites/{id}").json()
    elif caller == "bookings":
        from UI.pages.bookings_page import show_my_bookings
        back_button.configure(command=lambda: show_my_bookings(app))
        event = requests.get(f"http://127.0.0.1:8000/bookings/{id}").json()
    back_button.pack(padx=55, pady=(10, 10), anchor="w")
    if event is None:
        ctk.CTkLabel(app, text="Event not found").pack(pady=(10, 20))
        ctk.CTkButton(app, text="Back to Events", width=100, height=28, command=lambda: show_events(app)).pack(pady=(10, 10))
    else:
        # print(f"ID: {id} Caller: {caller}")
        # print(f"event: {event}")
        ctk.CTkLabel(app, text=event['name']).pack(pady=(10, 10))
        ctk.CTkLabel(app, text=event['description']).pack(pady=(0, 20))
        ctk.CTkLabel(app, text=f"Location: {event['room_id']}").pack(pady=(0, 10))
        ctk.CTkLabel(app, text=f"Start Time: {event['start_time']}").pack(pady=(0, 10))
        ctk.CTkLabel(app, text=f"End Time: {event['end_time']}").pack(pady=(0, 20))
        if caller in ["events", "invites"]:
            ctk.CTkButton(
                app,
                text="Accept",
                width=100,
                height=28,
                fg_color="#33cc33",
                hover_color="#00cc00",
                command=lambda id=event['invite_id']: accept_invite(app, id)
            ).pack(padx=10, pady=(10, 10), anchor="e")
            ctk.CTkButton(
                app,
                text="Decline",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda id=event['invite_id']: decline_invite(app, id)
            ).pack(padx=10, pady=(10, 10), anchor="e")

        if caller == "bookings":
            ctk.CTkButton(
                app,
                text="Cancel Booking",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda id=event['booking_id']: cancel_booking(app,id)
            ).pack(padx=10, pady=(10, 10), anchor="e")

def accept_invite(app, id):
    # TODO Awaiting Backend Implemnentation to store accepted invite
    success_screen = ctk.CTkToplevel(app)
    success_screen.geometry("300x150")
    success_screen.title("University Room Booking System - Invite Accepted")
    ctk.CTkLabel(success_screen, text="Invite Accepted Successfully!").pack(pady=20)
    ctk.CTkButton(success_screen, text="OK", command=lambda: close_accept_and_decline_screen(app, success_screen)).pack(pady=20)
    success_screen.focus_force()
    success_screen.attributes("-topmost", True)
    success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))

def close_accept_and_decline_screen(app, screen):
    from UI.pages.events_page import show_events
    screen.destroy()
    show_events(app)

def decline_invite(app, id):
    # TODO Awaiting Backend Implemnentation to store accepted invite
    success_screen = ctk.CTkToplevel(app)
    success_screen.geometry("300x150")
    success_screen.title("University Room Booking System - Invite Declined")
    ctk.CTkLabel(success_screen, text="Invite Declined!").pack(pady=20)
    ctk.CTkButton(success_screen, text="OK", command=lambda: close_accept_and_decline_screen(app, success_screen)).pack(pady=20)
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
    
