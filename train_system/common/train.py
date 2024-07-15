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
        self.speed = 0 # suggested speed
        self.authority = 0 # authority
        self.stops = []
        self.arrival_times = []

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
    
def time_to_seconds(time_str: str):

    """
    Converts a time string in the format 'HH:MM' to the number of seconds since midnight.

    Args:
        time_str (str): The time string to convert.

    Returns:
        int: The number of seconds since midnight.
    """

    hours, minutes = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60