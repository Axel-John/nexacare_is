from database import get_connection, generate_user_id
from mysql.connector import Error

def get_user(email_or_id: str, password: str, role: str) -> dict:
    try:
        conn = get_connection()
        if conn is None:
            return None
            
        table = "doctors" if role == "Doctor" else ("hrs" if role == "HR" else "admins")
        cursor = conn.cursor(dictionary=True)
        
        # Try to find user by email or ID
        cursor.execute(
            f"SELECT * FROM {table} WHERE (email = %s OR user_id = %s) AND password = %s",
            (email_or_id, email_or_id, password)
        )
        
        user = cursor.fetchone()
        return user
        
    except Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_doctors() -> list:
    """Fetch all doctors from the database"""
    try:
        conn = get_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT user_id, first_name, last_name, email, is_verified
        FROM doctors
        ORDER BY created_at DESC
        """)
        doctors = cursor.fetchall()
        return doctors
        
    except Error as e:
        print(f"Error getting doctors: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_hrs() -> list:
    """Fetch all HR staff from the database"""
    try:
        conn = get_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
        SELECT user_id, first_name, last_name, email, is_verified
        FROM hrs
        ORDER BY created_at DESC
        """)
        hrs = cursor.fetchall()
        return hrs
        
    except Error as e:
        print(f"Error getting HR staff: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(first_name: str, last_name: str, email: str, password: str, role: str) -> tuple[bool, str, str]:
    """
    Create a new user (doctor, HR, or admin) in the database
    Returns: (success: bool, message: str, user_id: str)
    """
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed", None
            
        cursor = conn.cursor()
        table = "doctors" if role == "Doctor" else ("hrs" if role == "HR" else "admins")
        
        # Check if email exists in the correct table
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return False, "Email already registered", None
            
        # Basic validation
        if len(first_name) < 2 or len(last_name) < 2:
            return False, "First and last names must be at least 2 characters long", None
        if len(password) < 8:
            return False, "Password must be at least 8 characters long", None
        if not email.endswith("@nexacare.med"):
            return False, "Email must end with @nexacare.med", None
        if role not in ['Doctor', 'HR', 'Admin']:
            return False, "Invalid role selected", None

        user_id = generate_user_id(role)
        if not user_id:
            return False, "Failed to generate user ID", None
            
        # Insert new user into the correct table
        cursor.execute(f"""
        INSERT INTO {table} (user_id, first_name, last_name, email, password)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, email, password))
        
        conn.commit()
        return True, "Account created successfully", user_id
        
    except Error as e:
        print(f"Error creating user: {e}")
        error_message = str(e)
        
        # Handle specific database constraint errors
        if "chk_doc_names" in error_message or "chk_hr_names" in error_message or "chk_admin_names" in error_message:
            return False, "First and last names must be at least 2 characters long", None
        elif "chk_doc_email" in error_message or "chk_hr_email" in error_message or "chk_admin_email" in error_message:
            return False, "Email must end with @nexacare.med", None
        elif "chk_doc_password" in error_message or "chk_hr_password" in error_message or "chk_admin_password" in error_message:
            return False, "Password must be at least 8 characters long", None
        elif "Duplicate entry" in error_message:
            return False, "Email already registered", None
        else:
            return False, "Error creating account. Please try again.", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def verify_doctor(user_id: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Update doctor's verification status
        cursor.execute("""
        UPDATE doctors 
        SET is_verified = TRUE 
        WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        return True, "Doctor verified successfully"
        
    except Error as e:
        print(f"Error verifying doctor: {e}")
        return False, f"Error verifying doctor: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_doctor(user_id: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Delete doctor from database
        cursor.execute("""
        DELETE FROM doctors 
        WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        return True, "Doctor deleted successfully"
        
    except Error as e:
        print(f"Error deleting doctor: {e}")
        return False, f"Error deleting doctor: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_doctor(user_id: str, first_name: str, last_name: str, email: str) -> tuple[bool, str]:
    """
    Update doctor information in the database
    Returns: (success: bool, message: str)
    """
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Basic validation
        if len(first_name) < 2 or len(last_name) < 2:
            return False, "First and last names must be at least 2 characters long"
        if not email.endswith("@nexacare.med"):
            return False, "Email must end with @nexacare.med"
            
        # Check if email is already used by another doctor
        cursor.execute("""
        SELECT COUNT(*) FROM doctors 
        WHERE email = %s AND user_id != %s
        """, (email, user_id))
        if cursor.fetchone()[0] > 0:
            return False, "Email is already registered to another doctor"
            
        # Update doctor information
        cursor.execute("""
        UPDATE doctors 
        SET first_name = %s, last_name = %s, email = %s
        WHERE user_id = %s
        """, (first_name, last_name, email, user_id))
        
        conn.commit()
        return True, "Doctor information updated successfully"
        
    except Error as e:
        print(f"Error updating doctor: {e}")
        error_message = str(e)
        
        # Handle specific database constraint errors
        if "chk_doc_names" in error_message:
            return False, "First and last names must be at least 2 characters long"
        elif "chk_doc_email" in error_message:
            return False, "Email must end with @nexacare.med"
        else:
            return False, f"Error updating doctor: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def verify_hr(user_id: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Update HR's verification status
        cursor.execute("""
        UPDATE hrs 
        SET is_verified = TRUE 
        WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        return True, "HR staff verified successfully"
        
    except Error as e:
        print(f"Error verifying HR staff: {e}")
        return False, f"Error verifying HR staff: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_hr(user_id: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Delete HR staff from database
        cursor.execute("""
        DELETE FROM hrs 
        WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        return True, "HR staff deleted successfully"
        
    except Error as e:
        print(f"Error deleting HR staff: {e}")
        return False, f"Error deleting HR staff: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_hr(user_id: str, first_name: str, last_name: str, email: str) -> tuple[bool, str]:
    """
    Update HR staff information in the database
    Returns: (success: bool, message: str)
    """
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Basic validation
        if len(first_name) < 2 or len(last_name) < 2:
            return False, "First and last names must be at least 2 characters long"
        if not email.endswith("@nexacare.med"):
            return False, "Email must end with @nexacare.med"
            
        # Check if email is already used by another HR staff
        cursor.execute("""
        SELECT COUNT(*) FROM hrs 
        WHERE email = %s AND user_id != %s
        """, (email, user_id))
        if cursor.fetchone()[0] > 0:
            return False, "Email is already registered to another HR staff"
            
        # Update HR staff information
        cursor.execute("""
        UPDATE hrs 
        SET first_name = %s, last_name = %s, email = %s
        WHERE user_id = %s
        """, (first_name, last_name, email, user_id))
        
        conn.commit()
        return True, "HR staff information updated successfully"
        
    except Error as e:
        print(f"Error updating HR staff: {e}")
        error_message = str(e)
        
        # Handle specific database constraint errors
        if "chk_hr_names" in error_message:
            return False, "First and last names must be at least 2 characters long"
        elif "chk_hr_email" in error_message:
            return False, "Email must end with @nexacare.med"
        else:
            return False, f"Error updating HR staff: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_patients():
    """
    Retrieve all patients from the database.
    Returns a list of patient dictionaries.
    """
    conn = get_connection()
    if conn is None:
        return []
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT user_id, first_name, last_name, email, phone_number
            FROM users
            WHERE role = 'patient'
            ORDER BY first_name, last_name
        """)
        
        patients = cursor.fetchall()
        return patients
    except Error as e:
        print(f"Error fetching patients: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_user_by_id(user_id):
    """
    Retrieve a user by their ID.
    Returns a user dictionary or None if not found.
    """
    conn = get_connection()
    if conn is None:
        return None
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT user_id, first_name, last_name, email, role, is_verified
            FROM users
            WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def verify_user(user_id):
    """
    Mark a user as verified.
    Returns True if successful, False otherwise.
    """
    conn = get_connection()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users
            SET is_verified = TRUE
            WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        return True
    except Error as e:
        print(f"Error verifying user: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(first_name, last_name, email, password, role, phone_number=None):
    """
    Create a new user in the database.
    Returns the user_id if successful, None otherwise.
    """
    conn = get_connection()
    if conn is None:
        return None
        
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password, role, phone_number, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, password, role, phone_number, role != 'doctor'))
        
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error creating user: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def authenticate_user(email, password):
    """
    Authenticate a user with email and password.
    Returns a user dictionary if successful, None otherwise.
    """
    conn = get_connection()
    if conn is None:
        return None
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT user_id, first_name, last_name, email, role, is_verified
            FROM users
            WHERE email = %s AND password = %s
        """, (email, password))
        
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
