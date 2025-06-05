import flet as ft
import sys
sys.path.append("../")
from utils.navigation import navigate_to_login, create_sidebar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from database import get_all_patients, add_patient, update_patient_status, delete_patient, update_patient, get_all_doctors, add_appointment, get_all_appointments
from models.user import get_all_doctors

visit_date_picker = None

# Define HR dashboard colors
HR_PRIMARY = "#00897B"  # Teal primary
HR_SECONDARY = "#FFFFFF"  # White background
HR_TEXT = "#00695C"  # Darker teal for text
HR_ICON = "#00897B"  # Teal for icons
HR_HOVER = "#E0F2F1"  # Light teal for hover states
HR_WHITE = "#FFFFFF"  # White for contrast
HR_BORDER = "#B2DFDB"  # Light teal for borders
HR_SUCCESS = "#4CAF50"  # Green for success states
HR_WARNING = "#FFA726"  # Orange for warning states
HR_ERROR = "#EF5350"  # Red for error states
HR_INFO = "#2196F3"  # Blue for info states
HR_GRAY = "#9E9E9E"  # Gray for neutral states

def show_date_picker_dialog(page, text_field_to_update, patient_form_state, state_key, dialog_title, get_current_step_content, min_date=None, max_date=None, on_date_selected=None):
    # Create a container to hold the date picker
    container = ft.Container(
        padding=20,
        width=400,
    )
    
    # Create a new date picker instance
    date_picker = ft.DatePicker(
        first_date=min_date or datetime(1900, 1, 1),
        last_date=max_date or datetime.now() + timedelta(days=3650),
        on_dismiss=lambda e: page.update()
    )
    
    # Add the date picker to the container
    container.content = date_picker
    
    def handle_date_confirmed(e):
        if date_picker.value:
            # Format the date as YYYY-MM-DD
            formatted_date = date_picker.value.strftime('%Y-%m-%d')
            # Update form state
            patient_form_state[state_key] = formatted_date
            
            # Update the text field directly
            if text_field_to_update is not None and hasattr(text_field_to_update, 'value'):
                text_field_to_update.value = formatted_date
            
            # Close the dialog
            page.dialog.open = False
            
            # Force-update the visit date field if this is the visit date picker
            if state_key == "visit_date":
                visit_field = find_control_by_key(page, "visit_date_field")
                if visit_field is not None:
                    visit_field.value = formatted_date
            
            # Refresh the stepper content
            if hasattr(page, 'add_patient_modal') and page.add_patient_modal.current is not None:
                modal_content = page.add_patient_modal.current.content.content
                if len(modal_content.controls) > 2:
                    modal_content.controls[2].content = get_current_step_content()
            
            # Call the on_date_selected callback if provided
            if on_date_selected:
                on_date_selected()
            
            # Force UI update
            page.update()
    
    # Set up the date picker change handler
    date_picker.on_change = lambda e: handle_date_confirmed(e)
    
    def handle_cancel(e):
        # Close the dialog
        page.dialog.open = False
        page.update()

    # Create the alert dialog
    alert_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(dialog_title),
        content=container,
        actions=[
            ft.TextButton("OK", on_click=handle_date_confirmed),
            ft.TextButton("Cancel", on_click=handle_cancel),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: page.update()
    )
    
    # Show the date picker and dialog
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)
    page.dialog = alert_dialog
    alert_dialog.open = True
    date_picker.open = True
    page.update()

# --- Tag Functions ---
def add_tag(page, tag_list, tag_text, max_length=50):
    tag_text = str(tag_text).strip()
    if not tag_text:
        return
    # Clear any previous error
    error_text = find_control_by_key(page, 'error_text')
    if error_text:
        error_text.visible = False
    if len(tag_text) > max_length:
        if error_text:
            error_text.value = f"Tag cannot be longer than {max_length} characters"
            error_text.visible = True
        page.update()
        return
    if tag_text and tag_text not in tag_list:
        tag_list.append(tag_text)
        # Clear the input field
        input_field = find_control_by_attr(page, 'on_submit')
        if input_field:
            input_field.value = ""
        page.update()

def remove_tag(page, tag_list, tag_text):
    if tag_text in tag_list:
        tag_list.remove(tag_text)
        page.update()

def find_control_by_key(page, key):
    """Helper function to find a control by its key"""
    try:
        return next(
            control for control in page.controls 
            if hasattr(control, 'key') and control.key == key
        )
    except StopIteration:
        return None

def find_control_by_attr(page, attr):
    """Helper function to find a control by its attribute"""
    for control in page.controls:
        if hasattr(control, 'content'):
            result = _find_control_by_attr_recursive(control, attr)
            if result:
                return result
    return None

def _find_control_by_attr_recursive(control, attr):
    """Recursively search for a control with the given attribute"""
    if hasattr(control, attr):
        return control
    if hasattr(control, 'content') and hasattr(control.content, 'controls'):
        for c in control.content.controls:
            result = _find_control_by_attr_recursive(c, attr)
            if result:
                return result
    return None

# --- Stat Card ---
def create_stat_card(title, value, icon, color, trend=None):
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(title, size=14, color=HR_TEXT),
                ft.Icon(icon, color=color, size=24),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(str(value), size=32, weight=ft.FontWeight.BOLD, color=HR_TEXT),
            ft.Row([
                ft.Text(trend if trend else "", size=12, color=color),
            ]) if trend else ft.Container(),
        ], spacing=6),
        padding=20,
        bgcolor=HR_WHITE,
        border_radius=12,
        expand=True,
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=8, color=ft.Colors.with_opacity(0.08, HR_TEXT), offset=ft.Offset(0, 2)
        ),
    )

# --- Appointment Timeline Item ---
def create_appointment_timeline_item(apt, selected=False, on_select=None):
    status_color = HR_SUCCESS if apt.get('status') == 'completed' else (HR_WARNING if apt.get('status') == 'pending' else HR_ERROR)
    return ft.Container(
        content=ft.Row([
            ft.CircleAvatar(
                content=ft.Text(apt['patient_name'][0].upper(), color=HR_WHITE, size=16),
                bgcolor=HR_PRIMARY,
                radius=16,
            ),
            ft.Column([
                ft.Text(apt['patient_name'], size=14, weight=ft.FontWeight.W_500, color=HR_TEXT),
                ft.Text(apt['doctor_name'], size=12, color=HR_TEXT),
            ], spacing=2),
            ft.Container(expand=True),
            ft.Text(apt['time'] if 'time' in apt else '', size=12, color=HR_TEXT),
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=status_color, size=18) if apt.get('status') == 'completed' else (
                ft.Icon(ft.Icons.SCHEDULE, color=status_color, size=18) if apt.get('status') == 'pending' else ft.Icon(ft.Icons.ERROR, color=status_color, size=18)
            ),
        ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=HR_HOVER if selected else None,
        border_radius=8,
        padding=10,
        on_click=on_select,
    )

# --- Ongoing Appointment Details ---
def create_ongoing_appointment_details(apt):
    if not apt:
        return ft.Container()
    return ft.Container(
        bgcolor=HR_WHITE,
        border_radius=12,
        padding=20,
        expand=True,
        content=ft.Column([
            ft.Text("Patient Info", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
            ft.Divider(height=10, color=HR_BORDER),
            ft.Row([
                ft.CircleAvatar(content=ft.Text(apt['patient_name'][0].upper(), color=HR_WHITE, size=18), bgcolor=HR_PRIMARY, radius=20),
                ft.Column([
                    ft.Text(apt['patient_name'], size=14, weight=ft.FontWeight.W_500, color=HR_TEXT),
                    ft.Text(f"Gender: {apt.get('gender', '')}", size=12, color=HR_TEXT),
                ], spacing=2),
            ], spacing=10),
            ft.Container(height=10),
            ft.Text(f"Doctor: {apt['doctor_name']}", size=12, color=HR_TEXT),
            ft.Text(f"Date: {apt['date']} {apt.get('time', '')}", size=12, color=HR_TEXT),
            ft.Text(f"Reason: {apt.get('reason', 'Consultation')}", size=12, color=HR_TEXT),
            ft.Container(height=10),
            ft.Text("Consultation Notes", size=14, weight=ft.FontWeight.BOLD, color=HR_TEXT),
            ft.Text(apt.get('notes', 'No notes.'), size=12, color=HR_TEXT),
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton("Reschedule", bgcolor=HR_HOVER, color=HR_TEXT, style=ft.ButtonStyle()),
                ft.ElevatedButton("Finish consultation", bgcolor=HR_PRIMARY, color=HR_WHITE, style=ft.ButtonStyle()),
            ], spacing=10),
        ], spacing=10),
    )

def create_patients_tab(page, user):

    
    # Birthdate field with icon
    birthdate_textfield_control = ft.TextField(
        label="Birthdate",
        read_only=True,
        value="",  # Start with empty string
        width=470,
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        label_style=ft.TextStyle(color=HR_TEXT),
    )
    birthdate_icon_button = ft.IconButton(
        ft.Icons.CALENDAR_MONTH,
        tooltip="Select Birthdate",
        on_click=lambda e: show_date_picker_dialog(
            page,
            visit_date_textfield_control, 
            patient_form_state,
            "visit_date",
            "Select Visit Date",
            get_current_step_content,
            min_date=datetime.now() - timedelta(days=3650),
            max_date=datetime.now() + timedelta(days=3650)
        )

    )
    birthdate_field = ft.Row(
        [birthdate_textfield_control, birthdate_icon_button],
        spacing=5,
        alignment=ft.MainAxisAlignment.START
    )
    
    # Visit Date field with icon
    visit_date_textfield_control = ft.TextField(
        label="Visit Date",
        width=200,  # Adjusted width for icon
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        label_style=ft.TextStyle(color=HR_TEXT),
        read_only=True
    )
    visit_date_icon_button = ft.IconButton(
        ft.Icons.CALENDAR_MONTH,
        tooltip="Select Visit Date",
        on_click=lambda e: show_date_picker_dialog(
            page,
            visit_date_textfield_control,
            patient_form_state,
            "visit_date",
            "Select Visit Date",
            get_current_step_content,
            min_date=datetime.now() - timedelta(days=3650),
            max_date=datetime.now() + timedelta(days=3650)
        )
    )
    visit_date_field = ft.Row(
        [visit_date_textfield_control, visit_date_icon_button],
        spacing=5,
        alignment=ft.MainAxisAlignment.START
    )

    # Main container for the patients tab
    container = ft.Container(
        expand=True,
        bgcolor=HR_SECONDARY,
        content=ft.Column([], spacing=0)
    )
    
    # Add header
    container.content.controls.append(create_header("Patients", user))
    
    # Create a container for the main content
    content_container = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=15, vertical=10),  # Reduced vertical padding
        content=ft.Column(spacing=0)  # No spacing between elements
    )
    container.content.controls.append(content_container)
    
    # Get patients from database
    patients = get_all_patients()
    
    # Get verified doctors from database
    verified_doctors = [d for d in get_all_doctors() if d.get('is_verified', False)]
    doctors = [
        {"id": d['user_id'], "name": f"Dr. {d['first_name']} {d['last_name']}", "department": f"Department (ID: {d['user_id']})"}
        for d in verified_doctors
    ]

    # Define status colors with opacity using Flet's color format
    status_colors = {
        "Scheduled": "#0000FF1A",  # Blue with 10% opacity
        "Pending": "#FFA5001A",  # Orange with 10% opacity
        "Completed": "#0080001A",  # Green with 10% opacity
        "Cancelled": "#FF00001A",  # Red with 10% opacity
        "No Show": "#8080801A",  # Grey with 10% opacity
    }

    # Modal dialogs
    add_patient_modal = ft.Ref[ft.Container]()
    patient_details_modal = ft.Ref[ft.Container]()
    edit_patient_modal = ft.Ref[ft.Container]()
    delete_confirm_modal = ft.Ref[ft.Container]()
    filter_modal = ft.Ref[ft.Container]()

    # Filter state
    filter_state = {
        "status": None,
        "doctor": None,
        "consultation_type": None
    }

    def apply_filters():
        # Get all patients
        all_patients = get_all_patients()
        
        # Apply search filter
        search_term = search_field.value.lower() if search_field.value else ""
        filtered_patients = [
            p for p in all_patients
            if (search_term in p['full_name'].lower() or 
                search_term in p['last_name'].lower() or 
                search_term in str(p['id']).lower() or
                search_term in p.get('phone', '').lower())
        ]
        
        # Apply status filter
        if filter_state["status"]:
            filtered_patients = [
                p for p in filtered_patients
                if p['status'] == filter_state["status"]
            ]
            
        # Apply doctor filter
        if filter_state["doctor"]:
            filtered_patients = [
                p for p in filtered_patients
                if p.get('doctor_id') == filter_state["doctor"]
            ]
            
        # Apply consultation type filter
        if filter_state["consultation_type"]:
            filtered_patients = [
                p for p in filtered_patients
                if p.get('consultation_type') == filter_state["consultation_type"]
            ]
            
        # Update the grid
        patients_grid.controls = [create_patient_card(p) for p in filtered_patients]
        page.update()

    def show_filter_modal(e):
        # Create filter modal content
        filter_content = ft.Container(
            width=400,
            height=400,
            bgcolor=HR_WHITE,
            border_radius=10,
            padding=20,
            content=ft.Column([
                ft.Text("Filter Patients", size=20, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                ft.Container(height=20),
                # Status filter
                ft.Dropdown(
                    label="Status",
                    value=filter_state["status"],
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("Scheduled"),
                        ft.dropdown.Option("Pending"),
                        ft.dropdown.Option("Completed"),
                        ft.dropdown.Option("Cancelled"),
                        ft.dropdown.Option("No Show"),
                    ],
                    width=360,
                    border_color=HR_BORDER,
                    focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    on_change=lambda e: filter_state.update({"status": e.control.value if e.control.value != "All" else None})
                ),
                ft.Container(height=10),
                # Doctor filter
                ft.Dropdown(
                    label="Doctor",
                    value=filter_state["doctor"],
                    options=[
                        ft.dropdown.Option("All"),
                        *[ft.dropdown.Option(d["id"], d["name"]) for d in doctors]
                    ],
                    width=360,
                    border_color=HR_BORDER,
                    focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    on_change=lambda e: filter_state.update({"doctor": e.control.value if e.control.value != "All" else None})
                ),
                ft.Container(height=10),
                # Consultation type filter
                ft.Dropdown(
                    label="Consultation Type",
                    value=filter_state["consultation_type"],
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("General Checkup"),
                        ft.dropdown.Option("Follow-up"),
                        ft.dropdown.Option("Emergency"),
                        ft.dropdown.Option("Specialist Consultation"),
                        ft.dropdown.Option("Lab Test"),
                        ft.dropdown.Option("Vaccination"),
                        ft.dropdown.Option("Other"),
                    ],
                    width=360,
                    border_color=HR_BORDER,
                    focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    on_change=lambda e: filter_state.update({"consultation_type": e.control.value if e.control.value != "All" else None})
                ),
                ft.Container(height=20),
                # Action buttons
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Apply Filters",
                            style=ft.ButtonStyle(
                                color=HR_WHITE,
                                bgcolor=HR_PRIMARY,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            on_click=lambda e: (setattr(filter_modal.current, "visible", False), apply_filters())
                        ),
                        ft.Container(width=10),
                        ft.OutlinedButton(
                            "Clear Filters",
                            style=ft.ButtonStyle(
                                color=HR_PRIMARY,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            on_click=lambda e: (
                                filter_state.update({"status": None, "doctor": None, "consultation_type": None}),
                                setattr(filter_modal.current, "visible", False),
                                apply_filters()
                            )
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, HR_TEXT),
                offset=ft.Offset(0, 3),
            ),
        )
        
        filter_modal.current.content = filter_content
        filter_modal.current.visible = True
        page.update()

    def close_patient_details_modal():
        patient_details_modal.current.visible = False
        page.update()

    def extract_display_value(x):
        if isinstance(x, dict):
            return x.get("name") or x.get("value") or str(x)
        return str(x)

    def show_patient_details(patient):
        # Get doctor and consultation info
        doctor_info = patient.get('doctor_name', 'Awaiting Doctor Assignment')
        consultation_info = f"{patient.get('visit_type', 'N/A')} - {patient.get('visit_date', 'No date set')}"

        # Create a two-column layout for better organization
        left_column = ft.Column([
            # Basic Information Section
                ft.Container(
                content=ft.Column([
                    ft.Text("Basic Information", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Divider(color=HR_BORDER),
                            ft.Row([
                                ft.Column([
                            ft.Row([ft.Icon(ft.Icons.PERSON, size=16, color=HR_TEXT), 
                                   ft.Text(f"Name: {patient.get('full_name', 'N/A')}", size=14, color=HR_TEXT)], spacing=8),
                            ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=HR_TEXT), 
                                   ft.Text(f"Birthdate: {patient.get('birthdate', 'N/A')}", size=14, color=HR_TEXT)], spacing=8),
                            ft.Row([ft.Icon(ft.Icons.PHONE, size=16, color=HR_TEXT), 
                                   ft.Text(f"Phone: {patient.get('phone', 'N/A')}", size=14, color=HR_TEXT)], spacing=8),
                        ], spacing=4),
                                ft.Column([
                            ft.Row([ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color=HR_TEXT), 
                                   ft.Text(f"Gender: {patient.get('gender', 'N/A')}", size=14, color=HR_TEXT)], spacing=8),
                            ft.Row([ft.Icon(ft.Icons.FAMILY_RESTROOM, size=16, color=HR_TEXT), 
                                   ft.Text(f"Civil Status: {patient.get('civil_status', 'N/A')}", size=14, color=HR_TEXT)], spacing=8),
                            ft.Row([ft.Icon(ft.Icons.LOCATION_ON, size=16, color=HR_TEXT), 
                                   ft.Text(f"Address: {patient.get('address', 'N/A')}", size=14, color=HR_TEXT)], spacing=8),
                        ], spacing=4),
                    ], spacing=20),
                                ], spacing=8),
                padding=10,
                bgcolor=HR_WHITE,
                border_radius=8,
            ),

            # Emergency Contact Section
            ft.Container(
                content=ft.Column([
                            ft.Text("Emergency Contact", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Divider(color=HR_BORDER),
                                ft.Row([
                        ft.Icon(ft.Icons.EMERGENCY, size=16, color=HR_TEXT),
                        ft.Column([
                            ft.Text(f"Name: {patient.get('emergency_contact_name', 'N/A')}", size=14, color=HR_TEXT),
                            ft.Text(f"Phone: {patient.get('emergency_contact_phone', 'N/A')}", size=14, color=HR_TEXT),
                        ], spacing=4),
                                ], spacing=8),
                                ], spacing=8),
                padding=10,
                bgcolor=HR_WHITE,
                border_radius=8,
            ),

            # Medical Information Section
            ft.Container(
                content=ft.Column([
                            ft.Text("Medical Information", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Divider(color=HR_BORDER),
                    ft.Row([
                            ft.Column([
                            ft.Row([ft.Icon(ft.Icons.WARNING, size=16, color=HR_TEXT), 
                                   ft.Text("Allergies:", size=14, color=HR_TEXT, weight=ft.FontWeight.BOLD)], spacing=8),
                            ft.Text(", ".join(filter_words_only(patient.get('allergies', []))) or "None", size=14, color=HR_TEXT),
                        ], spacing=4),
                        ft.Column([
                            ft.Row([ft.Icon(ft.Icons.MEDICAL_SERVICES, size=16, color=HR_TEXT), 
                                   ft.Text("Chronic Illnesses:", size=14, color=HR_TEXT, weight=ft.FontWeight.BOLD)], spacing=8),
                            ft.Text(", ".join(filter_words_only(patient.get('chronic_illnesses', []))) or "None", size=14, color=HR_TEXT),
                        ], spacing=4),
                    ], spacing=20),
                                ft.Row([
                                    ft.Icon(ft.Icons.MEDICATION, size=16, color=HR_TEXT),
                        ft.Text("Current Medications:", size=14, color=HR_TEXT, weight=ft.FontWeight.BOLD),
                                ], spacing=8),
                    ft.Text(", ".join(filter_words_only(patient.get('current_medications', []))) or "None", size=14, color=HR_TEXT),
                            ], spacing=8),
                padding=10,
                bgcolor=HR_WHITE,
                border_radius=8,
            ),
        ], spacing=10)

        right_column = ft.Column([
            # Visit Information Section
            ft.Container(
                content=ft.Column([
                    ft.Text("Visit Information", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Divider(color=HR_BORDER),
                                ft.Row([
                                    ft.Icon(ft.Icons.MEDICAL_SERVICES, size=16, color=HR_TEXT),
                                    ft.Text(doctor_info, size=14, color=HR_TEXT),
                                ], spacing=8),
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=HR_TEXT),
                                    ft.Text(consultation_info, size=14, color=HR_TEXT),
                                ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.BUSINESS, size=16, color=HR_TEXT),
                        ft.Text(f"Insurance: {patient.get('insurance_provider', 'N/A')}", size=14, color=HR_TEXT),
                            ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.SOURCE, size=16, color=HR_TEXT),
                        ft.Text(f"Referral: {patient.get('referral_source', 'N/A')}", size=14, color=HR_TEXT),
                    ], spacing=8),
                ], spacing=8),
                padding=10,
                bgcolor=HR_WHITE,
                border_radius=8,
            ),

            # Status and Registration Section
            ft.Container(
                content=ft.Column([
                    ft.Text("Status & Registration", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Divider(color=HR_BORDER),
                    ft.Row([
                        ft.Icon(ft.Icons.INFO, size=16, color=HR_TEXT),
                        ft.Text(f"Status: {patient.get('status', 'N/A')}", size=14, color=HR_TEXT),
                    ], spacing=8),
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_MONTH, size=16, color=HR_TEXT),
                                ft.Text(
                            f"Registration Date: {patient.get('created_at', 'N/A').strftime('%B %d, %Y') if isinstance(patient.get('created_at'), datetime) else patient.get('created_at', 'N/A')}",
                                    size=14,
                                    color=HR_TEXT
                                ),
                            ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.BADGE, size=16, color=HR_TEXT),
                        ft.Text(f"Patient ID: {patient.get('patient_code', 'N/A')}", size=14, color=HR_TEXT),
                    ], spacing=8),
                ], spacing=8),
                padding=10,
                bgcolor=HR_WHITE,
                border_radius=8,
            ),

            # Additional Notes Section
                ft.Container(
                content=ft.Column([
                    ft.Text("Additional Notes", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Divider(color=HR_BORDER),
                    ft.Text(patient.get('remarks', 'No additional notes'), size=14, color=HR_TEXT),
                ], spacing=8),
                padding=10,
                bgcolor=HR_WHITE,
                border_radius=8,
            ),
        ], spacing=10)

        # Main container with two columns
        details_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Patient Details", size=20, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=HR_TEXT,
                        on_click=lambda e: close_patient_details_modal()
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=HR_BORDER),
                ft.Row([
                    left_column,
                    right_column,
                ], spacing=20),
            ], spacing=15),
            padding=20,
            bgcolor=HR_SECONDARY,
            border_radius=10,
            width=850,
            height=600,
        )
        patient_details_modal.current.content = details_container
        patient_details_modal.current.visible = True
        page.update()

    def refresh_patients():
        patients = get_all_patients()
        patients_grid.controls = [create_patient_card(p) for p in patients]
        page.update()

    def handle_delete_patient(patient_id):
        def confirm_delete(e):
            try:
                # Delete patient from database
                success, message = delete_patient(patient_id)
                if success:
                    delete_confirm_modal.current.visible = False
                    refresh_patients()
                else:
                    error_text.value = message
                    error_text.visible = True
                page.update()
            except Exception as e:
                error_text.value = f"Error: {str(e)}"
                error_text.visible = True
                page.update()

        # Create confirmation dialog
        dialog_content = ft.Container(
            width=400,
            height=200,
            bgcolor=HR_WHITE,
            border_radius=10,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Confirm Delete", size=20, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Container(height=20),
                    ft.Text("Are you sure you want to delete this patient?", color=HR_TEXT),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Delete",
                                style=ft.ButtonStyle(color=HR_WHITE, bgcolor=HR_ERROR),
                                on_click=confirm_delete
                            ),
                            ft.Container(width=20),
                            ft.OutlinedButton(
                                "Cancel",
                                style=ft.ButtonStyle(color=HR_PRIMARY),
                                on_click=lambda e: (setattr(delete_confirm_modal.current, "visible", False), page.update())
                            ),
                        ],
                    ),
                ],
            ),
        )
        delete_confirm_modal.current.content = dialog_content
        delete_confirm_modal.current.visible = True
        page.update()

    def handle_edit_patient(patient):
        # Create edit form fields with current values
        edit_form_state = {
            "full_name": patient.get("full_name", ""),
            "phone": patient.get("phone", ""),
            "age": str(patient.get("age", "")),
            "gender": patient.get("gender", ""),
            "address": patient.get("address", ""),
            "status": patient.get("status", "Pending"),
            "doctor_id": patient.get("doctor_id", ""),
            "consultation_type": patient.get("consultation_type", ""),
            "allergies": patient.get("allergies", []),
            "chronic_illnesses": patient.get("chronic_illnesses", []),
            "current_medications": patient.get("current_medications", []),
        }

        # Create edit form fields
        edit_first_name = ft.TextField(
            label="Full Name",
            value=edit_form_state["full_name"],
            width=250,
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"full_name": e.control.value})
        )
        edit_last_name = ft.TextField(
            label="Last Name",
            value=edit_form_state["last_name"],
            width=250,
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"last_name": e.control.value})
        )
        edit_phone = ft.TextField(
            label="Phone Number",
            value=edit_form_state["phone"],
            width=520,
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"phone": e.control.value})
        )
        edit_age = ft.TextField(
            label="Age",
            value=edit_form_state["age"],
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"age": e.control.value})
        )
        edit_gender = ft.Dropdown(
            label="Gender",
            value=edit_form_state["gender"],
            width=120,
            options=[
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Other")
            ],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"gender": e.control.value})
        )
        edit_status = ft.Dropdown(
            label="Status",
            value=edit_form_state["status"],
            width=120,
            options=[
                ft.dropdown.Option("Scheduled"),
                ft.dropdown.Option("Pending"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("Cancelled"),
                ft.dropdown.Option("No Show"),
            ],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"status": e.control.value})
        )
        edit_doctor = ft.Dropdown(
            label="Doctor",
            value=edit_form_state["doctor_id"],
            width=250,
            options=[ft.dropdown.Option(d["id"], d["name"]) for d in doctors],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"doctor_id": e.control.value})
        )
        edit_consultation = ft.Dropdown(
            label="Consultation Type",
            value=edit_form_state["consultation_type"],
            width=250,
            options=[
                ft.dropdown.Option("General Checkup"),
                ft.dropdown.Option("Follow-up"),
                ft.dropdown.Option("Emergency"),
                ft.dropdown.Option("Specialist Consultation"),
                ft.dropdown.Option("Lab Test"),
                ft.dropdown.Option("Vaccination"),
                ft.dropdown.Option("Other"),
            ],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"consultation_type": e.control.value})
        )
        edit_address = ft.TextField(
            label="Address",
            value=edit_form_state["address"],
            width=520,
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            text_style=ft.TextStyle(color=HR_TEXT),
            label_style=ft.TextStyle(color=HR_TEXT),
            on_change=lambda e: edit_form_state.update({"address": e.control.value})
        )

        def handle_edit_submit(e):
            try:
                # Convert age to integer
                age = int(edit_form_state["age"])
                
                # Update patient in database
                success, message = update_patient(
                    patient_id=patient["id"],
                    full_name=edit_form_state["full_name"],
                    last_name=edit_form_state["last_name"],
                    age=age,
                    gender=edit_form_state["gender"],
                    phone=edit_form_state["phone"],
                    address=edit_form_state["address"],
                    status=edit_form_state["status"],
                    doctor_id=edit_form_state["doctor_id"],
                    consultation_type=edit_form_state["consultation_type"]
                )
                
                if success:
                    edit_patient_modal.current.visible = False
                    refresh_patients()
                else:
                    error_text.value = message
                    error_text.visible = True
                page.update()
                
            except ValueError:
                error_text.value = "Please enter a valid age."
                error_text.visible = True
                page.update()
            except Exception as e:
                error_text.value = f"Error: {str(e)}"
                error_text.visible = True
                page.update()

        # Create edit modal content
        edit_modal_content = ft.Container(
            width=600,
            height=650,
            bgcolor=HR_WHITE,
            border_radius=10,
            padding=30,
            content=ft.Column([
                # Header Section
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        controls=[
                            ft.Text(
                                "Edit Patient",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=HR_TEXT,
                            ),
                            ft.Text(
                                f"ID: {patient['id']}",
                                size=14,
                                color=HR_TEXT,
                            ),
                        ],
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # Form Fields Section
                ft.Container(
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            # Name Fields Row
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=edit_first_name,
                                        expand=1,
                                    ),
                                    ft.Container(width=10),
                                    ft.Container(
                                        content=edit_last_name,
                                        expand=1,
                                    ),
                                ],
                            ),
                            # Contact Information
                            ft.Container(
                                content=edit_phone,
                                width=520,
                            ),
                            # Personal Information Row
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=edit_age,
                                        expand=1,
                                    ),
                                    ft.Container(width=10),
                                    ft.Container(
                                        content=edit_gender,
                                        expand=1,
                                    ),
                                    ft.Container(width=10),
                                    ft.Container(
                                        content=edit_status,
                                        expand=1,
                                    ),
                                ],
                            ),
                            # Doctor and Consultation Row
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=edit_doctor,
                                        expand=1,
                                    ),
                                    ft.Container(width=10),
                                    ft.Container(
                                        content=edit_consultation,
                                        expand=1,
                                    ),
                                ],
                            ),
                            # Address
                            ft.Container(
                                content=edit_address,
                                width=520,
                            ),
                        ],
                    ),
                    width=520,
                ),
                # Messages Section
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        controls=[error_text],
                    ),
                    padding=ft.padding.symmetric(vertical=10),
                ),
                # Buttons Section
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "Back",
                                style=ft.ButtonStyle(
                                    color=HR_PRIMARY,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                ),
                                width=120,
                                on_click=lambda e: (setattr(edit_patient_modal.current, "visible", False), page.update())
                            ),
                            ft.Container(width=10),
                            ft.ElevatedButton(
                                "Save Changes",
                                style=ft.ButtonStyle(
                                    color=HR_WHITE,
                                    bgcolor=HR_PRIMARY,
                                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                ),
                                width=160,
                                on_click=handle_edit_submit
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(top=10),
                ),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, HR_TEXT),
                offset=ft.Offset(0, 3),
            ),
        )

        edit_patient_modal.current.content = edit_modal_content
        edit_patient_modal.current.visible = True
        page.update()

    def filter_words_only(items):
        if not items:
            return []
        if isinstance(items, str):
            # Split the string by commas and clean each item
            items = [x.strip() for x in items.split(',') if x.strip()]
        return [str(x) for x in items if isinstance(x, (str, int)) and (isinstance(x, str) and not x.isdigit() or isinstance(x, int))]

    def create_patient_card(patient):
        # Define status colors
        status_color = status_colors.get(patient.get('status', 'Pending'), HR_GRAY)
        
        # Get doctor and consultation info with fallbacks
        doctor_info = patient.get('doctor_name', 'Awaiting Doctor Assignment')
        consultation_info = patient.get('consultation_type', 'To be determined by doctor')
        
        # Create avatar content based on photo availability
        avatar_content = (
            ft.Container(
                content=ft.Image(
                    src=patient.get('photo_path'),
                    width=60,
                    height=60,
                    fit=ft.ImageFit.COVER,
                ),
                border_radius=30,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                border=ft.border.all(2, HR_PRIMARY),
            ) if patient.get('photo_path') else ft.Text(patient.get('full_name', 'P')[0].upper(), size=24)
        )
        
        # Prepare chronic illnesses and allergies display (filter out numbers)
        chronic_illnesses = ', '.join(filter_words_only(patient.get('chronic_illnesses', ''))) or "None"
        allergies = ', '.join(filter_words_only(patient.get('allergies', ''))) or "None"
        current_medications = ', '.join(filter_words_only(patient.get('current_medications', ''))) or "None"
        
        # Calculate age from birthdate if available
        def calculate_age_from_birthdate(birthdate_str):
            try:
                # Try parsing in common formats
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        birthdate = datetime.strptime(birthdate_str, fmt)
                        break
                    except Exception:
                        continue
                else:
                    return None
                today = datetime.today()
                return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            except Exception:
                return None
        birthdate_str = patient.get('birthdate')
        age = None
        if birthdate_str:
            age = calculate_age_from_birthdate(birthdate_str)
        if age is None:
            age = patient.get('age', 'N/A')
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header with avatar and status
                    ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=avatar_content,
                                radius=25,
                                bgcolor=HR_PRIMARY,
                                color=HR_WHITE,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    patient.get('status', 'Pending'),
                                    color=HR_WHITE,
                                    size=10,
                                    weight=ft.FontWeight.W_500,
                                ),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=12,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Patient's name and ID
                    ft.Text(
                        f"{patient.get('full_name', 'Unknown Patient')}", 
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=HR_TEXT,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        width=250,
                    ),
                    ft.Text(
                        f"ID: {str(patient.get('id', 'N/A')).zfill(4)}", 
                        size=12,
                        color=HR_TEXT,
                    ),
                    # Patient information
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.PHONE, size=14, color=HR_TEXT),
                                        ft.Text(patient.get("phone", "No phone"), size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.PERSON, size=14, color=HR_TEXT),
                                        ft.Text(f"{age} years, {patient.get('gender', 'Not specified')}", size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.MEDICAL_SERVICES, size=14, color=HR_TEXT),
                                        ft.Text(doctor_info, size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=HR_TEXT),
                                        ft.Text(consultation_info, size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.WARNING, size=14, color=HR_TEXT),
                                        ft.Text(f"Allergies: {allergies}", size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.MEDICAL_SERVICES, size=14, color=HR_TEXT),
                                        ft.Text(f"Chronic Illnesses: {chronic_illnesses}", size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.MEDICATION, size=14, color=HR_TEXT),
                                        ft.Text(f"Medications: {current_medications}", size=12, color=HR_TEXT, max_lines=1, width=200, overflow=ft.TextOverflow.ELLIPSIS),
                                    ],
                                    spacing=6,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=ft.padding.only(top=8),
                    ),
                    # Action buttons
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "View Details",
                                    icon=ft.Icons.VISIBILITY_OUTLINED,
                                    style=ft.ButtonStyle(
                                        bgcolor=HR_WHITE,
                                        color=HR_PRIMARY,
                                        side=ft.border.all(1, HR_PRIMARY),
                                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                    ),
                                    on_click=lambda e, p=patient: show_patient_details(p),
                                    height=36,
                                ),
                                ft.Container(expand=True),  # Spacer
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=18,
                                    icon_color=HR_INFO,
                                    tooltip="Edit",
                                    on_click=lambda e, p=patient: handle_edit_patient(p),
                                    style=ft.ButtonStyle(
                                        side=ft.border.all(1, HR_BORDER),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                    ),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=18,
                                    icon_color=HR_ERROR,
                                    tooltip="Delete",
                                    on_click=lambda e, p=patient: handle_delete_patient(p.get('id')),
                                    style=ft.ButtonStyle(
                                        side=ft.border.all(1, HR_BORDER),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=6,
                        ),
                        padding=ft.padding.only(top=8),
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            bgcolor=HR_WHITE,
            border_radius=8,
            width=280,
            border=ft.border.all(1, HR_BORDER),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, HR_TEXT),
                offset=ft.Offset(0, 2),
            ),
        )

    # State for fields
    patient_form_state = {
        # Basic Information
        "full_name": "",
        "birthdate": "",
        "visit_date": "",
        "gender": "Male",
        "civil_status": "Single",
        "phone": "",
        "address": "",
        "emergency_contact_name": "",
        "emergency_contact_relation": "",
        "emergency_contact_phone": "",
        "blood_type": "",
        
        # Medical Information
        "allergies": "",
        "medical_conditions": "",
        "current_medications": "",
        "family_history": [],
        "surgical_history": [],
        "social_history": [],
        "chief_complaint": "",
        "history_of_present_illness": "",
        "review_of_systems": "",
        "vital_signs": {
            "blood_pressure": "",
            "heart_rate": "",
            "respiratory_rate": "",
            "temperature": "",
            "oxygen_saturation": "",
            "height": "",
            "weight": "",
            "bmi": ""
        },
        "physical_exam": "",
        "assessment": "",
        "plan": "",
        "prescriptions": [],
        "follow_up_instructions": "",
        "referrals": [],
        
        # Visit & Admin Info
        "status": "Scheduled",
        "assigned_doctor": "",
        "visit_type": "New Patient",
        "insurance_provider": "",
        "referral_source": "",
        "remarks": ""
    }

    # Error text for validation
    error_text = ft.Text("", color=HR_ERROR, visible=False)

    # Create stepper state
    current_step = ft.Ref[int]()
    current_step.current = 0

    # Widget fields (define before get_current_step_content)
    gender_field = ft.Dropdown(
        label="Gender",
        value=patient_form_state["gender"],
        width=140,
        options=[
            ft.dropdown.Option("Male"),
            ft.dropdown.Option("Female"),
            ft.dropdown.Option("Other")
        ],
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        label_style=ft.TextStyle(color=HR_TEXT),
        on_change=lambda e: patient_form_state.update({"gender": e.control.value})
    )
    status_field = ft.Dropdown(
        label="Status",
        value=patient_form_state.get("status", "Pending"),
        width=150,
        options=[
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Scheduled"),
            ft.dropdown.Option("Completed"),
            ft.dropdown.Option("Cancelled"),
            ft.dropdown.Option("No Show"),
        ],
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        label_style=ft.TextStyle(color=HR_TEXT),
        on_change=lambda e: patient_form_state.update({"status": e.control.value})
    )
    doctor_field = ft.Dropdown(
        label="Assigned Doctor",
        value=patient_form_state.get("assigned_doctor", ""),
        width=250,
        options=[ft.dropdown.Option(d["id"], d["name"]) for d in doctors],
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        label_style=ft.TextStyle(color=HR_TEXT),
        on_change=lambda e: patient_form_state.update({"assigned_doctor": e.control.value})
    )
    visit_type_field = ft.Dropdown(
        label="Visit Type",
        value=patient_form_state.get("visit_type", "New Patient"),
        width=250,
        options=[
            ft.dropdown.Option("New Patient"),
            ft.dropdown.Option("Follow-up"),
            ft.dropdown.Option("Walk-in"),
        ],
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        label_style=ft.TextStyle(color=HR_TEXT),
        on_change=lambda e: patient_form_state.update({"visit_type": e.control.value})
    )
    photo_avatar = ft.CircleAvatar(
        content=ft.Text("", size=24),
        radius=30,
        bgcolor=HR_PRIMARY,
        color=HR_WHITE,
    )

    # File picker and upload handler
    def handle_photo_upload(e):
        if e.files:
            file = e.files[0]
            patient_form_state["photo"] = file
            photo_avatar.content = ft.Image(
                src=file.path,
                width=60,
                height=60,
                fit=ft.ImageFit.COVER,
                border_radius=30,
            )
            page.update()

    file_picker = ft.FilePicker(
        on_result=handle_photo_upload
    )
    page.overlay.append(file_picker)

    photo_upload = ft.ElevatedButton(
        "Upload Photo",
        icon=ft.Icons.UPLOAD_FILE,
        style=ft.ButtonStyle(
            color=HR_WHITE,
            bgcolor=HR_PRIMARY,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
        on_click=lambda e: file_picker.pick_files()
    )

    def create_stepper():
        def handle_step_click(step):
            if step <= current_step.current + 1:  # Allow clicking current or next step
                current_step.current = step
                add_patient_modal.current.content.content.controls[2].content = get_current_step_content()
                page.update()
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.IconButton(
                            icon=ft.Icons.PERSON_OUTLINE,
                            icon_color=HR_PRIMARY if current_step.current >= 0 else HR_GRAY,
                            icon_size=24,
                            on_click=lambda e: handle_step_click(0)
                        ),
                        ft.TextButton(
                            text="Basic Details",
                            style=ft.ButtonStyle(
                                color=HR_PRIMARY if current_step.current >= 0 else HR_GRAY,
                            ),
                            on_click=lambda e: handle_step_click(0)
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    width=100,
                ),
                ft.Container(
                    content=ft.Container(
                        bgcolor=HR_PRIMARY if current_step.current >= 1 else HR_GRAY,
                        height=2,
                        width=50,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.IconButton(
                            icon=ft.Icons.DESCRIPTION_OUTLINED,
                            icon_color=HR_PRIMARY if current_step.current >= 1 else HR_GRAY,
                            icon_size=24,
                            on_click=lambda e: handle_step_click(1)
                        ),
                        ft.TextButton(
                            text="Visit Info",
                            style=ft.ButtonStyle(
                                color=HR_PRIMARY if current_step.current >= 1 else HR_GRAY,
                            ),
                            on_click=lambda e: handle_step_click(1)
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    width=100,
                ),
                ft.Container(
                    content=ft.Container(
                        bgcolor=HR_PRIMARY if current_step.current >= 2 else HR_GRAY,
                        height=2,
                        width=50,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.IconButton(
                            ft.Icons.INFO_OUTLINE,
                            icon_color=HR_PRIMARY if current_step.current >= 2 else HR_GRAY,
                            icon_size=24,
                            on_click=lambda e: handle_step_click(2)
                        ),
                        ft.TextButton(
                            text="Pre-Medical",
                            style=ft.ButtonStyle(
                                color=HR_PRIMARY if current_step.current >= 2 else HR_GRAY,
                            ),
                            on_click=lambda e: handle_step_click(2)
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    width=100,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.only(bottom=20),
    )

    def get_current_step_content():
        # Step 1: Basic Details
        if current_step.current == 0:
            def _create_birthdate_row_for_step_content():
                gcs_birthdate_tf = ft.TextField(
                    label="Birthdate",
                    value=patient_form_state.get("birthdate", ""),
                    width=470, # Adjusted for icon
                    border_color=HR_BORDER,
                    focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    read_only=True
                )
                gcs_birthdate_icon = ft.IconButton(
                    ft.Icons.CALENDAR_MONTH,
                    tooltip="Select Birthdate",
                    on_click=lambda e, tf_control=gcs_birthdate_tf: show_date_picker_dialog(
                        page,
                        tf_control,
                        patient_form_state,
                        "birthdate",
                        "Select Birthdate",
                        get_current_step_content,
                        min_date=datetime.now() - timedelta(days=365*100),
                        max_date=datetime.now()
                    )
                )
                return ft.Row(
                    [gcs_birthdate_tf, gcs_birthdate_icon],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=5
                )
            return ft.Column([
                # Photo upload and avatar at the top
                ft.Row([
                    photo_avatar,
                    ft.Container(width=10),
                    photo_upload
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                # Full Name
                ft.Row([
                    ft.TextField(
                        label="Full Name",
                        value=patient_form_state["full_name"],
                        width=520,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        text_style=ft.TextStyle(color=HR_TEXT),
                        label_style=ft.TextStyle(color=HR_TEXT),
                        on_change=lambda e: patient_form_state.update({"full_name": e.control.value})
                    ),
                ]),
                # Birthdate
                _create_birthdate_row_for_step_content(),
                # Gender and Civil Status
                ft.Row([
                    ft.Dropdown(
                        label="Gender",
                        value=patient_form_state["gender"],
                        options=[
                            ft.dropdown.Option("Male"),
                            ft.dropdown.Option("Female"),
                            ft.dropdown.Option("Other"),
                            ft.dropdown.Option("Prefer not to say")
                        ],
                        width=250,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        on_change=lambda e: patient_form_state.update({"gender": e.control.value})
                    ),
                    ft.Container(width=10),
                    ft.Dropdown(
                        label="Civil Status",
                        value=patient_form_state["civil_status"],
                        options=[
                            ft.dropdown.Option("Single"),
                            ft.dropdown.Option("Married"),
                            ft.dropdown.Option("Separated"),
                            ft.dropdown.Option("Divorced"),
                            ft.dropdown.Option("Widowed"),
                            ft.dropdown.Option("Other")
                        ],
                        width=250,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        on_change=lambda e: patient_form_state.update({"civil_status": e.control.value})
                    ),
                ]),
                # Contact Information
                ft.Row([
                    ft.TextField(
                        label="Contact Number",
                        value=patient_form_state["phone"],
                        width=520,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        text_style=ft.TextStyle(color=HR_TEXT),
                        label_style=ft.TextStyle(color=HR_TEXT),
                        on_change=lambda e: patient_form_state.update({"phone": e.control.value})
                    ),
                ]),
                # Address
                ft.Row([
                    ft.TextField(
                        label="Address",
                        value=patient_form_state["address"],
                        width=520,
                        multiline=True,
                        min_lines=2,
                        max_lines=3,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        text_style=ft.TextStyle(color=HR_TEXT),
                        label_style=ft.TextStyle(color=HR_TEXT),
                        on_change=lambda e: patient_form_state.update({"address": e.control.value})
                    ),
                ]),
            ], spacing=15)
        # Step 2: Visit & Admin Info
        elif current_step.current == 1:
            visit_date_field = ft.Ref[ft.TextField]()
            def update_visit_date(e=None):
                if e is not None and hasattr(e, 'control') and hasattr(e.control, 'value'):
                    patient_form_state["visit_date"] = e.control.value
                elif visit_date_field.current is not None:
                    visit_date_field.current.value = patient_form_state.get("visit_date", "")
            return ft.Column([
                # Visit Type
                ft.Row([
                    ft.Column([
                        ft.Text("Visit Type", size=14, color=HR_TEXT, weight=ft.FontWeight.BOLD),
                        ft.RadioGroup(
                            content=ft.Column([
                                ft.Radio(
                                    value="New Patient",
                                    label="New Patient",
                                    fill_color=HR_PRIMARY,
                                    active_color=HR_PRIMARY,
                                ),
                                ft.Radio(
                                    value="Follow-up",
                                    label="Follow-up",
                                    fill_color=HR_PRIMARY,
                                    active_color=HR_PRIMARY,
                                ),
                                ft.Radio(
                                    value="Walk-in",
                                    label="Walk-in",
                                    fill_color=HR_PRIMARY,
                                    active_color=HR_PRIMARY,
                                )
                            ], spacing=5),
                            value=patient_form_state["visit_type"],
                            on_change=lambda e: patient_form_state.update({"visit_type": e.control.value})
                        )
                    ], spacing=5)
                ]),
                # Assigned Doctor
                ft.Row([
                    ft.Dropdown(
                        label="Assigned Doctor",
                        value=patient_form_state["assigned_doctor"],
                        options=[
                            ft.dropdown.Option(d["id"], d["name"]) for d in doctors
                        ],
                        width=520,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        on_change=lambda e: patient_form_state.update({"assigned_doctor": e.control.value})
                    ),
                ]),
                # Visit Date and Time
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.TextField(
                                ref=visit_date_field,
                                key="visit_date_field",
                                label="Visit Date",
                                value=patient_form_state.get("visit_date", ""),
                                width=250,
                                border_color=HR_BORDER,
                                focused_border_color=HR_PRIMARY,
                                text_style=ft.TextStyle(color=HR_TEXT),
                                label_style=ft.TextStyle(color=HR_TEXT),
                                read_only=True,
                                on_change=update_visit_date,
                                on_focus=lambda e: show_date_picker_dialog(
                                    page,
                                    visit_date_field.current,
                                    patient_form_state,
                                    "visit_date",
                                    "Select Visit Date",
                                    get_current_step_content,
                                    min_date=datetime.now()
                                )
                            ),
                            ft.IconButton(
                                ft.Icons.CALENDAR_MONTH,
                                tooltip="Select Visit Date",
                                on_click=lambda e: show_date_picker_dialog(
                                    page,
                                    visit_date_field.current,
                                    patient_form_state,
                                    "visit_date",
                                    "Select Visit Date",
                                    get_current_step_content,
                                    min_date=datetime.now()
                                )
                            ),
                        ]),
                        key="visit_date_container"
                    ),
                    ft.Container(width=10),
                    ft.TextField(
                        label="Visit Time",
                        value="",
                        width=200,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        text_style=ft.TextStyle(color=HR_TEXT),
                        label_style=ft.TextStyle(color=HR_TEXT)
                    ),
                ]),
                # Optional Fields
                ft.Row([
                    ft.TextField(
                        label="Insurance Provider",
                        value=patient_form_state["insurance_provider"],
                        width=250,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        text_style=ft.TextStyle(color=HR_TEXT),
                        label_style=ft.TextStyle(color=HR_TEXT),
                        on_change=lambda e: patient_form_state.update({"insurance_provider": e.control.value})
                    ),
                    ft.Container(width=10),
                    ft.Dropdown(
                        label="Referral Source",
                        value=patient_form_state["referral_source"],
                        options=[
                            ft.dropdown.Option("Walk-in"),
                            ft.dropdown.Option("Friend"),
                            ft.dropdown.Option("Facebook"),
                            ft.dropdown.Option("Other")
                        ],
                        width=250,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                        on_change=lambda e: patient_form_state.update({"referral_source": e.control.value})
                    ),
                ]),
            ], spacing=15)
        # Step 3: Pre-Medical Info
        elif current_step.current == 2:
            # Allergies
            allergies_field = ft.TextField(
                label="Allergies (comma-separated or one per line)",
                value=patient_form_state.get("allergies", ""),
                width=520,
                multiline=True,
                min_lines=2,
                max_lines=4,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                text_style=ft.TextStyle(color=HR_TEXT),
                label_style=ft.TextStyle(color=HR_TEXT),
                on_change=lambda e: patient_form_state.update({"allergies": e.control.value})
            )
            # Chronic Illnesses
            chronic_illnesses_field = ft.TextField(
                label="Chronic Illnesses (comma-separated or one per line)",
                value=patient_form_state.get("chronic_illnesses", ""),
                width=520,
                multiline=True,
                min_lines=2,
                max_lines=4,
                border_color=HR_BORDER,
                focused_border_color=HR_PRIMARY,
                text_style=ft.TextStyle(color=HR_TEXT),
                label_style=ft.TextStyle(color=HR_TEXT),
                on_change=lambda e: patient_form_state.update({"chronic_illnesses": e.control.value})
            )
            # Current Medications
            medications_field = ft.TextField(
                label="Current Medications (comma-separated or one per line)",
                value=patient_form_state.get("current_medications", ""),
                width=520,
                multiline=True,
                min_lines=2,
                max_lines=4,
                border_color=HR_BORDER,
                focused_border_color=HR_PRIMARY,
                text_style=ft.TextStyle(color=HR_TEXT),
                label_style=ft.TextStyle(color=HR_TEXT),
                on_change=lambda e: patient_form_state.update({"current_medications": e.control.value})
            )
            # Emergency Contact fields ADDED here
            emergency_contact_container = ft.Row([
                    ft.TextField(
                    label="Emergency Contact Name",
                    value=patient_form_state["emergency_contact_name"],
                    width=250,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    on_change=lambda e: patient_form_state.update({"emergency_contact_name": e.control.value})
                ),
                ft.Container(width=10),
                    ft.TextField(
                    label="Emergency Contact Number",
                    value=patient_form_state["emergency_contact_phone"],
                    width=250,
                        border_color=HR_BORDER,
                        focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    on_change=lambda e: patient_form_state.update({"emergency_contact_phone": e.control.value})
                ),
            ])
            return ft.Column([
                allergies_field,
                chronic_illnesses_field,
                medications_field,
                emergency_contact_container,
                ft.TextField(
                    label="Remarks",
                    value=patient_form_state["remarks"],
                    width=520,
                    multiline=True,
                    min_lines=3,
                    max_lines=5,
                    border_color=HR_BORDER,
                    focused_border_color=HR_PRIMARY,
                    text_style=ft.TextStyle(color=HR_TEXT),
                    label_style=ft.TextStyle(color=HR_TEXT),
                    on_change=lambda e: patient_form_state.update({"remarks": e.control.value})
                ),
            ], spacing=15)

    def handle_next(e):
        if current_step.current < 2:  
            current_step.current += 1
            add_patient_modal.current.content.content.controls[2].content = get_current_step_content()
            page.update()

    def handle_back(e):
        if current_step.current > 0:
            current_step.current -= 1
            add_patient_modal.current.content.content.controls[2].content = get_current_step_content()
            page.update()

    def handle_submit(e=None):
        # Simple validation
        required_fields = ["full_name", "phone", "gender", "birthdate", "visit_type", "assigned_doctor"]
        missing_fields = [field for field in required_fields if not patient_form_state.get(field)]
        
        if missing_fields:
            error_text.value = "Please fill in all required fields: " + ", ".join(missing_fields)
            error_text.visible = True
            page.update()
            return
            
        try:
            
            # Get photo path if photo was uploaded
            photo_path = patient_form_state["photo"].path if patient_form_state["photo"] else None
            
            # Add patient to database
            success, message, patient_id = add_patient(
                full_name=patient_form_state["full_name"],
                birthdate=patient_form_state["birthdate"],
                gender=patient_form_state["gender"],
                civil_status=patient_form_state["civil_status"],
                phone=patient_form_state["phone"],
                address=patient_form_state["address"],
                emergency_contact_name=patient_form_state["emergency_contact_name"],
                emergency_contact_phone=patient_form_state["emergency_contact_phone"],
                # Patient ID is generated automatically by the database
                visit_date=patient_form_state["visit_date"],
                insurance_provider=patient_form_state["insurance_provider"],
                referral_source=patient_form_state["referral_source"],
                allergies=[x.strip() for x in (patient_form_state.get("allergies") or "").replace("\n", ",").split(",") if x.strip()],
                chronic_illnesses=[x.strip() for x in (patient_form_state.get("chronic_illnesses") or "").replace("\n", ",").split(",") if x.strip()],
                current_medications=[x.strip() for x in (patient_form_state.get("current_medications") or "").replace("\n", ",").split(",") if x.strip()],
                remarks=patient_form_state["remarks"],
                status=patient_form_state.get("status", "Pending"),
                assigned_doctor=patient_form_state.get("assigned_doctor", ""),
                visit_type=patient_form_state.get("visit_type", "New Patient"),
                photo_path=photo_path
            )
            
            if success:
                # Reset form state
                patient_form_state.update({
                    # Basic Information
                    "full_name": "",
                    "birthdate": "",
                    "gender": "",
                    "civil_status": "",
                    "phone": "",
                    "address": "",
                    "emergency_contact_name": "",
                    "emergency_contact_phone": "",
                    # Visit & Admin Info
                    # Patient ID is generated automatically by the database
                    "visit_type": "New Patient",
                    "assigned_doctor": "",
                    "visit_date": "",
                    "insurance_provider": "",
                    "referral_source": "",
                    # Pre-Medical Info
                    "allergies": "",
                    "chronic_illnesses": "",
                    "current_medications": "",
                    "remarks": ""
                })
                
                # Reset dropdown fields
                gender_field.value = ""
                status_field.value = "Pending"
                doctor_field.value = ""
                visit_type_field.value = "New Patient"
                
                # Reset photo
                photo_avatar.content = ft.Text("", size=24)
                
                # Reset stepper
                current_step.current = 0
                
                # Update UI
                error_text.value = "Patient added successfully!"
                error_text.visible = True
                add_patient_modal.current.visible = False
                
                # Refresh patient list
                patients = get_all_patients()
                patients_grid.controls = [create_patient_card(p) for p in patients]
                page.update()
            else:
                error_text.value = message
                error_text.visible = True
                page.update()
                
        except ValueError:
            error_text.value = "Please enter a valid age."
            error_text.visible = True
            page.update()
        except Exception as e:
            error_text.value = f"Error: {str(e)}"
            error_text.visible = True
            page.update()

    # Modal content (stepper form)
    add_patient_modal_content = ft.Container(
        width=600,
        height=700,
        bgcolor=HR_WHITE,
        border_radius=10,
        padding=30,
        content=ft.Column([
            # Header Section with Close Icon
            ft.Container(
                content=ft.Stack([
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=0,
                        controls=[
                            ft.Text(
                                "Add New Patient",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=HR_TEXT,
                                text_align=ft.TextAlign.LEFT,
                            ),
                            ft.Text(
                                "Create patient record with comprehensive information",
                                size=12,
                                color=HR_TEXT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=HR_TEXT,
                            icon_size=20,
                            on_click=lambda e: (setattr(add_patient_modal.current, "visible", False), page.update())
                        ),
                        alignment=ft.alignment.top_right,
                    ),
                ]),
                padding=ft.padding.only(bottom=20),
            ),
            # Stepper
            create_stepper(),
            # Form Fields Section
            ft.Container(
                content=get_current_step_content(),
                width=520,
            ),
            # Messages Section
            ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    controls=[error_text],
                ),
                padding=ft.padding.symmetric(vertical=10),
            ),
            # Buttons Section
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.OutlinedButton(
                            "Back",
                            style=ft.ButtonStyle(
                                color=HR_PRIMARY,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            width=120,
                            on_click=handle_back,
                            visible=current_step.current > 0
                        ),
                        ft.Container(width=10),
                        ft.ElevatedButton(
                            "Add Patient",
                            style=ft.ButtonStyle(
                                color=HR_WHITE,
                                bgcolor=HR_PRIMARY,
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                            width=200,
                            on_click=handle_submit
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(top=10),
            ),
        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.15, HR_TEXT),
            offset=ft.Offset(0, 3),
        ),
    )

    # --- Top bar with search, filters, download, and add button ---
    def filter_patients(e):
        search_term = search_field.value.lower() if search_field.value else ""
        filtered_patients = [
            p for p in patients
            if search_term in p['full_name'].lower() or 
               search_term in p['last_name'].lower() or 
               search_term in str(p['id']).lower() or
               search_term in p.get('phone', '').lower()
        ]
        patients_grid.controls = [create_patient_card(p) for p in filtered_patients]
        page.update()

    search_field = ft.TextField(
        hint_text="Search here",
        expand=True,
        border_radius=8,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=HR_WHITE,
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        hint_style=ft.TextStyle(color=HR_TEXT),
        text_style=ft.TextStyle(color=HR_TEXT),
        on_change=filter_patients
    )
    filter_btn = ft.IconButton(
        icon=ft.Icons.FILTER_LIST,
        icon_color=HR_PRIMARY,
        tooltip="Filters",
        on_click=show_filter_modal
    )
    download_btn = ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_color=HR_PRIMARY, tooltip="Download", on_click=lambda _: None)
    def show_add_patient_modal(e=None):
        add_patient_modal.current.visible = True
        page.update()

    add_btn = ft.ElevatedButton(
        "Add Patient",
        icon=ft.Icons.PERSON_ADD,
        bgcolor=HR_PRIMARY,
        color=HR_WHITE,
        style=ft.ButtonStyle(),
        on_click=show_add_patient_modal
    )
    top_bar = ft.Row([
        search_field,
        filter_btn,
        download_btn,
        ft.Container(width=10),
        add_btn
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Fetch patients from database
    patients = get_all_patients()
    
    # Create patients grid with 3 cards per row
    patients_grid = ft.Row(
        controls=[
            ft.Container(
                content=create_patient_card(p),
                width=280,  # Reduced from 300
                margin=ft.margin.only(bottom=15, right=15)  # Reduced margins
            ) for p in patients
        ],
        wrap=True,
        spacing=0,
        run_spacing=0,
        width=900,  # Reduced from 1000 to fit better with smaller cards
    )

    # --- Available doctors ---
    def doctor_avatar(d):
        return ft.Column([
            ft.CircleAvatar(content=ft.Text(d['name'].split()[1][0], color=HR_WHITE, size=16), bgcolor=HR_PRIMARY, radius=22),
            ft.Text(d['name'], size=12, weight=ft.FontWeight.BOLD, color=HR_TEXT, max_lines=1, width=90, text_align=ft.TextAlign.CENTER),
            ft.Text(d['department'], size=10, color=HR_TEXT, max_lines=1, width=90, text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2, width=90)
    
    # Get verified doctors from database
    verified_doctors = [d for d in get_all_doctors() if d.get('is_verified', False)]
    doctors = [
        {"id": d['user_id'], "name": f"Dr. {d['first_name']} {d['last_name']}", "department": f"Department (ID: {d['user_id']})"}
        for d in verified_doctors
    ]

    # Doctor search functionality
    def filter_doctors(e):
        search_term = doctor_search_field.value.lower() if doctor_search_field.value else ""
        filtered_doctors = [
            d for d in doctors
            if search_term in d['name'].lower() or search_term in d['department'].lower()
        ]
        doctors_row.controls = [doctor_avatar(d) for d in filtered_doctors]
        page.update()

    doctor_search_field = ft.TextField(
        hint_text="Search here",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=HR_WHITE,
        border_color=HR_BORDER,
        focused_border_color=HR_PRIMARY,
        text_style=ft.TextStyle(color=HR_TEXT),
        hint_style=ft.TextStyle(color=HR_TEXT),
        height=36,
        on_change=filter_doctors
    )

    doctors_row = ft.Row(
        controls=[doctor_avatar(d) for d in doctors],
        wrap=True,
        spacing=10,
        run_spacing=10
    )
    
    available_doctors = ft.Container(
        content=ft.Column([
            ft.Text("Available Doctors", size=15, weight=ft.FontWeight.BOLD, color=HR_TEXT),
            doctor_search_field,
            doctors_row,
        ], spacing=10, expand=True),
        bgcolor=HR_WHITE,
        border_radius=10,
        padding=16,
        width=260,
        expand=True
    )

    # Create a container for the main content area (search + grid)
    main_content = ft.Column(
        spacing=10,  # Space between search and grid
        controls=[
            # Search bar
            top_bar,
            # Main content row (patients grid + doctors panel)
            ft.Container(
                content=ft.Row([
                    # Patients grid with 3 columns
                    ft.Container(
                        content=ft.Column([
                            patients_grid
                        ], scroll=ft.ScrollMode.AUTO, expand=True),
                        expand=True,
                        alignment=ft.alignment.top_left,
                    ),
                    # Doctors panel
                    ft.Container(
                        content=available_doctors,
                        width=280,
                        expand=False,
                        alignment=ft.alignment.top_left,
                    )
                ], 
                expand=True, 
                spacing=15,
                vertical_alignment=ft.CrossAxisAlignment.START  # Align to top
                ),
                expand=True,
                padding=0
            )
        ],
        expand=True
    )
    
    # Add the main content to the container
    content_container.content.controls.append(main_content)
    
    # Create a stack to handle modals on top of content
    modal_stack = ft.Stack(
        [
            # Main content
            container,
            # Modals (initially hidden)
            ft.Container(
                ref=add_patient_modal,
                visible=False,
                bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                expand=True,
                alignment=ft.alignment.center,
                content=add_patient_modal_content
            ),
            ft.Container(
                ref=patient_details_modal,
                visible=False,
                bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                expand=True,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                ref=edit_patient_modal,
                visible=False,
                bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                expand=True,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                ref=delete_confirm_modal,
                visible=False,
                bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                expand=True,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                ref=filter_modal,
                visible=False,
                bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                expand=True,
                alignment=ft.alignment.center,
            )
        ],
        expand=True
    )
    
    # Return the stack containing content and modals
    return modal_stack

# Helper to create consistent header
def create_header(title, user):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Text(user.get('first_name', 'U')[0].upper(), size=18),
                        radius=20,
                        bgcolor=HR_PRIMARY,
                        color=HR_WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
    )

def dashboard_ui(page, user):
    # Get verified doctors from database
    doctors = get_all_doctors()
    
    page.clean()
    page.title = "NexaCare Dashboard"
    page.bgcolor = HR_SECONDARY
    page.padding = 0

    # Modal dialog container (unchanged)
    dialog_modal = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
        expand=True,
        alignment=ft.alignment.center,
    )

    # Track currently selected menu item
    current_selection = ft.Ref[str]()
    current_selection.current = "Dashboard"

    # Main content container (will be updated by menu handler)
    main_content = ft.Container(expand=True)

    def create_stat_card(title, value, icon, color, trend=None):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=40,
                        height=40,
                        border_radius=8,
                        bgcolor=f"{color}20",
                        content=ft.Icon(icon, color=color, size=20),
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(expand=True),
                    ft.Text(f"{trend}%" if trend else "", 
                           color=HR_SUCCESS if trend and trend > 0 else HR_ERROR if trend else HR_GRAY,
                           size=12)
                ]),
                ft.Container(height=8),
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                ft.Text(title, size=12, color=HR_GRAY),
            ]),
            padding=20,
            bgcolor=HR_WHITE,
            border_radius=12,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    def create_appointment_item(apt, selected=False, on_select=None):
        status_color = {
            "completed": HR_SUCCESS,
            "pending": HR_WARNING,
            "cancelled": HR_ERROR
        }.get(apt["status"].lower(), HR_GRAY)
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=8,
                    bgcolor=f"{HR_PRIMARY}10",
                    content=ft.Text(
                        apt["patient_name"][0].upper(),
                        color=HR_PRIMARY,
                        weight=ft.FontWeight.BOLD,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(apt["patient_name"], weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Text(apt["doctor_name"], size=12, color=HR_GRAY),
                ], spacing=2, expand=True, alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    ft.Text(apt["time"], color=HR_TEXT, weight=ft.FontWeight.W_500),
                    ft.Container(
                        content=ft.Text(
                            apt["status"].capitalize(),
                            color=ft.Colors.WHITE,
                            size=10,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=10,
                    )
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.WHITE if not selected else f"{HR_PRIMARY}10",
            border_radius=8,
            border=ft.border.all(1, f"{HR_PRIMARY}30" if selected else HR_BORDER),
            on_click=on_select,
            data=apt,
        )

    def create_consultation_notes(apt):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Consultation Notes", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                ]),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Text(
                        apt.get("notes", "No notes available"),
                        color=HR_TEXT,
                        size=14,
                    ),
                    padding=16,
                    bgcolor=HR_WHITE,
                    border_radius=8,
                    expand=True,
                ),
            ], expand=True),
        )

    # Helper to create dashboard content (returns the dashboard UI content)
    def create_dashboard_ui_content(page, user):
        # --- Static/mock data ---
        appointments = [
            {"patient_name": "Audrey Mann", "doctor_name": "Dr. Smith", "time": "09:00 AM", "date": "06/05/24", "status": "completed", "notes": "Patient reported improvement in symptoms. Prescribed medication refill and scheduled follow-up in 2 weeks."},
            {"patient_name": "Rudy Hikke", "doctor_name": "Dr. Johnson", "time": "09:30 AM", "date": "06/05/24", "status": "completed", "notes": "Routine checkup completed. Blood work ordered. Patient to return in 1 month."},
            {"patient_name": "Johanna Ebert", "doctor_name": "Dr. Williams", "time": "10:00 AM", "date": "06/05/24", "status": "in-progress", "notes": "Patient presents with persistent cough and fever. Ordered chest X-ray and prescribed antibiotics."},
            {"patient_name": "Armando Shade", "doctor_name": "Dr. Brown", "time": "10:30 AM", "date": "06/05/24", "status": "pending", "notes": "Annual physical examination. Patient reports feeling well overall."},
            {"patient_name": "Bessi Shair", "doctor_name": "Dr. Davis", "time": "11:00 AM", "date": "06/05/24", "status": "pending", "notes": "Follow-up for chronic condition management. Reviewing lab results."},
            {"patient_name": "Tamara Dewski", "doctor_name": "Dr. Miller", "time": "11:30 AM", "date": "06/05/24", "status": "pending", "notes": "New patient consultation. Completing initial assessment."},
            {"patient_name": "Phoebe Fadil", "doctor_name": "Dr. Wilson", "time": "12:45 PM", "date": "06/05/24", "status": "pending", "notes": "Pre-operative consultation. Reviewing medical history and procedure details."},
        ]
        selected_apt = appointments[2]  # Johanna Ebert as ongoing

        # Info Cards
        info_cards = ft.Row([
            create_stat_card("Appointments", "24", ft.Icons.CALENDAR_MONTH, HR_PRIMARY, 12.5),
            create_stat_card("New Patients", "8", ft.Icons.PERSON_ADD, HR_INFO, 8.3),
            create_stat_card("Follow Up", "5", ft.Icons.UPDATE, HR_WARNING, -2.1),
        ], spacing=16)

        # Appointments List
        appointments_list = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Today's Appointments", size=16, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Container(expand=True),
                    ft.Text("View All", size=12, color=HR_PRIMARY),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=16),
                ft.Column([
                    create_appointment_item(apt, selected=(apt==selected_apt), 
                                         on_select=lambda e: update_selected_appointment(e.control.data))
                    for apt in appointments
                ], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
            ], expand=True),
            padding=20,
            bgcolor=HR_WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            ),
            expand=True,
        )

        # Ongoing Appointment Details
        def create_detail_row(label, value, icon=None):
            return ft.Container(
                content=ft.Row([
                    ft.Text(f"{label}:", width=120, color=HR_GRAY, size=14),
                    ft.Row([
                        ft.Icon(icon, size=16, color=HR_GRAY) if icon else None,
                        ft.Text(value, color=HR_TEXT, size=14, weight=ft.FontWeight.W_500),
                    ], spacing=8) if icon else ft.Text(value, color=HR_TEXT, size=14, weight=ft.FontWeight.W_500),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.symmetric(vertical=8),
            )

        # Action buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "Reschedule",
                icon=ft.Icons.CALENDAR_TODAY,
                style=ft.ButtonStyle(
                    bgcolor=HR_WHITE,
                    color=HR_PRIMARY,
                    side=ft.border.BorderSide(1, HR_PRIMARY),
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                ),
            ),
            ft.Container(width=12),
            ft.ElevatedButton(
                "Finish Consultation",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                style=ft.ButtonStyle(
                    bgcolor=HR_PRIMARY,
                    color=HR_WHITE,
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                ),
            ),
        ], alignment=ft.MainAxisAlignment.END)

        ongoing_details = ft.Container(
            content=ft.Column([
                # Patient info
                ft.Row([
                    ft.Container(
                        width=60,
                        height=60,
                        border_radius=30,
                        bgcolor=f"{HR_PRIMARY}10",
                        content=ft.Text(
                            selected_apt["patient_name"][0].upper(),
                            size=24,
                            color=HR_PRIMARY,
                            weight=ft.FontWeight.BOLD,
                        ),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(selected_apt["patient_name"], size=18, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                        ft.Text(f"{selected_apt['time']} • {selected_apt['date']}", color=HR_GRAY, size=12),
                    ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=16),
                ft.Container(height=20),
                # Patient details
                create_detail_row("Age", "32 years", ft.Icons.PERSON_OUTLINE),
                create_detail_row("Phone", "+1 (555) 123-4567", ft.Icons.PHONE),
                create_detail_row("Issue", "Fever & Cough", ft.Icons.HEALING),
                create_detail_row("Doctor", selected_apt["doctor_name"], ft.Icons.MEDICAL_SERVICES),
            ]),
            padding=24,
            bgcolor=HR_WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            ),
            expand=True,
        )

        # Consultation Notes
        consultation_notes = create_consultation_notes(selected_apt)

        def update_selected_appointment(apt):
            nonlocal selected_apt
            selected_apt = apt
            main_content.content = create_dashboard_ui_content(page, user)
            page.update()
        
        # Main layout
        return ft.Container(
            expand=True,
            bgcolor=HR_SECONDARY,
            content=ft.Column([
                # Header
                create_header("Dashboard", user),
                # Info Cards
                info_cards,
                # Main Content
                ft.Row([
                    # Appointments List (Left)
                    ft.Container(
                        content=appointments_list,
                        width=400,
                        expand=False,
                    ),
                    # Spacing
                    ft.Container(width=20),
                    # Middle and Right Sections
                    ft.Column([
                        # Action buttons above the container
                        action_buttons,
                        ft.Container(height=12),
                        # Ongoing Appointment (Top)
                        ongoing_details,
                        ft.Container(height=20),
                        # Consultation Notes (Bottom)
                        consultation_notes,
                    ], expand=True, spacing=0),
                ], expand=True, spacing=0),
            ], spacing=24, scroll=ft.ScrollMode.AUTO, expand=True),
            padding=ft.padding.all(24),
        )

    def show_add_appointment_dialog():
        from database import get_all_patients, get_all_doctors, add_appointment
        import datetime

        # Fetch patients and doctors
        patients = get_all_patients()
        doctors = get_all_doctors()

        # State for form
        appointment_form_state = {
            "patient_id": None,
            "doctor_id": None,
            "date": None,
            "time": None,
            "type": None,
            "status": "Scheduled",
            "notes": ""
        }

        # Create a container for the date display
        date_display = ft.Text(
            f"Selected date: {appointment_form_state.get('date', '') or 'No date selected'}",
            size=12,
            color=HR_TEXT,
            visible=True
        )

        def update_date_display():
            date_display.value = f"Selected date: {appointment_form_state.get('date', '') or 'No date selected'}"
            page.update()

        # Patient dropdown
        patient_dropdown = ft.Dropdown(
            label="Patient",
            hint_text="Select patient",
            options=[ft.dropdown.Option(str(p["id"]), p["full_name"]) for p in patients],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            expand=True,
            on_change=lambda e: appointment_form_state.update({"patient_id": e.control.value})
        )
        # Doctor dropdown
        doctor_dropdown = ft.Dropdown(
            label="Doctor",
            hint_text="Select doctor",
            options=[ft.dropdown.Option(d["user_id"], f"Dr. {d['first_name']} {d['last_name']}") for d in doctors if d.get('is_verified', False)],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            width=150,  # Decreased width for the dropdown
            on_change=lambda e: appointment_form_state.update({"doctor_id": e.control.value})
        )
        # Date field (with date picker)
        date_field = ft.TextField(
            label="Date",
            hint_text="YYYY-MM-DD",
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            expand=True,
            read_only=True,
            value=appointment_form_state.get("date", ""),
        )
        date_icon_button = ft.IconButton(
            ft.Icons.CALENDAR_MONTH,
            tooltip="Select Date",
            on_click=lambda e: show_date_picker_dialog(
                page,
                date_field,
                appointment_form_state,
                "date",
                "Select Appointment Date",
                lambda: None,  # No stepper refresh needed here
                min_date=datetime.datetime.now(),
                on_date_selected=update_date_display  # Pass the update function
            )
        )
        # Time field
        time_field = ft.TextField(
            label="Time",
            hint_text="HH:MM",
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            expand=True,
            on_change=lambda e: appointment_form_state.update({"time": e.control.value})
        )
        # Type dropdown
        type_dropdown = ft.Dropdown(
            label="Appointment Type",
            hint_text="Select type",
            options=[
                ft.dropdown.Option("Check-up"),
                ft.dropdown.Option("Follow-up"),
                ft.dropdown.Option("Consultation"),
                ft.dropdown.Option("Emergency"),
                ft.dropdown.Option("Routine"),
                ft.dropdown.Option("Specialist"),
                ft.dropdown.Option("Surgery"),
                ft.dropdown.Option("Therapy")
            ],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            expand=True,
            on_change=lambda e: appointment_form_state.update({"type": e.control.value})
        )
        # Status dropdown
        status_dropdown = ft.Dropdown(
            label="Status",
            value="Scheduled",
            options=[ft.dropdown.Option(s) for s in ["Scheduled", "Completed", "Pending", "Cancelled", "No Show"]],
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            expand=True,
            on_change=lambda e: appointment_form_state.update({"status": e.control.value})
        )
        # Notes field
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=HR_BORDER,
            focused_border_color=HR_PRIMARY,
            expand=True,
            on_change=lambda e: appointment_form_state.update({"notes": e.control.value})
        )

        def close_dialog(e=None):
            dialog_modal.visible = False
            page.update()
            
        def save_appointment(e=None):
            # Validate required fields
            if not all([appointment_form_state["patient_id"], appointment_form_state["doctor_id"], appointment_form_state["date"], appointment_form_state["time"], appointment_form_state["type"]]):
                page.snack_bar = ft.SnackBar(content=ft.Text("Please fill all required fields."))
                page.snack_bar.open = True
                page.update()
                return
            # Combine date and time
            appointment_datetime = f"{appointment_form_state['date']} {appointment_form_state['time']}"
            # Call backend
            success, msg, _ = add_appointment(
                int(appointment_form_state["patient_id"]),
                appointment_form_state["doctor_id"],
                appointment_datetime,
                appointment_form_state["type"],
                appointment_form_state["status"],
                appointment_form_state["notes"]
            )
            if success:
                page.snack_bar = ft.SnackBar(content=ft.Text("Appointment added successfully!"))
                page.snack_bar.open = True
                page.update()
                close_dialog()
                # Refresh only the schedule tab
                handle_menu_selection("Schedule")
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {msg}"))
                page.snack_bar.open = True
                page.update()

        # Build dialog content
        dialog_content = ft.Container(
            width=500,
            height=600,
            bgcolor=HR_WHITE,
            border_radius=10,
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Add New Appointment", size=18, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.IconButton(icon=ft.Icons.CLOSE, on_click=close_dialog, icon_color=HR_TEXT),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color=HR_BORDER),
                patient_dropdown,
                ft.Container(height=10),
                # Date row with visible text
                ft.Column([
                    ft.Row([date_field, date_icon_button, ft.Container(width=10), time_field]),
                    date_display,
                ]),
                ft.Container(height=10),
                doctor_dropdown,
                type_dropdown,
                status_dropdown,
                notes_field,
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        "Cancel",
                        on_click=close_dialog,
                        style=ft.ButtonStyle(bgcolor=HR_WHITE, color=HR_TEXT),
                    ),
                    ft.Container(width=10),
                    ft.ElevatedButton(
                        "Save Appointment",
                        on_click=save_appointment,
                        style=ft.ButtonStyle(bgcolor=HR_PRIMARY, color=HR_WHITE),
                    ),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=10),
        )
        dialog_modal.content = dialog_content
        dialog_modal.visible = True
        page.update()
    
    # Sidebar menu selection handler
    def handle_menu_selection(title, e=None):
        current_selection.current = title
        if title == "Dashboard":
            main_content.content = create_dashboard_ui_content(page, user)
        elif title == "Patients":
            main_content.content = create_patients_tab(page, user)
        elif title == "Schedule":
            if not hasattr(page, "schedule_tab_state"):
                page.schedule_tab_state = {"selected_appointment": None}
            selected_appointment = page.schedule_tab_state.get("selected_appointment")

            def handle_row_click(e, apt):
                page.schedule_tab_state["selected_appointment"] = apt
                handle_menu_selection("Schedule")

            # Define search/filter/download controls locally
            search_field = ft.TextField(
                hint_text="Search here",
                expand=True,
                border_radius=8,
                filled=True,
                prefix_icon=ft.Icons.SEARCH,
                bgcolor=HR_WHITE,
                border_color=HR_BORDER,
                focused_border_color=HR_PRIMARY,
                hint_style=ft.TextStyle(color=HR_TEXT),
                text_style=ft.TextStyle(color=HR_TEXT),
            )
            filter_btn = ft.IconButton(
                icon=ft.Icons.FILTER_LIST,
                icon_color=HR_PRIMARY,
                tooltip="Filters",
            )
            download_btn = ft.IconButton(
                icon=ft.Icons.DOWNLOAD,
                icon_color=HR_PRIMARY,
                tooltip="Download",
            )

            # Fetch appointments
            from database import get_all_appointments
            success, msg, appointments_data = get_all_appointments()
            if not success:
                appointments_data = []

            # Build table rows
            table_rows = []
            for apt in appointments_data:
                status_color = {
                    "Scheduled": HR_SUCCESS,
                    "Completed": HR_INFO,
                    "Pending": HR_WARNING,
                    "Cancelled": HR_ERROR,
                    "No Show": HR_ERROR
                }.get(apt.get("status", "Scheduled"), HR_TEXT)
                date_str = ""
                if apt.get("appointment_date"):
                    try:
                        date_obj = datetime.strptime(str(apt["appointment_date"]), "%Y-%m-%d %H:%M:%S")
                        date_str = date_obj.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        date_str = str(apt["appointment_date"])[:10]
                is_selected = selected_appointment and selected_appointment["id"] == apt["id"]
                row_bgcolor = HR_PRIMARY + "1A" if is_selected else HR_WHITE
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Container(
                            ft.Row([
                                ft.CircleAvatar(
                                    content=ft.Text(apt.get("patient_name", "")[0] if apt.get("patient_name") else "?"),
                                    radius=15,
                                    bgcolor=HR_PRIMARY,
                                    color=HR_WHITE
                                ),
                                ft.Text(apt.get("patient_name", "Unknown"))
                            ], spacing=10),
                            bgcolor=row_bgcolor
                        )),
                        ft.DataCell(ft.Container(ft.Text(date_str), bgcolor=row_bgcolor)),
                        ft.DataCell(ft.Container(ft.Text(apt.get("doctor_name", "")), bgcolor=row_bgcolor)),
                        ft.DataCell(ft.Container(ft.Text(apt.get("consultation_type", "")), bgcolor=row_bgcolor)),
                        ft.DataCell(ft.Container(
                            ft.Container(
                                content=ft.Text(
                                    apt.get("status", ""),
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_500
                                ),
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=15,
                                bgcolor=status_color
                            ),
                            bgcolor=row_bgcolor
                        )),
                    ],
                    on_select_changed=lambda e, apt=apt: handle_row_click(e, apt),
                    data=apt,
                )
                table_rows.append(row)

            appointments_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(header)) for header in ["NAME", "DATE", "DOCTOR", "TYPE", "STATUS"]
                ],
                rows=table_rows,
                border=ft.border.all(1, HR_BORDER),
                border_radius=8,
                vertical_lines=ft.border.BorderSide(1, HR_BORDER),
                horizontal_lines=ft.border.BorderSide(1, HR_BORDER),
                sort_column_index=0,
                sort_ascending=True,
                width=1200,
                heading_row_color=HR_WHITE,
                heading_text_style=ft.TextStyle(color=HR_TEXT, weight=ft.FontWeight.BOLD),
                data_row_color=HR_WHITE,
                data_row_min_height=50,
                data_row_max_height=50,
                data_text_style=ft.TextStyle(color=HR_TEXT),
            )

            # Top bar for Schedule tab
            top_bar = ft.Row([
                search_field,
                filter_btn,
                download_btn,
                ft.Container(width=10),
                ft.ElevatedButton(
                    "Add Appointment",
                    icon=ft.Icons.ADD_ALARM,
                    bgcolor=HR_PRIMARY,
                    color=HR_WHITE,
                    style=ft.ButtonStyle(),
                    on_click=lambda e: show_add_appointment_dialog()
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    "Delete Appointment",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=HR_ERROR,
                    color=HR_WHITE,
                    style=ft.ButtonStyle(),
                    on_click=lambda e: create_delete_confirmation_dialog(page, selected_appointment["id"], selected_appointment["patient_name"], handle_menu_selection) if selected_appointment else None,
                    disabled=not selected_appointment,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

            # Pagination controls
            pagination = ft.Row([
                ft.Text("Page:"),
                ft.Container(width=5),
                ft.Text("1", weight=ft.FontWeight.BOLD),
                ft.Container(width=2),
                ft.Text("of"),
                ft.Container(width=2),
                ft.Text("1"),
                ft.Container(width=5),
                ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS, icon_size=15, disabled=True),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD_IOS, icon_size=15, disabled=True),
            ], alignment=ft.MainAxisAlignment.END)

            # Main layout for Schedule tab
            main_content.content = ft.Container(
                expand=True,
                bgcolor=HR_SECONDARY,
                content=ft.Column([
                    create_header("Schedule", user),
                    top_bar,
                    ft.Container(content=appointments_table, expand=True),
                    ft.Container(content=pagination, padding=ft.padding.only(top=10)),
                ], spacing=0),
            )
        elif title == "Settings":
            main_content.content = ft.Container(
                content=ft.Column([
                    create_header("Settings", user),
                    ft.Container(
                        content=ft.Text("Settings tab coming soon...", size=16, color=HR_TEXT),
                        padding=ft.padding.only(top=20, left=15, right=15),
                    )
                ]),
                expand=True,
                bgcolor=HR_SECONDARY,
            )
        page.update()

    # Logout handler
    def handle_logout(e):
        def close_dialog(confirmed=False):
            dialog_modal.visible = False
            if confirmed:
                navigate_to_login(page)
            page.update()
        dialog_content = ft.Container(
            width=400,
            height=200,
            bgcolor=HR_WHITE,
            border_radius=10,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Confirm Logout", size=20, weight=ft.FontWeight.BOLD, color=HR_TEXT),
                    ft.Container(height=20),
                    ft.Text("Are you sure you want to logout?", color=HR_TEXT),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                "Yes",
                                style=ft.ButtonStyle(color=HR_WHITE, bgcolor=HR_PRIMARY),
                                on_click=lambda _: close_dialog(True)
                            ),
                            ft.Container(width=20),
                            ft.OutlinedButton(
                                "No",
                                style=ft.ButtonStyle(
                                    color=HR_PRIMARY,
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

    # Sidebar with menu handler
    sidebar = create_sidebar(page, "hr", handle_logout, current_selection, handle_menu_selection)

    # Set initial content
    main_content.content = create_dashboard_ui_content(page, user)

    # Combine sidebar and content
    page.add(
        ft.Stack([
            ft.Row([
                sidebar,
                main_content
            ], expand=True),
            dialog_modal
        ], expand=True)
    )

    # Pagination controls
    pagination = ft.Row([
        ft.Text("Page:"),
        ft.Container(width=5),
        ft.Text("1", weight=ft.FontWeight.BOLD),
        ft.Container(width=2),
        ft.Text("of"),
        ft.Container(width=2),
        ft.Text("1"),
        ft.Container(width=5),
        ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS, icon_size=15, disabled=True),
        ft.IconButton(icon=ft.Icons.ARROW_FORWARD_IOS, icon_size=15, disabled=True),
    ], alignment=ft.MainAxisAlignment.END)

# Add this at the top-level (outside any function):
def create_delete_confirmation_dialog(page, appointment_id, patient_name, state):
    def handle_delete(e):
        from database import delete_appointment
        success, msg = delete_appointment(appointment_id)
        if success:
            page.snack_bar = ft.SnackBar(content=ft.Text("Appointment deleted successfully!"))
            page.snack_bar.open = True
            page.schedule_tab_state['selected_appointment'] = None
            # Refresh the Schedule tab
            state.handle_menu_selection("Schedule")
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {msg}"))
            page.snack_bar.open = True
        page.dialog.open = False
        page.update()
    def handle_cancel(e):
        page.dialog.open = False
        page.update()
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text(f"Are you sure you want to delete the appointment for {patient_name}?"),
        actions=[
            ft.TextButton("Cancel", on_click=handle_cancel),
            ft.TextButton("Delete", on_click=handle_delete, style=ft.ButtonStyle(color=HR_ERROR)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog.open = True
    page.update()

