import sqlite3
import hashlib
import secrets
import os


DATABASE = "users.db"


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    return sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )


def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return password_hash, salt


def verify_password(password, stored_hash, salt):

    password_hash, _ = hash_password(
        password,
        salt
    )

    return secrets.compare_digest(
        password_hash,
        stored_hash
    )


# =========================================================
# REGISTER
# =========================================================

def register_user(
    username,
    email,
    password
):

    username = username.strip()
    email = email.strip().lower()

    if not username:
        return False, "Username is required."

    if not email:
        return False, "Email is required."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        OR email = ?
        """,
        (username, email)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        conn.close()

        return False, "Username or email already exists."

    password_hash, salt = hash_password(
        password
    )

    cursor.execute(
        """
        INSERT INTO users
        (
            username,
            email,
            password_hash,
            salt
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            email,
            password_hash,
            salt
        )
    )

    conn.commit()

    conn.close()

    return True, "Account created successfully."


# =========================================================
# LOGIN
# =========================================================

def login_user(
    username,
    password
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            email,
            password_hash,
            salt
        FROM users
        WHERE username = ?
        OR email = ?
        """,
        (
            username.strip(),
            username.strip().lower()
        )
    )

    user = cursor.fetchone()

    conn.close()

    if not user:

        return None

    user_id = user[0]
    db_username = user[1]
    email = user[2]
    password_hash = user[3]
    salt = user[4]

    if verify_password(
        password,
        password_hash,
        salt
    ):

        return {
            "id": user_id,
            "username": db_username,
            "email": email
        }

    return None


# =========================================================
# USER
# =========================================================

def get_user(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    return {
        "id": user[0],
        "username": user[1],
        "email": user[2]
    }


# Initialize database

init_db()