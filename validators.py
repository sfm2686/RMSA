def is_username_valid(username):
    return len(username) <= 20 and len(username) >= 6 and username.isalnum()

def is_password_valid(password):
    return len(password) <= 20 and len(password) >= 8 and password.isalnum()
