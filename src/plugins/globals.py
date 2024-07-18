# globals.py

from enum import Enum

class ChatMode(Enum):
    NORMAL = (0, "normal", "智障模式")
    SMART = (1, "smart", "智能模式")

    def __init__(self, code, mode_name, description):
        self.code = code
        self.node_name = mode_name
        self.description = description


