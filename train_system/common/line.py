# train_system/common/line.py

import os
import json
import pandas as pd
import math
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from anytree import Node, RenderTree
from collections import deque

from train_system.common.track_block import TrackBlock
from train_system.common.track_switch import TrackSwitch
from train_system.common.station import Station

class Route:
    def __init__(self, line: str, yard: int, to_yard: List[int], from_yard: List[int], past_yard: List[int], default_route: List[int]) -> None:
        """
        Initializes the Route object.

        Args:
            line (str): The name of the train line.
            yard (int): The block number of the yard.
            to_yard (List[int]): The list of block numbers in the "to yard" segment.
            from_yard (List[int]): The list of block numbers in the "from yard" segment.
            past_yard (List[int]): The list of block numbers in the "past yard" segment.
            default_route (List[int]): The list of block numbers in the default route segment.
        """
        self.line = line
        self.yard = yard
        self.to_yard = to_yard
        self.from_yard = from_yard
        self.past_yard = past_yard
        self.default_route = default_route

        # Build the route tree
        self.root = Node(yard)
        self.build_tree()

    def build_tree(self):
        """
        Builds the route tree for the line.

                          root(yard)
                              |
                          from_yard
                              |
                        default_route
                     /                 \\
                 to_yard             past_yard
                    |                    |
                   yard            default_route
                  /            /                 \\
            from_yard     past_yard             to_yard
                                                   |
                                                  yard
        """
        # Create the root branch starting from the yard
        current_node = self.root
        for block_id in self.from_yard:
            current_node = Node(block_id, parent=current_node)
        for block_id in self.default_route:
            current_node = Node(block_id, parent=current_node)
        end_of_default_route_node = current_node

        # Create the to_yard branch starting from the end of the default route
        current_node = end_of_default_route_node
        for block_id in self.to_yard:
            current_node = Node(block_id, parent=current_node)
        current_node = Node(self.yard, parent=current_node)
        for block_id in self.from_yard:
            current_node = Node(block_id, parent=current_node)
        
        # Create the past_yard branch starting from the end of the default route
        current_node = end_of_default_route_node
        for block_id in self.past_yard:
            current_node = Node(block_id, parent=current_node)
        for block_id in self.default_route:
            current_node = Node(block_id, parent=current_node)
        end_of_default_route_node2 = current_node

        # Create the second past_yard branch starting from the end of the second default route
        current_node = end_of_default_route_node2
        for block_id in self.past_yard:
            current_node = Node(block_id, parent=current_node)
        
        # Create the second to_yard branch starting from the end of the second past yard
        current_node = end_of_default_route_node2
        for block_id in self.to_yard:
            current_node = Node(block_id, parent=current_node)
        current_node = Node(self.yard, parent=current_node)

    def bfs_find_path(self, prev: int, start: int, end: int) -> Optional[List[int]]:
        """
        Performs a breadth-first search to find the path from start to end after finding the first instance of (parent: prev, child: start).

        Args:
            prev (int): The parent block number to start the search from.
            start (int): The starting block number for the new search.
            end (int): The ending block number for the path search.

        Returns:
            Optional[List[int]]: The path from start to end if found, otherwise None.
        """
        def bfs_find_start_node(root: Node, prev: int, start: int) -> Optional[Node]:
            queue = deque([root])
            while queue:
                node = queue.popleft()
                for child in node.children:
                    if node.name == prev and child.name == start:
                        return child
                    queue.append(child)
            return None

        def bfs_find_path_from_node(start_node: Node, end: int) -> Optional[List[int]]:
            queue = deque([(start_node, [start_node.name])])
            while queue:
                current_node, path = queue.popleft()
                if current_node.name == end:
                    return path
                for child in current_node.children:
                    queue.append((child, path + [child.name]))
            return None

        # If start is the yard block, start from the root
        if start == self.yard:
            start_node = self.root
        else:
            start_node = bfs_find_start_node(self.root, prev, start)

        if start_node:
            return bfs_find_path_from_node(start_node, end)
        return None
    

class Line(QObject):

    # Signals to notify track block updates (block number, attribute value)
    track_block_suggested_speed_updated = pyqtSignal(int, int)
    track_block_authority_updated = pyqtSignal(int, int)
    track_block_occupancy_updated = pyqtSignal(int, bool)
    track_block_crossing_signal_updated = pyqtSignal(int, int)
    track_block_under_maintenance_updated = pyqtSignal(int, bool)
    track_block_track_failure_updated = pyqtSignal(int, int)

    # Signals to notify switch updates
    switch_position_updated = pyqtSignal(int)

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
        self.switches: List[TrackSwitch] = []
        self.stations: List[Station] = [] # TODO: Implement stations
        self.yard: int = None
        self.to_yard: List[int] = []
        self.from_yard: List[int] = []
        self.past_yard: List[int] = []
        self.default_route: List[int] = []

        self.route: Route = None

    def __repr__(self) -> str:

        """
        Returns a string representation of the Line object.
        
        Returns:
            str: String representation of the Line object.
        """

        blocks_repr = "\n".join(
            repr(block) for block in self.track_blocks
        )

        switch_repr = "\n".join(
            repr(switch) for switch in self.switches
        )

        res = (
            f"Line:          {self.name}\n"
            f"Track Blocks:  [\n{blocks_repr}\n]\n"
            f"Switches:      [\n{switch_repr}\n]\n"
            f"yard:          {self.yard}\n"
            f"to_yard:       {self.to_yard}\n"
            f"from_yard:     {self.from_yard}\n"
            f"past_yard:     {self.past_yard}\n"
            f"default_route: {self.default_route}"
        )

        return res

    def add_track_block(self, track_block: TrackBlock) -> None:

        """
        Adds a track block to the line and connects its signals.

        Args:
            track_block (TrackBlock): The track block to add.
        """

        self.track_blocks.append(track_block)
        self.connect_track_block_signals(track_block)

    def set_track_block(self, track_block: TrackBlock) -> None:
        
        """
        Sets a track block in the line and connects its signals.
        
        Args:
            track_block (TrackBlock): The track block to set.
        """
        
        self.track_blocks[track_block.number - 1] = track_block
        self.connect_track_block_signals(track_block)

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

    def connect_track_block_signals(self, track_block: TrackBlock) -> None:

        """
        Connects the signals of a track block to the corresponding signals of the line.
        
        Args:
            track_block (TrackBlock): The track block to connect signals for.
        """

        track_block.suggested_speed_updated.connect(lambda new_speed, blk=track_block: self.track_block_suggested_speed_updated.emit(blk.number, new_speed))
        track_block.authority_updated.connect(lambda new_authority, blk=track_block: self.track_block_authority_updated.emit(blk.number, new_authority))
        track_block.occupancy_updated.connect(lambda new_occupancy, blk=track_block: self.track_block_occupancy_updated.emit(blk.number, new_occupancy))
        track_block.crossing_signal_updated.connect(lambda new_signal, blk=track_block: self.track_block_crossing_signal_updated.emit(blk.number, new_signal))
        track_block.under_maintenance_updated.connect(lambda new_maintenance, blk=track_block: self.track_block_under_maintenance_updated.emit(blk.number, new_maintenance))

    def add_switch(self, track_switch: TrackSwitch) -> None:
        
        """
        Adds a switch to the line and connects its signals.
        
        Args:
            track_switch (TrackSwitch): The switch to add.
        """
        
        self.switches.append(track_switch)
        self.connect_switch_signals(track_switch)

        # Connect the switch to the corresponding track blocks
        for switch in self.switches:
            for block_id in switch.connected_blocks:
                block = self.get_track_block(block_id)
                block.switch = switch

    def get_switch(self, number: int) -> TrackSwitch:
            
        """
        Retrieves a switch by its number.
        
        Args:
            number (int): The switch number to retrieve.
        
        Returns:
            TrackSwitch: The retrieved TrackSwitch object.
        """

        if number < len(self.switches) and number > 0:
            return self.switches[number - 1]
        print(f"Switch {number} does not exist.")
        return None

    def toggle_switch(self, number: int) -> None:

        """
        Toggles the position of a switch.
        
        Args:
            number (int): The switch number to toggle.
        """

        switch = self.get_switch(number)
        if switch is not None:
            switch.toggle()

    def connect_switch_signals(self, switch: TrackSwitch) -> None:

        """
        Connects the signals of a switch to the corresponding signals of the line.
        
        Args:
            switch (TrackSwitch): The switch to connect signals for.
        """

        switch.position_updated.connect(lambda new_position, sw=switch: self.switch_position_updated.emit(sw.number))

    def get_unobstructed_path(self, path: List[int]) -> List[int]:

        """
        Computes the unobstructed path between two blocks on the line inclusive of the
        start and end blocks. This includes checking for block occupancy, maintenance,
        and switch connections.

        Args:
            path (List[int]): The list of block numbers in the path.

        Returns:
            List[int]: The list of block numbers in the unobstructed path.
        """

        # Check if the first block is obstructed
        if not path:
            return []

        # Check if the path is obstructed
        current_block = self.get_track_block(path[0])
        for i in range(1, len(path)):
            
            # Get the next track block along the path
            next_block = self.get_track_block(path[i])

            # Check if the block is occupied or under maintenance
            if next_block.occupancy or next_block.under_maintenance:
                return path[:i]

            # Check if the block is a switch and the next block is not the next block in the path
            if current_block.switch is not None and next_block.switch is not None:
                if not current_block.switch.is_connected(current_block.number, next_block.number):
                    return path[:i]

            current_block = next_block

        return path

    def get_path(self, prev: int, start: int, end: int) -> List[int]:

        """
        Computes the path between two blocks on the line inclusive of the
        start and end blocks along the route.

        Args:
            prev (int): The previous block number.
            start (int): The starting block number.
            end (int): The ending block number.

        Returns:
            List[int]: The list of block numbers in the path.
        """

        path = self.route.bfs_find_path(prev, start, end)

        """
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
            start_index = self.search_route(start, self.from_yard, prev=prev)
            if end in self.from_yard:

                # Find the index of the end block in the "from yard" segment, ideally after the start block
                # If the end block is before the start block in the "from yard" segment, the path wraps around the entire line
                end_index = self.search_route(end, self.from_yard, seed=start_index)
                if start_index < end_index:
                    path = self.from_yard[start_index:end_index + 1]
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
            elif end == self.yard:
                path = self.from_yard[start_index:] + self.default_route + self.to_yard + [self.yard]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

        # Determine the path if we start in the "default route" segment
        elif start in self.default_route:
            start_index = self.search_route(start, self.default_route, prev=prev)
            if end == self.yard:
                path = self.default_route[start_index:] + self.to_yard + [self.yard]
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = self.default_route[start_index:] + self.to_yard + [self.yard] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route, seed=start_index)
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
            start_index = self.search_route(start, self.to_yard, prev=prev)
            if end == self.yard:
                path = self.to_yard[start_index:] + [self.yard]
            elif end in self.from_yard:
                end_index = self.search_route(end, self.from_yard)
                path = self.to_yard[start_index:] + [self.yard] + self.from_yard[:end_index + 1]
            elif end in self.default_route:
                end_index = self.search_route(end, self.default_route)
                path = self.to_yard[start_index:] + [self.yard] + self.from_yard + self.default_route[:end_index + 1]
            elif end in self.to_yard:
                end_index = self.search_route(end, self.to_yard, seed=start_index)
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
            start_index = self.search_route(start, self.past_yard, prev=prev)
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
                end_index = self.search_route(end, self.past_yard, seed=start_index)
                if start_index < end_index:
                    path = self.past_yard[start_index:end_index + 1]
                else:
                    path = self.past_yard[start_index:] + self.default_route + self.past_yard[:end_index + 1]
            else:
                print(f"Error: No path found between blocks {start} and {end}.")

        # If the start block is not found in any segment, return an error
        else:
            print(f"Error: No path found between blocks {start} and {end}.")
        """

        return path
    
    def search_route(self, start: int, route_segment: List[int], seed: int = 0, prev: Optional[int] = None) -> int:
        
        """
        Searches for the index of a specific block in a route segment. The seed 
        parameter is used to start the search from a specific index and the prev
        parameter is used to search for a specific block pair.

        Parameters:
        - start (int): The block to search for.
        - route_segment (List[int]): The route segment to search within.
        - seed (int): The starting index for the search.
        - prev (Optional[int]): The previous block before the start block, if applicable.

        Returns:
        - int: The index of the start block in the route segment, or -1 if not found.
        """
        
        # If the route segment is empty or the start block is not in the route segment, return -1
        if not route_segment or start not in route_segment:
            print(f"Error: Route does not exist or {start} is not in the route.")
            return -1
        
        # If the route segment has only one block, return 0
        if len(route_segment) == 1:
            return 0
        
        # If no previous block was given or the previous block is the start block, find the first instance of the start block after the seed
        # If the start block is not found after the seed, check before the seed
        if prev is None or prev == start:
            for i in range(seed, len(route_segment)):
                if route_segment[i] == start:
                    return i
            for i in range(0, seed):
                if route_segment[i] == start:
                    return i
        
        # If a previous block was given, find the index of the (prev, start) block pair
        # If the pair is not found after the seed, check before the seed
        else:
            if prev not in route_segment:
                return 0
            
            for i in range(seed, len(route_segment)):
                if route_segment[i] == start and i > 0 and route_segment[i - 1] == prev:
                    return i
            for i in range(0, seed):
                if route_segment[i] == start and i > 0 and route_segment[i - 1] == prev:
                    return i
        
        # If the block or pair is not found, return -1
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

        if not path:
            return 0

        time = 0       
        for i in range(1, len(path) - 1):
            time += self.get_track_block(path[i]).traversal_time
        return time

    def get_path_length(self, path: List[int]) -> int:

        """
        Computes the distance between two blocks on the line exclusive of
        the start and end blocks.

        Args:
            path (List[int]): The list of block numbers in the path.

        Returns:
            int: The distance (in meters) between the two blocks.
        """

        if not path:
            return 0

        distance = 0       
        for i in range(1, len(path) - 1):
            distance += self.get_track_block(path[i]).length
        return distance

    def load_defaults(self) -> None:
            
        """
        Loads track blocks, switches, and routes from default files.
        """

        self.load_track_blocks()
        self.load_routes()
        self.load_switches()

    def load_track_blocks(self, file_path: str = None) -> None:

        """
        Loads track blocks from an Excel file.
        
        Args:
            file_path (str): The path to the Excel file.
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
            block = TrackBlock(
                line=row['Line'],
                section=row['Section'],
                number=row['Block Number'],
                length=row['Block Length (m)'],
                grade=row['Block Grade (%)'],
                speed_limit=row['Speed Limit (Km/Hr)'],
                elevation=row['ELEVATION (M)'],
                cumulative_elevation=row['CUMALTIVE ELEVATION (M)'],
                underground=row['Underground'],
                crossing=row['Crossing'],
                connecting_blocks=connecting_blocks,
            )
            self.add_track_block(block)

    def load_routes(self, file_path: str = None) -> None:

        """
        Loads routes from a JSON file.
        
        Args:
            file_path (str): The path to the JSON file.
        """

        if not self.track_blocks:
            print("Error: Track blocks must be loaded before routes.")
            return

        if not file_path:
            file_path = os.path.abspath(os.path.join("system_data\\routes", f"{self.name.lower()}_routes.json"))

        with open(file_path, 'r') as file:
            data = json.load(file)

        self.yard = data['yard']
        self.to_yard = data['to_yard']
        self.from_yard = data['from_yard']
        self.past_yard = data['past_yard']
        self.default_route = data['default_route']

        self.route = Route(
            line=self.name,
            yard=self.yard,
            to_yard=self.to_yard,
            from_yard=self.from_yard,
            past_yard=self.past_yard,
            default_route=self.default_route
        )

    def load_switches(self, file_path: str = None) -> None:

        """
        Loads switches from a JSON file.
        
        Args:
            file_path (str): The path to the JSON file.
        """

        if not self.track_blocks:
            print("Error: Track blocks must be loaded before switches.")
            return

        if not file_path:
            file_path = os.path.abspath(os.path.join("system_data\\switches", f"{self.name.lower()}_switches.json"))

        with open(file_path, 'r') as file:
            data = json.load(file)

        for switch_info in data['track_switches']:
            switch = TrackSwitch(
                line=self.name,
                number=switch_info['number'],
                parent_block=switch_info['parent_block'],
                child_blocks=switch_info['child_blocks'],
                initial_child=switch_info['initial_child']
            )
            self.add_switch(switch)

if __name__ == "__main__":
    line = Line('Red')
    line.load_defaults()
    print(line)

    target = 15
    path = line.get_path(line.yard, line.yard, target)
    print(f"Path from yard to block {target}: {path}")