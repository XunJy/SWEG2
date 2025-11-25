import customtkinter as ctk
import requests
from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, accept_invite, decline_invite


def fetch_booking_details(booking_id):
    response = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}")
    if response.status_code != 200:
        return {"booking_id": booking_id}

    booking = response.json()
    room_id = booking.get("room_id")

    if room_id:
        room_response = requests.get(f"http://127.0.0.1:8000/rooms/{room_id}")
        if room_response.status_code == 200:
            room = room_response.json()
            booking["room_number"] = room.get("number")
            booking["room_building"] = room.get("building")

    return booking


@clear_contents
def show_invites(app):
    if hasattr(app, "invites_refresh_job"):
        try:
            app.after_cancel(app.invites_refresh_job)
        except Exception:
            pass

    invites_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    invites_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="Invited Events", font=("Arial", 18, "bold")).pack(pady=20)

    def refresh_invites():
        if not invites_frame.winfo_exists():
            return

        for widget in invites_frame.winfo_children():
            widget.destroy()

        if not getattr(app, "user_id", None):
            ctk.CTkLabel(invites_frame, text="Please log in to view your invites.").pack(pady=20)
            return

        response = requests.get(f"http://127.0.0.1:8000/users/{app.user_id}/invites")
        if response.status_code != 200:
            ctk.CTkLabel(invites_frame, text="Unable to load invites from the server.").pack(pady=20)
            return

        invites = response.json()
        if not invites:
            ctk.CTkLabel(invites_frame, text="You have no invites at this time.").pack(pady=20)
        else:
            for invite in invites:
                booking = fetch_booking_details(invite.get("booking_id"))
                invite_id = invite.get("invite_id")

                name = booking.get("name")
                description = booking.get("description") or ""
                start_time = booking.get("start_time")
                end_time = booking.get("end_time")
                room_number = booking.get("room_number") or booking.get("room_id")
                building = booking.get("room_building")
                room_display = f"Room {room_number}" if room_number else "Room"
                if building:
                    room_display = f"{room_display} - {building}"

                frame = ctk.CTkFrame(invites_frame)
                frame.pack(fill="x", padx=10, pady=10)

                ctk.CTkLabel(frame, text=name, anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
                ctk.CTkLabel(frame, text=description, wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

                info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
                info_row.pack(fill="x", padx=10, pady=(5, 5))
                ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(anchor="w")
                if start_time or end_time:
                    ctk.CTkLabel(info_row, text=f"Time: {start_time} - {end_time}", anchor="w").pack(anchor="w")

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
                    command=lambda id=invite_id, booking=invite.get("booking_id"): accept_invite(app, id, booking),
                ).pack(side="right", padx=5)

                ctk.CTkButton(
                    button_row,
                    text="Decline",
                    width=100,
                    height=28,
                    fg_color="#cc3333",
                    hover_color="#990000",
                    command=lambda id=invite_id: decline_invite(app, id),
                ).pack(side="right", padx=5)

                ctk.CTkButton(
                    button_row,
                    text="View More",
                    width=100,
                    height=28,
                    fg_color="#0078D7",
                    hover_color="#005A9E",
                    command=lambda id=invite_id, booking_id=booking.get("booking_id"): view_event_details(app, id, caller="invites", booking_id=booking_id),
                ).pack(side="right", padx=5)

        app.invites_refresh_job = app.after(3000, refresh_invites)

    refresh_invites()
