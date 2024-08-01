# train_system/common/authority.py

class Authority:
    def __init__(self, distance: float, stop_block: int = None) -> None:
        self.authority = f"{distance}:"
        if stop_block:
            self.authority = f"{distance}:{stop_block}"

    def __repr__(self) -> str:
        return f"{self.authority}"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Authority):
            return False
        return self.authority == value.authority
    
    def set_distance(self, distance: float) -> None:
        self.authority = f"{distance}:{self.get_stop_block()}"
    
    def get_distance(self) -> float:
        return float(self.authority.split(":")[0])
    
    def set_stop_block(self, stop_block: int) -> None:
        self.authority = f"{self.get_distance()}:{stop_block}"
    
    def get_stop_block(self) -> int:
        if len(self.authority.split(":")[1]) > 1:
            return int(self.authority.split(":")[1])
        return None
    