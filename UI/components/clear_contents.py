from UI.components.sidebar_functions import hide_sidebar

def clear_contents(func):
    def wrapper(app, *args, **kwargs):
        if app.sidebar_visible:
            hide_sidebar(app)
        for widget in app.winfo_children():
            if widget not in app.always_present:
                widget.destroy()
        result =  func(app, *args, **kwargs)
        app.sidebar.lift()
        app.burger_menu_button.lift()        
        return result
    return wrapper