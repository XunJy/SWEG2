import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, cancel_booking


@clear_contents
def show_my_bookings(app):
    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Bookings", font=("Arial", 18, "bold")).pack(pady=20)

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
        return

    for booking in bookings:
        booking_id = booking.get("booking_id")
        details = fetch_booking_details(booking_id)

        name = details.get("name")
        description = details.get("description") or ""
        start_time = details.get("start_time")
        end_time = details.get("end_time")
        room_number = details.get("room_number") or details.get("room_id")
        room_building = details.get("room_building")
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
        ).pack(side="right", padx=5)


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


def invite_users(app, booking_id):
    invite_window = ctk.CTkToplevel(app)
    invite_window.geometry("460x360")
    invite_window.title("Invite Users")
    invite_window.grab_set()

    ctk.CTkLabel(invite_window, text="Create an Invite", font=("Arial", 16, "bold")).pack(pady=(12, 4))
    ctk.CTkLabel(invite_window, text="Enter the user's name and email, then add a message to send the invite.").pack(pady=(0, 10))

    form = ctk.CTkFrame(invite_window)
    form.pack(fill="both", expand=True, padx=16, pady=8)

    name_var = ctk.StringVar()
    email_var = ctk.StringVar()
    status_var = ctk.StringVar(value="")
    selected_user = {"user_id": None, "name": None}

    ctk.CTkLabel(form, text="User Name").grid(row=0, column=0, sticky="w", padx=8, pady=(10, 5))
    name_entry = ctk.CTkEntry(form, textvariable=name_var, width=260)
    name_entry.grid(row=0, column=1, sticky="we", padx=8, pady=(10, 5))

    ctk.CTkLabel(form, text="User Email").grid(row=1, column=0, sticky="w", padx=8, pady=5)
    email_entry = ctk.CTkEntry(form, textvariable=email_var, width=260)
    email_entry.grid(row=1, column=1, sticky="we", padx=8, pady=5)

    status_label = ctk.CTkLabel(form, textvariable=status_var, text_color="gray")
    status_label.grid(row=1, column=2, sticky="w", padx=4)

    ctk.CTkLabel(form, text="Invite Message").grid(row=2, column=0, sticky="nw", padx=8, pady=(10, 5))
    message_box = ctk.CTkTextbox(form, width=260, height=100)
    message_box.grid(row=2, column=1, columnspan=2, sticky="we", padx=8, pady=(10, 5))

    form.grid_columnconfigure(1, weight=1)

    def verify_user():
        status_var.set("")
        status_label.configure(text_color="gray")
        selected_user.update({"user_id": None, "name": None})
        email = email_var.get().strip()
        name = name_var.get().strip()

        if not email or not name:
            status_var.set("Please provide both name and email.")
            status_label.configure(text_color="#cc3333")
            return

        try:
            response = requests.get(f"http://127.0.0.1:8000/users/email/{email}")
        except requests.RequestException:
            status_var.set("Unable to reach the server. Try again.")
            status_label.configure(text_color="#cc3333")
            return

        if response.status_code != 200:
            status_var.set("User not found. Check the email.")
            status_label.configure(text_color="#cc3333")
            return

        user = response.json()
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        if full_name.lower() != name.lower():
            status_var.set(f"Found account: {full_name}. Update the name to confirm.")
            status_label.configure(text_color="#cc3333")
            return

        selected_user.update({"user_id": user.get("user_id"), "name": full_name})
        status_var.set(f"Selected user: {full_name}")
        status_label.configure(text_color="#2fa572")

    def send_invite():
        if not selected_user.get("user_id"):
            status_var.set("Please verify the user before sending.")
            status_label.configure(text_color="#cc3333")
            return

        message = message_box.get("1.0", "end").strip()
        payload = {
            "booking_id": booking_id,
            "user_email": email_var.get().strip(),
            "message": message,
            "inviter_id": app.user_id,
        }

        try:
            response = requests.post("http://127.0.0.1:8000/invites", json=payload)
        except requests.RequestException:
            status_var.set("Failed to send invite. Please try again.")
            status_label.configure(text_color="#cc3333")
            return

        if response.status_code != 200:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else ""
            status_var.set(detail or "Invite could not be created.")
            status_label.configure(text_color="#cc3333")
            return

        status_var.set(f"Invite sent to {selected_user['name']}")
        status_label.configure(text_color="#2fa572")

    button_row = ctk.CTkFrame(invite_window)
    button_row.pack(fill="x", padx=16, pady=(0, 12))

    ctk.CTkButton(button_row, text="Verify User", width=110, command=verify_user).pack(side="left", padx=6, pady=6)
    ctk.CTkButton(button_row, text="Send Invite", width=110, command=send_invite).pack(side="right", padx=6, pady=6)
