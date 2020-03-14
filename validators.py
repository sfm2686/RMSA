import re
from enums import *

def is_username_valid(username):
    return len(username) <= 20 and len(username) >= 6 and username.isalnum()

def is_password_valid(password):
    return len(password) <= 20 and len(password) >= 8

def is_group_name_valid(group_name):
    regex = re.compile("^[a-zA-Z0-9 ]{2,20}$") # to ensure only acceptable values are alphanumeric and spaces
    return regex.match(group_name)

def is_report_name_valid(name):
    # to ensure only acceptable values are alphanumeric and spaces and some special characters
    # regex = re.compile("^[a-zA-Z \-\!\(\)\_\.\,\?\:\^\`\~\'\%\$\*\&\@\#]*$")
    regex = re.compile("^[a-zA-Z0-9 \-\!\(\)\_\.\,\?\:\^\`\~\'\%\$\*\&\@\#]{4,60}$")
    return regex.match(name)

def is_report_desc_valid(desc):
    # to ensure only acceptable values are alphanumeric and spaces and some special characters
    # regex = re.compile("^[a-zA-Z \-\!\(\)\_\.\,\?\:\^\`\~\'\%\$\*\&\@\#]*$")
    regex = re.compile("^[a-zA-Z0-9 \-\!\(\)\_\.\,\?\:\;\^\`\~\'\%\$\*\&\@\#]{0,200}$")
    return regex.match(desc)

def is_filename_valid(name):
    # buidling '.ext1|.ext2...etc' string from allowed media types enum
    allowed_exts = ".|".join([e.name for e in Media_types_enum])
    allowed_exts = "." + allowed_exts
    regex = re.compile("^[\W\w\s]+\.[%s]{3}$" % allowed_exts)
    return regex.match(name)
