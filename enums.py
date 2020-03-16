from enum import Enum

class Roles_enum(Enum):
    ADMIN = 1
    USER  = 2

class Media_types_enum(Enum):
    pdf = 1
    txt = 2
    png = 3
    mp3 = 4
    mp4 = 5

class Tags_enum(Enum):
    Technology = 1
    Medicine   = 2
    Sports     = 3
    Science    = 4
    Academic   = 5
    Art        = 6
