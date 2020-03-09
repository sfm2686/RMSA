def is_username_valid(username):
    return len(username) <= 20 and username.isalnum()
