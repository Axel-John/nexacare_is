import flet as ft
from .dashboards import doctor, hr, admin
from models.user import get_user
from .login import login_ui  # Remove: , login_user
from database import create_user, check_email_exists

# Define color constants
PRIMARY_BLUE = "#2A70FF"
SECONDARY_BLUE = "#31D7E9"
LIGHT_BLUE = "#EBF3FF"
ACCENT_TEAL = "#2CAFA4"

# Define text styles
HEADING_STYLE = ft.TextStyle(
    size=32,
    weight=ft.FontWeight.W_600,
    font_family="PoppinsSemiBold"
)

SUBHEADING_STYLE = ft.TextStyle(
    size=18,
    weight=ft.FontWeight.W_500,
    font_family="PoppinsMedium"
)

BODY_STYLE = ft.TextStyle(
    size=15,
    font_family="Lato"
)

BUTTON_STYLE = ft.TextStyle(
    size=16,
    weight=ft.FontWeight.W_500,
    font_family="PoppinsMedium"
)

def show_error(page, message):
    snack = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE, style=BODY_STYLE),
        bgcolor=ft.Colors.RED_700,
        duration=3000,
        open=True
    )
    page.snack_bar = snack
    page.update()

def show_success(page, message):
    snack = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE, style=BODY_STYLE),
        bgcolor=ft.Colors.GREEN_700,
        duration=3000,
        open=True
    )
    page.snack_bar = snack
    page.update()

def signup_ui(page: ft.Page):
    page.title = "Sign Up - NexaCare"
    page.padding = 0  # Remove page padding
    page.bgcolor = LIGHT_BLUE
    page.window_resizable = True
    page.window_maximized = True
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = None  # Disable scrolling

    # Focus the first name field when the page loads
    def on_page_load(e):
        first_name.focus()
        page.update()

    page.on_load = on_page_load
    
    def on_role_change(e):
        role_dropdown.value = e.data
        page.update()

    # Add error texts for password and confirm password fields
    password_error_text = ft.Text("", color=ft.Colors.RED, size=14, visible=False)
    confirm_password_error_text = ft.Text("", color=ft.Colors.RED, size=14, visible=False)

    def validate_passwords():
        password_error_text.value = ""
        password_error_text.visible = False
        confirm_password_error_text.value = ""
        confirm_password_error_text.visible = False
        if password_field.value != confirm_password_field.value:
            password_error_text.value = "Passwords do not match"
            password_error_text.visible = True
            confirm_password_error_text.value = "Passwords do not match"
            confirm_password_error_text.visible = True
            page.update()
            return False
        return True

    def validate_form():
        print("[DEBUG] Starting form validation")
        
        if not first_name.value or len(first_name.value.strip()) < 2:
            print("[DEBUG] First name validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("First name must be at least 2 characters long", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not last_name.value or len(last_name.value.strip()) < 2:
            print("[DEBUG] Last name validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Last name must be at least 2 characters long", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not email_field.value:
            print("[DEBUG] Email empty")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please enter your email address", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        email = email_field.value.strip()
        if not email.endswith('@nexacare.med'):
            print("[DEBUG] Invalid email domain")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Email must end with @nexacare.med", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not role_dropdown.value:
            print("[DEBUG] No role selected")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please select your role", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if role_dropdown.value not in ['Doctor', 'HR']:
            print("[DEBUG] Invalid role selected")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Invalid role selected", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not password_field.value or len(password_field.value) < 8:
            print("[DEBUG] Password validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Password must be at least 8 characters long", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not confirm_password_field.value:
            print("[DEBUG] Confirm password empty")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please confirm your password", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not maiden_name.value or len(maiden_name.value.strip()) < 2:
            print("[DEBUG] Mother's maiden name validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please enter your mother's maiden name", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not nickname.value or len(nickname.value.strip()) < 2:
            print("[DEBUG] Nickname validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please enter your childhood nickname", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not fav_media.value or len(fav_media.value.strip()) < 2:
            print("[DEBUG] Favorite media validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please enter your favorite book or movie", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        if not birth_city.value or len(birth_city.value.strip()) < 2:
            print("[DEBUG] Birth city validation failed")
            show_dialog(
                "Sign Up Failed",
                [ft.Text("Please enter your city of birth", size=16, color=ft.Colors.RED_700)],
                success=False
            )
            return False
            
        print("[DEBUG] Form validation successful")
        return True

    def show_dialog(title, content, success=True):
        print(f"[DEBUG] Showing dialog - Title: {title}, Success: {success}")
        
        def close_dlg(e):
            print("[DEBUG] Dialog close button clicked")
            overlay.visible = False
            page.update()
            if success:
                print("[DEBUG] Success dialog closed, redirecting to login")
                page.clean()
                login_ui(page)

        # Create a semi-transparent overlay
        overlay = ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(title, style=HEADING_STYLE, size=24, color=ACCENT_TEAL),
                        ft.Container(height=20),
                        *content,
                        ft.Container(height=30),
                        ft.ElevatedButton(
                            "OK",
                            width=200,
                            height=40,
                            on_click=close_dlg,
                            style=ft.ButtonStyle(
                                bgcolor=ACCENT_TEAL,
                                color=ft.Colors.WHITE
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=400,
                height=300,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=30,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4)
                )
            ),
            expand=True,  # This will make it fill the available space
            bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
            alignment=ft.alignment.center,
            visible=True
        )

        # Add the overlay to the page
        page.overlay.append(overlay)
        page.update()
        print("[DEBUG] Dialog should now be visible")

    def on_signup(e):
        print("[DEBUG] Sign up button clicked")
        # Clear previous error messages
        password_error_text.value = ""
        password_error_text.visible = False
        confirm_password_error_text.value = ""
        confirm_password_error_text.visible = False
        page.update()
        
        print("[DEBUG] Validating passwords...")
        if not validate_passwords():
            print("[DEBUG] Password validation failed")
            return
            
        print("[DEBUG] Validating form...")
        if not validate_form():
            print("[DEBUG] Form validation failed")
            return

        try:
            print("[DEBUG] Creating user...")
            print(f"[DEBUG] User data: first_name={first_name.value}, last_name={last_name.value}, email={email_field.value}, role={role_dropdown.value}")
            result = create_user(
                first_name=first_name.value.strip(),
                last_name=last_name.value.strip(),
                email=email_field.value.strip().lower(),
                password=password_field.value,
                role=role_dropdown.value,
                maiden_name=maiden_name.value.strip(),
                nickname=nickname.value.strip(),
                favorite_media=fav_media.value.strip(),
                birth_city=birth_city.value.strip()
            )
            print(f"[DEBUG] Create user result: {result}")
            
            if isinstance(result, tuple) and len(result) == 3:
                success, message, user_id = result
            else:
                success, message = result
                user_id = None

            print(f"[DEBUG] Success: {success}, Message: {message}, User ID: {user_id}")

            if success:
                # Clear all fields before showing success dialog
                first_name.value = ""
                last_name.value = ""
                email_field.value = ""
                password_field.value = ""
                confirm_password_field.value = ""
                maiden_name.value = ""
                nickname.value = ""
                fav_media.value = ""
                birth_city.value = ""
                role_dropdown.value = None
                page.update()
                
                show_dialog(
                    "Account Created!",
                    [
                        ft.Text(message, style=BODY_STYLE),
                        ft.Text(f"Your User ID: {user_id or ''}", style=BODY_STYLE, color=ACCENT_TEAL)
                    ],
                    success=True
                )
            else:
                error_message = f"Error creating account: {message}"
                print(f"[DEBUG] {error_message}")
                show_dialog(
                    "Sign Up Failed",
                    [ft.Text(error_message, style=BODY_STYLE, color=ft.Colors.RED_700)],
                    success=False
                )
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            print(f"[DEBUG] {error_message}")
            show_dialog(
                "Sign Up Failed",
                [ft.Text(error_message, style=BODY_STYLE, color=ft.Colors.RED_700)],
                success=False
            )

    def go_back_to_login(e):
        page.clean()
        login_ui(page)

    # Left Panel - Personal Information
    first_name = ft.TextField(
        label="First Name",
        width=190,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
        autofocus=True,  # Start with first name focused
    )

    last_name = ft.TextField(
        label="Last Name",
        width=130,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    email_field = ft.TextField(
        label="Email Address",
        width=200,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
        hint_text="Enter your @nexacare.med email address",
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_400,
            size=11
        ),
    )

    role_dropdown = ft.Dropdown(
        label="Role",
        width=120,
        options=[
            ft.dropdown.Option("Doctor"),
            ft.dropdown.Option("HR"),
        ],
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
        on_change=on_role_change,
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=350,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    confirm_password_field = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=350,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    # Right Panel - Security Questions
    maiden_name = ft.TextField(
        label="Mother's Maiden Name",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    nickname = ft.TextField(
        label="Childhood Nickname",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    fav_media = ft.TextField(
        label="Favorite Book or Movie",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    birth_city = ft.TextField(
        label="City of Birth",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=BODY_STYLE,
        label_style=BODY_STYLE,
    )

    left_panel = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "Join us!",
                        size=24,
                        weight=ft.FontWeight.W_600,
                        font_family="PoppinsSemiBold",
                        color=ACCENT_TEAL
                    ),
                    margin=ft.margin.only(bottom=5),
                    alignment=ft.alignment.center_left
                ),
                ft.Container(
                    content=ft.Text(
                        "Confidence and care through nexacare.",
                        size=14,
                        font_family="Lato",
                        color=ft.Colors.GREY_700
                    ),
                    alignment=ft.alignment.center_left
                ),
                ft.Container(height=10),
                ft.Row(
                    [first_name, ft.Container(width=2), last_name],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Container(height=10),
                ft.Row( 
                    [email_field, ft.Container(width=2), role_dropdown],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Container(height=10),
                password_field,
                ft.Container(password_error_text, alignment=ft.alignment.center_left, padding=ft.padding.only(left=4, top=2, bottom=2)),
                ft.Container(height=10),
                confirm_password_field,
                ft.Container(confirm_password_error_text, alignment=ft.alignment.center_left, padding=ft.padding.only(left=4, top=2, bottom=2)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        padding=30,
        bgcolor="white",
        border_radius=10,
        width=400,
    )
    

    right_panel = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(
                        "Security Questions",
                        size=24,
                        weight=ft.FontWeight.W_600,
                        font_family="PoppinsSemiBold",
                        color=ACCENT_TEAL
                    ),
                    margin=ft.margin.only(bottom=5),
                    alignment=ft.alignment.center_left
                ),
                ft.Container(
                    content=ft.Text(
                        "Help us protect your account",
                        size=14,
                        font_family="Lato",
                        color=ft.Colors.GREY_700
                    ),
                    alignment=ft.alignment.center_left
                ),
                ft.Container(height=10),
                maiden_name,
                ft.Container(height=10),
                nickname,
                ft.Container(height=10),
                fav_media,
                ft.Container(height=10),
                birth_city,
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Create Account",
                        style=BUTTON_STYLE,
                        color="white"
                    ),
                    width=300,
                    height=50,
                    on_click=on_signup,  # <-- Ensure this is set!
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT_TEAL,
                        color="white"
                    )
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Text("Already have an account?", style=BODY_STYLE),
                        ft.TextButton(
                            "Login here",
                            on_click=go_back_to_login,
                            style=ft.ButtonStyle(color=PRIMARY_BLUE)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=5,
        ),
        padding=30,
        bgcolor="white",
        border_radius=10,
        width=400,
    )

    # Main Layout
    page.add(
        ft.Container(
            content=ft.Row(
                [
                    left_panel,
                    ft.VerticalDivider(
                        width=1,
                        color=ft.Colors.GREY_300
                    ),
                    right_panel
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=0,
            bgcolor="white",
            border_radius=10,
            width=900,
            height=600,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, "black"),
                offset=ft.Offset(0, 4)
            ),
        )
    )
