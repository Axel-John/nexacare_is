import flet as ft
from pages.dashboards import doctor, hr, admin
# hr, doctor, admin are already dashboard_ui functions, not modules
from models.user import get_user

# Define color constants
PRIMARY_BLUE = "#2A70FF"
SECONDARY_BLUE = "#31D7E9"
LIGHT_BLUE = "#EBF3FF"
ACCENT_TEAL = "#2CAFA4"

# Define color constants for admin theme
ADMIN_PRIMARY = "#1A1A1A"  # Almost black
ADMIN_SECONDARY = "#2D2D2D"  # Dark gray
ADMIN_ACCENT = "#4A4A4A"  # Medium gray
ADMIN_TEXT = "#E0E0E0"  # Light gray
ADMIN_HOVER = "#333333"  # Slightly lighter than primary

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
    page.snack_bar = ft.SnackBar(
        ft.Text(message, style=BODY_STYLE),
        bgcolor=ft.Colors.ERROR, 
        open=True
    )
    page.update()

def show_info_dialog(page, name, user_id, on_ok):
    print(f"[DEBUG] show_info_dialog called for {name} ({user_id})")
    
    def close_dlg(e):
        print("[DEBUG] Dialog close button clicked")
        overlay.visible = False
        page.update()
        print("[DEBUG] Dialog closed, proceeding to dashboard...")
        on_ok()

    # Create a semi-transparent overlay
    overlay = ft.Container(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Account Verified!", style=HEADING_STYLE, size=24, color=ACCENT_TEAL),
                    ft.Container(height=20),
                    ft.Text(f"Logging in as {name}", style=BODY_STYLE),
                    ft.Text(f"ID: {user_id}", style=BODY_STYLE, color=ACCENT_TEAL),
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
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        alignment=ft.alignment.center,
        visible=True
    )

    # Add the overlay to the page
    page.overlay.append(overlay)
    page.update()
    print("[DEBUG] Dialog should now be visible")

def create_admin_login_ui(page: ft.Page, return_to_main):
    """Create the admin login interface"""
    
    email_field = ft.Ref[ft.TextField]()
    password_field = ft.Ref[ft.TextField]()
    error_text = ft.Text("", color=ft.Colors.RED_400, size=14, visible=False)

    def handle_admin_login(e):
        email = email_field.current.value
        password = password_field.current.value
        error_text.visible = False
        
        if not email or not password:
            error_text.value = "Please fill in all fields"
            error_text.visible = True
            page.update()
            return

        user = get_user(email, password, "Admin")
        if user:
            page.clean()
            admin(page, user)
        else:
            error_text.value = "Invalid credentials"
            error_text.visible = True
            page.update()

    admin_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ADMIN_TEXT,
                            on_click=return_to_main
                        ),
                        ft.Text("Back to Login", color=ADMIN_TEXT, size=14)
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Container(height=20),
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=50, color=ADMIN_TEXT),
                ft.Container(height=10),
                ft.Text(
                    "Administrator Login",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ADMIN_TEXT
                ),
                ft.Container(height=5),
                ft.Text(
                    "Please enter your credentials",
                    size=14,
                    color=ft.Colors.GREY_400
                ),
                ft.Container(height=30),
                ft.TextField(
                    ref=email_field,
                    label="Admin ID or Email",
                    width=300,
                    border_color=ADMIN_ACCENT,
                    focused_border_color=ADMIN_TEXT,
                    prefix_icon=ft.Icons.PERSON,
                    bgcolor=ADMIN_SECONDARY,
                    color=ADMIN_TEXT,
                    label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                    cursor_color=ADMIN_TEXT,
                ),
                ft.Container(height=20),
                ft.TextField(
                    ref=password_field,
                    label="Password",
                    password=True,
                    can_reveal_password=True,
                    width=300,
                    border_color=ADMIN_ACCENT,
                    focused_border_color=ADMIN_TEXT,
                    prefix_icon=ft.Icons.LOCK,
                    bgcolor=ADMIN_SECONDARY,
                    color=ADMIN_TEXT,
                    label_style=ft.TextStyle(color=ft.Colors.GREY_400),
                    cursor_color=ADMIN_TEXT,
                    on_submit=handle_admin_login
                ),
                ft.Container(height=10),
                error_text,
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Login as Administrator",
                        weight=ft.FontWeight.BOLD,
                        color=ADMIN_PRIMARY,
                    ),
                    width=300,
                    height=45,
                    style=ft.ButtonStyle(
                        color=ADMIN_PRIMARY,
                        bgcolor=ADMIN_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=handle_admin_login
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=400,
        height=600,
        bgcolor=ADMIN_PRIMARY,
        border_radius=10,
        padding=30,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        ),
    )

    return admin_panel

def login_ui(page: ft.Page):
    page.title = "Login Window"
    page.padding = 0  
    page.bgcolor = LIGHT_BLUE
    page.window_resizable = False
    page.window_full_screen = True  
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = None

    email_field = ft.Ref[ft.TextField]()
    password_field = ft.Ref[ft.TextField]()
    current_role = "HR"  # Default role

    # Separate error texts for email/id and password
    email_error_text = ft.Text("", color=ft.Colors.RED, size=14, visible=False)
    password_error_text = ft.Text("", color=ft.Colors.RED, size=14, visible=False)

    # Add a text to show login status
    login_status_text = ft.Text("", color=ft.Colors.GREEN, size=15, visible=False)

    def update_role_selection():
        hr_text.current.color = PRIMARY_BLUE if current_role == "HR" else "black"
        doctor_text.current.color = PRIMARY_BLUE if current_role == "Doctor" else "black"
        hr_container.current.border = ft.border.only(bottom=ft.border.BorderSide(2, ACCENT_TEAL)) if current_role == "HR" else None
        doctor_container.current.border = ft.border.only(bottom=ft.border.BorderSide(2, ACCENT_TEAL)) if current_role == "Doctor" else None
        page.update()

    def on_role_click(role):
        def handle_click(e):
            nonlocal current_role
            current_role = role
            update_role_selection()
        return handle_click

    def on_sign_in(e):
        print("[DEBUG] Sign in button clicked")
        email = email_field.current.value if email_field.current else ""
        password = password_field.current.value if password_field.current else ""
        print(f"[DEBUG] Email: {email}, Password: {'*' * len(password)}, Role: {current_role}")
        email_error_text.value = ""
        email_error_text.visible = False
        password_error_text.value = ""
        password_error_text.visible = False
        login_status_text.value = ""
        login_status_text.visible = False
        if not email:
            print("[DEBUG] Email is empty")
            email_error_text.value = "Please enter your email or ID"
            email_error_text.visible = True
            page.update()
            return
        if not password:
            print("[DEBUG] Password is empty")
            password_error_text.value = "Please enter your password"
            password_error_text.visible = True
            page.update()
            return
        user = get_user(email, password, current_role)
        print(f"[DEBUG] get_user returned: {user}")
        if not user:
            # Check if email/id exists for more specific error
            from database import get_connection
            conn = get_connection()
            table = "doctors" if current_role == "Doctor" else ("hrs" if current_role == "HR" else "admins")
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                f"SELECT * FROM {table} WHERE email = %s OR user_id = %s",
                (email, email)
            )
            exists = cursor.fetchone()
            print(f"[DEBUG] User exists in table: {exists}")
            cursor.close()
            conn.close()
            if not exists:
                email_error_text.value = "Email or ID not found"
                email_error_text.visible = True
            else:
                password_error_text.value = "Incorrect password"
                password_error_text.visible = True
            page.update()
            return
        # --- Verification check for HR and Doctor ---
        if current_role in ("Doctor", "HR") and not user.get("is_verified", False):
            email_error_text.value = "Your account has not been verified by the admin yet."
            email_error_text.visible = True
            page.update()
            return
        # Show login status and then open dashboard
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        user_id = user.get('user_id', '')
        login_status_text.value = f"Logging in as {name} (ID: {user_id})... Redirecting to dashboard."
        login_status_text.visible = True
        page.update()
        import time
        time.sleep(0.5)  # Short pause for user to see the message
        page.clean()
        if current_role == "Doctor":
            print("[DEBUG] Redirecting to doctor dashboard")
            doctor(page, user)  # Call the function directly
        elif current_role == "HR":
            print("[DEBUG] Redirecting to HR dashboard")
            hr(page, user)      # Call the function directly
        elif current_role == "Admin":
            print("[DEBUG] Redirecting to admin dashboard")
            admin(page, user)   # Call the function directly

    def go_to_signup(e):
        from pages.signup import signup_ui
        page.clean()
        signup_ui(page)



    hr_text = ft.Ref[ft.Text]()
    doctor_text = ft.Ref[ft.Text]()
    hr_container = ft.Ref[ft.Container]()
    doctor_container = ft.Ref[ft.Container]()

    left_panel = ft.Container(
        content=ft.Image(
            src="assets/gifs/left_section_login.gif",
            width=340,
            height=500,
            fit=ft.ImageFit.CONTAIN,
        ),
        width=400,
        height=550,
        padding=30,
        border_radius=30,
        alignment=ft.alignment.center,
    )

    login_panel = ft.Container(
        content=ft.Column(
            [
                ft.Stack(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Container(
                                        ref=hr_container,
                                        content=ft.Text("👤 HR", ref=hr_text, style=SUBHEADING_STYLE, color=PRIMARY_BLUE),
                                        on_click=on_role_click("HR"),
                                        padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
                                        border=ft.border.only(bottom=ft.border.BorderSide(2, ACCENT_TEAL))
                                    ),
                                    ft.Container(width=5),
                                    ft.Container(
                                        ref=doctor_container,
                                        content=ft.Text("🩺 Doctor", ref=doctor_text, style=SUBHEADING_STYLE),
                                        on_click=on_role_click("Doctor"),
                                        padding=ft.padding.only(left=15, right=15, top=10, bottom=10)
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            width=400,
                        ),
                    ]
                ),
                ft.Container(height=20),
                ft.Text(
                    "Welcome back",
                    style=ft.TextStyle(
                        size=24,
                        weight=ft.FontWeight.W_600,
                        font_family="PoppinsSemiBold",
                        color=ACCENT_TEAL
                    )
                ),
                ft.Container(height=20),
                ft.Text(
                    "Log in to your account and we'll get you in to see our doctors",
                    style=BODY_STYLE,
                    color=ft.Colors.GREY_700
                ),
                ft.Container(height=20),
                ft.TextField(
                    label="Email Address",
                    width=400,
                    ref=email_field,
                    border_color=ACCENT_TEAL,
                    focused_border_color=ACCENT_TEAL,
                    text_style=BODY_STYLE,
                    label_style=BODY_STYLE,
                    hint_text="Enter email or automated ID",
                    hint_style=ft.TextStyle(
                        color=ft.Colors.GREY_400,
                        size=11
                    )
                ),
                ft.Container(email_error_text, alignment=ft.alignment.center_left, padding=ft.padding.only(left=4, top=2, bottom=2)),
                ft.Container(height=10),
                ft.TextField(
                    label="Password",
                    password=True,
                    can_reveal_password=True,
                    width=400,
                    ref=password_field,
                    border_color=ACCENT_TEAL,
                    focused_border_color=ACCENT_TEAL,
                    text_style=BODY_STYLE,
                    label_style=BODY_STYLE,
                    on_submit=on_sign_in
                ),
                ft.Container(password_error_text, alignment=ft.alignment.center_left, padding=ft.padding.only(left=4, top=2, bottom=2)),
                ft.Container(height=5),
                login_status_text,  # Show login status here
                ft.Container(
                    content=ft.Text("Forgot password?", style=BODY_STYLE, color=PRIMARY_BLUE),
                    on_click=lambda _: None,
                    padding=ft.padding.only(top=5, bottom=5),
                ),
                ft.Container(height=10),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Sign In",
                        style=BUTTON_STYLE,
                        color="white"
                    ),
                    width=400,
                    height=50,
                    on_click=on_sign_in,
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT_TEAL,
                        color="white"
                    )
                ),
                ft.Container(height=10),
                ft.Text("Don't have an account?", style=BODY_STYLE),
                ft.Container(height=5),
                ft.Row([
                    ft.Container(
                        content=ft.Text("Sign up", style=BODY_STYLE, color=PRIMARY_BLUE),
                        on_click=go_to_signup,
                        padding=ft.padding.only(top=5, bottom=5),
                    )
                ], spacing=10),
            ],
            spacing=5,
            alignment="center"
        ),
        padding=30,
        height=600,
    )

    # Function to handle admin shortcut (Ctrl+Alt+A) - only works in login UI
    def handle_keyboard(e):
        # Only handle the shortcut if we're in the login UI
        if not hasattr(page, 'current_ui') or page.current_ui != 'login':
            return
            
        if e.ctrl and e.alt and e.key == 'A':
            # Remove the keyboard event handler to prevent multiple bindings
            page.on_keyboard_event = None
            
            page.clean()
            page.bgcolor = ADMIN_PRIMARY  # Set the window background to admin color
            
            def return_to_main(_):
                page.clean()
                # Reset current UI state
                page.current_ui = 'login'
                login_ui(page)
                
            admin_panel = create_admin_login_ui(page, return_to_main)
            page.add(
                ft.Container(
                    content=admin_panel,
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
            page.update()
    
    # Only set the keyboard handler if we're in the login UI
    if not hasattr(page, 'current_ui') or page.current_ui != 'login':
        page.current_ui = 'login'
        page.on_keyboard_event = handle_keyboard
    
    page.add(
        ft.Container(
            content=ft.Row(
                [
                    left_panel,
                    login_panel
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

    update_role_selection()
