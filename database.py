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
        
        # Create doctors table first
        cursor.execute(r"""
        CREATE TABLE IF NOT EXISTS doctors (
            user_id VARCHAR(16) PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_doc_names CHECK (
                LENGTH(first_name) >= 2 AND
                LENGTH(last_name) >= 2
            ),
            CONSTRAINT chk_doc_email CHECK (
                email REGEXP '^[A-Za-z0-9._%+-]+@nexacare\.med$'
            ),
            CONSTRAINT chk_doc_password CHECK (LENGTH(password) >= 8)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        # Create patients table with doctor_id foreign key
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id VARCHAR(8) PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            birthdate DATE NOT NULL,
            gender ENUM('Male', 'Female', 'Other', 'Prefer not to say') NOT NULL,
            civil_status ENUM('Single', 'Married', 'Separated', 'Divorced', 'Widowed', 'Other') NOT NULL,
            phone VARCHAR(20) NOT NULL,
            address TEXT NOT NULL,
            emergency_contact_name VARCHAR(100) NOT NULL,
            emergency_contact_phone VARCHAR(20) NOT NULL,
            patient_id VARCHAR(20),
            visit_type ENUM('New Patient', 'Follow-up', 'Walk-in') NOT NULL DEFAULT 'New Patient',
            assigned_doctor VARCHAR(16),
            visit_date DATETIME,
            insurance_provider VARCHAR(100),
            referral_source ENUM('Walk-in', 'Friend', 'Facebook', 'Other'),
            allergies JSON,
            chronic_illnesses JSON,
            current_medications JSON,
            remarks TEXT,
            status ENUM('Pending', 'Scheduled', 'Completed', 'Cancelled', 'No Show') NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_patient_name CHECK (LENGTH(full_name) >= 2),
            CONSTRAINT chk_patient_phone CHECK (LENGTH(phone) >= 7),
            CONSTRAINT fk_patient_doctor
                FOREIGN KEY (assigned_doctor) 
                REFERENCES doctors(user_id) ON DELETE SET NULL
                ON UPDATE CASCADE
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
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT chk_hr_names CHECK (
                LENGTH(first_name) >= 2 AND
                LENGTH(last_name) >= 2
            ),
            CONSTRAINT chk_hr_email CHECK (
                email REGEXP '^[A-Za-z0-9._%+-]+@nexacare\.med$'
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
                email REGEXP '^[A-Za-z0-9._%+-]+@nexacare\.med$'
            ),
            CONSTRAINT chk_admin_password CHECK (LENGTH(password) >= 8)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Create appointments table with foreign key constraints
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            doctor_id VARCHAR(16) NOT NULL,
            appointment_date DATETIME NOT NULL,
            consultation_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        conn.commit()

        # Create initial admin account if it doesn't exist
        success, message = create_initial_admin()
        if success:
            print("Initial admin account created successfully")
        else:
            print(f"Note: {message}")

        # Create initial HR account if it doesn't exist
        success, message = create_initial_hr()
        if success:
            print("Initial HR account created successfully")
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

def create_user(first_name: str, last_name: str, email: str, password: str, role: str, 
                maiden_name: str = None, nickname: str = None, 
                favorite_media: str = None, birth_city: str = None) -> tuple[bool, str, str]:
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

        try:
            # Insert new user into the correct table
            cursor.execute(f"""
            INSERT INTO {table} (user_id, first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """, (user_id, first_name, last_name, email, password))
            
            # Only insert security questions if all fields are provided
            if all([maiden_name, nickname, favorite_media, birth_city]):
                try:
                    cursor.execute("""
                    INSERT INTO security_questions (user_id, maiden_name, nickname, favorite_media, birth_city)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, maiden_name, nickname, favorite_media, birth_city))
                except Error as e:
                    print(f"Warning: Could not save security questions: {e}")
                    # Continue even if security questions fail - they're optional
            
            conn.commit()
            return True, "Account created successfully", user_id
            
        except Error as e:
            if conn.in_transaction:
                conn.rollback()
            print(f"Error creating user: {e}")
            error_message = str(e)
            
            if "chk_doc_names" in error_message or "chk_hr_names" in error_message or "chk_admin_names" in error_message:
                return False, "First and last names must be at least 2 characters long", None
            elif "chk_doc_email" in error_message or "chk_hr_email" in error_message or "chk_admin_email" in error_message:
                return False, "Email must end with @nexacare.med", None
            elif "chk_doc_password" in error_message or "chk_hr_password" in error_message or "chk_admin_password" in error_message:
                return False, "Password must be at least 8 characters long", None
            elif "Duplicate entry" in error_message:
                return False, "Email already registered", None
            else:
                return False, f"Error creating account: {error_message}", None
                
    except Error as e:
        print(f"Error creating user: {e}")
        return False, f"Error creating account: {str(e)}", None
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
        VALUES ('2025A0001', 'Axel', 'Admin', 'admin@nexacare.med', 'admin123')
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

def get_all_doctors():
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

def get_all_hrs():
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

def add_patient(full_name: str, birthdate: str, gender: str, civil_status: str, phone: str, address: str = None,
                emergency_contact_name: str = None, emergency_contact_phone: str = None,
                patient_id: str = None, visit_type: str = "New Patient", assigned_doctor: str = None,
                visit_date: str = None, insurance_provider: str = None, referral_source: str = None,
                allergies: list = None, chronic_illnesses: list = None, current_medications: list = None,
                remarks: str = None, status: str = "Pending", photo_path: str = None) -> tuple[bool, str, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed", None
            
        cursor = conn.cursor()
        
        # Basic validation
        if not full_name:
            return False, "Full name is required", None
        if not birthdate:
            return False, "Birthdate is required", None
        if not gender or gender not in ['Male', 'Female', 'Other', 'Prefer not to say']:
            return False, "Valid gender is required", None
        if not civil_status or civil_status not in ['Single', 'Married', 'Separated', 'Divorced', 'Widowed', 'Other']:
            return False, "Valid civil status is required", None
        if not status or status not in ['Pending', 'Scheduled', 'Completed', 'Cancelled', 'No Show']:
            return False, "Valid status is required", None
        if visit_type and visit_type not in ['New Patient', 'Follow-up', 'Walk-in']:
            return False, "Invalid visit type", None

        try:
            # Generate patient ID if not provided
            if not patient_id:
                cursor.execute("SELECT COUNT(*) FROM patients")
                count = cursor.fetchone()[0]
                patient_id = f"NXCP{str(count + 1).zfill(4)}"
            
            # Convert list fields to JSON strings
            import json
            allergies_json = json.dumps(allergies) if allergies else json.dumps([])
            chronic_illnesses_json = json.dumps(chronic_illnesses) if chronic_illnesses else json.dumps([])
            current_medications_json = json.dumps(current_medications) if current_medications else json.dumps([])
            
            # Convert empty string to None for assigned_doctor
            doctor_id = assigned_doctor if assigned_doctor else None
            
            # Insert new patient
            cursor.execute("""
            INSERT INTO patients (
                id, full_name, birthdate, gender, civil_status, phone, address,
                emergency_contact_name, emergency_contact_phone, patient_id,
                visit_type, assigned_doctor, visit_date, insurance_provider, referral_source,
                allergies, chronic_illnesses, current_medications, remarks,
                status, photo_path, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                patient_id, full_name, birthdate, gender, civil_status, phone, address,
                emergency_contact_name, emergency_contact_phone, patient_id,
                visit_type, doctor_id, visit_date, insurance_provider, referral_source,
                allergies_json, chronic_illnesses_json, current_medications_json, remarks,
                status, photo_path
            ))
            
            conn.commit()
            return True, "Patient added successfully", patient_id
            
        except Error as e:
            if conn.in_transaction:
                conn.rollback()
            print(f"Error adding patient: {e}")
            return False, f"Error adding patient: {str(e)}", None
                
    except Error as e:
        print(f"Error adding patient: {e}")
        return False, f"Error adding patient: {str(e)}", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_patients():
    try:
        conn = get_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Try the query with the assigned_doctor join
            cursor.execute("""
            SELECT 
                p.*,
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name
            FROM patients p
            LEFT JOIN doctors d ON p.assigned_doctor = d.user_id
            ORDER BY p.created_at DESC
            """)
        except Error as e:
            # If the query fails, it's likely because the assigned_doctor column doesn't exist
            if "assigned_doctor" in str(e):
                # Run the query without the join
                cursor.execute("""
                SELECT 
                    p.*,
                    NULL as doctor_name
                FROM patients p
                ORDER BY p.created_at DESC
                """)
            else:
                # If it's a different error, re-raise it
                raise
                
        patients = cursor.fetchall()
        
        import json
        # Convert datetime objects to strings and parse JSON fields
        for patient in patients:
            if 'created_at' in patient and patient['created_at']:
                patient['created_at'] = patient['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Parse JSON fields
            for json_field in ['allergies', 'chronic_illnesses', 'current_medications']:
                if json_field in patient and patient[json_field]:
                    try:
                        if isinstance(patient[json_field], str):
                            patient[json_field] = json.loads(patient[json_field])
                    except json.JSONDecodeError:
                        # If JSON parsing fails, set to empty list
                        patient[json_field] = []
                else:
                    # Ensure the field exists in the patient dict
                    patient[json_field] = []
        
        return patients
    except Error as e:
        print(f"Error getting patients: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_patient_status(patient_id: int, new_status: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Validate status
        if new_status not in ['Scheduled', 'Pending', 'Completed', 'Cancelled', 'No Show']:
            return False, "Invalid status"
        
        # Update patient status
        cursor.execute("""
        UPDATE patients 
        SET status = %s 
        WHERE id = %s
        """, (new_status, patient_id))
        
        conn.commit()
        return True, "Patient status updated successfully"
        
    except Error as e:
        print(f"Error updating patient status: {e}")
        return False, f"Error updating patient status: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_patient(patient_id: str, full_name: str = None, birthdate: str = None, gender: str = None, civil_status: str = None,
                  phone: str = None, address: str = None, emergency_contact_name: str = None, emergency_contact_phone: str = None,
                  patient_custom_id: str = None, visit_type: str = None, assigned_doctor: str = None, visit_date: str = None,
                  insurance_provider: str = None, referral_source: str = None, allergies: list = None, chronic_illnesses: list = None,
                  current_medications: list = None, remarks: str = None, status: str = None, photo_path: str = None) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Basic validation
        if full_name is not None and not full_name:
            return False, "Full name cannot be empty"
        if gender is not None and gender not in ['Male', 'Female', 'Other', 'Prefer not to say']:
            return False, "Valid gender is required"
        if civil_status is not None and civil_status not in ['Single', 'Married', 'Separated', 'Divorced', 'Widowed', 'Other']:
            return False, "Valid civil status is required"
        if status is not None and status not in ['Pending', 'Scheduled', 'Completed', 'Cancelled', 'No Show']:
            return False, "Valid status is required"
        if visit_type is not None and visit_type not in ['New Patient', 'Follow-up', 'Walk-in']:
            return False, "Invalid visit type"

        try:
            # Build the update query dynamically based on provided fields
            update_fields = []
            params = []
            
            # Convert list fields to JSON strings if provided
            import json
            allergies_json = json.dumps(allergies) if allergies is not None else None
            chronic_illnesses_json = json.dumps(chronic_illnesses) if chronic_illnesses is not None else None
            current_medications_json = json.dumps(current_medications) if current_medications is not None else None
            
            # Convert empty string to None for assigned_doctor
            doctor_id = assigned_doctor if assigned_doctor else None
            
            fields = {
                'full_name': full_name,
                'birthdate': birthdate,
                'gender': gender,
                'civil_status': civil_status,
                'phone': phone,
                'address': address,
                'emergency_contact_name': emergency_contact_name,
                'emergency_contact_phone': emergency_contact_phone,
                'patient_id': patient_custom_id,
                'visit_type': visit_type,
                'assigned_doctor': doctor_id if assigned_doctor is not None else None,
                'visit_date': visit_date,
                'insurance_provider': insurance_provider,
                'referral_source': referral_source,
                'allergies': allergies_json,
                'chronic_illnesses': chronic_illnesses_json,
                'current_medications': current_medications_json,
                'remarks': remarks,
                'status': status,
                'photo_path': photo_path
            }
            
            for field, value in fields.items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return False, "No fields to update"
            
            # Add patient_id to params
            params.append(patient_id)
            
            query = f'''
            UPDATE patients 
            SET {', '.join(update_fields)}
            WHERE id = %s
            '''
            
            cursor.execute(query, params)
            conn.commit()
            return True, "Patient updated successfully"
            
        except Error as e:
            if conn.in_transaction:
                conn.rollback()
            print(f"Error updating patient: {e}")
            return False, f"Error updating patient: {str(e)}"
                
    except Error as e:
        print(f"Error updating patient: {e}")
        return False, f"Error updating patient: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_patient(patient_id: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        try:
            # Delete patient
            cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
            
            if cursor.rowcount == 0:
                return False, "Patient not found"
                
            conn.commit()
            return True, "Patient deleted successfully"
            
        except Error as e:
            if conn.in_transaction:
                conn.rollback()
            print(f"Error deleting patient: {e}")
            return False, f"Error deleting patient: {str(e)}"
                
    except Error as e:
        print(f"Error deleting patient: {e}")
        return False, f"Error deleting patient: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_patients_table():
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Drop the existing email constraint and add a new one
        try:
            cursor.execute("""
            ALTER TABLE patients
            DROP CONSTRAINT IF EXISTS chk_patient_email,
            ADD CONSTRAINT chk_patient_email CHECK (
                email IS NULL OR email LIKE '%@%.%'
            )
            """)
            
            conn.commit()
            return True, "Patients table updated successfully"
            
        except Error as e:
            if conn.in_transaction:
                conn.rollback()
            print(f"Error updating patients table: {e}")
            return False, f"Error updating patients table: {str(e)}"
                
    except Error as e:
        print(f"Error updating patients table: {e}")
        return False, f"Error updating patients table: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_hr(hr_data: dict) -> tuple[bool, str]:
    try:
        # Validate email format
        if not hr_data['email'].endswith('@nexacare.med'):
            return False, "Email must be in the format: username@nexacare.med"
            
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Update HR staff record
        cursor.execute("""
            UPDATE hrs 
            SET first_name = %s,
                last_name = %s,
                email = %s,
                password = %s,
                is_verified = %s
            WHERE user_id = %s
        """, (
            hr_data['first_name'],
            hr_data['last_name'],
            hr_data['email'],
            hr_data['password'],
            hr_data['is_verified'],
            hr_data['user_id']
        ))
        
        conn.commit()
        return True, "HR staff updated successfully"
        
    except Error as e:
        print(f"Error updating HR staff: {e}")
        return False, f"Error updating HR staff: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_initial_hr():
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Check if HR already exists
        cursor.execute("SELECT COUNT(*) FROM hrs WHERE user_id = '2025H0001'")
        if cursor.fetchone()[0] > 0:
            return False, "Initial HR account already exists"
        
        # Insert the HR account with a longer password
        cursor.execute("""
        INSERT INTO hrs (user_id, first_name, last_name, email, password, is_verified)
        VALUES ('2025H0001', 'HR', 'Manager', 'hr@nexacare.med', 'hrmanager123', TRUE)
        """)
        
        conn.commit()
        return True, "Initial HR account created successfully"
        
    except Error as e:
        print(f"Error creating initial HR: {e}")
        return False, f"Error creating initial HR: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def add_appointment(patient_id: int, doctor_id: str, appointment_date: str, 
                   consultation_type: str, status: str = "Scheduled", notes: str = None):
    """Add a new appointment to the database"""
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed", None
            
        cursor = conn.cursor()
        
        # Insert the appointment
        cursor.execute("""
        INSERT INTO appointments 
        (patient_id, doctor_id, appointment_date, consultation_type, status, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            patient_id,
            doctor_id,
            appointment_date,
            consultation_type,
            status,
            notes
        ))
        
        # Get the ID of the newly inserted appointment
        appointment_id = cursor.lastrowid
        
        conn.commit()
        return True, "Appointment added successfully", appointment_id
        
    except Error as e:
        if 'conn' in locals() and conn.is_connected() and conn.in_transaction:
            conn.rollback()
        print(f"Error adding appointment: {e}")
        return False, f"Error adding appointment: {str(e)}", None
    finally:
        if 'conn' in locals() and conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_all_appointments():
    """Get all appointments with patient and doctor information"""
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed", None
            
        cursor = conn.cursor(dictionary=True)
        
        # Get all appointments with patient and doctor names
        cursor.execute("""
        SELECT a.id, a.patient_id, a.doctor_id, a.appointment_date, a.consultation_type, 
               a.status, a.notes, a.created_at,
               CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
               CONCAT(d.first_name, ' ', d.last_name) AS doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.user_id
        ORDER BY a.appointment_date DESC
        """)
        
        appointments = cursor.fetchall()
        return True, "Appointments retrieved successfully", appointments
        
    except Error as e:
        print(f"Error retrieving appointments: {e}")
        return False, f"Error retrieving appointments: {str(e)}", None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def update_appointment_status(appointment_id: int, new_status: str):
    """Update the status of an appointment"""
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Update the appointment status
        cursor.execute("""
        UPDATE appointments
        SET status = %s
        WHERE id = %s
        """, (new_status, appointment_id))
        
        if cursor.rowcount == 0:
            return False, f"No appointment found with ID {appointment_id}"
        
        conn.commit()
        return True, "Appointment status updated successfully"
        
    except Error as e:
        if conn and conn.is_connected() and conn.in_transaction:
            conn.rollback()
        print(f"Error updating appointment status: {e}")
        return False, f"Error updating appointment status: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def delete_appointment(appointment_id: int):
    """Delete an appointment from the database"""
    try:
        conn = get_connection()
        if conn is None:
            return False, "Database connection failed"
            
        cursor = conn.cursor()
        
        # Delete the appointment
        cursor.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        
        if cursor.rowcount == 0:
            return False, f"No appointment found with ID {appointment_id}"
        
        conn.commit()
        return True, "Appointment deleted successfully"
        
    except Error as e:
        if conn and conn.is_connected() and conn.in_transaction:
            conn.rollback()
        print(f"Error deleting appointment: {e}")
        return False, f"Error deleting appointment: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
