import flet as ft
import sys
sys.path.append("../")
from utils.navigation import navigate_to_login, create_sidebar

def dashboard_ui(page, user):
    page.clean()
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
    sidebar = create_sidebar(page, "doctor", handle_logout)

    # Top bar with search and profile
    top_bar = ft.Row(
        controls=[
            ft.TextField(hint_text="Search Patients...", expand=True),
            ft.Icon(ft.Icons.NOTIFICATIONS),
            ft.Icon(ft.Icons.LIGHT_MODE),
            ft.Icon(ft.Icons.SETTINGS),
            ft.CircleAvatar(
                content=ft.Text(user.get('first_name', 'D')[0]),
                radius=20,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Main content area
    main_content = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                top_bar,
                ft.Container(height=20),  # Spacing
                ft.Text(
                    f"Welcome back, Dr. {user.get('first_name', '')} {user.get('last_name', '')}",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    f"ID: {user.get('user_id', '')}",
                    size=14,
                    color=ft.Colors.BLUE_GREY_700
                ),
                ft.Container(height=20),  # Spacing
                ft.Row(
                    controls=[
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.CALENDAR_TODAY, size=24, color=ft.Colors.BLUE_600),
                                                ft.Text("Today's Appointments", weight=ft.FontWeight.BOLD)
                                            ],
                                            alignment=ft.MainAxisAlignment.START
                                        ),
                                        ft.Text("5 Scheduled", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text("Next: 10:30 AM - John Doe")
                                    ]
                                ),
                                padding=20,
                                width=250
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.PEOPLE, size=24, color=ft.Colors.BLUE_600),
                                                ft.Text("Active Patients", weight=ft.FontWeight.BOLD)
                                            ],
                                            alignment=ft.MainAxisAlignment.START
                                        ),
                                        ft.Text("28", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text("3 New This Week")
                                    ]
                                ),
                                padding=20,
                                width=250
                            )
                        ),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.MEDICAL_SERVICES, size=24, color=ft.Colors.BLUE_600),
                                                ft.Text("Prescriptions", weight=ft.FontWeight.BOLD)
                                            ],
                                            alignment=ft.MainAxisAlignment.START
                                        ),
                                        ft.Text("12", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text("4 Pending Renewals")
                                    ]
                                ),
                                padding=20,
                                width=250
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
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
