import customtkinter as ctk
import requests
import UI.components.passwords as pwd

def reset_password(app):
    for widget in app.winfo_children():
        widget.destroy()

    ctk.CTkButton(app, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E", command=app.create_widgets).grid(row=0, column=0, padx=10, pady=10, sticky="w")   
    ctk.CTkLabel(
        app,
        text="Reset Password",
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="center",
        justify="center"
    ).grid(row=0, column=1, columnspan=2, pady=10, sticky="nw")
    ctk.CTkLabel(app, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    email_entry = ctk.CTkEntry(app, width=180)
    email_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(app, text="Recovery Code:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    recovery_code_entry = ctk.CTkEntry(app, width=180)
    recovery_code_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(app, text="New Password:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    new_password_entry = ctk.CTkEntry(app, show="*", width=180)
    new_password_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w") 
    ctk.CTkLabel(app, text="Confirm New Password:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    confirm_new_password_entry = ctk.CTkEntry(app, show="*", width=180)
    confirm_new_password_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    submit_btn = ctk.CTkButton(
        app, 
        text="Submit", 
        width=100, 
        state="disabled",
        command=lambda: handle_new_password_submission(
            app,
            email_entry.get(),
            recovery_code_entry.get(),
            new_password_entry.get(),
            confirm_new_password_entry.get()
        )
    )
    submit_btn.grid(row=8, column=0, columnspan=2, pady=20)

    def validate_fields(*args):
        if (
            email_entry.get().strip() and
            recovery_code_entry.get().strip() and
            new_password_entry.get().strip() and
            confirm_new_password_entry.get().strip()
        ):
            submit_btn.configure(state="normal")
        else:
            submit_btn.configure(state="disabled")

# Implementation based on https://stackoverflow.com/questions/27215326/tkinter-keypress-and-keyrelease-events
    email_entry.bind("<KeyRelease>", validate_fields)
    recovery_code_entry.bind("<KeyRelease>", validate_fields)
    new_password_entry.bind("<KeyRelease>", validate_fields)
    confirm_new_password_entry.bind("<KeyRelease>", validate_fields)

def handle_new_password_submission(app, email, recovery_code, new_password, confirm_new_password):
    confirm_new_password = pwd.hash_password(confirm_new_password)
    if pwd.check_password(confirm_new_password, new_password) is False:
        ctk.CTkLabel(
            app,
            text="Password Reset Failed: Passwords do not match",
            text_color="red"
        ).grid(row=6, column=0, columnspan=2, pady=(0,10))
        return
    else:
        result = requests.post(
            "http://127.0.0.1:8000/users/email/password",
            json={
                "email": email,
                "recovery_code": recovery_code,
                "new_password": confirm_new_password
            }
        )

        if result.status_code == 200:
            for widget in app.winfo_children():
                widget.destroy()
            ctk.CTkLabel(app, text="Password Reset Successful! Please login with your new password.").grid(row=0, column=0, columnspan=2, pady=(30, 10))
            ctk.CTkButton(app, text="Back to Login", width=120, command=app.create_widgets).grid(row=1, column=0, columnspan=2, pady=20)
        # TODO: Waiting For Backend upate to provide specific error messages
        else:
            error_message = result.json().get("detail", "Login failed")
            if error_message == "User not found":
                ctk.CTkLabel(app, text="Login Failed: User not found", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            elif error_message == "Incorrect password":
                ctk.CTkLabel(app, text="Login Failed: Incorrect password", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            else:
                ctk.CTkLabel(app, text=f"Login Failed: {error_message}", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
