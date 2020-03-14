from enum import Enum

class Roles_enum(Enum):
    ADMIN = 1
    USER  = 2

class Media_types_enum(Enum):
    txt = 1
    png = 2
    mp3 = 3
    mp4 = 4
    pdf = 5

class Tags_enum(Enum):
    Technology = 1
    Medicine   = 2
    Sports     = 3
    Science    = 4
    Academic   = 5
    Art        = 6
