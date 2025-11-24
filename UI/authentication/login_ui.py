import customtkinter as ctk
import requests
from .register_ui import create_account
from .reset_password import reset_password

class LoginUI(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        if self.winfo_children():
            for widget in self.winfo_children():
                widget.destroy()

        ctk.CTkLabel(self, text="Welcome", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(30, 10))
        ctk.CTkLabel(self, text="University Room Booking System", font=("Arial", 14)).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        ctk.CTkLabel(self, text="Username:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.username_entry = ctk.CTkEntry(self, width=180)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self, text="Password:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.password_entry = ctk.CTkEntry(self, show="*", width=180)
        self.password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkButton(self, text="Login", width=100, command=self.handle_login).grid(row=4, column=0, columnspan=2, pady=20)

        link_frame = ctk.CTkFrame(self, fg_color="transparent")
        link_frame.grid(row=5, column=0, columnspan=2)

        create_btn = ctk.CTkButton(link_frame, text="Create Account", width=120, height=25, fg_color="transparent", text_color="blue", hover_color="#E0E0E0", command=lambda: create_account(self))
        create_btn.grid(row=0, column=0, padx=5)

        reset_btn = ctk.CTkButton(link_frame, text="Forgot Password?", width=120, height=25, fg_color="transparent", text_color="blue", hover_color="#E0E0E0", command=lambda: reset_password(self))
        reset_btn.grid(row=0, column=1, padx=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        response = requests.post("http://127.0.0.1:8000/login", json={"email": username, "password": password})
        if response.status_code == 200:
            user_id = response.json().get("user_id")
            self.on_success(user_id)
        else:
            error_message = response.json().get("detail", "Login failed")
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and "Login Failed" in widget.cget("text"):
                    widget.destroy()
            if username == "":
                ctk.CTkLabel(self, text="Login Failed: Username cannot be empty", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            elif error_message == "User not found":
                ctk.CTkLabel(self, text="Login Failed: User not found", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            elif password == "":
                ctk.CTkLabel(self, text="Login Failed: Password cannot be empty", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            elif error_message == "Incorrect password":
                ctk.CTkLabel(self, text="Login Failed: Incorrect password", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            else:
                ctk.CTkLabel(self, text=f"Login Failed: {error_message}", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))