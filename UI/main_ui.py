import customtkinter as ctk
from PIL import ImageTk, Image

from UI.authentication.login_ui import LoginUI
from UI.components.sidebar import fill_sidebar
from UI.components.sidebar_functions import toggle_sidebar
from UI.pages.events_page import show_events



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

    def login_success(user_id):
        global login_screen
        if login_screen is not None and login_screen.winfo_exists():
            login_screen.destroy()
        app.burger_menu_button.configure(state="normal")
        app.user_id = user_id
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

    button = ctk.CTkButton(app, text="Login", command=show_login)
    button.pack( pady=20)

    show_login()

    main_app.mainloop()

