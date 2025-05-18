import flet as ft
from .dashboards import doctor, hr, admin
from models.user import get_user

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
    page.snack_bar = ft.SnackBar(
        ft.Text(message, style=BODY_STYLE),
        bgcolor=ft.colors.ERROR,
        open=True
    )
    page.update()

def login_ui(page: ft.Page):
    page.title = "Login Window"
    page.padding = 0  # Remove page padding
    page.bgcolor = LIGHT_BLUE
    page.window_resizable = True
    page.window_maximized = True
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = None  # Disable scrolling

    # State for role selection
    selected_role = ft.Ref[ft.Text]()
    email_field = ft.Ref[ft.TextField]()
    password_field = ft.Ref[ft.TextField]()
    current_role = "HR"  # Default role

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
        email = email_field.current.value
        password = password_field.current.value
        login_user(page, email, password, current_role)

    def go_to_signup(e):
        page.clean()
        from .signup import signup_ui
        signup_ui(page)

    # Create refs for role selection elements
    hr_text = ft.Ref[ft.Text]()
    doctor_text = ft.Ref[ft.Text]()
    hr_container = ft.Ref[ft.Container]()
    doctor_container = ft.Ref[ft.Container]()

    left_panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("← Back", color="white", size=14, style=BODY_STYLE),
                ft.Text(
                    "Empowering better healthcare through smart,\nsecure records.",
                    color="white",
                    style=HEADING_STYLE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text("✔ Secure access to health records", color="white", style=SUBHEADING_STYLE),
                        ft.Text("✔ Trusted care, anytime you need it", color="white", style=SUBHEADING_STYLE),
                        ft.Text("✔ Simple tools for smarter healthcare", color="white", style=SUBHEADING_STYLE),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=25,
        ),
        width=400,
        height=550,
        bgcolor=PRIMARY_BLUE,
        padding=30,
        border_radius=10,
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
                    label_style=BODY_STYLE
                ),
                ft.Container(height=15),
                ft.TextField(
                    label="Password",
                    password=True,
                    can_reveal_password=True,
                    width=400,
                    ref=password_field,
                    border_color=ACCENT_TEAL,
                    focused_border_color=ACCENT_TEAL,
                    text_style=BODY_STYLE,
                    label_style=BODY_STYLE
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text("Forgot password?", style=BODY_STYLE, color=PRIMARY_BLUE),
                    on_click=lambda _: None,
                    padding=ft.padding.only(top=5, bottom=5),
                ),
                ft.Container(height=15),
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
                ft.Container(height=20),
                ft.Text("Don't have an account?", style=BODY_STYLE),
                ft.Container(height=10),
                ft.Row([
                    ft.Container(
                        content=ft.Text("Sign up", style=BODY_STYLE, color=PRIMARY_BLUE),
                        on_click=go_to_signup,
                        padding=ft.padding.only(top=5, bottom=5),
                    ),
                    ft.Container(
                        content=ft.Text("Admin Login", style=BODY_STYLE, color=PRIMARY_BLUE),
                        on_click=lambda _: None,
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

# handle backend functionalities
def login_user(page, email, password, role):
    user = get_user(email, password, role)  # from user.py
    if not user:
        show_error(page, "Invalid credentials")
    elif role == "Doctor":
        doctor.dashboard_ui(page, user)
    elif role == "HR":
        hr.dashboard_ui(page, user)
    elif role == "Admin":
        admin.dashboard_ui(page, user)
