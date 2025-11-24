import customtkinter as ctk
import requests
from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, cancel_booking

@clear_contents
def show_my_bookings(app):
    # Hard Coded Bookings TODO: Wait for backend implementation
    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Bookings", font=("Arial", 18, "bold")).pack(pady=20)

    bookings = requests.get("http://127.0.0.1:8000/bookings").json()
    for booking in bookings:
        booking_id = booking.get("booking_id")
        name = booking.get("name")
        description = booking.get("description")
        start_time = booking.get("start_time") 
        end_time = booking.get("end_time")
        room_id = booking.get("room_id")   
        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=name, anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=description, wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

        button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(button_row, text=f"Location: {room_id}", anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            button_row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=booking_id: view_event_details(app, booking_id, caller="bookings")
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            button_row,
            text="Cancel Booking",
            width=100,
            height=28,
            fg_color="#cc3333",
            hover_color="#990000",
            command=lambda id=booking_id: cancel_booking(app, booking_id)
        ).pack(side="right", padx=5)