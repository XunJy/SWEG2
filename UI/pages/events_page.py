import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.pages.bookings_page import fetch_booking_details


@clear_contents
def show_events(app):
    from UI.pages.event_details_page import view_event_details

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="Available Events", font=("Arial", 18, "bold")).pack(pady=20)

    def render_events():
        def schedule_next():
            app.refresh_job = app.after(5000, render_events)

        for widget in events_frame.winfo_children():
            widget.destroy()

        if not getattr(app, "user_id", None):
            ctk.CTkLabel(events_frame, text="Please log in to view available events.").pack(pady=20)
            schedule_next()
            return

        try:
            response = requests.get(
                "http://127.0.0.1:8000/bookings/public", params={"user_id": app.user_id}
            )
        except requests.RequestException:
            ctk.CTkLabel(events_frame, text="Unable to load events from the server.").pack(pady=20)
            schedule_next()
            return

        if response.status_code != 200:
            ctk.CTkLabel(events_frame, text="Unable to load events from the server.").pack(pady=20)
            schedule_next()
            return

        events = response.json()
        if not events:
            ctk.CTkLabel(events_frame, text="No public events available right now.").pack(pady=20)
            schedule_next()
            return

        for event in events:
            details = fetch_booking_details(event.get("booking_id"))
            attendee_count = details.get("attendee_count") or event.get("attendee_count") or 0
            capacity = details.get("room_capacity") or event.get("room_capacity")
            remaining_capacity = details.get("available_capacity")

            frame = ctk.CTkFrame(events_frame)
            frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(frame, text=details.get("name"), anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(frame, text=details.get("description", ""), wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

            info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
            info_row.pack(fill="x", padx=10, pady=(5, 5))

            room_number = details.get("room_number") or details.get("room_id")
            room_building = details.get("room_building")
            room_display = f"Room {room_number}" if room_number else "Room"
            if room_building:
                room_display = f"{room_display} - {room_building}"

            ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(anchor="w")
            ctk.CTkLabel(info_row, text=f"Time: {details.get('start_time')} - {details.get('end_time')}", anchor="w").pack(anchor="w")

            if capacity:
                ctk.CTkLabel(
                    info_row,
                    text=f"Attendees: {attendee_count}/{capacity}" + (f"  (Remaining: {remaining_capacity})" if remaining_capacity is not None else ""),
                    anchor="w",
                ).pack(anchor="w")

            button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
            button_row.pack(fill="x", padx=10, pady=(0, 10))

            actions = [("View More", lambda id=details.get("booking_id"): view_event_details(app, id, caller="events", booking_details=details))]
            join_disabled = bool(capacity and remaining_capacity is not None and remaining_capacity <= 0)
            if not join_disabled:
                actions.insert(0, ("Apply to Join", lambda id=details.get("booking_id"): request_join(app, id)))
            else:
                actions.insert(0, ("Full (Unavailable)", lambda: None))

            actions_var = ctk.StringVar(value="☰ Actions")

            def handle_action(choice: str, action_map=actions):
                for label, fn in action_map:
                    if label == choice and fn:
                        fn()
                        break
                actions_var.set("☰ Actions")

            ctk.CTkOptionMenu(
                button_row,
                variable=actions_var,
                values=[label for label, _ in actions],
                command=handle_action,
                width=140,
                anchor="w",
            ).pack(side="right")

        schedule_next()

    render_events()


@clear_contents
def show_my_events(app):
    from UI.pages.event_details_page import view_event_details

    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Events", font=("Arial", 18, "bold")).pack(pady=20)

    def render_my_events():
        def schedule_next():
            app.refresh_job = app.after(5000, render_my_events)

        for widget in events_frame.winfo_children():
            widget.destroy()

        if not getattr(app, "user_id", None):
            ctk.CTkLabel(events_frame, text="Please log in to view your events.").pack(pady=20)
            schedule_next()
            return

        try:
            response = requests.get(f"http://127.0.0.1:8000/users/{app.user_id}/bookings")
        except requests.RequestException:
            ctk.CTkLabel(events_frame, text="Unable to load your events.").pack(pady=20)
            schedule_next()
            return

        if response.status_code != 200:
            ctk.CTkLabel(events_frame, text="Unable to load your events.").pack(pady=20)
            schedule_next()
            return

        events = response.json()
        if not events:
            ctk.CTkLabel(events_frame, text="You have no events yet.").pack(pady=20)
            schedule_next()
            return

        for event in events:
            details = fetch_booking_details(event.get("booking_id"))
            attendee_count = details.get("attendee_count") or 0
            capacity = details.get("room_capacity")

            frame = ctk.CTkFrame(events_frame)
            frame.pack(fill="x", padx=10, pady=10)

            role = "Organiser" if event.get("organiser") else "Attendee"
            header = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
            header.pack(fill="x", padx=10, pady=(8, 4))
            ctk.CTkLabel(header, text=details.get("name"), anchor="w", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(header, text=role, anchor="w", text_color="#2fa572" if event.get("organiser") else "#4a6fa5").pack(side="left")

            ctk.CTkLabel(frame, text=details.get("description", ""), wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
            row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
            row.pack(fill="x", padx=10, pady=(0, 10))

            room_number = details.get("room_number") or details.get("room_id")
            room_building = details.get("room_building")
            room_display = f"Room {room_number}" if room_number else "Room"
            if room_building:
                room_display = f"{room_display} - {room_building}"

            ctk.CTkLabel(row, text=f"Room: {room_display}", anchor="w").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                row,
                text=f"Time: {details.get('start_time')} - {details.get('end_time')}",
                anchor="w",
            ).pack(side="left", padx=(0, 10))
            if capacity:
                ctk.CTkLabel(row, text=f"Attendees: {attendee_count}/{capacity}").pack(side="left", padx=(0, 10))
            ctk.CTkButton(
                row,
                text="View More",
                width=100,
                height=28,
                fg_color="#0078D7",
                hover_color="#005A9E",
                command=lambda id=details.get("booking_id"): view_event_details(app, id, caller="events"),
            ).pack(side="right")

        schedule_next()

    render_my_events()


def request_join(app, booking_id: str):
    if not getattr(app, "user_id", None):
        return

    try:
        response = requests.post(
            f"http://127.0.0.1:8000/bookings/{booking_id}/join-requests",
            json={"user_id": app.user_id},
        )
    except requests.RequestException:
        toast = ctk.CTkToplevel(app)
        toast.geometry("320x140")
        ctk.CTkLabel(toast, text="Unable to submit request.").pack(pady=20)
        ctk.CTkButton(toast, text="OK", command=toast.destroy).pack(pady=8)
        return

    toast = ctk.CTkToplevel(app)
    toast.geometry("320x140")
    if response.status_code == 200:
        ctk.CTkLabel(toast, text="Join request submitted.").pack(pady=20)
    else:
        detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else "Request failed"
        ctk.CTkLabel(toast, text=detail or "Request failed").pack(pady=20)
    ctk.CTkButton(toast, text="OK", command=toast.destroy).pack(pady=8)
