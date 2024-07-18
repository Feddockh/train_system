from enum import Enum, auto

class TestbenchDatatype(Enum):
    ADD_OCC = auto()
    REM_OCC = auto()
    TIX = auto()
    SIG = auto()
    SWI = auto()