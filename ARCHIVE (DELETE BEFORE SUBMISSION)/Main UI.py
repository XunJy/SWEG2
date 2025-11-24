import customtkinter as ctk
import datetime
import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar

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

        create_btn = ctk.CTkButton(link_frame, text="Create Account", width=120, height=25, fg_color="transparent", text_color="blue", hover_color="#E0E0E0", command=self.create_account)
        create_btn.grid(row=0, column=0, padx=5)

        reset_btn = ctk.CTkButton(link_frame, text="Forgot Password?", width=120, height=25, fg_color="transparent", text_color="blue", hover_color="#E0E0E0", command=self.reset_password)
        reset_btn.grid(row=0, column=1, padx=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # TODO: Waiting on Backend to implment login logic
        if username == "admin" and password == "123":
            self.on_success()
        else:
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and "Login Failed" in widget.cget("text"):
                    widget.destroy()
            if username == "":
                ctk.CTkLabel(self, text="Login Failed: Username cannot be empty", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            elif username != "admin":
                ctk.CTkLabel(self, text="Login Failed: User not found", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            elif password == "":
                ctk.CTkLabel(self, text="Login Failed: Password cannot be empty", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))
            else:
                ctk.CTkLabel(self, text="Login Failed: Incorrect password", text_color="red").grid(row=6, column=0, columnspan=2, pady=(0,10))

    def create_account(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkButton(
            self, text="Back", width=60, height=28, fg_color="#0078D7",
            hover_color="#005A9E", command=self.create_widgets
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(self, text="First Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        firstname_entry = ctk.CTkEntry(self, width=180)
        firstname_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Surname:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        surname_entry = ctk.CTkEntry(self, width=180)
        surname_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Email:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        email_entry = ctk.CTkEntry(self, width=180)
        email_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        password_entry = ctk.CTkEntry(self, show="*", width=180)
        password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Confirm Password:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        confirm_password_entry = ctk.CTkEntry(self, show="*", width=180)
        confirm_password_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        submit_btn = ctk.CTkButton(
            self, 
            text="Submit", 
            width=100, 
            state="disabled",
            command=lambda: self.handle_account_creation(
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

    def handle_account_creation(self, first_name, last_name, email, password, confirm_password):
        # TODO: Waiting on Backend to implement account creation logic
        success = True
        recovery_code = "123"
        if success:
            for widget in self.winfo_children():
                widget.destroy()
            ctk.CTkLabel(self, text="Account Created Successfully! Please login.").grid(row=0, column=0, columnspan=2, pady=(30, 10))
            ctk.CTkLabel(self, text="Recovery Code: " + recovery_code).grid(row=1, column=0, columnspan=2, pady=(0,10))
            ctk.CTkLabel(self, text="Please keep this recovery code safe for future password resets.").grid(row=2, column=0, columnspan=2, pady=(0,10))
            ctk.CTkButton(self, text="Back to Login", width=120, command=self.create_widgets).grid(row=3, column=0, columnspan=2, pady=20)

    def reset_password(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkButton(self, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E", command=self.create_widgets).grid(row=0, column=0, padx=10, pady=10, sticky="w")   

        ctk.CTkLabel(self, text="Email:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        email_entry = ctk.CTkEntry(self, width=180)
        email_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Recovery Code:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        recovery_code_entry = ctk.CTkEntry(self, width=180)
        recovery_code_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        submit_btn = ctk.CTkButton(
            self, 
            text="Submit", 
            width=100, 
            state="disabled",
            command=lambda: self.handle_password_reset_prompt(
                email_entry.get(),
                recovery_code_entry.get()
            )
        )
        submit_btn.grid(row=3, column=0, columnspan=2, pady=20)

        def validate_fields(*args):
            if (
                email_entry.get().strip() and
                recovery_code_entry.get().strip()
            ):
                submit_btn.configure(state="normal")
            else:
                submit_btn.configure(state="disabled")

# Implementation based on https://stackoverflow.com/questions/27215326/tkinter-keypress-and-keyrelease-events
        email_entry.bind("<KeyRelease>", validate_fields)
        recovery_code_entry.bind("<KeyRelease>", validate_fields)


    def handle_password_reset_prompt(self, email, recovery_code):
        # TODO: Waiting on Backend to implement password reset logic
        if email != "admin" and recovery_code != "123":
            ctk.CTkLabel(self, text="Reset Failed: User not found and Invalid Recovery Code", text_color="red").grid(row=3, column=0, columnspan=2, pady=(0,10))
        else:
            for widget in self.winfo_children():
                widget.destroy()

            ctk.CTkButton(self, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E", command=self.create_widgets).grid(row=0, column=0, padx=10, pady=10, sticky="w")   
            ctk.CTkLabel(self, text="New Password:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            new_password_entry = ctk.CTkEntry(self, show="*", width=180)
            new_password_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w") 
            ctk.CTkLabel(self, text="Confirm New Password:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            confirm_new_password_entry = ctk.CTkEntry(self, show="*", width=180)
            confirm_new_password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
            submit_btn = ctk.CTkButton(
                self, 
                text="Submit", 
                width=100, 
                state="disabled",
                command=lambda: self.handle_new_password_submission(
                    new_password_entry.get(),
                    confirm_new_password_entry.get()
                )
            )
            submit_btn.grid(row=3, column=0, columnspan=2, pady=20)

            def validate_fields(*args):
                if (
                    new_password_entry.get().strip() and
                    confirm_new_password_entry.get().strip()
                ):
                    submit_btn.configure(state="normal")
                else:
                    submit_btn.configure(state="disabled")

            new_password_entry.bind("<KeyRelease>", validate_fields)
            confirm_new_password_entry.bind("<KeyRelease>", validate_fields)

    def handle_new_password_submission(self, new_password, confirm_new_password):
        if hash(new_password) != hash(confirm_new_password):
            ctk.CTkLabel(self, text="Password Reset Failed: Passwords do not match", text_color="red").grid(row=3, column=0, columnspan=2, pady=(0,10))
        else:
            for widget in self.winfo_children():
                widget.destroy()
            ctk.CTkLabel(self, text="Password Reset Successful! Please login with your new password.").grid(row=0, column=0, columnspan=2, pady=(30, 10))
            ctk.CTkButton(self, text="Back to Login", width=120, command=self.create_widgets).grid(row=1, column=0, columnspan=2, pady=20)

class MainUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.sidebar_visible = False

        self.burger_menu_button = ctk.CTkButton(
            self, 
            text="☰",
            width=40,
            height=40,
            command=self.toggle_sidebar
        )
        self.burger_menu_button.place(x=10, y=10)
        self.sidebar = ctk.CTkFrame(
            self,
            width = 150,
            height = 150,
        )
        self.sidebar.place(x=-175, y=50)
        self.always_present = [self.sidebar, self.burger_menu_button]
        self.fill_sidebar()

        # Hard Coded Events, Invites and Rooms, TODO: Pull from backend once implemented
        self.events = [
            {"id": 1, "name": "event 1", "description":"This is an event"},
            {"id": 2, "name": "event 2", "description":"This is an event"},
            {"id": 3, "name": "event 3", "description":"This is an event"},
            {"id": 4, "name": "event 4", "description":"This is an event"},
            {"id": 5, "name": "event 5", "description":"This is an event"},
            {"id": 6, "name": "event 6", "description":"This is an event"},
        ]

        self.invites = [
            {"id": 1, "name": "event 1", "description":"This is an event"},
            {"id": 2, "name": "event 2", "description":"This is an event"},
            {"id": 3, "name": "event 3", "description":"This is an event"},
        ]
        
        self.bookings = [
            {"id": 4, "name": "event 4", "description":"This is an event"},
            {"id": 5, "name": "event 5", "description":"This is an event"},
            {"id": 6, "name": "event 6", "description":"This is an event"},
        ]

        self.rooms = ["Room 101", "Room 102", "Room 201", "Room 202"]

    def fill_sidebar(self):
        ctk.CTkButton(self.sidebar, text="Events", width=100, command=self.show_events).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="My Invites", width=100, command=self.show_invites).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Make Booking (by Date)", width=100, command=self.show_booking_date).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Make Booking (by Room)", width=100, command=self.show_booking_room).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="My Bookings", width=100, command=self.show_my_bookings).pack(pady=10)

        ctk.CTkLabel(self.sidebar, text="Theme:", anchor="w").pack(padx=10, pady=(0, 5))
        self.theme_option = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Light", "Dark"],
            command=self.change_theme,
            width=160
        )
        self.theme_option.set(ctk.get_appearance_mode())
        self.theme_option.pack(padx=10, pady=(0, 20))

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.hide_sidebar()
        else:
            self.show_sidebar()

    def show_sidebar(self):
        self.sidebar_visible = True
        for x in range(-200, 10, 20):
            self.sidebar.place(x=x, y=50)
            self.sidebar.update()

    def hide_sidebar(self):
        self.sidebar_visible = False
        for x in range(10, -200, -20):
            self.sidebar.place(x=x, y=50)
            self.sidebar.update()

    def clear_contents(func):
        def wrapper(self, *args, **kwargs):
            if self.sidebar_visible:
                self.hide_sidebar()
            for widget in self.winfo_children():
                if widget not in self.always_present:
                    widget.destroy()
            result =  func(self, *args, **kwargs)
            self.sidebar.lift()
            self.burger_menu_button.lift()        
            return result
        return wrapper
    
    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.winfo_toplevel().update_idletasks()
        for win in self.winfo_toplevel().winfo_children():
            if isinstance(win, ctk.CTkToplevel):
                win.update_idletasks()
        self.apply_calendar_theme()

    def apply_calendar_theme(self):
        mode = ctk.get_appearance_mode().lower()
        if hasattr(self, 'calander'):
            # https://stackoverflow.com/questions/61493630/is-there-a-way-to-change-tkcalendars-color
            style = ttk.Style()
            style.theme_use("clam")
            if mode == "light":  
                style.configure("Treeview", background="white", foreground="black")
                self.calander.configure(background="white", foreground="black", headersbackground="#f0f0f0", normalbackground="white", weekendbackground="#f0f0f0", othermonthbackground="#d9d9d9", othermonthwebackground="#d9d9d9")
            else:
                style.configure("TCombobox", fieldbackground="#2b2b2b", foreground="white")
                self.calander.configure(background="#2b2b2b", foreground="white", headersbackground="#3a3a3a", normalbackground="#2b2b2b", weekendbackground="#3a3a3a", othermonthbackground="#1e1e1e", othermonthwebackground="#3a3a3a")


    # ================= Invite Related UI Methods ================
    @clear_contents
    def show_invites(self):
    # Hard Coded Event Invitess TODO: Wait for backend implementation
        invites_frame = ctk.CTkScrollableFrame(self, width=450, height=400)
        invites_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self, text="Invited Events").pack(pady=(10, 20))

        for invite in self.invites:
            frame = ctk.CTkFrame(invites_frame)
            frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(frame, text=invite["name"], anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(frame, text=invite["description"], wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
            ctk.CTkButton(
                frame,
                text="Accept",
                width=100,
                height=28,
                fg_color="#33cc33",
                hover_color="#00cc00",
                command=lambda id=invite["id"]: self.accept_invite(id)
            ).pack(padx=10, pady=(10, 10), anchor="e")
            ctk.CTkButton(
                frame,
                text="Decline",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda id=invite["id"]: self.decline_invite(id)
            ).pack(padx=10, pady=(10, 10), anchor="e")
            ctk.CTkButton(
                frame,
                text="View More",
                width=100,
                height=28,
                fg_color="#0078D7",
                hover_color="#005A9E",
                command=lambda id=invite["id"]: self.view_event_details(id, caller="invites")
            ).pack(padx=10, pady=(10, 10), anchor="e")


    # ================ Event Related UI Methods ================
    @clear_contents
    def show_events(self):
        # Hard Coded Events TODO: Wait for backend implementation
        events_frame = ctk.CTkScrollableFrame(self, width=450, height=400)
        events_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self, text="Available Events").pack(pady=(10, 20))

        for event in self.events:
            frame = ctk.CTkFrame(events_frame)
            frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(frame, text=event["name"], anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(frame, text=event["description"], wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
            ctk.CTkButton(
                frame,
                text="View More",
                width=100,
                height=28,
                fg_color="#0078D7",
                hover_color="#005A9E",
                command=lambda id=event["id"]: self.view_event_details(id, caller="events")
            ).pack(padx=10, pady=(10, 10), anchor="e")
    
    @clear_contents
    def view_event_details(self, id, caller):
        back_button = ctk.CTkButton(self, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E",
        )
        if caller == "events":
            back_button.configure(command=self.show_events)
        else:
            back_button.configure(command=self.show_invites)
        back_button.pack(padx=55, pady=(10, 10), anchor="w")

        
        event = None
        for event in self.events:
            if event["id"] == id:
                event = event
                break
        if event is None:
            ctk.CTkLabel(self, text="Event not found").pack(pady=(10, 20))
        else:
            ctk.CTkLabel(self, text=event["name"]).pack(pady=(10, 10))
            ctk.CTkLabel(self, text=event["description"]).pack(pady=(0, 20))
        invite = None
        booking = None
        for inv in self.invites:
            if inv["id"] == id:
                invite = inv
                break
        for book in self.bookings:
            if book["id"] == id:
                booking = book
                break
        if invite is not None:
            ctk.CTkButton(
                self,
                text="Accept",
                width=100,
                height=28,
                fg_color="#33cc33",
                hover_color="#00cc00",
                command=lambda id=invite["id"]: self.accept_invite(id)
            ).pack(padx=10, pady=(10, 10), anchor="e")
            ctk.CTkButton(
                self,
                text="Decline",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda id=invite["id"]: self.decline_invite(id)
            ).pack(padx=10, pady=(10, 10), anchor="e")

        if booking is not None:
            ctk.CTkButton(
                self,
                text="Cancel Booking",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda id=booking["id"]: self.cancel_booking(id)
            ).pack(padx=10, pady=(10, 10), anchor="e")


# ================ Event/Invite Action Methods ================
    def accept_invite(self, id):
        # TODO Awaiting Backend Implemnentation to store accepted invite
        success_screen = ctk.CTkToplevel(main_app)
        success_screen.geometry("300x150")
        success_screen.title("University Room Booking System - Invite Accepted")
        ctk.CTkLabel(success_screen, text="Invite Accepted Successfully!").pack(pady=20)
        ctk.CTkButton(success_screen, text="OK", command=lambda: self.close_accept_and_decline_screen(success_screen)).pack(pady=20)
        success_screen.focus_force()
        success_screen.attributes("-topmost", True)
        success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))

    def close_accept_and_decline_screen(self, screen):
        screen.destroy()
        self.show_events()

    def decline_invite(self, id):
        # TODO Awaiting Backend Implemnentation to store accepted invite
        success_screen = ctk.CTkToplevel(main_app)
        success_screen.geometry("300x150")
        success_screen.title("University Room Booking System - Invite Declined")
        ctk.CTkLabel(success_screen, text="Invite Declined!").pack(pady=20)
        ctk.CTkButton(success_screen, text="OK", command=lambda: self.close_accept_and_decline_screen(success_screen)).pack(pady=20)
        success_screen.focus_force()
        success_screen.attributes("-topmost", True)
        success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))
        

# ================= Booking Related UI Methods ================
    @clear_contents
    def show_booking_date(self):
        ctk.CTkLabel(self, text="Select Date for Booking").pack(pady=(10, 20))
        ctk.CTkLabel(self, text="Please select a room:").pack(pady=(0,10))
        # TODO: Populate with available rooms from backend
        self.room_select = ctk.CTkOptionMenu(
            self,
            values=["Select a room"] + self.rooms,
            width=160,
            command=self.on_room_selected
        )
        self.room_select.pack(pady=(0,20))
        self.room_select.set("Select a room")

        self.calander = tkcalendar.Calendar(self, selectmode='day', mindate=datetime.date.today(), font=("Arial", 14))
        self.calander.selection_set(date=datetime.date.today())
        self.calander.config(state="disabled")

    def on_room_selected(self, value):
        if value != "Select a room":
            self.calander.place(relx=0.5, rely=0.5, anchor="e")
            self.calander.config(state="normal") 
            self.calander.bind("<<CalendarSelected>>", lambda ev, cal=self.calander: self._on_calendar_selected(ev, cal))
            self.apply_calendar_theme()
            if hasattr(self, 'time_slots_frame') and self.time_slots_frame is not None:
                self.time_slots_frame.destroy()     
            self.time_slots_frame = ctk.CTkFrame(self, width=200, height=300)
            self.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")
            self.show_time_slots_for_date(value, datetime.date.today())

    def _on_calendar_selected(self, event, cal_widget):
        try:
            selected_date = cal_widget.selection_get()
            selected_room = self.room_select.get()
        except Exception:
            selected_date = datetime.date.today()
        self.show_time_slots_for_date(selected_room, selected_date)

    def show_time_slots_for_date(self, room,  date):
        if not hasattr(self, 'time_slots_frame') or self.time_slots_frame is None:
            self.time_slots_frame = ctk.CTkFrame(self, width=200, height=300)
            self.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")

        for child in self.time_slots_frame.winfo_children():
            child.destroy()

        header = ctk.CTkLabel(self.time_slots_frame, text=f"Slots for {date.isoformat()}")
        header.pack(pady=(8, 6))

        # Hard Coded Room Availability TODO: Wait for backend implementation
        slots = [f"{h:02d}:00 - {h+1:02d}:00" for h in range(9, 17)]

        for slot in slots:
            btn = ctk.CTkButton(self.time_slots_frame, text=slot, width=160, height=30,
                                command=lambda s=slot, d=date: self.select_time_slot("timeslots",d, s, room_id=room))
            btn.pack(padx=10, pady=4)

    def back_button_to_booking_date(self, room_id, date):
        self.show_booking_date()
        self.room_select.set(room_id)
        self.calander.place(relx=0.5, rely=0.5, anchor="e")
        self.calander.config(state="normal") 
        self.calander.selection_set(date=date)
        self.calander.bind("<<CalendarSelected>>", lambda ev, cal=self.calander: self._on_calendar_selected(ev, cal))
        self.apply_calendar_theme()
        if hasattr(self, 'time_slots_frame') and self.time_slots_frame is not None:
            self.time_slots_frame.destroy()     
        self.time_slots_frame = ctk.CTkFrame(self, width=200, height=300)
        self.time_slots_frame.place(relx=0.5, rely=0.5, anchor="w")
        self.show_time_slots_for_date(room_id, date)

    def back_button_to_booking_room(self, date, time_slot):
        self.show_booking_room()
        self.date_picker.set_date(date)
        hour, minute = map(int, time_slot.split(" - ")[0].split(":"))
        ampm = "AM"


    # https://stackoverflow.com/questions/26902034/how-to-center-a-tkinter-widget-in-a-sticky-frame
    @clear_contents
    def select_time_slot(self, caller, date, slot_text, room_id=None):
        back_button = ctk.CTkButton(self, text="Back", width=60, height=28, fg_color="#0078D7", hover_color="#005A9E",
        )
        if caller == "timeslots":
            back_button.configure(
            command=lambda: self.back_button_to_booking_date(room_id, date)
        )
        else:
            back_button.configure(command=lambda: self.back_button_to_booking_room(date, slot_text))
        back_button.pack(padx=55, pady=(10, 10), anchor="w")

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=10)

        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Booking Title:").grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        self.title_entry = ctk.CTkEntry(form_frame, width=250)
        self.title_entry.grid(
            row=0, column=1, padx=10, pady=5, sticky="w"
        )

        ctk.CTkLabel(form_frame, text="Booking Description:").grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.description_entry = ctk.CTkEntry(form_frame, width=250)
        self.description_entry.grid(
            row=1, column=1, padx=10, pady=5, sticky="w"
        )

        self.submit_button = ctk.CTkButton(form_frame, text="Submit", command=self.submit_booking)
        self.submit_button.grid(
            row=2, column=0, columnspan=2, pady=20
        )
    
    def submit_booking(self):
        # TODO Awaiting Backend Implemnentation to store booking and handle race conditions
        success = True
        notification_screen = ctk.CTkToplevel(main_app)
        notification_screen.geometry("300x150")
        notification_screen.title("University Room Booking System - Notification")
        button = ctk.CTkButton(notification_screen, text="OK", command=notification_screen.destroy)
        if self.title_entry.get() == "":
            ctk.CTkLabel(notification_screen, text="Booking Failed! Title is required.").pack(pady=20)
        elif self.description_entry.get() == "":
            ctk.CTkLabel(notification_screen, text="Booking Failed! Description is required.").pack(pady=20)
        elif not success:
            ctk.CTkLabel(notification_screen, text="Booking Failed!").pack(pady=20)
        else:
            ctk.CTkLabel(notification_screen, text="Booking Successful!").pack(pady=20)
            button.configure(command=lambda: self.handle_close_booking(success, notification_screen))
        button.pack(pady=10)
        notification_screen.focus_force()
        notification_screen.attributes("-topmost", True)
        notification_screen.after(1000, lambda: notification_screen.attributes("-topmost", False))

    def handle_close_booking(self, success, notification_screen):
        notification_screen.destroy()
        if success:
            self.show_my_bookings()

    # Reimplemented https://pythonguides.com/create-date-time-picker-using-python-tkinter in customtkinter
    @clear_contents
    def show_booking_room(self):
        ctk.CTkLabel(self, text="Room Booking", font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Please select a date:").pack(pady=(0, 10))

        self.date_picker = tkcalendar.DateEntry(self)
        self.date_picker.pack(pady=(0, 20))
        ctk.CTkLabel(self, text="Select Time:", font=("Arial", 14)).pack(pady=(10, 5))

        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(pady=5)

        hour_var = tk.StringVar(value="12")
        minute_var = tk.StringVar(value="00")
        ampm_var = ctk.StringVar(value="AM")

        self.hour_spin = tk.Spinbox(
            time_frame, from_=1, to=12, wrap=True,
            textvariable=hour_var, width=4,
            font=("Arial", 14), justify="center"
        )
        self.hour_spin.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(time_frame, text=":", font=("Arial", 14)).pack(side="left")

        self.minute_spin = tk.Spinbox(
            time_frame, from_=0, to=59, wrap=True,
            textvariable=minute_var, width=4,
            font=("Arial", 14), justify="center"
        )
        self.minute_spin.pack(side="left", padx=(5, 0))

        ampm_menu = ctk.CTkOptionMenu(time_frame, values=["AM", "PM"], variable=ampm_var, width=70)
        ampm_menu.pack(side="left", padx=(10, 0))

        ctk.CTkButton(self, text="Search")

        ctk.CTkLabel(self, text="Select a Room:", font=("Arial", 14)).pack(pady=(20, 5))

        rooms_frame = ctk.CTkScrollableFrame(self, width=450, height=300)
        rooms_frame.pack(pady=10)

        def handle_room_click(selected_room):

            date = self.date_picker.get_date()

            hour = int(hour_var.get())
            minute = int(minute_var.get())
            ampm = ampm_var.get()

            if ampm == "PM" and hour != 12:
                hour += 12
            if ampm == "AM" and hour == 12:
                hour = 0

            slot_text = f"{hour:02d}:{minute:02d}"
            self.select_time_slot("date", date, slot_text, selected_room)


        for room in self.rooms:
            frame = ctk.CTkFrame(rooms_frame)
            frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(frame, text=room, anchor="w").pack(anchor="w", padx=10, pady=(10, 5))

            ctk.CTkButton(
                frame,
                text="Book This Room",
                width=160,
                command=lambda r=room: handle_room_click(r)
            ).pack(pady=(0, 10), anchor="e")

    @clear_contents
    def show_my_bookings(self):
        # Hard Coded Bookings TODO: Wait for backend implementation
        events_frame = ctk.CTkScrollableFrame(self, width=450, height=400)
        events_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self, text="My Event Bookings").pack(pady=(10, 20))

        for booking in self.bookings:
            frame = ctk.CTkFrame(events_frame)
            frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(frame, text=booking["name"], anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(frame, text=booking["description"], wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)
            ctk.CTkButton(
                frame,
                text="View More",
                width=100,
                height=28,
                fg_color="#0078D7",
                hover_color="#005A9E",
                command=lambda id=booking["id"]: self.view_event_details(id, caller="bookings")
            ).pack(padx=10, pady=(10, 10), anchor="e")
            ctk.CTkButton(
                frame,
                text="Cancel Booking",
                width=100,
                height=28,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda id=booking["id"]: self.cancel_booking(id)
            ).pack(padx=10, pady=(10, 10), anchor="e")

    def cancel_booking(self, id):
        # TODO Awaiting Backend Implemnentation to handle booking cancellation
        success_screen = ctk.CTkToplevel(main_app)
        success_screen.geometry("300x150")
        success_screen.title("University Room Booking System - Booking Cancelled")
        ctk.CTkLabel(success_screen, text="Booking Cancelled Successfully!").pack(pady=20)
        ctk.CTkButton(success_screen, text="OK", command=lambda: self.close_cancel_booking_screen(success_screen)).pack(pady=20)
        success_screen.focus_force()
        success_screen.attributes("-topmost", True)
        success_screen.after(1000, lambda: success_screen.attributes("-topmost", False))

    def close_cancel_booking_screen(self, screen):
        screen.destroy()
        self.show_my_bookings()


if __name__ == "__main__":
    ctk.set_appearance_mode("system")

    main_app = ctk.CTk()
    main_app.geometry("600x600")
    main_app.title("University Room Booking System")

    app = MainUI(main_app)

    def login_success():
        login_screen.destroy()
        app.show_events()

    login_screen = ctk.CTkToplevel(main_app)
    login_screen.geometry("400x400")
    login_screen.title("Login")

    LoginUI(login_screen, on_success=login_success)

    login_screen.focus_force()
    login_screen.grab_set()  
    login_screen.attributes("-topmost", True)
    login_screen.after(300, lambda: login_screen.attributes("-topmost", False))

    # login_success()
    main_app.mainloop()
