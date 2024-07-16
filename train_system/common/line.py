# train_system/common/line.py

import os
import json
import pandas as pd
from typing import List
from PyQt6.QtCore import QObject, pyqtSignal

from train_system.common.track_block import TrackBlock
from train_system.common.station import Station

class Line(QObject):

    # Signals to notify updates (block number, attribute value)
    track_block_suggested_speed_updated = pyqtSignal(int, int)
    track_block_authority_updated = pyqtSignal(int, int)
    track_block_occupancy_updated = pyqtSignal(int, bool)
    track_block_switch_position_updated = pyqtSignal(int, int)
    track_block_crossing_signal_updated = pyqtSignal(int, int)
    track_block_under_maintenance_updated = pyqtSignal(int, bool)

    def __init__(self, name: str) -> None:
        super().__init__()

        """
        Initializes the Line object.
        
        Args:
            name (str): The name of the train line.
        
        Returns:
            None
        """

        self.name = name
        self.track_blocks: List[TrackBlock] = []
        self.yard: int = None
        self.to_yard: List[int] = []
        self.from_yard: List[int] = []
        self.past_yard: List[int] = []
        self.default_route: List[int] = []

    def __repr__(self) -> str:

        """
        Returns a string representation of the Line object.
        
        Returns:
            str: String representation of the Line object.
        """

        blocks_repr = "\n".join(
            repr(block) for block in self.track_blocks
        )

        res = (
            f"Line:          {self.name}\n"
            f"track_blocks:  [\n{blocks_repr}\n]\n"
            f"yard:          {self.yard}\n"
            f"to_yard:       {self.to_yard}\n"
            f"from_yard:     {self.from_yard}\n"
            f"past_yard:     {self.past_yard}\n"
            f"default_route: {self.default_route}"
        )

        return res

    def add_track_block(self, track_block: TrackBlock) -> None:
        self.track_blocks.append(track_block)
        self.connect_signals(track_block)

    def set_track_block(self, track_block: TrackBlock) -> None:
        self.track_blocks[track_block.number - 1] = track_block
        self.connect_signals(track_block)

    def connect_signals(self, track_block: TrackBlock) -> None:
        track_block.suggested_speed_updated.connect(lambda new_speed, blk=track_block: self.track_block_suggested_speed_updated.emit(blk.number, new_speed))
        track_block.authority_updated.connect(lambda new_authority, blk=track_block: self.track_block_authority_updated.emit(blk.number, new_authority))
        track_block.occupancy_updated.connect(lambda new_occupancy, blk=track_block: self.track_block_occupancy_updated.emit(blk.number, new_occupancy))
        track_block.switch_position_updated.connect(lambda new_position, blk=track_block: self.track_block_switch_position_updated.emit(blk.number, new_position))
        track_block.crossing_signal_updated.connect(lambda new_signal, blk=track_block: self.track_block_crossing_signal_updated.emit(blk.number, new_signal))
        track_block.under_maintenance_updated.connect(lambda new_maintenance, blk=track_block: self.track_block_under_maintenance_updated.emit(blk.number, new_maintenance))

    def get_track_block(self, number: int) -> TrackBlock:

        """
        Retrieves a track block by its number.
        
        Args:
            number (int): The block number to retrieve.
        
        Returns:
            TrackBlock: The retrieved TrackBlock object.
        """

        try:
            return self.track_blocks[number - 1]
        except IndexError:
            print(f"Track block {number} not found.")
            return None

    def load_track_blocks(self, file_path: str = None) -> None:

        """
        Loads track blocks from an Excel file.
        
        Args:
            file_path (str): The path to the Excel file.
        
        Returns:
            None
        """
        
        if not file_path:
            file_path = os.path.abspath(os.path.join("system_data\\lines", f"{self.name.lower()}_line.xlsx"))

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

        for _, row in df.iterrows():
            connecting_blocks = [int(block.strip()) for block in str(row['Connecting Blocks']).split(',') if block.strip().isdigit()]
            next_blocks = [int(block.strip()) for block in str(row['Initial Next Blocks']).split(',') if block.strip().isdigit()]
            station = row['Station'] if not pd.isna(row['Station']) and str(row['Station']).strip() else ""
            station_side = row['Station Side'] if not pd.isna(row['Station Side']) and str(row['Station Side']).strip() else ""
            switch_options = [int(block.strip()) for block in str(row['Switch Options']).split(',') if block.strip().isdigit()]
            block = TrackBlock(
                line=row['Line'],
                section=row['Section'],
                number=row['Block Number'],
                length=row['Block Length (m)'],
                grade=row['Block Grade (%)'],
                speed_limit=row['Speed Limit (Km/Hr)'],
                elevation=row['ELEVATION (M)'],
                cumulative_elevation=row['CUMALTIVE ELEVATION (M)'],
                connecting_blocks=connecting_blocks,
                next_blocks=next_blocks,
                station=station,
                station_side=station_side,
                switch_options=switch_options
            )
            self.add_track_block(block)

    def load_routes(self, file_path: str = None) -> None:

        if not file_path:
            file_path = os.path.abspath(os.path.join("system_data\\routes", f"{self.name.lower()}_routes.json"))

        with open(file_path, 'r') as file:
            data = json.load(file)

        self.yard = data['yard']
        self.to_yard = data['to_yard']
        self.from_yard = data['from_yard']
        self.past_yard = data['past_yard']
        self.default_route = data['default_route']

    def get_path(self, start: int, end: int) -> List[int]:

        path = []

        # Determine the path if we start from the yard
        if start == self.yard:

            # If the end block is the yard, return the yard
            if end == self.yard:
                path = [start]

            # If the end block is in the "from yard" segment, return the path from the yard to the block in the "from yard" segment
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = [start] + self.from_yard[:end_index + 1]
            
            # If the end block is in the "default route" segment, return the path from the yard to the block in the "default route" segment
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = [start] + self.from_yard + self.default_route[:end_index + 1]

            # If the end block is in the "to yard" segment, return the path from the yard to the block in the "to yard" segment
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = [start] + self.from_yard + self.default_route + self.to_yard[:end_index + 1]

            # If the end block is in the "past yard" segment, return the path from the yard to the block in the "past yard" segment
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = [start] + self.from_yard + self.default_route + self.past_yard[:end_index + 1]

            # If the end block is not found, return an error message
            else:
                print(f"Error: No path found between blocks {start} and {end}.")
        
        # Determine the path if we start in the "from yard" segment
        elif start in self.from_yard:
           
            # Get the index of the start block in the "from yard" route segment
            start_index = self.search_route(start, self.from_yard)

            # If the end block is the yard, return the path from the start block to the yard
            if end == self.yard:
                path = self.from_yard[start_index:] + self.default_route + self.to_yard + [self.yard]

            # If the end block is also in the "from yard" segment, return the path between the two blocks
            elif end == self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                if start_index < end_index:
                    path = self.from_yard[start_index:end_index + 1]

                # If the end block is before the start block in the "from yard" segment, the path wraps around the entire line
                else:
                    path = self.from_yard[start_index:] + self.default_route + self.to_yard + [self.yard] + self.from_yard[:end_index + 1]

            # If the end block is in the "default route" segment, return the path from the start block to the block in the "default route" segment
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = self.from_yard[start_index:] + self.default_route[:end_index + 1]

            # If the end block is in the "to yard" segment, return the path from the start block to the block in the "to yard" segment
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = self.from_yard[start_index:] + self.default_route + self.to_yard[:end_index + 1]

            # If the end block is in the "past yard" segment, return the path from the start block to the block in the "past yard" segment
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = self.from_yard[start_index:] + self.default_route + self.past_yard[:end_index + 1]

            # If the end block is not found, return an error message
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

        # Determine the path if we start in the "default route" segment
        elif start in self.default_route:

            # Get the index of the start block in the "default route" route segment
            start_index = self.search_route(start, self.default_route)

            # If the end block is the yard, return the path from the start block to the yard
            if end == self.yard:
                path = self.default_route[start_index:] + self.to_yard + [self.yard]

            # If the end block is in the "from yard" segment, return the path from the start block to the block in the "from yard" segment
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = self.default_route[start_index:] + self.to_yard + [self.yard] + self.from_yard[:end_index + 1]

            # If the end block is also in the "default route" segment, return the path between the two blocks
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                if start_index < end_index:
                    path = self.default_route[start_index:end_index + 1]

                # If the end block is before the start block in the "default route" segment, the path wraps around the entire line
                else:
                    path = self.default_route[start_index:] + self.past_yard + self.default_route[:end_index + 1]

            # If the end block is in the "to yard" segment, return the path from the start block to the block in the "to yard" segment
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = self.default_route[start_index:] + self.to_yard[:end_index + 1]

            # If the end block is in the "past yard" segment, return the path from the start block to the block in the "past yard" segment
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = self.default_route[start_index:] + self.past_yard[:end_index + 1]

            # If the end block is not found, return an error message
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

                





        return path
    
    # Return the index of the first occurence of the block in the route segment
    def search_route(self, block: int, route_segment: List[int]) -> int:
        for i in range(len(route_segment)):
            if route_segment[i] == block:
                return i


    # def get_distance(self, start: int, end: int):

    #     # recursively search for the path between the two blocks
    #     path = []
    #     self.path_search([], start, end, path)

    #     # if the path is not found, return -1
    #     if not path:
    #         return -1
        
    #     # calculate the distance between the two blocks (or the first occupied/under_maintenance block along the path)
    #     distance = 0
    #     for i in range(len(path) - 1):
    #         block = self.get_track_block(path[i])
    #         if block.occupancy or block.under_maintenance:
    #             break
    #         else:
    #             distance += block.length

    #     return distance

    # def path_search(self, closed: list[int], start: int, end: int, path: list[int]) -> None:
    
    #         # If the start and end blocks are the same, return the distance
    #         if start == end:
    #             return path
            
    #         # Add the current block to the closed list
    #         closed.append(start)
    #         path.append(start)
    
    #         # Get the current block
    #         current_block = self.get_track_block(start)
    #         # print("Current Block: " + str(current_block.number))
    
    #         # If the current block is not found, return -1
    #         if not current_block:
    #             path.pop()
    #             return -1
    
    #         # For each connecting block
    #         for connecting_block in current_block.connecting_blocks:

    #             # If the connecting block is in the closed list, skip it
    #             if connecting_block in closed:
    #                 continue

    #             # Recursively search for the path
    #             result = self.path_search(closed, connecting_block, end, path)
    
    #             # If the result is not -1, return the result
    #             if result != -1:
    #                 return result
    
    #         # If the end block is not found, return -1
    #         path.pop()
    #         return -1

if __name__ == "__main__":
    line = Line('Green')
    line.load_track_blocks()
    line.load_routes()
    print(line)
