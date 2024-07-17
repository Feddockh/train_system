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

    def connect_signals(self, track_block: TrackBlock) -> None:
        track_block.suggested_speed_updated.connect(lambda new_speed, blk=track_block: self.track_block_suggested_speed_updated.emit(blk.number, new_speed))
        track_block.authority_updated.connect(lambda new_authority, blk=track_block: self.track_block_authority_updated.emit(blk.number, new_authority))
        track_block.occupancy_updated.connect(lambda new_occupancy, blk=track_block: self.track_block_occupancy_updated.emit(blk.number, new_occupancy))
        track_block.switch_position_updated.connect(lambda new_position, blk=track_block: self.track_block_switch_position_updated.emit(blk.number, new_position))
        track_block.crossing_signal_updated.connect(lambda new_signal, blk=track_block: self.track_block_crossing_signal_updated.emit(blk.number, new_signal))
        track_block.under_maintenance_updated.connect(lambda new_maintenance, blk=track_block: self.track_block_under_maintenance_updated.emit(blk.number, new_maintenance))

    def get_path(self, start: int, end: int) -> List[int]:

        """
        Computes the path between two blocks on the line inclusive of the
        start and end blocks.

        Args:
            start (int): The starting block number.
            end (int): The ending block number.

        Returns:
            List[int]: The list of block numbers in the path.
        """

        path = []

        # Determine the path if we start from the yard
        if start == self.yard:
            if end == self.yard:
                path = [start]
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = [start] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = [start] + self.from_yard + self.default_route[:end_index + 1]
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = [start] + self.from_yard + self.default_route + self.to_yard[:end_index + 1]
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = [start] + self.from_yard + self.default_route + self.past_yard[:end_index + 1]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")
        
        # Determine the path if we start in the "from yard" segment
        elif start in self.from_yard:
            start_index = self.search_route(start, self.from_yard)
            if end == self.yard:
                path = self.from_yard[start_index:] + self.default_route + self.to_yard + [self.yard]
            elif end == self.from_yard:

                # Find the index of the end block in the "from yard" segment, ideally after the start block
                end_index = self.search_route(end, self.from_yard, start_index)
                if start_index < end_index:
                    path = self.from_yard[start_index:end_index + 1]
                
                # If the end block is before the start block in the "from yard" segment, the path wraps around the entire line
                else:
                    path = self.from_yard[start_index:] + self.default_route + self.to_yard + [self.yard] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = self.from_yard[start_index:] + self.default_route[:end_index + 1]
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = self.from_yard[start_index:] + self.default_route + self.to_yard[:end_index + 1]
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = self.from_yard[start_index:] + self.default_route + self.past_yard[:end_index + 1]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

        # Determine the path if we start in the "default route" segment
        elif start in self.default_route:
            start_index = self.search_route(start, self.default_route)
            if end == self.yard:
                path = self.default_route[start_index:] + self.to_yard + [self.yard]
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = self.default_route[start_index:] + self.to_yard + [self.yard] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route, start_index)
                if start_index < end_index:
                    path = self.default_route[start_index:end_index + 1]
                else:
                    path = self.default_route[start_index:] + self.past_yard + self.default_route[:end_index + 1]
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = self.default_route[start_index:] + self.to_yard[:end_index + 1]
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = self.default_route[start_index:] + self.past_yard[:end_index + 1]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

        # Determine the path if we start in the "to yard" segment
        elif start in self.to_yard:
            start_index = self.search_route(start, self.to_yard)
            if end == self.yard:
                path = self.to_yard[start_index:] + [self.yard]
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = self.to_yard[start_index:] + [self.yard] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = self.to_yard[start_index:] + [self.yard] + self.from_yard + self.default_route[:end_index + 1]
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard, start_index)
                if start_index < end_index:
                    path = self.to_yard[start_index:end_index + 1]
                else:
                    path = self.to_yard[start_index:] + [self.yard] + self.from_yard + self.default_route + self.to_yard[:end_index + 1]
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard)
                path = self.to_yard[start_index:] + [self.yard] + self.from_yard + self.default_route + self.past_yard[:end_index + 1]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")
        
        # Determine the path if we start in the "past yard" segment
        elif start in self.past_yard:
            start_index = self.search_route(start, self.past_yard)
            if end == self.yard:
                path = self.past_yard[start_index:] + self.default_route + self.to_yard + [self.yard]
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = self.past_yard[start_index:] + self.default_route + self.to_yard + [self.yard] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = self.past_yard[start_index:] + self.default_route[:end_index + 1]
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard)
                path = self.past_yard[start_index:] + self.default_route + self.to_yard[:end_index + 1]
            elif end in self.past_yard:
                end_index = self.search_route(end, self.past_yard, start_index)
                if start_index < end_index:
                    path = self.past_yard[start_index:end_index + 1]
                else:
                    path = self.past_yard[start_index:] + self.default_route + self.past_yard[:end_index + 1]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

        # If the start block is not found in any segment, return an error
        else:
            print(f"Error: No path found between blocks {start} and {end}.")

        return path
    
    def search_route(self, block_number: int, route_segment: List[int], seed: int = 0) -> int:

        # Try to return the block in front of the seed index
        if seed > 0:
            for i in range(seed, len(route_segment)):
                if route_segment[i] == block_number:
                    return i

        # If there is no block in front of the seed index, search the entire segment
        for i in range(len(route_segment)):
            if route_segment[i] == block_number:
                return i
        
        return -1

    def get_travel_time(self, path: List[int]) -> int:

        """
        Computes the travel time between two blocks on the line exclusive of
        the start and end blocks.

        Args:
            path (List[int]): The list of block numbers in the path.

        Returns:
            int: The time to travel (in seconds) between the two blocks.
        """

        time = 0
        for i in range(1, len(path) - 1):
            time += self.get_track_block(path[i]).traversal_time
        return time

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

if __name__ == "__main__":
    line = Line('Green')
    line.load_track_blocks()
    line.load_routes()
    print(line)

    target = 100
    path = line.get_path(line.yard, target)
    print(f"Path from yard to block {target}: {path}")