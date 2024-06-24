# train_system/common/line.py

import pandas as pd
import os
import re
from train_system.common.track_block import TrackBlock
from train_system.common.station import Station

class Line:
    def __init__(self, name: str) -> None:

        """
        Initializes the Line object.
        
        Args:
            name (str): The name of the train line.
        
        Returns:
            None
        """

        self.name = name
        self.track_blocks = {}
        self.stations = []

    def __repr__(self) -> str:

        """
        Returns a string representation of the Line object.
        
        Returns:
            str: String representation of the Line object.
        """

        blocks_repr = "\n".join(
            repr(block) for block in self.track_blocks.values()
        )
        return f"Line(name={self.name}, track_blocks=[\n{blocks_repr}\n])"

    def add_track_block(self, track_block: TrackBlock) -> None:

        """
        Adds a track block to the line.
        
        Args:
            track_block (TrackBlock): The TrackBlock object to add.
        
        Returns:
            None
        """

        self.track_blocks[track_block.number] = track_block

    def get_track_block(self, number: int) -> TrackBlock:

        """
        Retrieves a track block by its number.
        
        Args:
            number (int): The block number to retrieve.
        
        Returns:
            TrackBlock: The retrieved TrackBlock object.
        """

        try:
            return self.track_blocks[number]
        except KeyError:
            print(f"Track block {number} not found.")
            return None

    def load_track_blocks(self, file_path: str) -> None:

        """
        Loads track blocks from an Excel file.
        
        Args:
            file_path (str): The path to the Excel file.
        
        Returns:
            None
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
                line=self.name,
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
            self.add_track_block(block)

        open = [1]
        closed = []
        self.connection_search(open, closed)
        self.station_search()

    def connection_search(self, open: list, closed: list) -> None:

        """
        Recursively establishes connections between track blocks.
        
        Args:
            open (list): List of block numbers to process.
            closed (list): List of processed block numbers.
        
        Returns:
            None
        """

        if not open:
            return

        block_number = open.pop(0)
        block = self.track_blocks[block_number]
        closed.append(block_number)

        match = None
        if block.infrastructure:
            match = re.search(r'SWITCH\s*\((.*?)\)', block.infrastructure)

        if match:
            connections = match.group(1).split(';')
            for connection in connections:
                start, end = map(int, connection.split('-'))
                next_block = self.get_track_block(end)

                if next_block not in block.connecting_blocks:
                    block.connecting_blocks.append(next_block)
                    next_block.connecting_blocks.append(block)

                if (next_block.number not in closed and 
                    next_block.number not in open):
                    open.append(next_block.number)
        else:
            if block_number + 1 > len(self.track_blocks):
                return

            next_block = self.get_track_block(block_number + 1)
            if not next_block.connecting_blocks:
                block.connecting_blocks.append(next_block)
                next_block.connecting_blocks.append(block)
            elif len(next_block.connecting_blocks) == 1:
                block.connecting_blocks.append(next_block)
                next_block.connecting_blocks.append(block)

            if (next_block.number not in open and
                next_block.number not in closed):
                open.append(next_block.number)

        self.connection_search(open, closed)

    def station_search(self) -> None:

        """
        Searches for station infrastructure and assigns to track blocks.
        
        Args:
            None
        
        Returns:
            None
        """

        # Check through all of the block values
        for block in self.track_blocks.values():

            # Check if the block has infrastructure
            if block.infrastructure:

                # Search for the station infrastructure
                match = re.search(r'STATION\s+(\w+)', block.infrastructure)

                # If the station infrastructure is found
                if match:

                    # create the station object
                    station_name = match.group(1)
                    station = Station(
                        name=station_name,
                        line=self.name,
                        block_number=block.number
                    )

                    # Add the station object to the list of stations on the line
                    self.stations.append(station)

                    # Assign the station to the block
                    block.station = station

    def get_distance(self, start: int, end: int) -> int:

        """
        Returns the distance between two track blocks.
        
        Args:
            start (int): The starting block number.
            end (int): The ending block number.
        
        Returns:
            int: The distance between the two blocks.
        """

        # recursively search for the distance between the two blocks
        return self.distance_search([], start, end, 0)
    
    def distance_search(self, closed: list[int], start: int, end: int, distance: int) -> int:
            
            """
            Recursively searches for the distance between two track blocks.
            
            Args:
                start (int): The starting block number.
                end (int): The ending block number.
                distance (int): The distance between the two blocks.
            
            Returns:
                int: The distance between the two blocks.
            """
    
            # If the start and end blocks are the same, return the distance
            if start == end:
                return distance
            
            # Add the current block to the closed list
            closed.append(start)
    
            # Get the current block
            current_block = self.get_track_block(start)
            # print("Current Block: " + str(current_block.number))
    
            # If the current block is not found, return -1
            if not current_block:
                return -1
    
            # For each connecting block
            for connecting_block in current_block.connecting_blocks:

                # If the connecting block is in the closed list, skip it
                if connecting_block.number in closed:
                    continue
    
                # Recursively search for the distance
                # print("Connecting Block: " + str(connecting_block.number))
                track_block_length = current_block.length
                result = self.distance_search(
                    closed, connecting_block.number, end, distance + track_block_length
                )
    
                # If the result is not -1, return the result
                if result != -1:
                    return result
    
            # If the end block is not found, return -1
            return -1

if __name__ == "__main__":
    file_path = (
        'C:/Users/hayde/OneDrive/Pitt/2024_Summer_Term/ECE 1140/'
        'Project/train_system/tests/blue_line.xlsx'
    )

    line = Line('Blue')
    line.load_track_blocks(file_path)
    line.station_search()
    print(line)
