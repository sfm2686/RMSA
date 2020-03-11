import re

def is_username_valid(username):
    return len(username) <= 20 and len(username) >= 6 and username.isalnum()

def is_password_valid(password):
    return len(password) <= 20 and len(password) >= 8 and password.isalnum()

def is_group_name_valid(group_name):
    regex = re.compile("^[a-zA-Z ]*$") # to ensure only acceptable values are alphanumeric and spaces
    return len(group_name) <= 20 and len(group_name) >= 2 and regex.match(group_name)
