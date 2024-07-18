from enum import Enum, auto

class TrackFailure(Enum):
    NONE = auto()
    TRACK = auto()
    CIRCUIT = auto()
    POWER = auto()