import customtkinter as ctk
import requests
from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, accept_invite, decline_invite
from UI.pages.bookings_page import fetch_booking_details


@clear_contents
def show_invites(app):
    invites_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    invites_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="Invited Events", font=("Arial", 18, "bold")).pack(pady=20)

    if not getattr(app, "user_id", None):
        ctk.CTkLabel(invites_frame, text="Please log in to view your invites.").pack(pady=20)
        return

    response = requests.get(f"http://127.0.0.1:8000/users/{app.user_id}/invites")
    if response.status_code != 200:
        ctk.CTkLabel(invites_frame, text="Unable to load invites from the server.").pack(pady=20)
        return

    results = response.json()
    if not results:
        ctk.CTkLabel(invites_frame, text="No pending invites at the moment.").pack(pady=20)
        return

    inviter_cache: dict[str, str] = {}

    def get_inviter_name(inviter_id: str | None) -> str:
        if not inviter_id:
            return "Unknown"
        if inviter_id in inviter_cache:
            return inviter_cache[inviter_id]

        lookup = requests.get(f"http://127.0.0.1:8000/users/{inviter_id}")
        if lookup.status_code != 200:
            inviter_cache[inviter_id] = "Unknown"
            return inviter_cache[inviter_id]

        user = lookup.json()
        inviter_cache[inviter_id] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Unknown"
        return inviter_cache[inviter_id]

    for invite in results:
        booking = fetch_booking_details(invite.get("booking_id"))
        invite_id = invite.get("invite_id")
        name = booking.get("name")
        description = booking.get("description") or ""
        room_number = booking.get("room_number") or booking.get("room_id")
        building = booking.get("room_building")
        room_display = f"Room {room_number}" if room_number else "Room"
        if building:
            room_display = f"{room_display} - {building}"
        inviter_name = get_inviter_name(invite.get("inviter_id"))

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

        info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        info_row.pack(fill="x", padx=10, pady=(5, 5))
        ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            info_row,
            text=f"Time: {booking.get('start_time')} - {booking.get('end_time')}",
            anchor="w",
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(frame, text=f"Invited by: {inviter_name}", anchor="w").pack(anchor="w", padx=10, pady=(0, 8))

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
            command=lambda id=invite_id: accept_invite(app, id)
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
            command=lambda id=invite_id, booking_id=booking.get("booking_id"), invite_data=invite, organiser_name=inviter_name: view_event_details(app, id, caller="invites", booking_id=booking_id, invite=invite_data | {"inviter_name": organiser_name})
        ).pack(side="right", padx=5)
