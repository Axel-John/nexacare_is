import flet as ft
from pages.login import login_ui
from database import init_db

def main(page: ft.Page):
    init_db()
    
    # Window settings
    page.window_width = 1920
    page.window_height = 1080
    page.window_maximized = True
    page.window_full_screen = True
    page.window_minimizable = False
    page.window_resizable = True
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
    
    # Force full screen
    def maximize(e=None):
        page.window_maximized = True
        page.window_full_screen = True
        page.update()
    
    page.on_resize = maximize
    page.on_window_event = maximize
    maximize()  # Call immediately
    
    login_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
