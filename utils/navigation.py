import flet as ft

def navigate_to_login(page: ft.Page):
    """
    Clean the current page and navigate to login.
    This function will be imported by the dashboard modules.
    """
    from pages.login import login_ui
    page.clean()
    login_ui(page)

def create_sidebar(page: ft.Page, user_type: str, handle_logout, current_selection=None, menu_selection_handler=None):
    """
    Creates a sidebar with toggle functionality for both doctor and HR dashboards.
    Args:
        page: The flet page instance
        user_type: 'doctor', 'hr', or 'admin' to determine which menu items to show
        handle_logout: The logout handler function
        current_selection: Reference to track current selection
        menu_selection_handler: Callback function for menu item selection
    """
    # Add sidebar state
    is_sidebar_expanded = ft.Ref[bool]()
    is_sidebar_expanded.current = True

    # Define admin theme colors
    ADMIN_BLACK = "#1A1A1A"  # Deep black for text and buttons
    ADMIN_GRAY_DARK = "#2D2D2D"  # Dark gray for borders
    ADMIN_GRAY_MEDIUM = "#757575"  # Medium gray for secondary text
    ADMIN_GRAY_LIGHT = "#F5F5F5"  # Light gray for backgrounds
    ADMIN_WHITE = "#FFFFFF"  # White for card backgrounds
    ADMIN_SUCCESS = "#4CAF50"  # Green for success states
    ADMIN_WARNING = "#FFA726"  # Orange for warning states
    ADMIN_ERROR = "#EF5350"

    # Define medical theme colors
    MEDICAL_PRIMARY = "#00897B"  # Teal primary
    MEDICAL_SECONDARY = "#FFFFFF"  # White background
    MEDICAL_TEXT = "#00695C"  # Darker teal for text
    MEDICAL_ICON = "#00897B"  # Teal for icons
    MEDICAL_HOVER = "#E0F2F1"  # Light teal for hover states
    MEDICAL_WHITE = "#FFFFFF"  # White for contrast
    MEDICAL_BORDER = "#B2DFDB"  # Light teal for borders

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
                    # For the bottom section with logout
                    for sub_control in control.content.controls:
                        if isinstance(sub_control, (ft.Container, ft.ListTile)):
                            if hasattr(sub_control, 'content') and isinstance(sub_control.content, ft.ListTile):
                                sub_control.content.title.visible = is_sidebar_expanded.current
                            elif isinstance(sub_control, ft.ListTile):
                                sub_control.title.visible = is_sidebar_expanded.current
        
        page.update()

    def create_menu_item(title: str, icon, on_click_handler=None):
        """Helper function to create menu items with selection functionality"""
        if user_type == 'admin':
            if title == "Logout":
                return ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(title, color=ADMIN_GRAY_MEDIUM),
                        leading=ft.Icon(icon, color=ADMIN_GRAY_MEDIUM),
                    ),
                    on_click=on_click_handler,
                )
            return ft.Container(
                content=ft.ListTile(
                    title=ft.Text(title, color=ADMIN_WHITE if title == current_selection.current else ADMIN_GRAY_MEDIUM),
                    leading=ft.Icon(icon, color=ADMIN_WHITE if title == current_selection.current else ADMIN_GRAY_MEDIUM),
                ),
                bgcolor=ADMIN_GRAY_DARK if title == current_selection.current else None,
                border_radius=10,
                padding=5,
                on_click=lambda e: select_menu_item(title, e),
                data=title,
            )
        else:  # For HR and doctor dashboards
            if title == "Logout":
                return ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(title, color=MEDICAL_TEXT),
                        leading=ft.Icon(icon, color=MEDICAL_ICON),
                    ),
                    on_click=on_click_handler,
                )
            return ft.Container(
                content=ft.ListTile(
                    title=ft.Text(title, color=MEDICAL_TEXT if title == current_selection.current else MEDICAL_TEXT),
                    leading=ft.Icon(icon, color=MEDICAL_ICON if title == current_selection.current else MEDICAL_ICON),
                ),
                bgcolor=MEDICAL_HOVER if title == current_selection.current else None,
                border_radius=10,
                padding=5,
                on_click=lambda e: select_menu_item(title, e),
                data=title,
            )

    def select_menu_item(title: str, e):
        """Selection handler for HR and admin dashboards"""
        if title != "Logout":
            # Update current selection
            current_selection.current = title
            
            # Update all menu items' appearance
            for control in sidebar.content.controls:
                if isinstance(control, ft.Container):
                    if isinstance(control.content, ft.ListTile):
                        # Update ListTile items
                        if control.data == title:
                            if user_type == 'admin':
                                control.bgcolor = ADMIN_GRAY_DARK
                                control.content.title.color = ADMIN_WHITE
                                control.content.leading.color = ADMIN_WHITE
                            else:
                                control.bgcolor = MEDICAL_HOVER
                                control.content.title.color = MEDICAL_TEXT
                                control.content.leading.color = MEDICAL_ICON
                        else:
                            control.bgcolor = None
                            if user_type == 'admin':
                                control.content.title.color = ADMIN_GRAY_MEDIUM
                                control.content.leading.color = ADMIN_GRAY_MEDIUM
                            else:
                                control.content.title.color = MEDICAL_TEXT
                                control.content.leading.color = MEDICAL_ICON
            
            # Call the menu selection handler if provided
            if menu_selection_handler:
                menu_selection_handler(title, e)
            
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
            create_menu_item("HRs", ft.Icons.PEOPLE),
        ]
    else:  # HR menu items
        menu_items = [
            create_menu_item("Dashboard", ft.Icons.DASHBOARD),
            create_menu_item("Schedule", ft.Icons.CALENDAR_MONTH),
            create_menu_item("Patients", ft.Icons.PEOPLE),
            create_menu_item("Settings", ft.Icons.SETTINGS),
        ]

    # Create logout menu item
    logout_item = create_menu_item("Logout", ft.Icons.LOGOUT, handle_logout)

    # Create the sidebar
    sidebar = ft.Container(
        width=300,
        bgcolor=ADMIN_BLACK if user_type == 'admin' else MEDICAL_SECONDARY,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.MENU,
                                icon_color=ADMIN_WHITE if user_type == 'admin' else MEDICAL_ICON,
                                on_click=toggle_sidebar
                            ),
                            ft.Text("NexaCare", 
                                size=24, 
                                weight=ft.FontWeight.BOLD,
                                color=ADMIN_WHITE if user_type == 'admin' else MEDICAL_TEXT
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    padding=ft.padding.only(top=20, bottom=20),
                ),
                ft.Divider(color=ADMIN_GRAY_DARK if user_type == 'admin' else MEDICAL_HOVER),
                *menu_items,
                ft.Divider(color=ADMIN_GRAY_DARK if user_type == 'admin' else MEDICAL_HOVER),
                ft.Container(
                    content=ft.Column(
                        controls=[logout_item],
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
        border=ft.border.only(right=ft.BorderSide(1, ADMIN_GRAY_DARK if user_type == 'admin' else MEDICAL_HOVER))
    )

    return sidebar 