import customtkinter as ctk
from UI.components.clear_contents import clear_contents


@clear_contents
def show_events(app):
    # Hard Coded Events TODO: Wait for backend implementation
    from UI.pages.event_details_page import view_event_details   
    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="Available Events", font=("Arial", 18, "bold")).pack(pady=20)

    for event in app.events:
        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=event["name"], anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=event["description"], wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
        row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        row.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(row, text=f"Location: {event['room_id']}", anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=event["id"]: view_event_details(app, id, caller="events")
        ).pack(side="right")


@clear_contents
def show_my_events(app):
    # Hard Coded Events TODO: Wait for backend implementation
    from UI.pages.event_details_page import view_event_details   
    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Events", font=("Arial", 18, "bold")).pack(pady=20)

    for event in app.events:
        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=event["name"], anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=event["description"], wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
        row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        row.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(row, text=f"Location: {event['room_id']}", anchor="w").pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=event["id"]: view_event_details(app, id, caller="events")
        ).pack(side="right")