import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents
from UI.pages.event_details_page import view_event_details, cancel_booking
@clear_contents
def show_my_bookings(app):
    events_frame = ctk.CTkScrollableFrame(app, width=450, height=400)
    events_frame.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(app, text="My Bookings", font=("Arial", 18, "bold")).pack(pady=20)

    if not getattr(app, "user_id", None):
        ctk.CTkLabel(events_frame, text="Please log in to view your bookings.").pack(pady=20)
        return

    bookings_response = requests.get(f"http://127.0.0.1:8000/bookings/user/{app.user_id}")
    if bookings_response.status_code != 200:
        ctk.CTkLabel(events_frame, text="Unable to load bookings from the server.").pack(pady=20)
        return

    bookings = bookings_response.json()
    if not bookings:
        ctk.CTkLabel(events_frame, text="You have no bookings yet.").pack(pady=20)
        return

    for booking in bookings:
        booking_id = booking.get("booking_id")
        details = fetch_booking_details(booking_id)

        name = details.get("name")
        description = details.get("description") or ""
        start_time = details.get("start_time")
        end_time = details.get("end_time")
        room_number = details.get("room_number") or details.get("room_id")
        room_building = details.get("room_building")
        room_display = f"Room {room_number}" if room_number else "Room"
        if room_building:
            room_display = f"{room_display} - {room_building}"

        frame = ctk.CTkFrame(events_frame)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text=name, anchor="w", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame, text=description, wraplength=450, justify="left", anchor="w").pack(anchor="w", padx=10)

        info_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        info_row.pack(fill="x", padx=10, pady=(5, 5))
        ctk.CTkLabel(info_row, text=f"Room: {room_display}", anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_row, text=f"Time: {start_time} - {end_time}", anchor="w").pack(anchor="w")

        button_row = ctk.CTkFrame(frame, fg_color=frame.cget("fg_color"))
        button_row.pack(fill="x", padx=10, pady=(0, 10))

        organiser = user_is_organiser(app.user_id, booking_id)
        if organiser:
            ctk.CTkButton(
                button_row,
                text="查看加入请求",
                width=120,
                height=28,
                fg_color="#5C8DFF",
                hover_color="#3b6fdc",
                command=lambda id=booking_id: show_requests(app, id),
            ).pack(side="right", padx=5)
            ctk.CTkButton(
                button_row,
                text="邀请用户",
                width=120,
                height=28,
                fg_color="#6b6b6b",
                hover_color="#4a4a4a",
                command=lambda id=booking_id: invite_users(app, id),
            ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_row,
            text="View More",
            width=100,
            height=28,
            fg_color="#0078D7",
            hover_color="#005A9E",
            command=lambda id=booking_id: view_event_details(app, id, caller="bookings"),
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            button_row,
            text="Cancel Booking",
            width=120,
            height=28,
            fg_color="#cc3333",
            hover_color="#990000",
            command=lambda id=booking_id: cancel_booking(app, id),
        ).pack(side="right", padx=5)


def fetch_booking_details(booking_id):
    response = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}")
    if response.status_code != 200:
        return {"booking_id": booking_id}

    booking = response.json()
    room_id = booking.get("room_id")

    if room_id:
        room_response = requests.get(f"http://127.0.0.1:8000/rooms/{room_id}")
        if room_response.status_code == 200:
            room = room_response.json()
            booking["room_number"] = room.get("number")
            booking["room_building"] = room.get("building")

    return booking


def user_is_organiser(user_id: str, booking_id: str) -> bool:
    try:
        resp = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}/users")
        if resp.status_code != 200:
            return False
        participants = resp.json()
        for entry in participants:
            user = entry.get("user", {})
            if user.get("user_id") == user_id and entry.get("organiser"):
                return True
    except Exception:
        return False
    return False


def show_requests(app, booking_id):
    window = ctk.CTkToplevel(app)
    window.geometry("420x320")
    window.title("Join Requests")

    header = ctk.CTkLabel(window, text="等待审批的加入请求", font=("Arial", 14, "bold"))
    header.pack(pady=(10, 5))

    resp = requests.get(f"http://127.0.0.1:8000/bookings/{booking_id}/requests")
    if resp.status_code != 200:
        ctk.CTkLabel(window, text="无法加载请求", text_color="red").pack(pady=10)
    else:
        requests_list = resp.json()
        if not requests_list:
            ctk.CTkLabel(window, text="当前没有加入申请。", text_color="#666").pack(pady=10)
        for req in requests_list:
            user_info = requests.get(f"http://127.0.0.1:8000/users/{req['user_id']}").json()
            row = ctk.CTkFrame(window, fg_color=window.cget("fg_color"))
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=f"{user_info.get('first_name')} {user_info.get('last_name')} ({user_info.get('email')})").pack(anchor="w")
            btn_row = ctk.CTkFrame(row, fg_color=row.cget("fg_color"))
            btn_row.pack(anchor="e", pady=(2, 0))
            ctk.CTkButton(
                btn_row,
                text="接受",
                width=80,
                fg_color="#33cc33",
                hover_color="#00b300",
                command=lambda invite_id=req["invite_id"]: _update_invite(invite_id, "accept", window),
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                btn_row,
                text="拒绝",
                width=80,
                fg_color="#cc3333",
                hover_color="#990000",
                command=lambda invite_id=req["invite_id"]: _update_invite(invite_id, "decline", window),
            ).pack(side="left", padx=4)

    ctk.CTkButton(window, text="关闭", command=window.destroy).pack(pady=10)
    window.focus_force()
    window.attributes("-topmost", True)
    window.after(1000, lambda: window.attributes("-topmost", False))


def _update_invite(invite_id: str, action: str, window=None):
    endpoint = "accept" if action == "accept" else "decline"
    resp = requests.put(f"http://127.0.0.1:8000/invites/{invite_id}/status/{endpoint}")
    if window and resp.status_code == 200:
        window.destroy()


def invite_users(app, booking_id):
    directory = ctk.CTkToplevel(app)
    directory.geometry("420x360")
    directory.title("邀请用户")

    ctk.CTkLabel(directory, text="选择用户发送邀请", font=("Arial", 14, "bold")).pack(pady=(10, 5))

    resp = requests.get("http://127.0.0.1:8000/users")
    if resp.status_code != 200:
        ctk.CTkLabel(directory, text="无法加载用户列表", text_color="red").pack(pady=10)
        ctk.CTkButton(directory, text="关闭", command=directory.destroy).pack(pady=5)
        return

    user_list = resp.json()
    scroll = ctk.CTkScrollableFrame(directory, width=380, height=220)
    scroll.pack(padx=10, pady=5, fill="both", expand=True)

    for user in user_list:
        if user.get("user_id") == app.user_id:
            continue
        row = ctk.CTkFrame(scroll, fg_color=scroll.cget("fg_color"))
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(
            row,
            text=f"{user.get('first_name')} {user.get('last_name')} ({user.get('email')})",
            anchor="w",
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            row,
            text="邀请",
            width=70,
            command=lambda email=user.get("email"): _send_invite(booking_id, email),
        ).pack(side="right", padx=6)

    ctk.CTkButton(directory, text="关闭", command=directory.destroy).pack(pady=8)
    directory.focus_force()
    directory.attributes("-topmost", True)
    directory.after(1000, lambda: directory.attributes("-topmost", False))


def _send_invite(booking_id: str, email: str):
    requests.post(
        "http://127.0.0.1:8000/invites",
        json={"booking_id": booking_id, "user_email": email},
    )
