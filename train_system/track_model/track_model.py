# INPUTS
#
#  TRACK CONTROLLER
#   COMMANDED SPEED - INT
#   AUTHORITY - FLOAT
#   SWITCH POSITIONS - BOOL (FOR EACH BLOCK WITH A SWITCH)
#   SIGNAL STATUSES - BOOL (FOR EACH BLOCK WITH A SIGNAL)
#
#  USER - BUILDER
#   LAYOUT SPREADSHEET
#   BEACON DATA - STRING
#
#  USER - MURPHY
#   FAILURES - BOOL (FOR EACH BLOCK)
#
#  ENVIRONMENT
#   TEMPERATURE - INT
#
# OUTPUTS
#  
#  TRAIN MODEL
#   COMMANDED SPEED - INT
#   AUTHORITY - FLOAT
#   GRADE/ELEVATION - FLOAT/INT
#   BEACON DATA - STRING
#   POLARITY - INT (-1/1)
#
#  TRACK CONTROLLER
#   OCCUPANCY - BOOL (FOR EACH BLOCK)
#
#  CTC OFFICE
#   TICKET SALES - INT (FOR EACH STATION)
#
#
# ORGANIZATION
#
# UX
#  COMPLETELY REMOVED FROM MAIN - MAIN WILL CONTAIN AN INSTANCE OF UX OBJECT
#  DATA-ALTERING UX INPUTS (CREATE FAILURE, UPLOAD TRACK, TEST BENCH INPUTS, ETC) WILL CREATE A SIGNAL WITH A SLOT IN MAIN
#  ON OCCUPANCY UPDATE AND FAILURE UPDATE, SEND SIGNAL TO UX TO UPDATE MAP
#
# FUNCTIONS
#  SETTERS FOR ALL INPUTS, GETTERS FOR ALL OUTPUTS
#
# DATA
#  LIST OF BLOCKS FOR EACH LINE, LIST OF LINES FOR THE TRACK MODEL
#  START WITH HAYDEN'S LAYOUT SPREADSHEET PARSER AND MAP DRAWING TOOL FOR EACH PURPOSE RESPECTIVELY


import os
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.track_failures import TrackFailure

class TrackModel:

    def __init__(self, lines: list[Line]) -> None:

        self.temperature: int = 85
        self.heaters: bool = False
        self.stations_by_line: dict[str, dict[str, int]] = {}

        for line in lines:
            stations: dict[str, int] = {}
            for block in line.track_blocks:
                if type(block.station) == str:
                    stations[block.station] = 0
            self.stations_by_line[line.name] = stations


    def create_failure(self, block: TrackBlock, failure: TrackFailure) -> None:

        """
        Creates a track failure on a track block.

        Args:
            block (TrackBlock): The block to create a failure on.
            failure (TrackFailure): The type of failure to create on the track block.
        """

        block.track_failure(failure)


    def fix_failure(self, block: TrackBlock) -> None:

        """
        Remove any failure from a track block.

        Args:
            block (TrackBlock): The block to remove a failure from.
        """

        block.track_failure(TrackFailure.NONE)


    def sell_tickets(self, line: str, station: str, num: int) -> None:

        """
        Sell tickets at a station.

        Args:
            line (str): The name of the line that contains the station.
            station (str): The name of the station to sell tickets from.
            num (int): The number of tickets to sell.
        """

        if station in self.stations_by_line[line]:
            self.stations_by_line[line][station] += num

    def get_tickets(self, line: str) -> dict[str, int]:

        """
        Get tickets sold at stations and reset sales to 0.
        
        Args:
            line (str): The name of the line.
        Returns:
            dict[str, int]: Number of tickets sold by stations on line.
        """

        temp = self.stations_by_line[line].copy()
        for st in self.stations_by_line[line]:
            self.stations_by_line[line][st] = 0

        return temp
    
    def update_heaters(self) -> None:

        """
        Update heater state based on temperature
        """

        if self.temperature <= 36:
            self.heaters = True
        else:
            self.heaters = False
    

    @property
    def temperature(self) -> int:
        return self.temperature
    
    @temperature.setter
    def temperature(self, value: int):
        self.temperature = value
        self.update_heaters()
    

if __name__ == "__main__":
    line = Line('Blue')
    file_path = os.path.abspath(os.path.join("tests", "blue_line.xlsx"))
    line.load_track_blocks(file_path)

    model = TrackModel([line])
    model.sell_tickets('Blue', 'B', 4)
    model.sell_tickets('Blue', 'C', 11)
    print(model.get_tickets('Blue'))
    print(model.stations_by_line)