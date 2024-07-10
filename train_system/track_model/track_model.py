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
from pandas import pd
from train_system.common.track_block import TrackBlock
from train_system.common.station import Station
from train_system.common.crossing_signal import CrossingSignal
from train_system.common.line import Line
from train_system.common.track_failures import TrackFailure

class TrackModel:

    def __init__(self) -> None:

        self.lines = [Line("Red"), Line("Green")]

        self.ticket_sales = []


    def import_track(self, file_path: str) -> None:

        """
        Loads lines from an Excel file.
        
        Args:
            file_path (str): The path to the Excel file.
        """

        if not os.path.isfile(file_path):
            print(f"Error: The file {file_path} does not exist.")
            return
        
        try:
            df = pd.read_excel(file_path)
        except PermissionError:
            print(
                f"Error: Permission denied while trying to read the file "
                f"{file_path}."
            )
            return
        except Exception as e:
            print(
                f"Error: An error occurred while trying to read the file "
                f"{file_path}."
            )
            print(e)
            return

        for index, row in df.iterrows():
            block = TrackBlock(
                line=row['Line'],
                section=row['Section'],
                number=row['Block Number'],
                length=row['Block Length (m)'],
                grade=row['Block Grade (%)'],
                speed_limit=row['Speed Limit (Km/Hr)'],
                elevation=row['ELEVATION (M)'],
                cumulative_elevation=row['CUMALTIVE ELEVATION (M)'],
                infrastructure=row['Infrastructure']
                if not pd.isna(row['Infrastructure']) else None,
                station_side=row['Station Side']
                if not pd.isna(row['Station Side']) else None
            )
            for line in self.lines:
                if(block.line == line.name):
                    line.add_track_block(block)
                    break


        open = [1]
        closed = []
        for line in self.lines:
            line.connection_search(open, closed)
            line.station_search()
        

    def check_occupancy(self) -> None:

        """
        Updates block occupancies based on each train's distance travelled.

        Args:
            TODO: List of TrainModels
        """


    def create_failure(self, block: TrackBlock, failure: TrackFailure) -> None:

        """
        Creates a track failure on a track block.

        Args:
            block (TrackBlock): The block to create a failure on.
            failure (TrackFailure): The type of failure to create on the track block.
        """

        block.failure(failure)


    def fix_failure(self, block: TrackBlock) -> None:

        """
        Remove any failure from a track block.

        Args:
            block (TrackBlock): The block to remove a failure from.
        """

        block.failure(TrackFailure.NONE)


    def sell_tickets(self, station: str, num: int) -> None:

        """
        Sell tickets at a station.

        Args:
            station (str): The name of the station to sell tickets from.
            num (int): The number of tickets to sell.
        """