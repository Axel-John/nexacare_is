from database import get_connection

def get_user(email, password, role):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role=?",
            (email, password, role)
        ).fetchone()
