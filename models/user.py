from database import get_connection
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
        cursor.execute("SELECT user_id, first_name, last_name, email FROM doctors")
        doctors = cursor.fetchall()
        return doctors
        
    except Error as e:
        print(f"Error getting doctors: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(first_name: str, last_name: str, email: str, password: str, role: str) -> tuple:
    """
    Create a new user (doctor, HR, or admin) in the database
    Returns: (success: bool, message: str, user_id: str)
    """
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed", None
            
        cursor = conn.cursor(dictionary=True)
        table = "doctors" if role == "Doctor" else ("hrs" if role == "HR" else "admins")
        
        # Check if email already exists
        cursor.execute(f"SELECT email FROM {table} WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "Email already exists", None
        
        # Generate user ID based on role and current count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count'] + 1
        year = "2025"  # You might want to make this dynamic
        role_prefix = "D" if role == "Doctor" else ("H" if role == "HR" else "A")
        user_id = f"{year}{role_prefix}{str(count).zfill(4)}"
        
        # Insert new user
        cursor.execute(
            f"INSERT INTO {table} (user_id, first_name, last_name, email, password) "
            f"VALUES (%s, %s, %s, %s, %s)",
            (user_id, first_name, last_name, email, password)
        )
        conn.commit()
        
        return True, "User created successfully", user_id
        
    except Error as e:
        print(f"Error creating user: {e}")
        return False, f"Database error: {str(e)}", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
