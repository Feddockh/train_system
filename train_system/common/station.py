# train_system.common.station.py

from typing import List, Tuple


class Station:
    def __init__(self, line: str, name: str, blocks: List[int] = None, sides: List[Tuple[int, int, str]] = None) -> None:
        
        """
        Initializes the Station object.

        Args:
            line (str): The line the station is on.
            name (str): The name of the station.
            blocks (List[int]): The block numbers the station is connected to.
            sides (List[Tuple[int, int, str]]): List of tuples containing previous block, current block, and side information.

        Returns:
            None
        """

        self.line = line
<<<<<<< HEAD
        self.name = name
        self.blocks = blocks
        self.sides = sides
    
    def __repr__(self):
        return (f"Station(line={self.line}, name={self.name}, blocks={self.blocks}, "
                f"sides={self.sides})")
=======
        self.connected_blocks = []

    def __repr__(self) -> str:

        """
        Returns a string representation of the Station object.

        Returns:
            str: String representation of the Station object.
        """

        return (
            f"Station {self.name}\n"
            f"Line: {self.line}\n"
            f"Block Number: {self.block_number}\n"
        )
>>>>>>> 5642103 (New and improved implementation of switches)

    def __eq__(self, other: object) -> bool:
        
        """
        Checks if two Station objects are equal.

        Args:
            value (object): The other Station object to compare with.

        Returns:
            bool: True if the Station objects are equal, False otherwise.

        Raises:
            TypeError: If the other object is not a Station.
        """

        if not isinstance(other, Station):
            raise TypeError(
                f"Expected a Station object, but got {type(other).__name__}"
            )
<<<<<<< HEAD
        return (self.line, self.name) == (other.line, other.name)
    
    def get_side(self, prev_block: int, current_block: int) -> str:
        
        """
        Gets the side of the station that is connected to the current block.

        Args:
            prev_block (int): The previous block number.
            current_block (int): The current block number.

        Returns:
            str: The side of the station that is connected to the current block.
        """

        for side in self.sides:
            if side[0] == prev_block and side[1] == current_block:
                return side[2]
        return None
=======
        return (self.name, self.line) == (
            other.name, other.line
        )
    
>>>>>>> 5642103 (New and improved implementation of switches)
