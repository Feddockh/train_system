# train_system.common.train.py

class Train:
    def __init__(self, train_id: int) -> None:

        """
        The Train class represents a train in the train system.

        Args:
            train_id (int): The unique identifier for the train.
        """

        self.train_id = train_id
        self.line = None
        self.block = None
        self.speed = 0
        self.authority = 0
        self.passenger_count = 0
        self.passenger_capacity = 0
        self.passenger_throughput = 0

    def __repr__(self) -> str:

        """
        String representation of the Train object.

        Returns:
            str: The string representation of the Train object.
        """

        return (
            f"Train:        {self.train_id}\n"
            f"Line:         {self.line}\n"
            f"Block:        {self.line}\n"
            f"Speed:        {self.line}\n"
            f"Authority:    {self.line}\n"
        )
        