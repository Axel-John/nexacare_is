import flet as ft

def dashboard_ui(page: ft.Page, user: dict):
    page.clean()
    page.title = "Admin Dashboard"
    page.padding = 20
    
    # Header
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(f"Welcome, Admin {user.get('name', 'User')}", size=24, weight="bold"),
                ft.ElevatedButton("Logout", on_click=lambda _: page.go("/"))
            ],
            alignment="space-between"
        ),
        padding=10
    )
    
    # Main content
    content = ft.Container(
        content=ft.Column(
            [
                ft.Text("Admin Dashboard Content", size=20),
                ft.Text("System management and settings will appear here.", size=16)
            ],
            spacing=20
        ),
        padding=20,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        shadow=ft.BoxShadow(2, 2, 2, 2, ft.colors.GREY_300)
    )
    
    page.add(header, content)
