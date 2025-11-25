from app.models.user import read_user_by_email, check_password
from app.logs import log_action

#-----------
# LOGIN
#-----------
def login(email, password_attempt):
    """
    Attempt to log a user in.
    Returns the User object if successful, or None otherwise.
    """
    user = read_user_by_email(email)
    if not user:
        return None

    if check_password(user["password"], password_attempt):
        log_action(user["user_id"], f"User {user['user_id']} logged in successfully.")
        return user

    return None  # Incorrect password

#USAGE:
    # current_user = login(email, password)
    # user is either a User object or None

#-----------
# LOGOUT
#-----------
def logout(current_user):
    """
    Logs out the user by simply clearing the user object reference.
    """
    if current_user:
        log_action(current_user.get("user_id", "unknown"), "User logged out")
    return None  # return None to represent 'no user is logged in'
