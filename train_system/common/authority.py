# train_system/common/authority.py

class Authority:
    def __init__(self, distance: float, stop_block: int = None) -> None:

        """
        Initializes a new Authority object stored as a string in the format "distance:stop_block".

        Args:
            distance (float): The distance of the authority.
            stop_block (int): The block number of the stop block.
        """

        self.authority = f"{distance}:{stop_block if stop_block is not None else ''}"

    def __repr__(self) -> str:

        """
        Returns a string representation of the Authority object.
        
        Returns:
            str: The string representation of the Authority object.
        """

        return f"{self.authority}"
    
    def __eq__(self, value: object) -> bool:

        """
        Returns True if the Authority object is equal to the given object, False otherwise.
        
        Args:
            value (object): The object to compare to.
            
        Returns:
            bool: True if the Authority object is equal to the given object, False otherwise.
        """

        if not isinstance(value, Authority):
            return False
        return self.authority == value.authority
    
    def __deepcopy__(self, memo) -> 'Authority':

        """
        Returns a deep copy of the Authority object.

        Args:
            memo: A dictionary that maps objects to the copies of those objects.
        
        Returns:
            Authority: A deep copy of the Authority object.
        """

        return Authority(self.get_distance(), self.get_stop_block())
    
    def set_distance(self, distance: float) -> None:

        """
        Sets the distance of the authority.

        Args:
            distance (float): The distance of the authority.
        """

        self.authority = f"{distance}:{self.get_stop_block() if self.get_stop_block() is not None else ''}"
    
    def get_distance(self) -> float:

        """
        Returns the distance of the authority.

        Returns:
            float: The distance of the authority.
        """

        return float(self.authority.split(":")[0])
    
    def set_stop_block(self, stop_block: int) -> None:

        """
        Sets the block number of the stop block.

        Args:
            stop_block (int): The block number of the stop block.
        """

        self.authority = f"{self.get_distance()}:{stop_block}"
    
    def get_stop_block(self) -> int:

        """
        Returns the block number of the stop block.

        Returns:
            int: The block number of the stop block.
        """

        stop_block_str = self.authority.split(":")[1]
        if stop_block_str:
            return int(stop_block_str)
        return None

    