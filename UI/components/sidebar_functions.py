
def toggle_sidebar(app):
    if app.sidebar_visible:
        hide_sidebar(app)
    else:
        show_sidebar(app)

def show_sidebar(app):
    app.sidebar_visible = True
    for x in range(-200, 10, 20):
        app.sidebar.place(x=x, y=50)
        app.sidebar.update()

def hide_sidebar(app):
    app.sidebar_visible = False
    for x in range(10, -200, -20):
        app.sidebar.place(x=x, y=50)
        app.sidebar.update()