import bcrypt
import streamlit as st
from db import get_conn

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def signup_user(username, password, full_name, role, phone_number):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role, phone_number, is_approved) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hash_password(password), full_name, role, phone_number, 0)
        )
        conn.commit()
        return True, "Signup successful. Wait for admin approval."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, password_hash, role, is_approved FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return False, "User not found"

    db_username, db_hash, role, is_approved = row

    if not verify_password(password, db_hash):
        return False, "Invalid password"

    if is_approved == 0:
        return False, "Account pending approval"

    st.session_state["logged_in"] = True
    st.session_state["username"] = db_username
    st.session_state["role"] = role
    return True, "Login successful"

def logout():
    for key in ["logged_in", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
