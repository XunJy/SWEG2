import customtkinter as ctk
import requests

from UI.components.clear_contents import clear_contents

API_BASE = "http://127.0.0.1:8000"


def _error_label(parent, message):
    ctk.CTkLabel(parent, text=message, text_color="red").pack(pady=(5, 0))


def _section_header(parent, text):
    ctk.CTkLabel(parent, text=text, font=("Arial", 16, "bold")).pack(anchor="w", pady=(15, 5))


@clear_contents
def show_admin_dashboard(app):
    dashboard = ctk.CTkScrollableFrame(app, width=500, height=520)
    dashboard.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(dashboard, text="管理员控制台", font=("Arial", 18, "bold")).pack(pady=(10, 0))
    ctk.CTkLabel(
        dashboard,
        text="初始管理员账号/密码：Admin / Admin",
        text_color="#0078D7",
    ).pack(pady=(0, 10))
    ctk.CTkButton(
        dashboard,
        text="Logout",
        width=120,
        fg_color="#cc3333",
        hover_color="#990000",
        command=lambda: app.handle_logout(),
    ).pack(pady=(0, 10))

    room_frame = ctk.CTkFrame(dashboard, fg_color=dashboard.cget("fg_color"))
    room_frame.pack(fill="x", padx=10, pady=10)
    _section_header(room_frame, "自习室与座位管理")
    _build_rooms_section(app, room_frame)

    booking_frame = ctk.CTkFrame(dashboard, fg_color=dashboard.cget("fg_color"))
    booking_frame.pack(fill="x", padx=10, pady=10)
    _section_header(booking_frame, "预约管理")
    _build_booking_section(app, booking_frame)

    user_frame = ctk.CTkFrame(dashboard, fg_color=dashboard.cget("fg_color"))
    user_frame.pack(fill="x", padx=10, pady=10)
    _section_header(user_frame, "用户管理")
    _build_user_section(app, user_frame)


def _build_rooms_section(app, frame):
    form = ctk.CTkFrame(frame)
    form.pack(fill="x", pady=(0, 10))

    entries = {}
    for idx, (label, width) in enumerate(
        [
            ("名称/编号", 120),
            ("楼栋", 80),
            ("容量", 60),
            ("开放时间", 100),
            ("关闭时间", 100),
        ]
    ):
        ctk.CTkLabel(form, text=label).grid(row=0, column=idx, padx=5, pady=5)
        entry = ctk.CTkEntry(form, width=width)
        entry.grid(row=1, column=idx, padx=5, pady=5)
        entries[label] = entry

    status_option = ctk.CTkOptionMenu(form, values=["available", "unavailable", "maintenance", "closed"])
    status_option.set("available")
    ctk.CTkLabel(form, text="状态").grid(row=0, column=5, padx=5, pady=5)
    status_option.grid(row=1, column=5, padx=5, pady=5)

    feedback = ctk.CTkLabel(form, text="")
    feedback.grid(row=2, column=0, columnspan=6, pady=(5, 0))

    def create_room():
        feedback.configure(text="", text_color="")
        try:
            capacity_val = int(entries["容量"].get())
        except ValueError:
            feedback.configure(text="容量必须为数字", text_color="red")
            return

        resp = requests.post(
            f"{API_BASE}/admin/rooms",
            json={
                "admin_id": getattr(app, "user_id", ""),
                "number": entries["名称/编号"].get(),
                "building": entries["楼栋"].get(),
                "capacity": capacity_val,
                "open_time": entries["开放时间"].get(),
                "close_time": entries["关闭时间"].get(),
                "status": status_option.get(),
            },
        )
        if resp.status_code == 200:
            feedback.configure(text=resp.json().get("message"), text_color="green")
            _refresh_rooms(app, frame)
        else:
            feedback.configure(text=f"创建失败: {resp.json().get('detail', '未知错误')}", text_color="red")

    ctk.CTkButton(form, text="添加自习室", command=create_room, width=140).grid(row=1, column=6, padx=10)

    _refresh_rooms(app, frame)


def _refresh_rooms(app, frame):
    for widget in frame.pack_slaves():
        if isinstance(widget, ctk.CTkScrollableFrame):
            widget.destroy()

    list_frame = ctk.CTkScrollableFrame(frame, width=480, height=180)
    list_frame.pack(fill="x", pady=(5, 0))

    resp = requests.get(f"{API_BASE}/admin/rooms", params={"admin_id": getattr(app, "user_id", "")})
    if resp.status_code != 200:
        _error_label(list_frame, "无法获取房间列表")
        return

    rooms = resp.json()
    if not rooms:
        ctk.CTkLabel(list_frame, text="暂无房间信息").pack(pady=10)
        return

    for room in rooms:
        row = ctk.CTkFrame(list_frame, fg_color=list_frame.cget("fg_color"))
        row.pack(fill="x", pady=5)
        info = f"{room.get('number')} - {room.get('building')} | 容量 {room.get('capacity')} | 状态 {room.get('status')}"
        if room.get("open_time") or room.get("close_time"):
            info += f" | 开放 {room.get('open_time') or '-'} ~ {room.get('close_time') or '-'}"
        ctk.CTkLabel(row, text=info, anchor="w").pack(side="left", padx=5)

        def make_status_updater(room_id, status_value):
            def updater():
                requests.put(
                    f"{API_BASE}/admin/rooms/{room_id}",
                    json={"admin_id": getattr(app, "user_id", ""), "status": status_value},
                )
                _refresh_rooms(app, frame)

            return updater

        actions = ctk.CTkFrame(row, fg_color=row.cget("fg_color"))
        actions.pack(side="right", padx=5)
        ctk.CTkButton(actions, text="标记不可用", width=100, command=make_status_updater(room.get("room_id"), "unavailable")).pack(side="left", padx=2)
        ctk.CTkButton(actions, text="恢复可用", width=90, command=make_status_updater(room.get("room_id"), "available")).pack(side="left", padx=2)
        ctk.CTkButton(
            actions,
            text="删除",
            fg_color="#b3261e",
            hover_color="#8c1d17",
            width=70,
            command=lambda rid=room.get("room_id"): _delete_room(app, frame, rid),
        ).pack(side="left", padx=2)


def _delete_room(app, frame, room_id):
    requests.delete(f"{API_BASE}/admin/rooms/{room_id}", params={"admin_id": getattr(app, "user_id", "")})
    _refresh_rooms(app, frame)


def _build_booking_section(app, frame):
    filters = ctk.CTkFrame(frame)
    filters.pack(fill="x", pady=(0, 10))

    entries = {}
    for idx, label in enumerate(["房间ID", "用户ID", "开始时间>=", "结束时间<="]):
        ctk.CTkLabel(filters, text=label).grid(row=0, column=idx, padx=5, pady=5)
        entry = ctk.CTkEntry(filters, width=120)
        entry.grid(row=1, column=idx, padx=5, pady=5)
        entries[label] = entry

    bookings_area = ctk.CTkScrollableFrame(frame, width=480, height=180)
    bookings_area.pack(fill="x")

    def load_bookings():
        params = {
            "admin_id": getattr(app, "user_id", ""),
            "room_id": entries["房间ID"].get() or None,
            "user_id": entries["用户ID"].get() or None,
            "start_after": entries["开始时间>="].get() or None,
            "end_before": entries["结束时间<="].get() or None,
        }
        resp = requests.get(f"{API_BASE}/admin/bookings", params=params)
        for widget in bookings_area.winfo_children():
            widget.destroy()
        if resp.status_code != 200:
            _error_label(bookings_area, "无法加载预约记录")
            return
        bookings = resp.json()
        if not bookings:
            ctk.CTkLabel(bookings_area, text="暂无预约").pack(pady=10)
            return
        for b in bookings:
            row = ctk.CTkFrame(bookings_area, fg_color=bookings_area.cget("fg_color"))
            row.pack(fill="x", pady=4)
            summary = f"{b.get('name')} | 房间 {b.get('room_id')} | {b.get('start_time')} - {b.get('end_time')}"
            ctk.CTkLabel(row, text=summary, anchor="w").pack(side="left", padx=5)
            ctk.CTkButton(
                row,
                text="强制取消",
                width=90,
                fg_color="#b3261e",
                hover_color="#8c1d17",
                command=lambda bid=b.get("booking_id"): _cancel_booking(app, bookings_area, bid, load_bookings),
            ).pack(side="right", padx=5)

    ctk.CTkButton(filters, text="查询预约", command=load_bookings, width=100).grid(row=1, column=4, padx=10)
    load_bookings()


def _cancel_booking(app, container, booking_id, refresh_callback):
    resp = requests.delete(
        f"{API_BASE}/admin/bookings/{booking_id}", params={"admin_id": getattr(app, "user_id", "")}
    )
    for widget in container.winfo_children():
        if isinstance(widget, ctk.CTkLabel) and "取消失败" in widget.cget("text"):
            widget.destroy()
    if resp.status_code != 200:
        _error_label(container, "取消失败")
    refresh_callback()


def _build_user_section(app, frame):
    form = ctk.CTkFrame(frame)
    form.pack(fill="x", pady=(0, 10))

    entries = {}
    labels = ["名", "姓", "邮箱", "密码"]
    for idx, label in enumerate(labels):
        ctk.CTkLabel(form, text=label).grid(row=0, column=idx, padx=5, pady=5)
        entry = ctk.CTkEntry(form, width=120, show="*" if label == "密码" else "")
        entry.grid(row=1, column=idx, padx=5, pady=5)
        entries[label] = entry

    admin_toggle = ctk.CTkCheckBox(form, text="管理员", width=20)
    admin_toggle.grid(row=1, column=len(labels), padx=10)
    feedback = ctk.CTkLabel(form, text="")
    feedback.grid(row=2, column=0, columnspan=5, pady=(5, 0))

    def create_user():
        resp = requests.post(
            f"{API_BASE}/admin/users",
            json={
                "admin_id": getattr(app, "user_id", ""),
                "first_name": entries["名"].get(),
                "last_name": entries["姓"].get(),
                "email": entries["邮箱"].get(),
                "password": entries["密码"].get(),
                "admin": bool(admin_toggle.get()),
            },
        )
        if resp.status_code == 200:
            feedback.configure(text=f"创建成功，恢复码: {resp.json().get('recovery_code')}", text_color="green")
            _refresh_users(app, frame)
        else:
            feedback.configure(text=f"创建失败: {resp.json().get('detail', '未知错误')}", text_color="red")

    ctk.CTkButton(form, text="添加用户", command=create_user, width=120).grid(row=1, column=len(labels) + 1, padx=10)

    _refresh_users(app, frame)


def _refresh_users(app, frame):
    for widget in frame.pack_slaves():
        if isinstance(widget, ctk.CTkScrollableFrame):
            widget.destroy()

    users_frame = ctk.CTkScrollableFrame(frame, width=480, height=180)
    users_frame.pack(fill="x", pady=(5, 0))

    resp = requests.get(f"{API_BASE}/admin/users", params={"admin_id": getattr(app, "user_id", "")})
    if resp.status_code != 200:
        _error_label(users_frame, "无法获取用户信息")
        return

    users = resp.json()
    if not users:
        ctk.CTkLabel(users_frame, text="暂无用户").pack(pady=10)
        return

    for user in users:
        row = ctk.CTkFrame(users_frame, fg_color=users_frame.cget("fg_color"))
        row.pack(fill="x", pady=4)
        summary = f"{user.get('first_name')} {user.get('last_name')} ({user.get('email')})"
        ctk.CTkLabel(row, text=summary, anchor="w").pack(side="left", padx=5)

        controls = ctk.CTkFrame(row, fg_color=row.cget("fg_color"))
        controls.pack(side="right", padx=5)

        admin_switch = ctk.CTkSwitch(controls, text="管理员", onvalue=1, offvalue=0)
        admin_switch.select() if user.get("admin") else admin_switch.deselect()
        admin_switch.pack(side="left", padx=5)

        def update_role(u_id, switch):
            requests.put(
                f"{API_BASE}/admin/users/{u_id}/role",
                json={"admin_id": getattr(app, "user_id", ""), "admin": bool(switch.get())},
            )

        admin_switch.configure(command=lambda uid=user.get("user_id"), sw=admin_switch: update_role(uid, sw))

        ctk.CTkButton(
            controls,
            text="删除",
            fg_color="#b3261e",
            hover_color="#8c1d17",
            width=70,
            command=lambda uid=user.get("user_id"): _delete_user(app, frame, uid),
        ).pack(side="left", padx=5)


def _delete_user(app, frame, user_id):
    requests.delete(f"{API_BASE}/admin/users/{user_id}", params={"admin_id": getattr(app, "user_id", "")})
    _refresh_users(app, frame)
