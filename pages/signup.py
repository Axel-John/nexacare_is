import flet as ft
from .login import PRIMARY_BLUE, SECONDARY_BLUE, LIGHT_BLUE, HEADING_STYLE, SUBHEADING_STYLE, BODY_STYLE, BUTTON_STYLE, ACCENT_TEAL

def signup_ui(page: ft.Page):
    page.title = "Sign Up - NexaCare"
    page.padding = 50
    page.bgcolor = LIGHT_BLUE
    page.window_resizable = True
    page.window_maximized = True
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "auto"

    def on_role_change(e):
        role_dropdown.value = e.data
        page.update()

    def validate_passwords():
        if password_field.value != confirm_password_field.value:
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Passwords do not match!", style=BODY_STYLE),
                    bgcolor=ft.Colors.ERROR
                )
            )
            return False
        return True

    def on_signup(e):
        if not validate_passwords():
            return
        # TODO: Implement signup logic
        pass

    def go_back_to_login(e):
        page.clean()
        from .login import login_ui
        login_ui(page)

    # Left Panel - Personal Information
    first_name = ft.TextField(
        label="First Name",
        width=190,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
    )

    last_name = ft.TextField(
        label="Last Name",
        width=130,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
    )

    email_field = ft.TextField(
        label="Email Address",
        width=200,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
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
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE,
        on_change=on_role_change
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=350,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
    )

    confirm_password_field = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        width=350,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
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
                    [email_field, ft.Container(width=2),role_dropdown],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Container(height=10),
                password_field,
                ft.Container(height=10),
                confirm_password_field,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        padding=30,
        bgcolor="white",
        border_radius=10,
        width=400,
    )

    # Right Panel - Security Questions
    maiden_name = ft.TextField(
        label="Mother's Maiden Name",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
    )

    nickname = ft.TextField(
        label="Childhood Nickname",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
    )

    fav_media = ft.TextField(
        label="Favorite Book or Movie",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
    )

    birth_city = ft.TextField(
        label="City of Birth",
        width=300,
        border_color=ACCENT_TEAL,
        focused_border_color=ACCENT_TEAL,
        text_style=ft.TextStyle(
            size=15,
            color="black",
            font_family="Lato"
        ),
        label_style=BODY_STYLE
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
                    on_click=on_signup,
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
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            padding=30,
            bgcolor="white",
            border_radius=10,
            width=900,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, "black"),
                offset=ft.Offset(0, 4)
            )
        )
    ) 