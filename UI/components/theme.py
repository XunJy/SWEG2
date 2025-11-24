import customtkinter as ctk
from tkinter import ttk

def change_theme(app, mode):
    ctk.set_appearance_mode(mode)
    app.winfo_toplevel().update_idletasks()
    for win in app.winfo_toplevel().winfo_children():
        if isinstance(win, ctk.CTkToplevel):
            win.update_idletasks()
    apply_calendar_theme(app)
    apply_datepicker_theme(app)

def apply_calendar_theme(app):
    mode = ctk.get_appearance_mode().lower()
    if hasattr(app, 'calander'):
        # https://stackoverflow.com/questions/61493630/is-there-a-way-to-change-tkcalendars-color
        style = ttk.Style()
        style.theme_use("clam")
        if mode == "light":  
            style.configure("Treeview", background="white", foreground="black")
            app.calander.configure(background="white", foreground="black", headersbackground="#f0f0f0", normalbackground="white", weekendbackground="#f0f0f0", othermonthbackground="#d9d9d9", othermonthwebackground="#d9d9d9")
        else:
            style.configure("TCombobox", fieldbackground="#2b2b2b", foreground="white")
            app.calander.configure(background="#2b2b2b", foreground="white", headersbackground="#3a3a3a", normalbackground="#2b2b2b", weekendbackground="#3a3a3a", othermonthbackground="#1e1e1e", othermonthwebackground="#3a3a3a")

def apply_datepicker_theme(app):
    mode = ctk.get_appearance_mode().lower()
    if hasattr(app, 'date_picker'):
        style = ttk.Style()
        style.theme_use("clam")
        if mode == "light":  
            style.configure("TCombobox", fieldbackground="white", foreground="black")
            app.date_picker.configure(background="white", foreground="black", bordercolor="black", headersbackground="#f0f0f0", normalbackground="white", weekendbackground="#f0f0f0", othermonthbackground="#d9d9d9", othermonthwebackground="#d9d9d9")
        else:
            style.configure("TCombobox", fieldbackground="#2b2b2b", foreground="white")
            app.date_picker.configure(background="#2b2b2b", foreground="white", bordercolor="white", headersbackground="#3a3a3a", normalbackground="#2b2b2b", weekendbackground="#3a3a3a", othermonthbackground="#1e1e1e", othermonthwebackground="#3a3a3a")