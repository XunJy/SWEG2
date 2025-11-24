import customtkinter as ctk
import requests
import UI.components.passwords as pwd
def create_account(app):
    for widget in app.winfo_children():
        widget.destroy()

    ctk.CTkButton(
        app, text="Back", width=60, height=28, fg_color="#0078D7",
        hover_color="#005A9E", command=app.create_widgets
    ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    ctk.CTkLabel(
        app,
        text="Create Account",
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="center",
        justify="center"
    ).grid(row=0, column=1, columnspan=2, pady=10, sticky="nw")

    ctk.CTkLabel(app, text="First Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    firstname_entry = ctk.CTkEntry(app, width=180)
    firstname_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(app, text="Surname:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    surname_entry = ctk.CTkEntry(app, width=180)
    surname_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(app, text="Email:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    email_entry = ctk.CTkEntry(app, width=180)
    email_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(app, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    password_entry = ctk.CTkEntry(app, show="*", width=180)
    password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(app, text="Confirm Password:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    confirm_password_entry = ctk.CTkEntry(app, show="*", width=180)
    confirm_password_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    submit_btn = ctk.CTkButton(
        app, 
        text="Submit", 
        width=100, 
        state="disabled",
        command=lambda: handle_account_creation(
            app,
            firstname_entry.get(),
            surname_entry.get(),
            email_entry.get(),
            password_entry.get(),
            confirm_password_entry.get()
        )
    )
    submit_btn.grid(row=6, column=0, columnspan=2, pady=20)

    def validate_fields(*args):
        if (
            firstname_entry.get().strip() and
            surname_entry.get().strip() and
            email_entry.get().strip() and
            password_entry.get().strip() and
            confirm_password_entry.get().strip()
        ):
            submit_btn.configure(state="normal")
        else:
            submit_btn.configure(state="disabled")

# Implementation based on https://stackoverflow.com/questions/27215326/tkinter-keypress-and-keyrelease-events
    firstname_entry.bind("<KeyRelease>", validate_fields)
    surname_entry.bind("<KeyRelease>", validate_fields)
    email_entry.bind("<KeyRelease>", validate_fields)
    password_entry.bind("<KeyRelease>", validate_fields)
    confirm_password_entry.bind("<KeyRelease>", validate_fields)

def handle_account_creation(app, first_name, last_name, email, password, confirm_password):
    # TODO: Waiting on Backend to implement account creation logic
    confirm_password = pwd.hash_password(confirm_password)
    if pwd.check_password(confirm_password, password) is False:
        ctk.CTkLabel(
            app,
            text="Account Creation Failed: Passwords do not match",
            text_color="red"
        ).grid(row=7, column=0, columnspan=2, pady=(0,10))
        return
    else:
        result = requests.post(
            "http://127.0.0.1:8000/users",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password
            }
        )
        status_code = result.status_code
        response_data = result.json()
        recovery_code = response_data.get("recovery_code")
        if status_code == 200:
            for widget in app.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                app,
                text="Create Account",
                font=ctk.CTkFont(size=20, weight="bold"),
                anchor="center",
                justify="center"
            ).grid(row=0, column=1, columnspan=2, pady=10, sticky="nw")
            ctk.CTkLabel(app, text="Account Created Successfully! Please login.").grid(row=0, column=0, columnspan=2, pady=(30, 10))
            ctk.CTkLabel(app, text="Recovery Code: " + recovery_code).grid(row=1, column=0, columnspan=2, pady=(0,10))
            ctk.CTkLabel(app, text="Please keep this recovery code safe for future password resets.").grid(row=2, column=0, columnspan=2, pady=(0,10))
            ctk.CTkButton(app, text="Back to Login", width=120, command=app.create_widgets).grid(row=3, column=0, columnspan=2, pady=20)
