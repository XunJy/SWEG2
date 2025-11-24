import customtkinter as ctk
from UI.components.theme import change_theme
from UI.pages.booking_by_date import show_booking_date
from UI.pages.booking_by_room import show_booking_room
from UI.pages.bookings_page import show_my_bookings
from UI.pages.events_page import show_events, show_my_events
from UI.pages.invites_page import show_invites


def fill_sidebar(app):
    for widget in app.sidebar.winfo_children():
        widget.destroy()

    if getattr(app, "is_admin", False):
        ctk.CTkButton(
            app.sidebar,
            text="Logout",
            width=100,
            command=getattr(app, "logout_callback", lambda: None),
        ).pack(pady=(10, 20))
        return

    ctk.CTkButton(app.sidebar, text="Available Events", width=100, command=lambda: show_events(app)).pack(pady=10)
    ctk.CTkButton(app.sidebar, text="My Events", width=100, command=lambda: show_my_events(app)).pack(pady=10)
    ctk.CTkButton(app.sidebar, text="My Invites", width=100, command=lambda: show_invites(app)).pack(pady=10)
    ctk.CTkButton(app.sidebar, text="Make Booking (by Date)", width=100, command=lambda: show_booking_date(app)).pack(pady=10)
    ctk.CTkButton(app.sidebar, text="Make Booking (by Room)", width=100, command=lambda: show_booking_room(app)).pack(pady=10)
    ctk.CTkButton(app.sidebar, text="My Bookings", width=100, command=lambda: show_my_bookings(app)).pack(pady=10)
    ctk.CTkLabel(app.sidebar, text="Theme:", anchor="w").pack(padx=10, pady=(0, 5))
    app.theme_option = ctk.CTkOptionMenu(
        app.sidebar,
        values=["Light", "Dark"],
        command=lambda mode: change_theme(app, mode),
        width=160,
    )
    app.theme_option.set(ctk.get_appearance_mode())
    app.theme_option.pack(padx=10, pady=(0, 20))
    ctk.CTkButton(
        app.sidebar,
        text="Logout",
        width=100,
        command=getattr(app, "logout_callback", lambda: None),
    ).pack(pady=(0, 20))
