import flet as ft

def navigate_to_login(page: ft.Page):
    """
    Clean the current page and navigate to login.
    This function will be imported by the dashboard modules.
    """
    from pages.login import login_ui
    page.clean()
    login_ui(page)

def create_sidebar(page: ft.Page, user_type: str, handle_logout, current_selection=None):
    """
    Creates a sidebar with toggle functionality for both doctor and HR dashboards.
    Args:
        page: The flet page instance
        user_type: 'doctor', 'hr', or 'admin' to determine which menu items to show
        handle_logout: The logout handler function
        current_selection: Reference to track current selection
    """
    # Add sidebar state
    is_sidebar_expanded = ft.Ref[bool]()
    is_sidebar_expanded.current = True

    def toggle_sidebar(e):
        is_sidebar_expanded.current = not is_sidebar_expanded.current
        sidebar.width = 300 if is_sidebar_expanded.current else 80
        
        # Toggle visibility of text elements
        for control in sidebar.content.controls:
            if isinstance(control, ft.Container):
                if isinstance(control.content, ft.Text):
                    # Hide/show NexaCare text
                    control.visible = is_sidebar_expanded.current
                elif isinstance(control.content, ft.ListTile):
                    # Hide/show text in list tiles
                    control.content.title.visible = is_sidebar_expanded.current
                elif isinstance(control.content, ft.Row):
                    # Handle the title row
                    for row_control in control.content.controls:
                        if isinstance(row_control, ft.Text):
                            row_control.visible = is_sidebar_expanded.current
                elif isinstance(control.content, ft.Column):
                    # For the bottom section with settings and logout
                    for sub_control in control.content.controls:
                        if isinstance(sub_control, (ft.Container, ft.ListTile)):
                            if hasattr(sub_control, 'content') and isinstance(sub_control.content, ft.ListTile):
                                sub_control.content.title.visible = is_sidebar_expanded.current
                            elif isinstance(sub_control, ft.ListTile):
                                sub_control.title.visible = is_sidebar_expanded.current
        
        page.update()

    def create_menu_item(title: str, icon, on_click_handler=None):
        """Helper function to create menu items with selection functionality"""
        if user_type in ['hr', 'admin']:
            return ft.Container(
                content=ft.ListTile(
                    title=ft.Text(title, color=ft.Colors.GREY_800),
                    leading=ft.Icon(icon, color=ft.Colors.GREY_800),
                ),
                bgcolor=ft.Colors.BLUE_50 if title == current_selection.current else None,
                border_radius=10,
                padding=5,
                on_click=on_click_handler if on_click_handler else lambda e: select_menu_item(title, e),
                data=title,
            )
        return ft.ListTile(
            title=ft.Text(title, color=ft.Colors.GREY_800),
            leading=ft.Icon(icon, color=ft.Colors.GREY_800),
        )

    def select_menu_item(title: str, e):
        """Selection handler for HR and admin dashboards"""
        if user_type in ['hr', 'admin'] and title != "Logout":
            current_selection.current = title
            for control in sidebar.content.controls:
                if isinstance(control, ft.Container) and hasattr(control, 'data'):
                    control.bgcolor = ft.Colors.BLUE_50 if control.data == title else None
                    if isinstance(control.content, ft.ListTile):
                        control.content.title.color = ft.Colors.PRIMARY if control.data == title else ft.Colors.GREY_800
                        control.content.leading.color = ft.Colors.PRIMARY if control.data == title else ft.Colors.GREY_800
            page.update()

    # Create main menu items based on user type
    menu_items = []
    if user_type == 'doctor':
        menu_items = [
            create_menu_item("Dashboard", ft.Icons.DASHBOARD),
            create_menu_item("Appointments", ft.Icons.CALENDAR_MONTH),
            create_menu_item("Patients", ft.Icons.PEOPLE),
            create_menu_item("Prescriptions", ft.Icons.MEDICAL_SERVICES),
        ]
    elif user_type == 'admin':
        menu_items = [
            create_menu_item("Dashboard", ft.Icons.DASHBOARD),
            create_menu_item("Doctors", ft.Icons.MEDICAL_SERVICES),
            create_menu_item("Patients", ft.Icons.PEOPLE),
            create_menu_item("Schedule", ft.Icons.CALENDAR_MONTH),
            create_menu_item("Reports", ft.Icons.ANALYTICS),
        ]
    else:  # HR menu items
        menu_items = [
            create_menu_item("Dashboard", ft.Icons.DASHBOARD),
            create_menu_item("Schedule", ft.Icons.CALENDAR_MONTH),
            create_menu_item("Patients", ft.Icons.PEOPLE),
        ]

    # Create settings menu items
    settings_items = [
        create_menu_item("Settings", ft.Icons.SETTINGS),
        create_menu_item("Logout", ft.Icons.LOGOUT, handle_logout),
    ]

    # Create the sidebar
    sidebar = ft.Container(
        width=300,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.MENU,
                                icon_color=ft.Colors.PRIMARY,
                                on_click=toggle_sidebar
                            ),
                            ft.Text("NexaCare", 
                                size=24, 
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.PRIMARY
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    padding=ft.padding.only(top=20, bottom=20),
                ),
                ft.Divider(color=ft.Colors.GREY_300),
                *menu_items,
                ft.Divider(color=ft.Colors.GREY_300),
                ft.Container(
                    content=ft.Column(
                        controls=settings_items,
                        spacing=0,
                        alignment=ft.MainAxisAlignment.END
                    ),
                    expand=True,
                    alignment=ft.alignment.bottom_left
                ),
            ],
            spacing=5,
            expand=True
        ),
        padding=10,
        border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_300))
    )

    return sidebar 