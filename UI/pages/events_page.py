import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents


@clear_contents
def show_events(app):
    from UI.pages.event_details_page import view_event_details

    if hasattr(app, "available_events_refresh_job"):
        try:
            app.after_cancel(app.available_events_refresh_job)
        except Exception:
            pass

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="Available Events", font=("Arial", 18, "bold")).pack(pady=20)

    def apply_to_event(booking_id, status_label, apply_button):
        if not getattr(app, "user_id", None):
            status_label.configure(text="Please log in to apply.", text_color="#cc3333")
            return

        response = requests.post(
            "http://127.0.0.1:8000/user-bookings",
            json={"user_id": app.user_id, "booking_id": booking_id, "organiser": False},
        )

        if response.status_code == 200:
            status_label.configure(text="Joined event!", text_color="#2ecc71")
            apply_button.configure(state="disabled", text="Applied")
            return

        try:
            detail = response.json().get("detail")
        except Exception:
            detail = None

        status_label.configure(
            text=f"❌ {detail or 'Unable to apply right now.'}", text_color="#cc3333"
        )

    def refresh_available_events():
        if not events_frame.winfo_exists():
            return

        for widget in events_frame.winfo_children():
            widget.destroy()

        if not getattr(app, "user_id", None):
            ctk.CTkLabel(events_frame, text="Please log in to view available events.").pack(pady=20)
            return

        response = requests.get(
            "http://127.0.0.1:8000/bookings/public", params={"user_id": app.user_id}
        )
        if response.status_code != 200:
            ctk.CTkLabel(events_frame, text="Unable to load events from the server.").pack(pady=20)
            return

        events = response.json()
        if not events:
            ctk.CTkLabel(events_frame, text="No public events available right now.").pack(pady=20)
        else:
            for event in events:
                booking_id = event.get("booking_id")
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

                ctk.CTkLabel(
                    frame, text=name, anchor="w", font=("Arial", 14, "bold")
                ).pack(anchor="w", padx=10, pady=(10, 5))
                ctk.CTkLabel(
                    frame, text=description, wraplength=450, justify="left", anchor="w"
                ).pack(anchor="w", padx=10)

                info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
                info_row.pack(fill="x", padx=10, pady=(5, 10))
                ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(anchor="w")
                ctk.CTkLabel(
                    info_row, text=f"Time: {start_time} - {end_time}", anchor="w"
                ).pack(anchor="w")

                button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
                button_row.pack(fill="x", padx=10, pady=(0, 10))
                status_label = ctk.CTkLabel(button_row, text="", anchor="w")
                status_label.pack(side="left", padx=5)

                apply_button = ctk.CTkButton(
                    button_row,
                    text="Apply",
                    width=100,
                    height=28,
                    fg_color="#2ecc71",
                    hover_color="#27ae60",
                )
                apply_button.configure(
                    command=lambda id=booking_id, label=status_label, btn=apply_button: apply_to_event(
                        id, label, btn
                    )
                )
                apply_button.pack(side="right", padx=5)

                ctk.CTkButton(
                    button_row,
                    text="View More",
                    width=100,
                    height=28,
                    fg_color="#0078D7",
                    hover_color="#005A9E",
                    command=lambda id=booking_id: view_event_details(app, id, caller="events"),
                ).pack(side="right", padx=5)

        app.available_events_refresh_job = app.after(3000, refresh_available_events)

    refresh_available_events()


@clear_contents
def show_my_events(app):
    from UI.pages.event_details_page import view_event_details

    if hasattr(app, "events_refresh_job"):
        try:
            app.after_cancel(app.events_refresh_job)
        except Exception:
            pass

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Events", font=("Arial", 18, "bold")).pack(pady=20)

    def refresh_events():
        if not events_frame.winfo_exists():
            return

        for widget in events_frame.winfo_children():
            widget.destroy()

        if not getattr(app, "user_id", None):
            ctk.CTkLabel(events_frame, text="Please log in to view your events.").pack(pady=20)
            return

        response = requests.get(f"http://127.0.0.1:8000/bookings/user/{app.user_id}")
        if response.status_code != 200:
            ctk.CTkLabel(events_frame, text="Unable to load your events.").pack(pady=20)
            return

        events = response.json()
        if not events:
            ctk.CTkLabel(events_frame, text="You have no events yet.").pack(pady=20)
            return

        for event in events:
            booking_id = event.get("booking_id")
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
            info_row.pack(fill="x", padx=10, pady=(5, 10))
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
                command=lambda id=booking_id: view_event_details(app, id, caller="events"),
            ).pack(side="right", padx=5)

        app.events_refresh_job = app.after(3000, refresh_events)

    refresh_events()


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
