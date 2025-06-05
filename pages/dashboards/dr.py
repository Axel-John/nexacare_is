import flet as ft
import sys
sys.path.append("../")
from utils.navigation import navigate_to_login, create_sidebar
from database import get_all_appointments, get_all_patients, update_appointment_status, update_patient

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

    # Initialize current_selection for sidebar menu
    current_selection = ft.Ref[str]()
    current_selection.current = "Dashboard"

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
    sidebar = create_sidebar(page, "doctor", handle_logout, current_selection)

    # Tab state
    tab_state = ft.Ref[int]()
    tab_state.current = 0

    def refresh():
        page.update()

    # --- Appointments Tab ---
    def appointments_tab():
        success, msg, appointments = get_all_appointments()
        if not success or appointments is None:
            return ft.Text("Failed to load appointments.", color=ft.Colors.RED)
        # Filter for this doctor
        doctor_appointments = [a for a in appointments if str(a.get("doctor_id")) == str(user["user_id"])]
        def mark_complete(apt):
            update_appointment_status(apt["id"], "Completed")
            page.snack_bar = ft.SnackBar(content=ft.Text("Appointment marked as completed."))
            page.snack_bar.open = True
            refresh()
        def view_details(apt):
            # Simple modal for now
            dialog_modal.content = ft.Container(
                width=400,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=20,
                content=ft.Column([
                    ft.Text(f"Patient: {apt.get('patient_name', '')}", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Date: {apt.get('appointment_date', '')}"),
                    ft.Text(f"Type: {apt.get('consultation_type', '')}"),
                    ft.Text(f"Status: {apt.get('status', '')}"),
                    ft.Text(f"Notes: {apt.get('notes', '')}"),
                    ft.Row([
                        ft.ElevatedButton("Close", on_click=lambda e: (setattr(dialog_modal, 'visible', False), page.update())),
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10),
            )
            dialog_modal.visible = True
            page.update()
        if not doctor_appointments:
            return ft.Text("No appointments assigned to you.")
        return ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"{apt['patient_name']} - {apt['appointment_date']}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Type: {apt['consultation_type']}", size=14),
                            ft.Text(f"Status: {apt['status']}", size=12),
                        ], spacing=2),
                        ft.Container(expand=True),
                        ft.ElevatedButton("View Details", on_click=lambda e, a=apt: view_details(a)),
                        ft.ElevatedButton("Mark Complete", on_click=lambda e, a=apt: mark_complete(a), disabled=apt['status'] == 'Completed'),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                )
            ) for apt in doctor_appointments
        ], spacing=10)

    # --- Patients Tab ---
    def patients_tab():
        patients = get_all_patients()
        # Show patients assigned to this doctor or unassigned
        my_id = str(user["user_id"])
        assigned = [p for p in patients if str(p.get("assigned_doctor", "")) == my_id]
        unassigned = [p for p in patients if not p.get("assigned_doctor")]  # None or empty
        def take_over_patient(patient):
            update_patient(patient["id"], assigned_doctor=my_id)
            page.snack_bar = ft.SnackBar(content=ft.Text("You are now assigned to this patient."))
            page.snack_bar.open = True
            refresh()
        def view_patient_details(patient):
            dialog_modal.content = ft.Container(
                width=400,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=20,
                content=ft.Column([
                    ft.Text(f"Name: {patient.get('full_name', '')}", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Phone: {patient.get('phone', '')}"),
                    ft.Text(f"Gender: {patient.get('gender', '')}"),
                    ft.Text(f"Status: {patient.get('status', '')}"),
                    ft.Text(f"Doctor: {patient.get('doctor_name', 'Unassigned')}", size=14),
                    ft.Row([
                        ft.ElevatedButton("Close", on_click=lambda e: (setattr(dialog_modal, 'visible', False), page.update())),
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10),
            )
            dialog_modal.visible = True
            page.update()
        def patient_card(patient, show_take_over):
            return ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(patient.get('full_name', ''), size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Phone: {patient.get('phone', '')}", size=12),
                            ft.Text(f"Status: {patient.get('status', '')}", size=12),
                        ], spacing=2),
                        ft.Container(expand=True),
                        ft.ElevatedButton("View Details", on_click=lambda e, p=patient: view_patient_details(p)),
                        ft.ElevatedButton("Take Over", on_click=lambda e, p=patient: take_over_patient(p), disabled=not show_take_over),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                )
            )
        return ft.Column([
            ft.Text("Assigned Patients", size=16, weight=ft.FontWeight.BOLD),
            *(patient_card(p, False) for p in assigned),
            ft.Container(height=20),
            ft.Text("Unassigned Patients", size=16, weight=ft.FontWeight.BOLD),
            *(patient_card(p, True) for p in unassigned),
        ], spacing=10)

    # Tab control
    tab_content = ft.Tabs(
        selected_index=tab_state.current,
        on_change=lambda e: (setattr(tab_state, 'current', e.control.selected_index), page.update()),
        tabs=[
            ft.Tab(text="Appointments", content=appointments_tab()),
            ft.Tab(text="Patients", content=patients_tab()),
        ]
    )

    # Main content area
    main_content = ft.Container(
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Text(f"Welcome back, Dr. {user.get('first_name', '')} {user.get('last_name', '')}", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Text(f"ID: {user.get('user_id', '')}", size=14, color=ft.Colors.BLUE_GREY_700),
            ]),
            ft.Container(height=20),
            tab_content,
        ], spacing=20),
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
