from enum import Enum, auto

class DispatchMode(Enum):
    MANUAL_FIXED_BLOCK = auto()
    AUTOMATIC_FIXED_BLOCK = auto()
    MANUAL_MBO_OVERLAY = auto()
    AUTOMATIC_MBO_OVERLAY = auto()
    MAINENANCE = auto()