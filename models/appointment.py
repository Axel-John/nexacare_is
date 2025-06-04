from datetime import datetime
from database import get_connection
from mysql.connector import Error

def get_all_appointments():
    """
    Retrieve all appointments from the database.
    Returns a list of appointment dictionaries.
    """
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                a.appointment_id,
                a.date,
                a.time,
                a.status,
                a.notes,
                d.first_name as doctor_first_name,
                d.last_name as doctor_last_name,
                d.user_id as doctor_id,
                p.name as patient_name,
                p.id as patient_id
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.user_id
            JOIN patients p ON a.patient_id = p.id
            ORDER BY a.date DESC, a.time DESC
        """)
        appointments = cursor.fetchall()
        return appointments
    except Error as e:
        print(f"Error fetching appointments: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_appointment(doctor_id, patient_id, date, time, notes=""):
    """
    Create a new appointment in the database.
    Returns True if successful, False otherwise.
    """
    conn = get_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO appointments (doctor_id, patient_id, date, time, status, notes)
            VALUES (%s, %s, %s, %s, 'scheduled', %s)
        """, (doctor_id, patient_id, date, time, notes))
        conn.commit()
        return True
    except Error as e:
        print(f"Error creating appointment: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_appointment_status(appointment_id, status):
    """
    Update the status of an appointment.
    Returns True if successful, False otherwise.
    """
    conn = get_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE appointments
            SET status = %s
            WHERE appointment_id = %s
        """, (status, appointment_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error updating appointment status: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_appointments_by_doctor(doctor_id):
    """
    Retrieve all appointments for a specific doctor.
    Returns a list of appointment dictionaries.
    """
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                a.appointment_id,
                a.date,
                a.time,
                a.status,
                a.notes,
                p.name as patient_name,
                p.id as patient_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.doctor_id = %s
            ORDER BY a.date DESC, a.time DESC
        """, (doctor_id,))
        appointments = cursor.fetchall()
        return appointments
    except Error as e:
        print(f"Error fetching doctor appointments: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_appointments_by_patient(patient_id):
    """
    Retrieve all appointments for a specific patient.
    Returns a list of appointment dictionaries.
    """
    conn = get_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                a.appointment_id,
                a.date,
                a.time,
                a.status,
                a.notes,
                d.first_name as doctor_first_name,
                d.last_name as doctor_last_name,
                d.user_id as doctor_id
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.user_id
            WHERE a.patient_id = %s
            ORDER BY a.date DESC, a.time DESC
        """, (patient_id,))
        appointments = cursor.fetchall()
        return appointments
    except Error as e:
        print(f"Error fetching patient appointments: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close() 