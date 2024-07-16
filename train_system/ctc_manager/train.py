# train_system.common.train.py

from typing import List

from train_system.common.line import Line


class Train:
    def __init__(self, train_id: int, line: Line) -> None:

        """
        The Train class represents a train in the train system.

        Args:
            train_id (int): The unique identifier for the train.
            line (Line): The line the train is running on.
        """

        self.train_id = train_id
        self.line = line

        self.current_block: int = None
        self.route: List[int] = []

        self.suggested_speed = 0
        self.authority = 0
        self.stops = []
        self.arrival_times = []

    def __repr__(self) -> str:

        """
        String representation of the Train object.

        Returns:
            str: The string representation of the Train object.
        """

        return (
            f"Train:          {self.train_id}\n"
            f"Line:           {self.line.name}\n"
            f"Current Block:  {self.current_block}\n"
            f"SuggestedSpeed: {self.suggested_speed}\n"
            f"Authority:      {self.authority}\n"
        )
    
    def set_stops(self, stops: List[int]) -> None:
        self.stops = stops