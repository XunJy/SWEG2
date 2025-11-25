import customtkinter as ctk
import tkinter as tk
import requests
from UI.components.clear_contents import clear_contents
from UI.pages.bookings_page import fetch_booking_details
from UI.pages.event_details_page import view_event_details, accept_invite, decline_invite

@clear_contents
def show_invites(app):
    invites_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    invites_frame.place(relx=0.5, rely=0.5, anchor="center")
    header = ctk.CTkFrame(app, fg_color=app.cget("fg_color"))
    header.pack(fill="x", pady=10)

    ctk.CTkLabel(header, text="Invited Events", font=("Arial", 18, "bold"), anchor="w").pack(
        side="left", padx=(20, 10), pady=(10, 0)
    )
    ctk.CTkButton(
        header,
        text="Refresh",
        width=90,
        height=28,
        fg_color="#6b6b6b",
        hover_color="#4a4a4a",
        command=lambda: show_invites(app),
    ).pack(side="right", padx=(0, 20), pady=(10, 0))

    results = requests.get(f"http://127.0.0.1:8000/users/{app.user_id}/invites").json()

    if not results:
        ctk.CTkLabel(invites_frame, text="No pending invites right now.").pack(pady=20)
        return

    for invite in results:
        booking = fetch_booking_details(invite["booking_id"])
        invite_id = invite['invite_id']
        name = booking.get('name')
        description = booking.get('description') or ""
        room_number = booking.get('room_number') or booking.get('room_id')
        building = booking.get('room_building')
        room_display = f"Room {room_number}" if room_number else "Room"
        if building:
            room_display = f"{room_display} - {building}"
        frame = ctk.CTkFrame(invites_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text=name,
            anchor="w",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text=description,
            wraplength=450,
            justify="left",
            anchor="w"
        ).pack(anchor="w", padx=10)

        ctk.CTkLabel(
            frame,
            text=f"Room: {room_display}",
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(5, 10))

        button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(button_row, text="").pack(side="left", expand=True)

        ctk.CTkButton(
            button_row,
            text="Accept",
            width=100,
            height=28,
            fg_color="#33cc33",
            hover_color="#00cc00",
            command=lambda id=invite_id, booking=invite.get('booking_id'): accept_invite(app, id, booking)
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_row,
            text="Decline",
            width=100,
            height=28,
            fg_color="#cc3333",
            hover_color="#990000",
            command=lambda id=invite_id: decline_invite(app, id)
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=invite_id, booking_id=booking.get('booking_id'): view_event_details(
                app, id, caller="invites", booking_id=booking_id
            )
        ).pack(side="right", padx=5)
