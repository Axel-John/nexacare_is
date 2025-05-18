import flet as ft
from pages.login import login_ui
from database import init_db

def main(page: ft.Page):
    init_db()

    # Initial window settings
    page.window_minimizable = False
    page.window_resizable = False
    page.bgcolor = ft.Colors.WHITE
    page.padding = 0

    # Theme settings
    page.theme = ft.Theme(
        font_family="Poppins",
        use_material3=True,
    )
    page.fonts = {
        "Poppins": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Regular.ttf",
        "PoppinsMedium": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Medium.ttf",
        "PoppinsSemiBold": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-SemiBold.ttf",
        "Lato": "https://raw.githubusercontent.com/google/fonts/main/ofl/lato/Lato-Regular.ttf",
        "LatoMedium": "https://raw.githubusercontent.com/google/fonts/main/ofl/lato/Lato-Bold.ttf"
    }

    # Use a timer to set fullscreen after UI is loaded
    def set_fullscreen(e):
        page.window_full_screen = True
        page.window_maximized = True
        page.update()
        page.timer_interval = 0  # Stop the timer

    page.timer_interval = 0.2  # 200ms after load
    page.on_timer = set_fullscreen

    login_ui(page)

if __name__ == "__main__":
    # Use view=ft.FLET_APP for desktop, or view=None for default browser
    ft.app(target=main)

