
class Beacon:

    def __init__(self, data: bytes):
        
        """
        Initialize Beacon object containing 128 bytes max of data.
        """

        if data.__sizeof__() > 128:
            raise ValueError("data is larger than 128 bytes")
        
        self.data = data

    def __str__(self) -> str:
        return self.data