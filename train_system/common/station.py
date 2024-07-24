# train_system.common.station.py

class Station:
    def __init__(self, line: str, block_number: int) -> None:

        """
        Initializes the Station object.

        Args:
            name (str): The name of the station.
            line (str): The line the station is on.
            block_number (int): The block number the station is on.

        Returns:
            None
        """

        self.name = name
        self.line = line
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
        return (self.name, self.line) == (
            other.name, other.line
        )
    
