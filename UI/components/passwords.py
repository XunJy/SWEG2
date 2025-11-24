import bcrypt
# PASSWORD ENCRPYTION
#-------------------------

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(hashed_pw, attempt):
    return bcrypt.checkpw(attempt.encode("utf-8"), hashed_pw.encode("utf-8"))
