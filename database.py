import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="nexacare_db"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def init_db():
    # First create the database if it doesn't exist
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS nexacare_db")
        conn.close()
    except Error as e:
        print(f"Error creating database: {e}")
        return

    # Now connect to the database and create tables
    try:
        conn = get_connection()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        # Create doctors table
        cursor.execute(r"""
        CREATE TABLE IF NOT EXISTS doctors (
            user_id VARCHAR(16) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_doc_names CHECK (
                LENGTH(first_name) >= 2 AND
                LENGTH(last_name) >= 2
            ),
            CONSTRAINT chk_doc_email CHECK (
                email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            ),
            CONSTRAINT chk_doc_password CHECK (LENGTH(password) >= 8)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Create hrs table
        cursor.execute(r"""
        CREATE TABLE IF NOT EXISTS hrs (
            user_id VARCHAR(16) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_hr_names CHECK (
                LENGTH(first_name) >= 2 AND
                LENGTH(last_name) >= 2
            ),
            CONSTRAINT chk_hr_email CHECK (
                email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            ),
            CONSTRAINT chk_hr_password CHECK (LENGTH(password) >= 8)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Create admins table
        cursor.execute(r"""
        CREATE TABLE IF NOT EXISTS admins (
            user_id VARCHAR(16) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_admin_names CHECK (
                LENGTH(first_name) >= 2 AND
                LENGTH(last_name) >= 2
            ),
            CONSTRAINT chk_admin_email CHECK (
                email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            ),
            CONSTRAINT chk_admin_password CHECK (LENGTH(password) >= 8)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Create patients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT,
            gender ENUM('Male', 'Female', 'Other'),
            diagnosis TEXT,
            doctor_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        conn.commit()

        # Create initial admin account
        success, message = create_initial_admin()
        if success:
            print("Initial admin account created successfully")
        else:
            print(f"Note: {message}")

    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def generate_user_id(role: str) -> str:
    try:
        conn = get_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        prefix = "D" if role == "Doctor" else ("H" if role == "HR" else "A")
        year = "2025"
        table = "doctors" if role == "Doctor" else ("hrs" if role == "HR" else "admins")
        cursor.execute(f"SELECT user_id FROM {table} ORDER BY user_id DESC LIMIT 1")
        row = cursor.fetchone()
        next_num = 1
        if row and row[0]:
            # Extract the numeric part from the user_id
            try:
                last_num = int(row[0][5:])
                next_num = last_num + 1
            except Exception:
                next_num = 1
        user_id = f"{year}{prefix}{next_num:04d}"
        return user_id
    except Exception as e:
        print(f"Error generating user ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(first_name: str, last_name: str, email: str, password: str, role: str) -> tuple[bool, str, str]:
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
        if "Duplicate entry" in str(e):
            return False, "Email already registered", None
        return False, "Error creating account", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def check_email_exists(email: str, role: str) -> bool:
    try:
        conn = get_connection()
        if conn is None:
            return False
        table = "doctors" if role == "Doctor" else ("hrs" if role == "HR" else "admins")
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE email = %s", (email,))
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        print(f"Error checking email: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_initial_admin():
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute("SELECT COUNT(*) FROM admins WHERE user_id = '2025A0001'")
        if cursor.fetchone()[0] > 0:
            return False, "Initial admin account already exists"
        
        # Insert the admin account
        cursor.execute("""
        INSERT INTO admins (user_id, first_name, last_name, email, password)
        VALUES ('2025A0001', 'Axel', 'Admin', 'admin@nexacare.com', 'admin123')
        """)
        
        conn.commit()
        return True, "Initial admin account created successfully"
        
    except Error as e:
        print(f"Error creating initial admin: {e}")
        return False, f"Error creating initial admin: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
