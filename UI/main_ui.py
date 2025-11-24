import customtkinter as ctk
from PIL import ImageTk, Image

from UI.authentication.login_ui import LoginUI
from UI.components.sidebar import fill_sidebar
from UI.components.sidebar_functions import toggle_sidebar
from UI.pages.admin_page import show_admin_dashboard
from UI.pages.events_page import show_events



class MainUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.user_id = None
        self.is_admin = False
        self.sidebar_visible = False
        self.logout_callback = lambda: None

        self.burger_menu_button = ctk.CTkButton(
            self,
            text="☰",
            width=40,
            height=40,
            command=lambda: toggle_sidebar(self),
            state="disabled"
        )
        self.burger_menu_button.place(x=10, y=10)
        self.sidebar = ctk.CTkFrame(
            self,
            width = 150,
            height = 150,
        )
        self.sidebar.place(x=-175, y=50)

        img = Image.open("UI/assets/logo.png")
        self.logo_image = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(60, 80)
        )

        self.logo = ctk.CTkLabel(self, image=self.logo_image, text="")
        self.logo.place(x=530, y=0)

        self.always_present = [self.sidebar, self.burger_menu_button, self.logo]
        fill_sidebar(self)

        # Hard Coded Events, Invites and Rooms, TODO: Pull from backend once implemented
        self.events = [
            {"id": 1, "name": "Event 1", "description":"This is an event", "room_id": "Room 101"},
            {"id": 2, "name": "Event 2", "description":"This is an event", "room_id": "Room 102"},
            {"id": 3, "name": "Event 3", "description":"This is an event", "room_id": "Room 201"},
            {"id": 4, "name": "Event 4", "description":"This is an event", "room_id": "Room 202"},
            {"id": 5, "name": "Event 5", "description":"This is an event", "room_id": "Room 101"},
            {"id": 6, "name": "Event 6", "description":"This is an event", "room_id": "Room 102"},
        ]

        self.invites = [
            {"id": 1, "name": "Event 1", "description":"This is an event", "room_id": "Room 101"},
            {"id": 2, "name": "Event 2", "description":"This is an event", "room_id": "Room 102"},
            {"id": 3, "name": "Event 3", "description":"This is an event", "room_id": "Room 201"},
        ]

        self.rooms = ["Room 101", "Room 102", "Room 201", "Room 202"]

if __name__ == "__main__":
    ctk.set_appearance_mode("system")

    main_app = ctk.CTk()
    main_app.geometry("600x600")
    main_app.title("University Room Booking System")

    app = MainUI(main_app)

    login_screen = None

    def login_success(user_id, is_admin):
        global login_screen
        if login_screen is not None and login_screen.winfo_exists():
            login_screen.destroy()
            login_screen = None
        app.burger_menu_button.configure(state="normal")
        app.user_id = user_id
        app.is_admin = is_admin
        fill_sidebar(app)
        if is_admin:
            show_admin_dashboard(app)
        else:
            show_events(app)

    def show_login():
        global login_screen
        if login_screen is not None and login_screen.winfo_exists():
            login_screen.lift()
        else:
            login_screen = ctk.CTkToplevel(main_app)
            login_screen.geometry("400x400")
            login_screen.title("Login")
            LoginUI(login_screen, on_success=login_success)
            login_screen.focus_force()
            login_screen.grab_set()
            login_screen.attributes("-topmost", True)
            login_screen.after(300, lambda: login_screen.attributes("-topmost", False))

    def handle_logout():
        if app.sidebar_visible:
            from UI.components.sidebar_functions import hide_sidebar

            hide_sidebar(app)
        app.user_id = None
        app.is_admin = False
        app.burger_menu_button.configure(state="disabled")
        for widget in app.winfo_children():
            if widget not in app.always_present:
                widget.destroy()
        fill_sidebar(app)
        show_login()

    app.logout_callback = handle_logout
    fill_sidebar(app)

    button = ctk.CTkButton(app, text="Login", command=show_login)
    button.pack( pady=20)

    show_login()

    main_app.mainloop()

