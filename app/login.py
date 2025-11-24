from user import read_user
from logs import log_action

#-----------
# LOGIN
#-----------
def login(email, password_attempt):
    """
    Attempt to log a user in.
    Returns the User object if successful, or None otherwise.
    """
    user = read_user(email)
    if not user:
        return None

    if user.check_password(password_attempt):
        log_action(f"User {user.user_id} logged in successfully.")
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
    return None  # return None to represent 'no user is logged in'
