import flet as ft
import sys
sys.path.append("../")
from utils.navigation import navigate_to_login, create_sidebar
from models.user import create_user, get_all_doctors

# Define admin theme colors
ADMIN_BLACK = "#1A1A1A"  # Deep black for text and buttons
ADMIN_GRAY_DARK = "#2D2D2D"  # Dark gray for borders
ADMIN_GRAY_MEDIUM = "#757575"  # Medium gray for secondary text
ADMIN_GRAY_LIGHT = "#F5F5F5"  # Light gray for backgrounds
ADMIN_WHITE = "#FFFFFF"  # White for card backgrounds
ADMIN_SUCCESS = "#4CAF50"  # Green for success states
ADMIN_WARNING = "#FFA726"  # Orange for warning states
ADMIN_ERROR = "#EF5350"  # Red for error states

def create_dashboard_content(page: ft.Page, user: dict, add_doctor_modal: ft.Container, doctors_grid: ft.Row, show_add_doctor_form) -> ft.Container:
    """Create the main dashboard content separate from the sidebar"""
    # Top bar with search and profile
    top_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD, color=ADMIN_BLACK),
                        ft.Container(width=20),
                        ft.Dropdown(
                            value="Today",
                            options=[
                                ft.dropdown.Option("Today"),
                                ft.dropdown.Option("This Week"),
                                ft.dropdown.Option("This Month"),
                            ],
                            width=150,
                            bgcolor=ADMIN_WHITE,
                            color=ADMIN_BLACK,
                            border_color=ADMIN_GRAY_DARK,
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color=ADMIN_BLACK),
                        ft.IconButton(icon=ft.Icons.LIGHT_MODE_OUTLINED, icon_color=ADMIN_BLACK),
                        ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, icon_color=ADMIN_BLACK),
                        ft.Container(
                            content=ft.CircleAvatar(
                                content=ft.Text(user.get('first_name', 'A')[0].upper(), size=18),
                                radius=20,
                                bgcolor=ADMIN_BLACK,
                                color=ADMIN_WHITE,
                            ),
                        ),
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=20,
    )

    # Overview Cards
    def create_stat_card(title, value, percent, up, down, icon, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(title, size=14, color=ADMIN_GRAY_MEDIUM),
                            ft.Container(
                                content=ft.Icon(icon, color=color, size=24),
                                padding=10,
                                border_radius=8,
                                bgcolor=ft.Colors.with_opacity(0.1, color),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=ADMIN_BLACK),
                    ft.Row(
                        controls=[
                            ft.Text(f"{percent}%", color=ADMIN_BLACK),
                            ft.Text(f"↑ {up}" if up else "", color=ADMIN_SUCCESS),
                            ft.Text(f"↓ {down}" if down else "", color=ADMIN_ERROR),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=ADMIN_WHITE,
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ADMIN_BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    overview_stats = ft.Row(
        controls=[
            create_stat_card("Total Doctors", "152", "65", "10", "2", ft.Icons.PERSON, ADMIN_BLACK),
            create_stat_card("Total Patients", "1145", "82", "230", "45", ft.Icons.PEOPLE, ADMIN_WARNING),
            create_stat_card("Schedule", "102", "27", "31", "23", ft.Icons.CALENDAR_TODAY, ADMIN_SUCCESS),
            create_stat_card("Beds Available", "15", "8", "11", "2", ft.Icons.BED, ADMIN_ERROR),
        ],
        spacing=20,
    )

    # Doctors Section
    doctors_header = ft.Row(
        controls=[
            ft.Text("Doctors", size=20, weight=ft.FontWeight.BOLD),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Add Doctor",
                        icon=ft.Icons.ADD,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                        ),
                        on_click=show_add_doctor_form
                    ),
                ],
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Main content container
    return ft.Container(
        content=ft.Column(
            controls=[
                top_bar,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            overview_stats,
                            ft.Container(height=30),
                            doctors_header,
                            doctors_grid,
                            ft.Container(height=30),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=20,
                ),
            ],
        ),
        expand=True,
    )

def dashboard_ui(page: ft.Page, user: dict):
    page.clean()
    page.title = "NexaCare Admin"
    page.bgcolor = "#e6edff"
    page.padding = 0

    # Track currently selected menu item
    current_selection = ft.Ref[str]()
    current_selection.current = "Dashboard"  # Default selection

    # Create a modal dialog container for logout
    dialog_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Create a modal dialog container for add doctor form
    add_doctor_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Form fields
    first_name_field = ft.TextField(
        label="First Name",
        width=600,
        height=40,
        border_color=ft.Colors.BLUE_200,
        focused_border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(
            color=ft.Colors.BLACK,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ft.Colors.BLUE_GREY,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter first name",
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_400,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )
    last_name_field = ft.TextField(
        label="Last Name",
        width=200,
        height=40,
        border_color=ft.Colors.BLUE_200,
        focused_border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(
            color=ft.Colors.BLACK,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ft.Colors.BLUE_GREY,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter last name",
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_400,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )
    email_field = ft.TextField(
        label="Email",
        width=800,
        height=40,
        border_color=ft.Colors.BLUE_200,
        focused_border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(
            color=ft.Colors.BLACK,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ft.Colors.BLUE_GREY,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter email address",
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_400,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )
    password_field = ft.TextField(
        label="Password",
        width=800,
        height=40,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.BLUE_200,
        focused_border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(
            color=ft.Colors.BLACK,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ft.Colors.BLUE_GREY,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter password",
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_400,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )
    error_text = ft.Text(
        "",
        color=ft.Colors.RED_400,
        size=11,
        weight=ft.FontWeight.W_500,
        visible=False
    )
    success_text = ft.Text(
        "",
        color=ft.Colors.GREEN,
        size=11,
        weight=ft.FontWeight.W_500,
        visible=False
    )

    def close_add_doctor_dialog(e=None):
        add_doctor_modal.visible = False
        # Clear the form fields
        first_name_field.value = ""
        last_name_field.value = ""
        email_field.value = ""
        password_field.value = ""
        error_text.visible = False
        success_text.visible = False
        page.update()

    def handle_add_doctor(e):
        error_text.visible = False
        success_text.visible = False
        
        # Basic validation
        if not all([first_name_field.value, last_name_field.value, email_field.value, password_field.value]):
            error_text.value = "Please fill in all fields"
            error_text.visible = True
            page.update()
            return

        # Create doctor account
        success, message, user_id = create_user(
            first_name_field.value,
            last_name_field.value,
            email_field.value,
            password_field.value,
            "Doctor"
        )

        if success:
            success_text.value = f"Doctor added successfully! ID: {user_id}"
            success_text.visible = True
            # Update the doctors grid
            update_doctors_grid()
            page.update()
            # Close the dialog after 2 seconds
            page.after(2, close_add_doctor_dialog)
        else:
            error_text.value = message
            error_text.visible = True
            page.update()

    def show_add_doctor_form(e):
        add_doctor_modal.content = ft.Container(
            width=550,
            height=400,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            padding=ft.padding.all(20),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    # Header Section
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                            controls=[
                                ft.Text(
                                    "Add New Doctor",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE,
                                ),
                                ft.Text(
                                    "Fill in the information below",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                        ),
                        padding=ft.padding.only(bottom=5),
                    ),
                    # Form Fields Section
                    ft.Container(
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                # Name Fields Row
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=first_name_field,
                                            expand=1,
                                        ),
                                        ft.Container(width=1),
                                        ft.Container(
                                            content=last_name_field,
                                            expand=1,
                                        ),
                                    ],
                                ),
                                email_field,
                                password_field,
                            ],
                        ),
                        width=500,
                    ),
                    # Messages Section
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                            controls=[
                                error_text,
                                success_text,
                            ],
                        ),
                        padding=ft.padding.symmetric(vertical=2),
                    ),
                    # Buttons Section
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Add Doctor",
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE,
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                    ),
                                    width=160,
                                    on_click=handle_add_doctor
                                ),
                                ft.OutlinedButton(
                                    "Cancel",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(width=1.5, color=ft.Colors.BLUE),
                                    ),
                                    width=160,
                                    on_click=close_add_doctor_dialog
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=ft.padding.only(top=5),
                    ),
                ],
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
        )
        add_doctor_modal.visible = True
        page.update()

    def create_doctor_card(doctor: dict):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(doctor["first_name"][0], size=24),
                        radius=30,
                        bgcolor=ft.Colors.BLUE_GREY,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        f"Dr. {doctor['first_name']} {doctor['last_name']}", 
                        size=14, 
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"ID: {doctor['user_id']}", 
                        size=12,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        doctor["email"],
                        size=12,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                        width=160,  # Set width to ensure proper text wrapping
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            width=180,
            height=160,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    doctors_grid = ft.Row(
        controls=[],
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        wrap=True,
    )

    def update_doctors_grid():
        doctors = get_all_doctors()
        doctors_grid.controls = [create_doctor_card(doctor) for doctor in doctors]
        page.update()

    # Initial load of doctors
    update_doctors_grid()

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

        dialog_modal.content = dialog_content
        dialog_modal.visible = True
        page.update()

    # Create sidebar using the centralized function with current_selection
    sidebar = create_sidebar(page, "admin", handle_logout, current_selection)

    # Create main dashboard content
    main_content = create_dashboard_content(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form)

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
                dialog_modal,
                add_doctor_modal,
            ],
            expand=True
        )
    )
