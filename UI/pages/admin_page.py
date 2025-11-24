import customtkinter as ctk

from UI.components.clear_contents import clear_contents


@clear_contents
def show_admin_dashboard(app):
    ctk.CTkLabel(app, text="Admin Dashboard", font=("Arial", 18, "bold")).pack(pady=20)
    ctk.CTkLabel(
        app,
        text="Administrator features will appear here.",
        wraplength=400,
        justify="center",
    ).pack(pady=10)
