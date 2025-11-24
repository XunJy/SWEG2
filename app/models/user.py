import bcrypt
    #this is a hashsing package to store the passwords better
import uuid
import sqlite3
from ..db.database import *
from pydantic import BaseModel
from secrets import token_urlsafe
from fastapi import HTTPException

#-------------------------
# USER CLASS
#-------------------------

class UserCreate(BaseModel):
    # user_id : str
        #this is generated automatically so mustnt be provided by user
    first_name: str
    last_name: str
    email: str
    password: str
    # recovery_code: str
        #this can be generated automatically too 
    admin: bool = False

class UserRead(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    admin: bool
    # No password or recovery code for read operations (security reasons)

# class UserOld:
#     def __init__(self,user_id, first_name, last_name, email, password, recovery_code, admin):
#         self.user_id = user_id
#         self.first_name = first_name
#         self.last_name = last_name
#         self.email = email
#         self.password = password  # stored hashed
#         self.recovery_code = recovery_code
#         self.admin = admin

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.email})"


#-------------------------
# PASSWORD ENCRPYTION
#-------------------------

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(hashed_pw, attempt):
    return bcrypt.checkpw(attempt.encode("utf-8"), hashed_pw.encode("utf-8"))

#-------------------------
# CHECK SYS ADMIN STATUS
#-------------------------
def is_admin(user_id):
    """Check if a user is a system admin."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        cursor.execute("SELECT admin FROM user WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return bool(row and row[0] == 1)

#-------------------------
# USER CRUD
#-------------------------
#CREATE
def create_user(user: UserCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            user_id = str(uuid.uuid4())
            recovery_code = token_urlsafe(16)

            cursor.execute("""
                INSERT INTO user (user_id, first_name, last_name, email, password, recovery_code, admin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user.first_name,
                user.last_name,
                user.email,
                hash_password(user.password),
                recovery_code,
                user.admin
            ))
            conn.commit()
            return user_id, recovery_code

        except sqlite3.IntegrityError:
            return None, None

# READ USER BY EMAIL
def read_user_by_email(email_to_find: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, first_name, last_name, email, password, recovery_code, admin
            FROM user
            WHERE email = ?
        """, (email_to_find,))
        row = cursor.fetchone()

    if row:
        return {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "password": row[4],
            "recovery_code": row[5],
            "admin": bool(row[6])
        }
    return None

# read user by user_id
def read_user_by_id(user_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, first_name, last_name, email, password, recovery_code, admin
            FROM user
            WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
    if row:
        return {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "password": row[4],
            "recovery_code": row[5],
            "admin": bool(row[6])
        }
    return None

# UPDATE USER NAME
def update_user_name(email: str, password: str, new_first: str, new_last: str):
    user = read_user_by_email(email)
    if not user or not check_password(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user SET first_name = ?, last_name = ? WHERE email = ?
        """, (new_first, new_last, email))
        conn.commit()
    return {"message": "Name updated successfully"}


# UPDATE USER PASSWORD
def update_user_password(email: str, recovery_code: str, new_password: str):
    user = read_user_by_email(email)
    if not user or user["recovery_code"] != recovery_code:
        raise HTTPException(status_code=401, detail="Invalid email or recovery code")

    hashed_pw = hash_password(new_password)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET password = ? WHERE email = ?", (hashed_pw, email))
        conn.commit()
    return {"message": "Password updated successfully"}


# UPDATE USER EMAIL
def update_user_email(current_email: str, password: str, new_email: str):
    user = read_user_by_email(current_email)
    if not user or not check_password(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE user SET email = ? WHERE email = ?", (new_email, current_email))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="This email address is already in use")
    return {"message": f"Email updated from '{current_email}' to '{new_email}'"}


# DELETE USER
def delete_user(email: str, password: str):
    user = read_user_by_email(email)
    if not user or not check_password(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE email = ?", (email,))
        conn.commit()
    return {"message": f"Account '{email}' deleted successfully"}

