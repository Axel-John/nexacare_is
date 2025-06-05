import flet as ft
import sys
import time
sys.path.append("../")
from utils.navigation import navigate_to_login, create_sidebar
from models.user import get_all_doctors, get_all_hrs, verify_doctor, delete_doctor, update_doctor, verify_hr, delete_hr, update_hr
from database import create_user  # Import create_user from database instead

# Define admin theme colors
ADMIN_BLACK = "#1A1A1A"  # Deep black for text and buttons
ADMIN_GRAY_DARK = "#2D2D2D"  # Dark gray for borders
ADMIN_GRAY_MEDIUM = "#757575"  # Medium gray for secondary text
ADMIN_GRAY_LIGHT = "#F5F5F5"  # Light gray for backgrounds
ADMIN_WHITE = "#FFFFFF"  # White for card backgrounds
ADMIN_SUCCESS = "#4CAF50"  # Green for success states
ADMIN_WARNING = "#FFA726"  # Orange for warning states
ADMIN_ERROR = "#EF5350"  # Red for error states

def create_dashboard_doctor_card(doctor: dict, page: ft.Page, dialog_modal: ft.Container, handle_menu_selection, main_content: ft.Container):
    """Create a simple doctor card for the dashboard matching HR card design with verification status"""
    is_verified = doctor.get('is_verified', False)
    status_color = ADMIN_SUCCESS if is_verified else ADMIN_WARNING
    
    def handle_card_click(e):
        def close_dialog(confirmed=False):
            dialog_modal.visible = False
            if confirmed:
                # Switch to doctors tab and show doctor's details
                handle_menu_selection("Doctors", None, lambda t, e, *args: handle_menu_selection(t, e, main_content))
                # Show doctor's details
                handle_view_details(doctor, page, dialog_modal)
            page.update()

        # Create dialog content
        dialog_content = ft.Container(
            width=400,
            height=250,
            bgcolor=ADMIN_GRAY_DARK,
            border_radius=10,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "View Doctor Details", 
                        size=20, 
                        weight=ft.FontWeight.BOLD, 
                        color=ADMIN_WHITE
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        f"Would you like to view details for Dr. {doctor['first_name']} {doctor['last_name']}?",
                        color=ADMIN_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Yes",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_BLACK,
                                ),
                                on_click=lambda _: close_dialog(True)
                            ),
                            ft.Container(width=20),
                            ft.OutlinedButton(
                                "No",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                ),
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

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Stack(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(doctor["first_name"][0], size=24),
                            radius=30,
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                        ),
                        ft.Container(
                            content=ft.Container(
                                width=12,
                                height=12,
                                border_radius=6,
                                bgcolor=status_color,
                            ),
                            alignment=ft.alignment.bottom_right,
                            margin=ft.margin.only(right=5, bottom=5),
                        ),
                    ],
                ),
                    alignment=ft.alignment.center,
                    width=280,
                ),
                ft.Container(height=15),  # Increased spacing after avatar
                ft.Text(
                    f"Dr. {doctor['first_name']} {doctor['last_name']}", 
                    size=16,  # Increased font size
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ADMIN_WHITE,
                ),
                ft.Container(height=8),  # Added spacing after name
                ft.Text(
                    f"ID: {doctor['user_id']}", 
                    size=13,  # Increased font size
                    color=ADMIN_GRAY_MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),  # Added spacing after ID
                ft.Text(
                    doctor["email"],
                    size=13,  # Increased font size
                    color=ADMIN_GRAY_MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                    width=240,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,  # Removed default spacing to use custom spacing
        ),
        padding=20,  # Increased padding
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        width=280,
        height=220,  # Increased height
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.1, ADMIN_BLACK),
            offset=ft.Offset(0, 2),
        ),
        on_click=handle_card_click,
    )

def create_dashboard_hr_card(hr: dict, page: ft.Page, dialog_modal: ft.Container, handle_menu_selection, main_content: ft.Container):
    """Create a simple HR card for the dashboard matching doctor card design with verification status"""
    is_verified = hr.get('is_verified', False)
    status_color = ADMIN_SUCCESS if is_verified else ADMIN_WARNING
    
    def handle_card_click(e):
        def close_dialog(confirmed=False):
            dialog_modal.visible = False
            if confirmed:
                # Switch to HR tab and show HR's details
                handle_menu_selection("HR", None, lambda t, e, *args: handle_menu_selection(t, e, main_content))
                # Show HR's details
                handle_view_hr_details(hr, page, dialog_modal)
            page.update()

        # Create dialog content
        dialog_content = ft.Container(
            width=400,
            height=250,
            bgcolor=ADMIN_GRAY_DARK,
            border_radius=10,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "View HR Details", 
                        size=20, 
                        weight=ft.FontWeight.BOLD, 
                        color=ADMIN_WHITE
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        f"Would you like to view details for {hr['first_name']} {hr['last_name']}?",
                        color=ADMIN_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Yes",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_BLACK,
                                ),
                                on_click=lambda _: close_dialog(True)
                            ),
                            ft.Container(width=20),
                            ft.OutlinedButton(
                                "No",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                ),
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

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Stack(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(hr["first_name"][0], size=24),
                            radius=30,
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                        ),
                        ft.Container(
                            content=ft.Container(
                                width=12,
                                height=12,
                                border_radius=6,
                                bgcolor=status_color,
                            ),
                            alignment=ft.alignment.bottom_right,
                            margin=ft.margin.only(right=5, bottom=5),
                        ),
                    ],
                ),
                    alignment=ft.alignment.center,
                    width=280,
                ),
                ft.Container(height=15),  # Increased spacing after avatar
                ft.Text(
                    f"{hr['first_name']} {hr['last_name']}", 
                    size=16,  # Increased font size
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ADMIN_WHITE,
                ),
                ft.Container(height=8),  # Added spacing after name
                ft.Text(
                    f"ID: {hr['user_id']}", 
                    size=13,  # Increased font size
                    color=ADMIN_GRAY_MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),  # Added spacing after ID
                ft.Text(
                    hr["email"],
                    size=13,  # Increased font size
                    color=ADMIN_GRAY_MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                    width=240,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,  # Removed default spacing to use custom spacing
        ),
        padding=20,  # Increased padding
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        width=280,
        height=220,  # Increased height
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.1, ADMIN_BLACK),
            offset=ft.Offset(0, 2),
        ),
        on_click=handle_card_click,
    )

def create_dashboard_content(page: ft.Page, user: dict, add_doctor_modal: ft.Container, doctors_grid: ft.Row, show_add_doctor_form, add_hr_modal: ft.Container, hrs_grid: ft.Row, show_add_hr_form, dialog_modal: ft.Container, handle_menu_selection, main_content: ft.Container) -> ft.Container:
    """Create the main dashboard content separate from the sidebar"""
    # Top bar with search and profile
    top_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD, color=ADMIN_WHITE),
                        ft.Container(width=20),
                        ft.Dropdown(
                            value="Today",
                            options=[
                                ft.dropdown.Option("Today"),
                                ft.dropdown.Option("This Week"),
                                ft.dropdown.Option("This Month"),
                            ],
                            width=150,
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                            border_color=ADMIN_GRAY_MEDIUM,
                        ),
                    ],
                ),
                        ft.Container(
                            content=ft.CircleAvatar(
                                content=ft.Text(user.get('first_name', 'A')[0].upper(), size=18),
                                radius=20,
                                bgcolor=ADMIN_GRAY_DARK,
                                color=ADMIN_WHITE,
                            ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=20,
    )

    # Get all doctors and HR staff
    all_doctors = get_all_doctors()
    all_hrs = get_all_hrs()
    
    # Calculate statistics
    total_doctors = len(all_doctors)
    total_hrs = len(all_hrs)
    verified_doctors = len([d for d in all_doctors if d.get('is_verified', False)])
    verified_hrs = len([h for h in all_hrs if h.get('is_verified', False)])
    pending_doctors = len([d for d in all_doctors if not d.get('is_verified', False)])
    pending_hrs = len([h for h in all_hrs if not h.get('is_verified', False)])

    # Overview Cards
    def create_stat_card(title, value, subtitle, icon, color):
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
                    ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=ADMIN_WHITE),
                    ft.Text(subtitle, size=12, color=ADMIN_GRAY_MEDIUM),
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=ADMIN_GRAY_DARK,
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
            create_stat_card(
                "Total Doctors", 
                str(total_doctors),
                f"{verified_doctors} verified • {pending_doctors} pending",
                ft.Icons.PERSON,
                ADMIN_WHITE
            ),
            create_stat_card(
                "Total HR Staff", 
                str(total_hrs),
                f"{verified_hrs} verified • {pending_hrs} pending",
                ft.Icons.PEOPLE,
                ADMIN_WARNING
            ),
            create_stat_card(
                "Verified Users", 
                str(verified_doctors + verified_hrs),
                f"{verified_doctors} doctors • {verified_hrs} HR staff",
                ft.Icons.VERIFIED,
                ADMIN_SUCCESS
            ),
            create_stat_card(
                "Pending Verification", 
                str(pending_doctors + pending_hrs),
                f"{pending_doctors} doctors • {pending_hrs} HR staff",
                ft.Icons.PENDING,
                ADMIN_ERROR
            ),
        ],
        spacing=20,
    )

    # Doctors Section
    doctors_header = ft.Row(
        controls=[
            ft.Text("Recent Doctors", size=20, weight=ft.FontWeight.BOLD, color=ADMIN_WHITE),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Add Doctor",
                        icon=ft.Icons.ADD,
                        style=ft.ButtonStyle(
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                            shape=ft.RoundedRectangleBorder(radius=2),
                        ),
                        on_click=show_add_doctor_form
                    ),
                ],
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Create doctors grid with simple cards
    doctor_cards = [create_dashboard_doctor_card(doctor, page, dialog_modal, handle_menu_selection, main_content) for doctor in get_all_doctors()[:5]]
    if not doctor_cards:
        doctor_cards = [ft.Container(width=280, height=220, opacity=0)]  # Invisible placeholder
    doctors_grid = ft.Row(
        controls=doctor_cards,
        wrap=True,
        spacing=20,
        run_spacing=20,
    )

    # HR Section
    hrs_header = ft.Row(
        controls=[
            ft.Text("HR Staff", size=20, weight=ft.FontWeight.BOLD, color=ADMIN_WHITE),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Add HR",
                        icon=ft.Icons.ADD,
                        style=ft.ButtonStyle(
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                            shape=ft.RoundedRectangleBorder(radius=3),
                        ),
                        on_click=show_add_hr_form
                    ),
                ],
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Create HR grid with simple cards
    hr_cards = [create_dashboard_hr_card(hr, page, dialog_modal, handle_menu_selection, main_content) for hr in get_all_hrs()[:5]]
    if not hr_cards:
        hr_cards = [ft.Container(width=280, height=220, opacity=0)]  # Invisible placeholder
    hrs_grid = ft.Row(
        controls=hr_cards,
        wrap=True,
        spacing=20,
        run_spacing=20,
    )

    # Main content container with scrolling
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
                            hrs_header,
                            hrs_grid,
                            ft.Container(height=30),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=20,
                    expand=True,
                ),
            ],
            expand=True,
        ),
        expand=True,
        bgcolor=ADMIN_BLACK,
    )

def update_doctors_grid(page: ft.Page, doctors_grid: ft.Row, dialog_modal: ft.Container, success_text: ft.Text):
    """Update the doctors grid with current data"""
    # Get fresh data from database
    doctors = get_all_doctors()
    
    # Create new cards with updated data
    doctors_grid.controls = [create_doctor_card(doctor, page, dialog_modal, doctors_grid, success_text) for doctor in doctors]
    
    # Update the page to reflect changes
    page.update()

def handle_verify_doctor(doctor: dict, page: ft.Page, dialog_modal: ft.Container, doctors_grid: ft.Row, success_text: ft.Text):
    """Handle doctor verification"""
    def close_dialog(confirmed=False):
        dialog_modal.visible = False
        if confirmed:
            # Update verification status in database
            result = verify_doctor(doctor['user_id'])
            if isinstance(result, tuple):
                success, message = result
            else:
                success, message = result, "Unknown error"
            if not success:
                # Show error dialog
                error_dialog = ft.Container(
                    width=400,
                    height=250,
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR,
                                size=48,
                                color=ADMIN_ERROR,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Verification Failed", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            ft.Text(
                                message,
                                color=ADMIN_WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "OK",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_ERROR,
                                ),
                                on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                            ),
                        ],
                    ),
                )
                dialog_modal.content = error_dialog
                dialog_modal.visible = True
                page.update()
                return

            # Update the UI immediately
            update_doctors_grid(page, doctors_grid, dialog_modal, success_text)
            # Create countdown text
            countdown_text = ft.Text(
                "Window will close in 3",
                color=ADMIN_GRAY_MEDIUM,
                size=12,
            )
            # Show success dialog
            success_dialog = ft.Container(
                width=400,
                height=400,
                bgcolor=ADMIN_GRAY_DARK,
                border_radius=10,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(height=20),
                        ft.Text(
                            "Verification Successful", 
                            size=20, 
                            weight=ft.FontWeight.BOLD, 
                            color=ADMIN_WHITE
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            f"Dr. {doctor['first_name']} {doctor['last_name']} has been verified successfully.",
                            color=ADMIN_WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "The verification status has been updated.",
                            color=ADMIN_GRAY_MEDIUM,
                            text_align=ft.TextAlign.CENTER,
                            size=12,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "OK",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                            ),
                            on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                        ),
                        ft.Container(height=10),
                        countdown_text,
                    ],
                ),
            )
            dialog_modal.content = success_dialog
            dialog_modal.visible = True
            page.update()
            # Start countdown
            def start_countdown():
                for i in range(3, 0, -1):
                    countdown_text.value = f"Window will close in {i}"
                    page.update()
                    time.sleep(1)
                dialog_modal.visible = False
                page.update()
            # Run countdown in a separate thread
            import threading
            threading.Thread(target=start_countdown).start()
        page.update()

    # Create verification confirmation dialog
    dialog_content = ft.Container(
        width=400,
        height=400,  # Increased height to ensure buttons are visible
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,  # Added spacing between elements
            controls=[
                ft.Text(
                    "Verify Doctor", 
                    size=20, 
                    weight=ft.FontWeight.BOLD, 
                    color=ADMIN_WHITE
                ),
                ft.Container(height=10),
                ft.Text(
                    f"Are you sure you want to verify Dr. {doctor['first_name']} {doctor['last_name']}?",
                    color=ADMIN_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                # Doctor's credentials section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Doctor's Credentials",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE,
                            ),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("Name:", color=ADMIN_GRAY_MEDIUM, size=12),
                                                ft.Text(f"Dr. {doctor['first_name']} {doctor['last_name']}", color=ADMIN_WHITE, size=12),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("ID:", color=ADMIN_GRAY_MEDIUM, size=12),
                                                ft.Text(doctor['user_id'], color=ADMIN_WHITE, size=12),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Email:", color=ADMIN_GRAY_MEDIUM, size=12),
                                                ft.Text(doctor['email'], color=ADMIN_WHITE, size=12),
                                            ],
                                            spacing=10,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                bgcolor=ADMIN_BLACK,
                                padding=10,
                                border_radius=5,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                ft.Container(height=10),
                ft.Text(
                    "This will allow the doctor to access the system.",
                    color=ADMIN_GRAY_MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                ),
                ft.Container(height=20),
                # Buttons section
                ft.Container(
                    content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    controls=[
                        ft.ElevatedButton(
                            "Verify",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            on_click=lambda _: close_dialog(True)
                        ),
                        ft.OutlinedButton(
                            "Cancel",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            on_click=lambda _: close_dialog(False)
                        ),
                    ],
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ],
        ),
    )

    dialog_modal.content = dialog_content
    dialog_modal.visible = True
    page.update()

def handle_view_details(doctor: dict, page: ft.Page, dialog_modal: ft.Container):
    """Handle viewing doctor details"""
    def close_dialog():
        dialog_modal.visible = False
        page.update()

    # Create dialog content
    dialog_content = ft.Container(
        width=500,
        height=450,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                # Header with avatar and name
                ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(doctor["first_name"][0], size=32),
                            radius=40,
                            bgcolor=ADMIN_BLACK,
                            color=ADMIN_WHITE,
                        ),
                        ft.Column(
            controls=[
                ft.Text(
                                    f"Dr. {doctor['first_name']} {doctor['last_name']}", 
                                    size=24, 
                    weight=ft.FontWeight.BOLD, 
                                    color=ADMIN_WHITE,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        "Verified" if doctor.get('is_verified', False) else "Pending Verification",
                                        color=ADMIN_SUCCESS if doctor.get('is_verified', False) else ADMIN_WARNING,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    bgcolor=ft.Colors.with_opacity(0.1, ADMIN_SUCCESS if doctor.get('is_verified', False) else ADMIN_WARNING),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                    border_radius=15,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                
                # Doctor's Information Section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Personal Information",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE,
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("User ID:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(doctor['user_id'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("First Name:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(doctor['first_name'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Last Name:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(doctor['last_name'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Email:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(doctor['email'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Status:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(
                                                    "Verified" if doctor.get('is_verified', False) else "Pending Verification",
                                                    color=ADMIN_SUCCESS if doctor.get('is_verified', False) else ADMIN_WARNING,
                                                    size=14,
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                    ],
                                    spacing=15,
                                ),
                                bgcolor=ADMIN_BLACK,
                                padding=20,
                                border_radius=10,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                
                # Close Button
                ft.ElevatedButton(
                    "Close",
                    style=ft.ButtonStyle(
                        color=ADMIN_WHITE,
                        bgcolor=ADMIN_BLACK,
                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    ),
                    on_click=lambda _: close_dialog()
                ),
            ],
        ),
    )

    dialog_modal.content = dialog_content
    dialog_modal.visible = True
    page.update()

def handle_edit_doctor(doctor: dict, page: ft.Page, dialog_modal: ft.Container, doctors_grid: ft.Row, success_text: ft.Text):
    """Handle editing doctor information"""
    # Create form fields with two-column layout
    first_name_field = ft.TextField(
        label="First Name",
        value=doctor['first_name'],
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    last_name_field = ft.TextField(
        label="Last Name",
        value=doctor['last_name'],
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    email_field = ft.TextField(
        label="Email",
        value=doctor['email'],
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    current_password_field = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_GRAY_MEDIUM,
        text_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
        value="••••••••••••••••",
        read_only=True,  # Make it non-editable
        disabled=True,   # Disable interaction
    )
    password_field = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    confirm_password_field = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    
    # Error text for validation messages
    error_text = ft.Text(
        "",
        color=ADMIN_ERROR,
        size=12,
        text_align=ft.TextAlign.CENTER,
        visible=False
    )

    def close_dialog(confirmed=False):
        dialog_modal.visible = False
        if confirmed:
            # Validate input
            if not all([first_name_field.value, last_name_field.value, email_field.value]):
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return

            # Validate passwords if provided
            if password_field.value:
                if not confirm_password_field.value:
                    error_text.value = "Please confirm the new password"
                    error_text.visible = True
                    page.update()
                    return
                if password_field.value != confirm_password_field.value:
                    error_text.value = "Passwords do not match"
                    error_text.visible = True
                    page.update()
                    return

            # Update doctor in database
            success, message = update_doctor(
                doctor['user_id'],
                first_name_field.value,
                last_name_field.value,
                email_field.value,
                password_field.value if password_field.value else None  # Only update password if provided
            )

            if not success:
                # Show error dialog
                error_dialog = ft.Container(
                    width=400,
                    height=250,
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR,
                                size=48,
                                color=ADMIN_ERROR,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Update Failed", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            ft.Text(
                                message,
                                color=ADMIN_WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "OK",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_ERROR,
                                ),
                                on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                            ),
                        ],
                    ),
                )
                dialog_modal.content = error_dialog
                dialog_modal.visible = True
                page.update()
                return

            # Update the UI
            update_doctors_grid(page, doctors_grid, dialog_modal, success_text)
            
            # Show success dialog
            success_dialog = ft.Container(
                width=400,
                height=300,
                bgcolor=ADMIN_GRAY_DARK,
                border_radius=10,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(height=20),
                        ft.Text(
                            "Update Successful", 
                            size=20, 
                            weight=ft.FontWeight.BOLD, 
                            color=ADMIN_WHITE
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            f"Dr. {first_name_field.value} {last_name_field.value}'s information has been updated successfully.",
                            color=ADMIN_WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "OK",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                            ),
                            on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                        ),
                    ],
                ),
            )
            
            dialog_modal.content = success_dialog
            dialog_modal.visible = True
            page.update()
        page.update()

    # Create dialog content with improved layout
    dialog_content = ft.Container(
        width=600,
        height=400,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                # Header with icon
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.MEDICAL_SERVICES,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Edit Doctor Profile", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            padding=ft.padding.only(left=10)
                        ),
                    ]
                ),
                ft.Container(height=20),
                # Form fields with icons in two columns
                ft.Container(
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            # First name and last name side by side
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                                controls=[
                                    ft.Container(
                                        content=ft.Column(
                                            spacing=0,
                                            controls=[
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Icon(ft.Icons.PERSON_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                                        ft.Container(width=10),
                                                        first_name_field,
                                                    ]
                                                ),
                                                ft.Container(height=15),
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Icon(ft.Icons.PERSON_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                                        ft.Container(width=10),
                                                        last_name_field,
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=280,
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            spacing=0,
                                            controls=[
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                                        ft.Container(width=10),
                                                        email_field,
                                                    ]
                                                ),
                                                ft.Container(height=15),
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Icon(ft.Icons.KEY_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                                        ft.Container(width=10),
                                                        current_password_field,
                                                    ]
                                                ),
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Icon(ft.Icons.KEY_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                                        ft.Container(width=10),
                                                        password_field,
                                                    ]
                                                ),
                                                ft.Row(
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Icon(ft.Icons.KEY_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                                        ft.Container(width=10),
                                                        confirm_password_field,
                                                    ]
                                                ),
                                            ]
                                        ),
                                        width=280,
                                    )
                                ]
                            ),
                            error_text,
                        ]
                    )
                ),
                # Action buttons with icons
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.ElevatedButton(
                            "Save Changes",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            icon=ft.Icons.SAVE_OUTLINED,
                            on_click=lambda _: close_dialog(True)
                        ),
                        ft.OutlinedButton(
                            "Cancel",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            icon=ft.Icons.CANCEL_OUTLINED,
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

def handle_delete_doctor(doctor: dict, page: ft.Page, dialog_modal: ft.Container, doctors_grid: ft.Row, success_text: ft.Text):
    """Handle deleting doctor account"""
    def close_dialog(confirmed=False):
        dialog_modal.visible = False
        if confirmed:
            # Delete doctor from database
            success, message = delete_doctor(doctor['user_id'])
            if not success:
                # Show error dialog
                error_dialog = ft.Container(
                    width=400,
                    height=250,
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR,
                                size=48,
                                color=ADMIN_ERROR,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Deletion Failed", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            ft.Text(
                                message,
                                color=ADMIN_WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "OK",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_ERROR,
                                ),
                                on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                            ),
                        ],
                    ),
                )
                dialog_modal.content = error_dialog
                dialog_modal.visible = True
                page.update()
                return

            # Get all doctors and remove the deleted doctor
            doctors = get_all_doctors()
            doctors = [d for d in doctors if d['user_id'] != doctor['user_id']]
            
            # Update the UI to reflect the change
            doctors_grid.controls = [create_doctor_card(d, page, dialog_modal, doctors_grid, success_text) for d in doctors]
            
            # Show success message
            success_dialog = ft.Container(
                width=400,
                height=380,
                bgcolor=ADMIN_GRAY_DARK,
                border_radius=10,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(height=20),
                        ft.Text(
                            "Doctor Deleted", 
                            size=20, 
                            weight=ft.FontWeight.BOLD, 
                            color=ADMIN_WHITE
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            f"Dr. {doctor['first_name']} {doctor['last_name']} has been deleted successfully.",
                            color=ADMIN_WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "The doctor's account has been removed from the system.",
                            color=ADMIN_GRAY_MEDIUM,
                            text_align=ft.TextAlign.CENTER,
                            size=12,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "OK",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                            ),
                            on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Window will close in 3",
                            color=ADMIN_GRAY_MEDIUM,
                            size=12,
                        ),
                    ],
                ),
            )
            
            dialog_modal.content = success_dialog
            dialog_modal.visible = True
            page.update()
            
            # Start countdown
            def start_countdown():
                for i in range(3, 0, -1):
                    dialog_modal.content.content.controls[-1].value = f"Window will close in {i}"
                    page.update()
                    time.sleep(1)
                dialog_modal.visible = False
                page.update()
            
            # Run countdown in a separate thread
            import threading
            threading.Thread(target=start_countdown).start()
        page.update()

    # Create dialog content
    dialog_content = ft.Container(
        width=400,
        height=250,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Delete Doctor", 
                    size=20, 
                    weight=ft.FontWeight.BOLD, 
                    color=ADMIN_WHITE
                ),
                ft.Container(height=20),
                ft.Text(
                    f"Are you sure you want to delete Dr. {doctor['first_name']} {doctor['last_name']}?",
                    color=ADMIN_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "This action cannot be undone.",
                    color=ADMIN_ERROR,
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                ),
                ft.Container(height=20),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton(
                            "Delete",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_ERROR,
                            ),
                            on_click=lambda _: close_dialog(True)
                        ),
                        ft.Container(width=20),
                        ft.OutlinedButton(
                            "Cancel",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                            ),
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

def create_doctor_card(doctor: dict, page: ft.Page, dialog_modal: ft.Container, doctors_grid: ft.Row, success_text: ft.Text):
    # Determine verification status and color
    is_verified = doctor.get('is_verified', False)
    status_color = ADMIN_SUCCESS if is_verified else ADMIN_WARNING
    status_text = "Verified" if is_verified else "Pending Verification"
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header with avatar and verification status
                ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(doctor["first_name"][0], size=24),
                            radius=30,
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                        ),
                        ft.Container(
                            content=ft.Text(
                                status_text,
                                color=status_color,
                                size=12,
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=ft.Colors.with_opacity(0.1, status_color),
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            border_radius=15,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Doctor's name and ID
                ft.Text(
                    f"Dr. {doctor['first_name']} {doctor['last_name']}", 
                    size=18, 
                    weight=ft.FontWeight.BOLD,
                    color=ADMIN_WHITE,
                ),
                ft.Text(
                    f"ID: {doctor['user_id']}", 
                    size=14,
                    color=ADMIN_GRAY_MEDIUM,
                ),
                # Contact information
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.EMAIL, size=16, color=ADMIN_GRAY_MEDIUM),
                                    ft.Text(doctor["email"], size=14, color=ADMIN_GRAY_MEDIUM),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.only(top=10),
                ),
                # Action buttons
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "View Details",
                                icon=ft.Icons.VISIBILITY,
                                style=ft.ButtonStyle(
                                    bgcolor=ADMIN_GRAY_DARK,
                                    color=ADMIN_WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                ),
                                on_click=lambda e: handle_view_details(doctor, page, dialog_modal)
                            ) if is_verified else ft.ElevatedButton(
                                "Verify",
                                icon=ft.Icons.VERIFIED,
                                style=ft.ButtonStyle(
                                    bgcolor=ADMIN_GRAY_DARK,
                                    color=ADMIN_WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                ),
                                on_click=lambda e: handle_verify_doctor(doctor, page, dialog_modal, doctors_grid, success_text)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ADMIN_WHITE,
                                tooltip="Edit",
                                on_click=lambda e: handle_edit_doctor(doctor, page, dialog_modal, doctors_grid, success_text)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ADMIN_ERROR,
                                tooltip="Delete",
                                on_click=lambda e: handle_delete_doctor(doctor, page, dialog_modal, doctors_grid, success_text)
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(top=15),
                ),
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        width=300,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.1, ADMIN_BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

def create_doctors_tab(page: ft.Page, user: dict, add_doctor_modal: ft.Container, doctors_grid: ft.Row, show_add_doctor_form, dialog_modal: ft.Container, success_text: ft.Text) -> ft.Container:
    """Create a comprehensive doctors tab with detailed information and management features"""
    
    # Search and Filter Section
    search_field = ft.TextField(
                    hint_text="Search doctors...",
                    width=300,
                    height=40,
                    border_color=ADMIN_GRAY_MEDIUM,
                    focused_border_color=ADMIN_WHITE,
                    text_style=ft.TextStyle(
                        color=ADMIN_WHITE,
                        size=13,
                    ),
                    hint_style=ft.TextStyle(
                        color=ADMIN_GRAY_MEDIUM,
                        size=13,
                    ),
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=6,
                    prefix_icon=ft.Icons.SEARCH,
    )

    status_dropdown = ft.Dropdown(
        label="Status",
        width=150,
                    options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Verified"),
            ft.dropdown.Option("Pending Verification"),
        ],
        value="All",
                    border_color=ADMIN_GRAY_MEDIUM,
                    focused_border_color=ADMIN_WHITE,
                    text_style=ft.TextStyle(
                        color=ADMIN_WHITE,
                        size=13,
                    ),
                    label_style=ft.TextStyle(
                        color=ADMIN_GRAY_MEDIUM,
                        size=13,
                    ),
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=6,
    )

    def filter_doctors():
        # Get all doctors
        all_doctors = get_all_doctors()
        
        # Apply search filter
        search_term = search_field.value.lower() if search_field.value else ""
        filtered_doctors = [
            doctor for doctor in all_doctors
            if search_term in doctor['first_name'].lower() or
               search_term in doctor['last_name'].lower() or
               search_term in doctor['email'].lower() or
               search_term in doctor['user_id'].lower()
        ]
        
        # Apply status filter
        status_filter = status_dropdown.value
        if status_filter != "All":
            is_verified = status_filter == "Verified"
            filtered_doctors = [
                doctor for doctor in filtered_doctors
                if doctor.get('is_verified', False) == is_verified
            ]
        
        # Update the grid with filtered doctors or show no results message
        if filtered_doctors:
            doctors_grid.controls = [create_doctor_card(doctor, page, dialog_modal, doctors_grid, success_text) for doctor in filtered_doctors]
        else:
            doctors_grid.controls = [
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.SEARCH_OFF,
                                size=48,
                                color=ADMIN_GRAY_MEDIUM,
                            ),
                            ft.Text(
                                "No doctors found",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE,
                            ),
                            ft.Text(
                                "Try adjusting your search or filter criteria",
                                size=14,
                                color=ADMIN_GRAY_MEDIUM,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    padding=40,
                )
            ]
        page.update()

    # Add event handlers for search and filter
    search_field.on_change = lambda _: filter_doctors()
    status_dropdown.on_change = lambda _: filter_doctors()

    search_bar = ft.Container(
        content=ft.Row(
            controls=[
                search_field,
                status_dropdown,
                ft.ElevatedButton(
                    "Add Doctor",
                    icon=ft.Icons.ADD,
                    style=ft.ButtonStyle(
                        bgcolor=ADMIN_GRAY_DARK,
                        color=ADMIN_WHITE,
                        shape=ft.RoundedRectangleBorder(radius=3),
                    ),
                    on_click=show_add_doctor_form
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=20,
    )

    # Create doctors grid with auto-refresh
    doctors_grid = ft.Row(
        controls=[],
        wrap=True,
        spacing=20,
        run_spacing=20,
    )

    # Initial load of doctors
    filter_doctors()

    # Set up auto-refresh timer
    def auto_refresh():
        while True:
            time.sleep(5)  # Refresh every 5 seconds
            filter_doctors()

    # Start auto-refresh in a separate thread
    import threading
    threading.Thread(target=auto_refresh, daemon=True).start()

    # Main content container
    return ft.Container(
        content=ft.Column(
            controls=[
                search_bar,
                ft.Container(
                    content=doctors_grid,
                    padding=20,
                ),
            ],
        ),
        expand=True,
        bgcolor=ADMIN_BLACK,
    )

def create_hr_tab(page: ft.Page, user: dict, add_hr_modal: ft.Container, hrs_grid: ft.Row, show_add_hr_form, dialog_modal: ft.Container, success_text: ft.Text) -> ft.Container:
    """Create a comprehensive HR tab with detailed information and management features"""
    
    # Search and Filter Section
    search_field = ft.TextField(
        hint_text="Search HR staff...",
        width=300,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
        ),
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=13,
        ),
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=6,
        prefix_icon=ft.Icons.SEARCH,
    )

    status_dropdown = ft.Dropdown(
                    label="Status",
                    width=150,
                    options=[
                        ft.dropdown.Option("All"),
            ft.dropdown.Option("Verified"),
                        ft.dropdown.Option("Pending Verification"),
                    ],
        value="All",
                    border_color=ADMIN_GRAY_MEDIUM,
                    focused_border_color=ADMIN_WHITE,
                    text_style=ft.TextStyle(
                        color=ADMIN_WHITE,
                        size=13,
                    ),
                    label_style=ft.TextStyle(
                        color=ADMIN_GRAY_MEDIUM,
                        size=13,
                    ),
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=6,
    )

    def filter_hrs():
        # Get all HR staff
        all_hrs = get_all_hrs()
        
        # Apply search filter
        search_term = search_field.value.lower() if search_field.value else ""
        filtered_hrs = [
            hr for hr in all_hrs
            if search_term in hr['first_name'].lower() or
               search_term in hr['last_name'].lower() or
               search_term in hr['email'].lower() or
               search_term in hr['user_id'].lower()
        ]
        
        # Apply status filter
        status_filter = status_dropdown.value
        if status_filter != "All":
            is_verified = status_filter == "Verified"
            filtered_hrs = [
                hr for hr in filtered_hrs
                if hr.get('is_verified', False) == is_verified
            ]
        
        # Update the grid with filtered HR staff or show no results message
        if filtered_hrs:
            hrs_grid.controls = [create_hr_card(hr, page, dialog_modal, hrs_grid, success_text) for hr in filtered_hrs]
        else:
            hrs_grid.controls = [
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.SEARCH_OFF,
                                size=48,
                                color=ADMIN_GRAY_MEDIUM,
                            ),
                            ft.Text(
                                "No HR staff found",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE,
                            ),
                            ft.Text(
                                "Try adjusting your search or filter criteria",
                                size=14,
                                color=ADMIN_GRAY_MEDIUM,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    padding=40,
                )
            ]
        page.update()

    # Add event handlers for search and filter
    search_field.on_change = lambda _: filter_hrs()
    status_dropdown.on_change = lambda _: filter_hrs()

    # Initial load of HR staff
    filter_hrs()

    # Set up auto-refresh timer
    def auto_refresh():
        while True:
            time.sleep(5)  # Refresh every 5 seconds
            filter_hrs()

    # Start auto-refresh in a separate thread
    import threading
    threading.Thread(target=auto_refresh, daemon=True).start()

    # Return the HR tab content container
    return ft.Container(
        content=ft.Column(
            controls=[
                # Search and filter section
                ft.Container(
                    content=ft.Row(
                        controls=[
                            search_field,
                            status_dropdown,
                ft.ElevatedButton(
                                "Add HR",
                    icon=ft.Icons.ADD,
                    style=ft.ButtonStyle(
                        bgcolor=ADMIN_GRAY_DARK,
                        color=ADMIN_WHITE,
                        shape=ft.RoundedRectangleBorder(radius=3),
                    ),
                                on_click=show_add_hr_form
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=20,
                ),
                # HR staff grid
                ft.Container(
                    content=hrs_grid,
                    padding=20,
                ),
            ],
        ),
        expand=True,
        bgcolor=ADMIN_BLACK,
    )

def create_hr_card(hr: dict, page: ft.Page, dialog_modal: ft.Container, hrs_grid: ft.Row, success_text: ft.Text):
    # Determine verification status and color
    is_verified = hr.get('is_verified', False)
    status_color = ADMIN_SUCCESS if is_verified else ADMIN_WARNING
    status_text = "Verified" if is_verified else "Pending Verification"
    
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header with avatar and verification status
                ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(hr["first_name"][0], size=24),
                            radius=30,
                            bgcolor=ADMIN_GRAY_DARK,
                            color=ADMIN_WHITE,
                        ),
                        ft.Container(
                            content=ft.Text(
                                status_text,
                                color=status_color,
                                size=12,
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=ft.Colors.with_opacity(0.1, status_color),
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            border_radius=15,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # HR staff name and ID
                ft.Text(
                    f"{hr['first_name']} {hr['last_name']}", 
                    size=18, 
                    weight=ft.FontWeight.BOLD,
                    color=ADMIN_WHITE,
                ),
                ft.Text(
                    f"ID: {hr['user_id']}", 
                    size=14,
                    color=ADMIN_GRAY_MEDIUM,
                ),
                # Contact information
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.EMAIL, size=16, color=ADMIN_GRAY_MEDIUM),
                                    ft.Text(hr["email"], size=14, color=ADMIN_GRAY_MEDIUM),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.only(top=10),
                ),
                # Action buttons
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "View Details",
                                icon=ft.Icons.VISIBILITY,
                                style=ft.ButtonStyle(
                                    bgcolor=ADMIN_GRAY_DARK,
                                    color=ADMIN_WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                ),
                                on_click=lambda e: handle_view_hr_details(hr, page, dialog_modal)
                            ) if hr.get('is_verified', False) else ft.ElevatedButton(
                                "Verify",
                                icon=ft.Icons.VERIFIED,
                                style=ft.ButtonStyle(
                                    bgcolor=ADMIN_GRAY_DARK,
                                    color=ADMIN_WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=3),
                                ),
                                on_click=lambda e: handle_verify_hr(hr, page, dialog_modal, hrs_grid, success_text)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ADMIN_WHITE,
                                tooltip="Edit",
                                on_click=lambda e: handle_edit_hr(hr, page, dialog_modal, hrs_grid, success_text)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ADMIN_ERROR,
                                tooltip="Delete",
                                on_click=lambda e: handle_delete_hr(hr, page, dialog_modal, hrs_grid, success_text)
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(top=15),
                ),
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        width=300,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=5,
            color=ft.Colors.with_opacity(0.1, ADMIN_BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

def handle_verify_hr(hr: dict, page: ft.Page, dialog_modal: ft.Container, hrs_grid: ft.Row, success_text: ft.Text):
    """Handle HR staff verification"""
    def close_dialog(confirmed=False):
        dialog_modal.visible = False
        if confirmed:
            # Update verification status in database
            success, message = verify_hr(hr['user_id'])
            if not success:
                # Show error dialog
                error_dialog = ft.Container(
                    width=400,
                    height=250,
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR,
                                size=48,
                                color=ADMIN_ERROR,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Verification Failed", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            ft.Text(
                                message,
                                color=ADMIN_WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "OK",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_ERROR,
                                ),
                                on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                            ),
                        ],
                    ),
                )
                dialog_modal.content = error_dialog
                dialog_modal.visible = True
                page.update()
                return

            # Update the UI immediately
            update_hrs_grid(page, hrs_grid, dialog_modal, success_text)
            
            # Show success dialog
            success_dialog = ft.Container(
                width=400,
                height=400,
                bgcolor=ADMIN_GRAY_DARK,
                border_radius=10,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(height=20),
                        ft.Text(
                            "Verification Successful", 
                            size=20, 
                            weight=ft.FontWeight.BOLD, 
                            color=ADMIN_WHITE
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            f"{hr['first_name']} {hr['last_name']} has been verified successfully.",
                            color=ADMIN_WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "The verification status has been updated.",
                            color=ADMIN_GRAY_MEDIUM,
                            text_align=ft.TextAlign.CENTER,
                            size=12,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "OK",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                            ),
                            on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                        ),
                    ],
                ),
            )
            
            dialog_modal.content = success_dialog
            dialog_modal.visible = True
            page.update()
        page.update()

    # Create verification confirmation dialog
    dialog_content = ft.Container(
        width=400,
        height=400,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text(
                    "Verify HR Staff", 
                    size=20, 
                    weight=ft.FontWeight.BOLD, 
                    color=ADMIN_WHITE
                ),
                ft.Container(height=10),
                ft.Text(
                    f"Are you sure you want to verify {hr['first_name']} {hr['last_name']}?",
                    color=ADMIN_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                # HR staff credentials section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "HR Staff Credentials",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE,
                            ),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("Name:", color=ADMIN_GRAY_MEDIUM, size=12),
                                                ft.Text(f"{hr['first_name']} {hr['last_name']}", color=ADMIN_WHITE, size=12),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("ID:", color=ADMIN_GRAY_MEDIUM, size=12),
                                                ft.Text(hr['user_id'], color=ADMIN_WHITE, size=12),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Email:", color=ADMIN_GRAY_MEDIUM, size=12),
                                                ft.Text(hr['email'], color=ADMIN_WHITE, size=12),
                                            ],
                                            spacing=10,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                bgcolor=ADMIN_BLACK,
                                padding=10,
                                border_radius=5,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                ft.Container(height=10),
                ft.Text(
                    "This will allow the HR staff to access the system.",
                    color=ADMIN_GRAY_MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                ),
                ft.Container(height=20),
                # Buttons section
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
                        controls=[
                            ft.ElevatedButton(
                                "Verify",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_SUCCESS,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                ),
                                on_click=lambda _: close_dialog(True)
                            ),
                            ft.OutlinedButton(
                                "Cancel",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                ),
                                on_click=lambda _: close_dialog(False)
                            ),
                        ],
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ],
        ),
    )

    dialog_modal.content = dialog_content
    dialog_modal.visible = True
    page.update()

def handle_view_hr_details(hr: dict, page: ft.Page, dialog_modal: ft.Container):
    """Handle viewing HR staff details"""
    def close_dialog():
        dialog_modal.visible = False
        page.update()

    # Create dialog content
    dialog_content = ft.Container(
        width=500,
        height=450,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                # Header with avatar and name
                ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(hr["first_name"][0], size=32),
                            radius=40,
                            bgcolor=ADMIN_BLACK,
                            color=ADMIN_WHITE,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    f"{hr['first_name']} {hr['last_name']}", 
                                    size=24, 
                                    weight=ft.FontWeight.BOLD,
                                    color=ADMIN_WHITE,
                                ),
                ft.Container(
                                    content=ft.Text(
                                        "Verified" if hr.get('is_verified', False) else "Pending Verification",
                                        color=ADMIN_SUCCESS if hr.get('is_verified', False) else ADMIN_WARNING,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    bgcolor=ft.Colors.with_opacity(0.1, ADMIN_SUCCESS if hr.get('is_verified', False) else ADMIN_WARNING),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                    border_radius=15,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                
                # HR Staff Information Section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Personal Information",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE,
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("User ID:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(hr['user_id'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("First Name:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(hr['first_name'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Last Name:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(hr['last_name'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Email:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(hr['email'], color=ADMIN_WHITE, size=14),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Text("Status:", color=ADMIN_GRAY_MEDIUM, size=14),
                                                ft.Text(
                                                    "Verified" if hr.get('is_verified', False) else "Pending Verification",
                                                    color=ADMIN_SUCCESS if hr.get('is_verified', False) else ADMIN_WARNING,
                                                    size=14,
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                    ],
                                    spacing=15,
                                ),
                                bgcolor=ADMIN_BLACK,
                    padding=20,
                                border_radius=10,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                
                # Close Button
                ft.ElevatedButton(
                    "Close",
                    style=ft.ButtonStyle(
                        color=ADMIN_WHITE,
        bgcolor=ADMIN_BLACK,
                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    ),
                    on_click=lambda _: close_dialog()
                ),
            ],
        ),
    )

    dialog_modal.content = dialog_content
    dialog_modal.visible = True
    page.update()

def handle_edit_hr(hr: dict, page: ft.Page, dialog_modal: ft.Container, hrs_grid: ft.Row, success_text: ft.Text):
    """Handle editing HR staff information"""
    # Create form fields with two-column layout
    first_name_field = ft.TextField(
        label="First Name",
        value=hr['first_name'],
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    last_name_field = ft.TextField(
        label="Last Name",
        value=hr['last_name'],
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    email_field = ft.TextField(
        label="Email",
        value=hr['email'],
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    # Current password field (read-only but visible)
    current_password_field = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_GRAY_MEDIUM,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
        value="••••••••••••••••",
        read_only=True,  # Make it non-editable
    )
    # New password field
    password_field = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    confirm_password_field = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=280,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(color=ADMIN_WHITE),
        label_style=ft.TextStyle(color=ADMIN_GRAY_MEDIUM),
        bgcolor=ADMIN_BLACK,
    )
    
    # Error text for validation messages
    error_text = ft.Text(
        "",
        color=ADMIN_ERROR,
        size=12,
        text_align=ft.TextAlign.CENTER,
        visible=False
    )

    def close_dialog(confirmed=False):
        dialog_modal.visible = False
        page.update()
        
        if confirmed:
            # Validate input
            if not all([first_name_field.value, last_name_field.value, email_field.value]):
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return

            # Validate email format
            if not email_field.value or "@" not in email_field.value:
                error_text.value = "Please enter a valid email address."
                error_text.visible = True
                page.update()
                return

            # Get new password if provided
            new_password = password_field.value if password_field.value else None

            # Update HR staff information
            updated_hr = {
                "user_id": hr['user_id'],
                "first_name": first_name_field.value,
                "last_name": last_name_field.value,
                "email": email_field.value,
                "password": new_password if new_password else hr['password'],  # Update password only if new one provided
                "is_verified": hr['is_verified']
            }

            try:
                result = update_hr_record()
                if result:
                    # Update the grid
                    update_hrs_grid(page, hrs_grid, dialog_modal, success_text)
                    # Show success dialog
                    success_dialog = ft.Container(
                        width=400,
                        height=300,
                        bgcolor=ADMIN_GRAY_DARK,
                        border_radius=10,
                        padding=20,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                            controls=[
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=48,
                                    color=ADMIN_SUCCESS,
                                ),
                                ft.Container(height=20),
                                ft.Text(
                                    "Update Successful", 
                                    size=20, 
                                    weight=ft.FontWeight.BOLD, 
                                    color=ADMIN_WHITE
                                ),
                                ft.Container(height=10),
                                ft.Text(
                                    f"{first_name_field.value} {last_name_field.value}'s information has been updated successfully.",
                                    color=ADMIN_WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "OK",
                                    style=ft.ButtonStyle(
                                        color=ADMIN_WHITE,
                                        bgcolor=ADMIN_SUCCESS,
                                    ),
                                    on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                                ),
                            ],
                        ),
                    )
                    
                    dialog_modal.content = success_dialog
                    dialog_modal.visible = True
                    page.update()
                else:
                    # Show error dialog
                    if 'message' not in locals():
                        message = "Unknown error"
                    error_dialog = ft.Container(
                        width=400,
                        height=250,
                        bgcolor=ADMIN_GRAY_DARK,
                        border_radius=10,
                        padding=20,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    ft.Icons.ERROR,
                                    size=48,
                                    color=ADMIN_ERROR,
                                ),
                                ft.Container(height=20),
                                ft.Text(
                                    "Update Failed", 
                                    size=20, 
                                    weight=ft.FontWeight.BOLD, 
                                    color=ADMIN_WHITE
                                ),
                                ft.Text(
                                    message,
                                    color=ADMIN_WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    "OK",
                                    style=ft.ButtonStyle(
                                        color=ADMIN_WHITE,
                                        bgcolor=ADMIN_ERROR,
                                    ),
                                    on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                                ),
                            ],
                        ),
                    )
                    dialog_modal.content = error_dialog
                    dialog_modal.visible = True
                    page.update()
            except Exception as e:
                error_text.value = str(e)
                error_text.visible = True
                page.update()
                return

            page.update()
        page.update()

    def update_hr_record():
        # Validate email format
        if not email_field.value or "@" not in email_field.value:
            error_text.value = "Please enter a valid email address."
            error_text.visible = True
            page.update()
            return

        # Get new password if provided
        new_password = password_field.value if password_field.value else None

        # Update HR staff information
        updated_hr = {
            "user_id": hr['user_id'],
            "first_name": first_name_field.value,
            "last_name": last_name_field.value,
            "email": email_field.value,
            "password": new_password if new_password else hr['password'],  # Update password only if new one provided
            "is_verified": hr['is_verified']
        }

        try:
            from database import update_hr
            success, message = update_hr(updated_hr)
            if success:
                # Update the grid
                update_hrs_grid(page, hrs_grid, dialog_modal, success_text)
                # Show success dialog
                success_dialog = ft.Container(
                    width=400,
                    height=300,
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                size=48,
                                color=ADMIN_SUCCESS,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Update Successful", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                f"{first_name_field.value} {last_name_field.value}'s information has been updated successfully.",
                                color=ADMIN_WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "OK",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_SUCCESS,
                                ),
                                on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                            ),
                        ],
                    ),
                )
                
                dialog_modal.content = success_dialog
                dialog_modal.visible = True
                page.update()
        except Exception as e:
            error_text.value = str(e)
            error_text.visible = True
            page.update()

    # Create update button
    update_button = ft.ElevatedButton(
        "Update",
        style=ft.ButtonStyle(
            color=ADMIN_WHITE,
            bgcolor=ADMIN_SUCCESS,
        ),
        on_click=lambda _: update_hr()
    )

    # Create dialog content with improved layout
    dialog_content = ft.Container(
        width=470,
        height=500,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                # Header with icon
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.PERSON_PIN_CIRCLE,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Edit HR Staff Profile", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            padding=ft.padding.only(left=10)
                        ),
                    ]
                ),
                ft.Container(height=20),
                # Form fields with icons
                ft.Container(
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.PERSON_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                    ft.Container(width=10),
                                    first_name_field,
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.PERSON_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                    ft.Container(width=10),
                                    last_name_field,
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.EMAIL_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                    ft.Container(width=10),
                                    email_field,
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.KEY_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                    ft.Container(width=10),
                                    current_password_field,
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.KEY_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                    ft.Container(width=10),
                                    password_field,
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.KEY_OUTLINED, color=ADMIN_GRAY_MEDIUM),
                                    ft.Container(width=10),
                                    confirm_password_field,
                                ]
                            ),
                            error_text,
                        ]
                    )
                ),
                # Action buttons with icons
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.ElevatedButton(
                            "Save Changes",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            icon=ft.Icons.SAVE_OUTLINED,
                            on_click=lambda _: close_dialog(True)
                        ),
                        ft.OutlinedButton(
                            "Cancel",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            icon=ft.Icons.CANCEL_OUTLINED,
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

def handle_delete_hr(hr: dict, page: ft.Page, dialog_modal: ft.Container, hrs_grid: ft.Row, success_text: ft.Text):
    """Handle deleting HR staff account"""
    def close_dialog(confirmed=False):
        dialog_modal.visible = False
        if confirmed:
            # Delete HR staff from database
            success, message = delete_hr(hr['user_id'])
            if not success:
                # Show error dialog
                error_dialog = ft.Container(
                    width=400,
                    height=250,
                    bgcolor=ADMIN_GRAY_DARK,
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR,
                                size=48,
                                color=ADMIN_ERROR,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Deletion Failed", 
                                size=20, 
                                weight=ft.FontWeight.BOLD, 
                                color=ADMIN_WHITE
                            ),
                            ft.Text(
                                message,
                                color=ADMIN_WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "OK",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_ERROR,
                                ),
                                on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                            ),
                        ],
                    ),
                )
                dialog_modal.content = error_dialog
                dialog_modal.visible = True
                page.update()
                return

            # Get all HR staff and remove the deleted one
            hrs = get_all_hrs()
            hrs = [h for h in hrs if h['user_id'] != hr['user_id']]
            
            # Update the UI to reflect the change
            hrs_grid.controls = [create_hr_card(h, page, dialog_modal, hrs_grid, success_text) for h in hrs]
            
            # Show success message
            success_dialog = ft.Container(
                width=400,
                height=350,
                bgcolor=ADMIN_GRAY_DARK,
                border_radius=10,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=48,
                            color=ADMIN_SUCCESS,
                        ),
                        ft.Container(height=20),
                        ft.Text(
                            "HR Staff Deleted", 
                            size=20, 
                            weight=ft.FontWeight.BOLD, 
                            color=ADMIN_WHITE
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            f"{hr['first_name']} {hr['last_name']} has been deleted successfully.",
                            color=ADMIN_WHITE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "The HR staff account has been removed from the system.",
                            color=ADMIN_GRAY_MEDIUM,
                            text_align=ft.TextAlign.CENTER,
                            size=12,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "OK",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_SUCCESS,
                            ),
                            on_click=lambda _: setattr(dialog_modal, 'visible', False) or page.update()
                        ),
                    ],
                ),
            )
            
            dialog_modal.content = success_dialog
            dialog_modal.visible = True
            page.update()
        page.update()

    # Create dialog content
    dialog_content = ft.Container(
        width=400,
        height=250,
        bgcolor=ADMIN_GRAY_DARK,
        border_radius=10,
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Delete HR Staff", 
                    size=20, 
                    weight=ft.FontWeight.BOLD, 
                    color=ADMIN_WHITE
                ),
                ft.Container(height=20),
                ft.Text(
                    f"Are you sure you want to delete {hr['first_name']} {hr['last_name']}?",
                    color=ADMIN_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "This action cannot be undone.",
                    color=ADMIN_ERROR,
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                ),
                ft.Container(height=20),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton(
                            "Delete",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                                bgcolor=ADMIN_ERROR,
                            ),
                            on_click=lambda _: close_dialog(True)
                        ),
                        ft.Container(width=20),
                        ft.OutlinedButton(
                            "Cancel",
                            style=ft.ButtonStyle(
                                color=ADMIN_WHITE,
                            ),
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

def update_hrs_grid(page: ft.Page, hrs_grid: ft.Row, dialog_modal: ft.Container, success_text: ft.Text):
    """Update the HR staff grid with current data"""
    # Get fresh data from database
    hrs = get_all_hrs()
    
    # Create new cards with updated data
    hrs_grid.controls = [create_hr_card(hr, page, dialog_modal, hrs_grid, success_text) for hr in hrs]
    
    # Update the page to reflect changes
    page.update()

def dashboard_ui(page: ft.Page, user: dict):
    page.clean()
    page.title = "NexaCare Admin"
    page.bgcolor = ADMIN_BLACK
    page.padding = 0

    # Track currently selected menu item
    current_selection = ft.Ref[str]()
    current_selection.current = "Dashboard"  # Default selection

    # Create modal dialog containers
    dialog_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    add_doctor_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    add_hr_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Form fields for doctor
    first_name_field = ft.TextField(
        label="First Name",
        width=700,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter first name",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )
    last_name_field = ft.TextField(
        label="Last Name",
        width=180,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter last name",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )
    email_field = ft.TextField(
        label="Email",
        width=800,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter email address",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )
    password_field = ft.TextField(
        label="Password",
        width=800,
        height=40,
        password=True,
        can_reveal_password=True,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter password",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )

    # Form fields for HR
    hr_first_name_field = ft.TextField(
        label="First Name",
        width=600,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter first name",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )
    hr_last_name_field = ft.TextField(
        label="Last Name",
        width=200,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter last name",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )
    hr_email_field = ft.TextField(
        label="Email",
        width=800,
        height=40,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter email address",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
    )
    hr_password_field = ft.TextField(
        label="Password",
        width=800,
        height=40,
        password=True,
        can_reveal_password=True,
        border_color=ADMIN_GRAY_MEDIUM,
        focused_border_color=ADMIN_WHITE,
        text_style=ft.TextStyle(
            color=ADMIN_WHITE,
            size=13,
            weight=ft.FontWeight.W_500
        ),
        label_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11,
            weight=ft.FontWeight.W_500
        ),
        hint_text="Enter password",
        hint_style=ft.TextStyle(
            color=ADMIN_GRAY_MEDIUM,
            size=11
        ),
        border_radius=6,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=5),
        bgcolor=ADMIN_GRAY_DARK,
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

    def close_add_hr_dialog(e=None):
        add_hr_modal.visible = False
        # Clear the form fields
        hr_first_name_field.value = ""
        hr_last_name_field.value = ""
        hr_email_field.value = ""
        hr_password_field.value = ""
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
            update_doctors_grid(page, doctors_grid, dialog_modal, success_text)
            page.update()
            # Close the dialog
            close_add_doctor_dialog()
        else:
            error_text.value = message
            error_text.visible = True
            page.update()

    def handle_add_hr(e):
        error_text.visible = False
        success_text.visible = False
        
        # Basic validation
        if not all([hr_first_name_field.value, hr_last_name_field.value, hr_email_field.value, hr_password_field.value]):
            error_text.value = "Please fill in all fields"
            error_text.visible = True
            page.update()
            return

        # Create HR account
        success, message, user_id = create_user(
            hr_first_name_field.value,
            hr_last_name_field.value,
            hr_email_field.value,
            hr_password_field.value,
            "HR"
        )

        if success:
            success_text.value = f"HR staff added successfully! ID: {user_id}"
            success_text.visible = True
            # Update the HRs grid
            update_hrs_grid(page, hrs_grid, dialog_modal, success_text)
            page.update()
            # Close the dialog
            close_add_hr_dialog()
        else:
            error_text.value = message
            error_text.visible = True
            page.update()

    def show_add_doctor_form(e):
        add_doctor_modal.content = ft.Container(
            width=550,
            height=400,  # Reduced height since we have fewer fields
            bgcolor=ADMIN_GRAY_DARK,
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
                                    color=ADMIN_WHITE,
                                ),
                                ft.Text(
                                    "Create doctor account with basic information",
                                    size=12,
                                    color=ADMIN_GRAY_MEDIUM,
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
                                        color=ADMIN_WHITE,
                                        bgcolor=ADMIN_BLACK,
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                    ),
                                    width=160,
                                    on_click=handle_add_doctor
                                ),
                                ft.OutlinedButton(
                                    "Cancel",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
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
                color=ft.Colors.with_opacity(0.15, ADMIN_BLACK),
                offset=ft.Offset(0, 3),
            ),
        )
        add_doctor_modal.visible = True
        page.update()

    def show_add_hr_form(e):
        add_hr_modal.content = ft.Container(
            width=550,
            height=400,
            bgcolor=ADMIN_GRAY_DARK,
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
                                    "Add New HR Staff",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ADMIN_WHITE,
                                ),
                                ft.Text(
                                    "Fill in the information below",
                                    size=12,
                                    color=ADMIN_GRAY_MEDIUM,
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
                                            content=hr_first_name_field,
                                            expand=1,
                                        ),
                                        ft.Container(width=1),
                                        ft.Container(
                                            content=hr_last_name_field,
                                            expand=1,
                                        ),
                                    ],
                                ),
                                hr_email_field,
                                hr_password_field,
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
                                    "Add HR",
                                    style=ft.ButtonStyle(
                                        color=ADMIN_WHITE,
                                        bgcolor=ADMIN_BLACK,
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                        shape=ft.RoundedRectangleBorder(radius=2),
                                    ),
                                    width=160,
                                    on_click=handle_add_hr
                                ),
                                ft.OutlinedButton(
                                    "Cancel",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(width=1.5, color=ADMIN_WHITE),
                                    ),
                                    width=160,
                                    on_click=close_add_hr_dialog
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
                color=ft.Colors.with_opacity(0.15, ADMIN_BLACK),
                offset=ft.Offset(0, 3),
            ),
        )
        add_hr_modal.visible = True
        page.update()

    def create_hr_card(hr: dict):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(hr["first_name"][0], size=24),
                        radius=30,
                        bgcolor=ADMIN_GRAY_DARK,
                        color=ADMIN_WHITE,
                    ),
                    ft.Text(
                        f"{hr['first_name']} {hr['last_name']}", 
                        size=14, 
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ADMIN_WHITE,
                    ),
                    ft.Text(
                        f"ID: {hr['user_id']}", 
                        size=12,
                        color=ADMIN_GRAY_MEDIUM,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        hr["email"],
                        size=12,
                        color=ADMIN_GRAY_MEDIUM,
                        text_align=ft.TextAlign.CENTER,
                        width=160,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=15,
            bgcolor=ADMIN_GRAY_DARK,
            border_radius=10,
            width=180,
            height=160,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ADMIN_BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    doctors_grid = ft.Row(
        controls=[],
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        wrap=True,
    )

    hrs_grid = ft.Row(
        controls=[],
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        wrap=True,
    )

    # Initial load of doctors and HRs
    update_doctors_grid(page, doctors_grid, dialog_modal, success_text)
    update_hrs_grid(page, hrs_grid, dialog_modal, success_text)

    def handle_logout(e):
        def close_dialog(confirmed=False):
            dialog_modal.visible = False
            if confirmed:
                # Clean up any running threads or resources
                page.clean()
                # Navigate to login
                navigate_to_login(page)
            page.update()

        # Create dialog content
        dialog_content = ft.Container(
            width=400,
            height=300,
            bgcolor=ADMIN_GRAY_DARK,
            border_radius=10,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.LOGOUT,
                        size=48,
                        color=ADMIN_WARNING,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Confirm Logout", 
                        size=20, 
                        weight=ft.FontWeight.BOLD, 
                        color=ADMIN_WHITE
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Are you sure you want to logout?",
                        color=ADMIN_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Yes, Logout",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    bgcolor=ADMIN_WARNING,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                ),
                                on_click=lambda _: close_dialog(True)
                            ),
                            ft.Container(width=20),
                            ft.OutlinedButton(
                                "Cancel",
                                style=ft.ButtonStyle(
                                    color=ADMIN_WHITE,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                ),
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

    def handle_menu_selection(title: str, e, main_content: ft.Container):
        """Handle menu item selection"""
        current_selection.current = title
        if title == "Doctors":
            main_content.content = create_doctors_tab(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, dialog_modal, success_text)
        elif title == "HRs":
            main_content.content = create_hr_tab(page, user, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, success_text)
        elif title == "Dashboard":
            main_content.content = create_dashboard_content(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, lambda t, e, *args: handle_menu_selection(t, e, main_content))
        else:
            main_content.content = create_dashboard_content(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, lambda t, e, *args: handle_menu_selection(t, e, main_content))
        page.update()

    # Create main content container first
    main_content = ft.Container(
        expand=True,
    )

    # Create sidebar using the centralized function with current_selection and menu handler
    sidebar = create_sidebar(page, "admin", handle_logout, current_selection, lambda t, e, *args: handle_menu_selection(t, e, main_content))

    # Update handle_menu_selection to properly pass main_content
    def handle_menu_selection(title: str, e, main_content: ft.Container):
        current_selection.current = title
        if title == "Doctors":
            main_content.content = create_doctors_tab(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, dialog_modal, success_text)
        elif title == "HRs":
            main_content.content = create_hr_tab(page, user, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, success_text)
        elif title == "Dashboard":
            main_content.content = create_dashboard_content(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, lambda t, e, *args: handle_menu_selection(t, e, main_content), main_content)
        else:
            main_content.content = create_dashboard_content(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, lambda t, e, *args: handle_menu_selection(t, e, main_content), main_content)
        page.update()

    # Create the dashboard content and add it to main_content
    main_content.content = ft.Column(
        controls=[
            create_dashboard_content(page, user, add_doctor_modal, doctors_grid, show_add_doctor_form, add_hr_modal, hrs_grid, show_add_hr_form, dialog_modal, handle_menu_selection, main_content)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
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
                dialog_modal,
                add_doctor_modal,
                add_hr_modal,
            ],
            expand=True
        )
    )
