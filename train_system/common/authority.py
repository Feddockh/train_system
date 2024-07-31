# train_system/common/authority.py

class Authority:
<<<<<<< HEAD
    def __init__(self, distance: float, stop_block: int = None) -> None:
        self.authority = f"{distance}:"
        if stop_block:
            self.authority = f"{distance}:{stop_block}"
=======
    def __init__(self, distance: float, stop_block: int) -> None:
        self.authority = f"{distance}:{stop_block}"
>>>>>>> 85e7551787be2c77b660fa047d08c46ed7dfe833

    def __repr__(self) -> str:
        return f"{self.authority}"
    
    def set_distance(self, distance: float) -> None:
        self.authority = f"{distance}:{self.get_stop_block()}"
    
    def get_distance(self) -> float:
<<<<<<< HEAD
        return self.authority.split(":")[0]
=======
        return float(self.authority.split(":")[0])
>>>>>>> 85e7551787be2c77b660fa047d08c46ed7dfe833
    
    def set_stop_block(self, stop_block: int) -> None:
        self.authority = f"{self.get_distance()}:{stop_block}"
    
    def get_stop_block(self) -> int:
        if len(self.authority.split(":")[1]) > 1:
            return int(self.authority.split(":")[1])
        return None
    