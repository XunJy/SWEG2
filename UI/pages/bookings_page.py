import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, cancel_booking


@clear_contents
def show_my_bookings(app):
    if hasattr(app, "bookings_refresh_job"):
        try:
            app.after_cancel(app.bookings_refresh_job)
        except Exception:
            pass

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Bookings", font=("Arial", 18, "bold")).pack(pady=20)

    def refresh_bookings():
        if not events_frame.winfo_exists():
            return

        for widget in events_frame.winfo_children():
            widget.destroy()

        if not getattr(app, "user_id", None):
            ctk.CTkLabel(events_frame, text="Please log in to view your bookings.").pack(pady=20)
            return

        bookings_response = requests.get(f"http://127.0.0.1:8000/bookings/user/{app.user_id}")
        if bookings_response.status_code != 200:
            ctk.CTkLabel(events_frame, text="Unable to load bookings from the server.").pack(pady=20)
            return

        bookings = bookings_response.json()
        if not bookings:
            ctk.CTkLabel(events_frame, text="You have no bookings yet.").pack(pady=20)
        else:
            for booking in bookings:
                booking_id = booking.get("booking_id")
                details = fetch_booking_details(booking_id)

                name = details.get("name")
                description = details.get("description") or ""
                start_time = details.get("start_time")
                end_time = details.get("end_time")
                room_number = details.get("room_number") or details.get("room_id")
                room_building = details.get("room_building")
                capacity = details.get("room_capacity")
                attendee_count = details.get("attendee_count") or 0
                remaining = capacity - attendee_count if capacity is not None else None
                room_display = f"Room {room_number}" if room_number else "Room"
                if room_building:
                    room_display = f"{room_display} - {room_building}"

                frame = ctk.CTkFrame(events_frame)
                frame.pack(fill="x", padx=10, pady=10)

                ctk.CTkLabel(frame, text=name, anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
                ctk.CTkLabel(frame, text=description, wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

                info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
                info_row.pack(fill="x", padx=10, pady=(5, 5))
                ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(anchor="w")
                ctk.CTkLabel(info_row, text=f"Time: {start_time} - {end_time}", anchor="w").pack(anchor="w")
                if remaining is not None:
                    ctk.CTkLabel(
                        info_row,
                        text=f"Capacity remaining: {remaining} of {capacity}",
                        anchor="w",
                    ).pack(anchor="w")

                button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
                button_row.pack(fill="x", padx=10, pady=(0, 10))
                ctk.CTkButton(
                    button_row,
                    text="View More",
                    width=100,
                    height=28,
                    fg_color="#0078D7",
                    hover_color="#005A9E",
                    command=lambda id=booking_id: view_event_details(app, id, caller="bookings"),
                ).pack(side="right", padx=5)
                ctk.CTkButton(
                    button_row,
                    text="Cancel Booking",
                    width=120,
                    height=28,
                    fg_color="#cc3333",
                    hover_color="#990000",
                    command=lambda id=booking_id: cancel_booking(app, id),
                ).pack(side="right", padx=5)
                ctk.CTkButton(
                    button_row,
                    text="Invite Users",
                    width=120,
                    height=28,
                    fg_color="#6b6b6b",
                    hover_color="#4a4a4a",
                    command=lambda id=booking_id: invite_users(app, id),
                    state=("disabled" if remaining is not None and remaining <= 0 else "normal"),
                ).pack(side="right", padx=5)

        app.bookings_refresh_job = app.after(3000, refresh_bookings)

    refresh_bookings()


def fetch_booking_details(booking_id):
    response = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}")
    if response.status_code != 200:
        return {"booking_id": booking_id}

    booking = response.json()
    room_id = booking.get("room_id")
    if booking.get("attendee_count") is None:
        booking["attendee_count"] = 0

    if room_id:
        room_response = requests.get(f"http://127.0.0.1:8000/rooms/{room_id}")
        if room_response.status_code == 200:
            room = room_response.json()
            booking["room_number"] = room.get("number")
            booking["room_building"] = room.get("building")
            booking.setdefault("room_capacity", room.get("capacity"))

    return booking


def invite_users(app, booking_id):
    dialog = ctk.CTkToplevel(app)
    dialog.geometry("420x260")
    dialog.title("Invite Users")

    ctk.CTkLabel(
        dialog,
        text="Enter the email of the user you want to invite",
        font=("Arial", 14, "bold"),
    ).pack(pady=(15, 5))

    form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    form_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

    ctk.CTkLabel(form_frame, text="User Email:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    email_var = ctk.StringVar()
    selected_invitee: dict[str, dict | None] = {"user": None}

    email_entry = ctk.CTkEntry(form_frame, width=240, textvariable=email_var)
    email_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    status_label = ctk.CTkLabel(form_frame, text="")
    status_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

    def show_status(text: str, color: str):
        status_label.configure(text=text, text_color=color)

    def lookup_user(event=None):
        email = email_var.get().strip()
        selected_invitee["user"] = None

        if not email or "@" not in email:
            show_status("Please enter a valid email address.", "#cc3333")
            return

        response = requests.get(f"http://127.0.0.1:8000/users/email/{email}")
        if response.status_code != 200:
            show_status("❌ User not found", "#cc3333")
            return

        user = response.json()
        selected_invitee["user"] = user
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        show_status(f"✅ {full_name or 'User found'}", "#2ecc71")

    email_entry.bind("<FocusOut>", lookup_user)
    email_entry.bind("<KeyRelease>", lambda _event: lookup_user())

    def submit_invite():
        invitee = selected_invitee.get("user")
        if invitee is None:
            lookup_user()
            invitee = selected_invitee.get("user")
        if invitee is None:
            show_status("Please select a valid user before inviting.", "#cc3333")
            return

        payload = {"booking_id": booking_id, "user_email": invitee.get("email")}
        response = requests.post("http://127.0.0.1:8000/invites", json=payload)

        if response.status_code == 200:
            show_status("Invite sent successfully!", "#2ecc71")
        else:
            detail = response.json().get("detail", "Failed to send invite")
            show_status(f"❌ {detail}", "#cc3333")

    button_row = ctk.CTkFrame(dialog, fg_color="transparent")
    button_row.pack(fill="x", padx=20, pady=(10, 15))

    ctk.CTkButton(
        button_row,
        text="Cancel",
        width=100,
        command=dialog.destroy,
        fg_color="#6b6b6b",
        hover_color="#4a4a4a",
    ).pack(side="right", padx=5)

    ctk.CTkButton(
        button_row,
        text="Send Invite",
        width=120,
        fg_color="#0078D7",
        hover_color="#005A9E",
        command=submit_invite,
    ).pack(side="right", padx=5)

    dialog.focus_force()
    dialog.attributes("-topmost", True)
    dialog.after(500, lambda: dialog.attributes("-topmost", False))
