import flet as ft
import sys
sys.path.append("../")
from utils.navigation import navigate_to_login, create_sidebar

def dashboard_ui(page, user):
    page.clean()  # <-- Add this to clear the page before adding dashboard UI
    page.title = "NexaCare Dashboard"
    page.bgcolor = "#e6edff"
    page.padding = 0

    # Create a modal dialog container
    dialog_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Track currently selected menu item
    current_selection = ft.Ref[str]()
    current_selection.current = "Dashboard"  # Default selection

    def handle_logout(e):
        def close_dialog(confirmed=False):
            dialog_modal.visible = False
            if confirmed:
                navigate_to_login(page)
            page.update()

        # Create dialog content
        dialog_content = ft.Container(
            width=400,
            height=200,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Confirm Logout", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Container(height=20),
                    ft.Text("Are you sure you want to logout?", color=ft.Colors.GREY_800),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Yes",
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.PRIMARY,
                                ),
                                on_click=lambda _: close_dialog(True)
                            ),
                            ft.Container(width=20),
                            ft.OutlinedButton(
                                "No",
                                on_click=lambda _: close_dialog(False)
                            ),
                        ],
                    ),
                ],
            ),
        )

        # Show the dialog
        dialog_modal.content = dialog_content
        dialog_modal.visible = True
        page.update()

    # Create sidebar using the centralized function
    sidebar = create_sidebar(page, "hr", handle_logout, current_selection)

    # Top bar with search and profile
    top_bar = ft.Row(
        controls=[
            ft.TextField(
                hint_text="Search Schedule...", 
                expand=True,
                border_radius=8,
                filled=True,
                prefix_icon=ft.Icons.SEARCH,
                bgcolor=ft.Colors.WHITE,
            ),
            ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color=ft.Colors.GREY_800),
            ft.IconButton(icon=ft.Icons.LIGHT_MODE_OUTLINED, icon_color=ft.Colors.GREY_800),
            ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, icon_color=ft.Colors.GREY_800),
            ft.Container(
                content=ft.CircleAvatar(
                    content=ft.Text(user.get('first_name', 'U')[0].upper(), size=18),
                    radius=20,
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                ),
                on_click=lambda _: None  # Add profile menu handler here
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Main content placeholder (to be expanded in next steps)
    main_content = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                top_bar,
                ft.Text("Main Dashboard Content Here (Overview, Doctors, Patients)", size=18)
            ],
            spacing=20,
        ),
        padding=20
    )

    # Combine sidebar and content in a Stack to allow overlay
    page.add(
        ft.Stack(
            controls=[
                ft.Row(
                    controls=[
                        sidebar,
                        main_content
                    ],
                    expand=True
                ),
                dialog_modal  # Add the modal dialog container
            ],
            expand=True
        )
    )
