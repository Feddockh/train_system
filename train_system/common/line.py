# train_system/common/line.py

import os
import json
import pandas as pd
import math
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
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

    def __repr__(self) -> str:
            
            """
            Returns a string representation of the Route object.
            
            Returns:
                str: String representation of the Route object.
            """
    
            res = (
                f"Line:          {self.line}\n"
                f"Yard:          {self.yard}\n"
                f"To Yard:       {self.to_yard}\n"
                f"From Yard:     {self.from_yard}\n"
                f"Past Yard:     {self.past_yard}\n"
                f"Default Route: {self.default_route}"
            )
    
            return res

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

    def bfs_find_start_node(self, root: Node, prev: int, start: int) -> Optional[Node]:
            queue = deque([root])
            while queue:
                node = queue.popleft()
                for child in node.children:
                    if node.name == prev and child.name == start:
                        return child
                    queue.append(child)
            return None
    
    def bfs_find_path_from_node(self, start_node: Node, end: int) -> Optional[List[int]]:
            queue = deque([(start_node, [start_node.name])])
            while queue:
                current_node, path = queue.popleft()
                if current_node.name == end:
                    return path
                for child in current_node.children:
                    queue.append((child, path + [child.name]))
            return None

    def bfs_find_path(self, prev: int, start: int, end: int) -> Optional[List[int]]:

        """
        Performs a breadth-first search to find the path from start to end after 
        finding the first instance of (parent: prev, child: start).

        Args:
            prev (int): The parent block number to start the search from.
            start (int): The starting block number for the new search.
            end (int): The ending block number for the path search.

        Returns:
            Optional[List[int]]: The path from start to end if found, otherwise None.
        """

        # If start is the yard block, start from the root
        if start == self.yard:
            start_node = self.root
        else:
            start_node = self.bfs_find_start_node(self.root, prev, start)

        if start_node:
            return self.bfs_find_path_from_node(start_node, end)
        return None
    

class Line(QObject):

    # Signals to notify track block updates (line name, block number, attribute value)
    track_block_suggested_speed_updated = pyqtSignal(str, int, int)
    track_block_authority_updated = pyqtSignal(str, int, int)
    track_block_occupancy_updated = pyqtSignal(str, int, bool)
    track_block_crossing_signal_updated = pyqtSignal(str, int, int)
    track_block_under_maintenance_updated = pyqtSignal(str, int, bool)
    track_block_track_failure_updated = pyqtSignal(str, int, int)

    # Signals to notify switch updates (line name, switch number)
    switch_position_updated = pyqtSignal(str, int)

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
        self.stations: List[Station] = []
        self.yard: int = None
        self.route: Route = None

    def __repr__(self) -> str:

        """
        Returns a string representation of the Line object.
        
        Returns:
            str: String representation of the Line object.
        """

        blocks_repr = "\n\n".join(
            repr(block) for block in self.track_blocks
        )

        switch_repr = "\n".join(
            repr(switch) for switch in self.switches
        )

        res = (
            f"Line:          {self.name}\n"
            f"Track Blocks:  [\n{blocks_repr}\n]\n"
            f"Switches:      [\n{switch_repr}\n]\n"
            f"Route:         [\n{self.route}\n]\n"
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

    def get_next_block(self, prev: int, current: int) -> TrackBlock:

        """
        Computes the next block along the route from the current block.

        Args:
            prev (int): The previous block number.
            current (int): The current block number.

        Returns:
            TrackBlock: The next block along the route.
        """

        # Find the (prev, current) pair in the route tree
        return self.route.bfs_find_start_node(self.route.root, prev, current).children[0].name

    def connect_track_block_signals(self, track_block: TrackBlock) -> None:

        """
        Connects the signals of a track block to the corresponding signals of the line.
        
        Args:
            track_block (TrackBlock): The track block to connect signals for.
        """

        track_block.suggested_speed_updated.connect(
            lambda new_speed, blk=track_block: self.track_block_suggested_speed_updated.emit(self.name, blk.number, new_speed)
        )
        track_block.authority_updated.connect(
            lambda new_authority, blk=track_block: self.track_block_authority_updated.emit(self.name, blk.number, new_authority)
        )
        track_block.occupancy_updated.connect(
            lambda new_occupancy, blk=track_block: self.track_block_occupancy_updated.emit(self.name, blk.number, new_occupancy)
        )
        track_block.crossing_signal_updated.connect(
            lambda new_signal, blk=track_block: self.track_block_crossing_signal_updated.emit(self.name, blk.number, new_signal)
        )
        track_block.under_maintenance_updated.connect(
            lambda new_maintenance, blk=track_block: self.track_block_under_maintenance_updated.emit(self.name, blk.number, new_maintenance)
        )
        track_block.track_failure_updated.connect(
            lambda new_failure, blk=track_block: self.track_block_track_failure_updated.emit(self.name, blk.number, new_failure)
        )

    def add_switch(self, track_switch: TrackSwitch) -> None:
        
        """
        Adds a switch to the line and connects its signals.
        
        Args:
            track_switch (TrackSwitch): The switch to add.
        """
        
        self.switches.append(track_switch)
        self.connect_switch_signals(track_switch)

        # Connect the switch to the corresponding track blocks
        for block_id in track_switch.connected_blocks:
            block = self.get_track_block(block_id)
            block.switch = track_switch

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

    def add_station(self, station: Station) -> None:
        
        """
        Adds a station to the line.
        
        Args:
            station (Station): The station to add.
        """
        
        self.stations.append(station)

        # Connect the station to the corresponding track blocks
        for block_id in station.blocks:
            block = self.get_track_block(block_id)
            block.station = station

    def get_station(self, name: str) -> Station:

        """
        Retrieves a station by its name.
        
        Args:
            name (str): The station name to retrieve.
        
        Returns:
            Station: The retrieved Station object.
        """

        for station in self.stations:
            if station.name == name:
                return station
        print(f"Station {name} does not exist.")
        return None

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

        return self.route.bfs_find_path(prev, start, end)

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
        Loads track blocks, route, switches, and stations from default file location.
        """

        self.load_track_blocks()
        self.load_route()
        self.load_switches()
        self.load_stations()

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
                crossing_signal=row['Crossing Signal'],
                light_signal=row['Light Signal'],
                connecting_blocks=connecting_blocks,
            )
            self.add_track_block(block)

    def load_route(self, file_path: str = None) -> None:

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
        to_yard = data['to_yard']
        from_yard = data['from_yard']
        past_yard = data['past_yard']
        default_route = data['default_route']

        self.route = Route(
            line=self.name,
            yard=self.yard,
            to_yard=to_yard,
            from_yard=from_yard,
            past_yard=past_yard,
            default_route=default_route
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

    def load_stations(self, file_path: str = None) -> None:
            
            """
            Loads stations from an Excel file.
            
            Args:
                file_path (str): The path to the Excel file.
            """
    
            if not self.track_blocks:
                print("Error: Track blocks must be loaded before stations.")
                return
    
            if not file_path:
                file_path = os.path.abspath(os.path.join("system_data\\stations", f"{self.name.lower()}_stations.json"))
    
            with open(file_path, 'r') as file:
                data = json.load(file)

            for station_info in data['stations']:
                sides = [(side['previous_block'], side['current_block'], side['side']) 
                     for side in station_info['station_sides']]
                station = Station(
                    line=self.name,
                    name=station_info['name'],
                    blocks=station_info['connected_blocks'],
                    sides=sides
                )
                self.add_station(station)
        
    @pyqtSlot(str, int, int)
    def handle_suggested_speed_updated(self, line: str, block: int, new_speed: int) -> None:
        
        """
        Handles the suggested speed updated signal from a track block.
        
        Args:
            line (str): The name of the line.
            block (int): The block number.
            new_speed (int): The new suggested speed.
        """
        
        if line == self.name:
            self.get_track_block(block).suggested_speed = new_speed

    @pyqtSlot(str, int, int)
    def handle_authority_updated(self, line: str, block: int, new_authority: int) -> None:
        
        """
        Handles the authority updated signal from a track block.
        
        Args:
            line (str): The name of the line.
            block (int): The block number.
            new_authority (int): The new authority.
        """
        
        if line == self.name:
            self.get_track_block(block).authority = new_authority

    @pyqtSlot(str, int, bool)
    def handle_occupancy_updated(self, line: str, block: int, new_occupancy: bool) -> None:
        
        """
        Handles the occupancy updated signal from a track block.
        
        Args:
            line (str): The name of the line.
            block (int): The block number.
            new_occupancy (bool): The new occupancy status.
        """
        
        if line == self.name:
            self.get_track_block(block).occupancy = new_occupancy

    @pyqtSlot(str, int, int)
    def handle_crossing_signal_updated(self, line: str, block: int, new_signal: int) -> None:
        
        """
        Handles the crossing signal updated signal from a track block.
        
        Args:
            line (str): The name of the line.
            block (int): The block number.
            new_signal (int): The new crossing signal.
        """
        
        if line == self.name:
            self.get_track_block(block).crossing_signal = new_signal

    @pyqtSlot(str, int, bool)
    def handle_under_maintenance_updated(self, line: str, block: int, new_maintenance: bool) -> None:
        
        """
        Handles the under maintenance updated signal from a track block.
        
        Args:
            line (str): The name of the line.
            block (int): The block number.
            new_maintenance (bool): The new maintenance status.
        """
        
        if line == self.name:
            self.get_track_block(block).under_maintenance = new_maintenance

    @pyqtSlot(str, int, int)
    def handle_track_failure_updated(self, line: str, block: int, new_failure: int) -> None:
        
        """
        Handles the track failure updated signal from a track block.
        
        Args:
            line (str): The name of the line.
            block (int): The block number.
            new_failure (int): The new track failure status.
        """
        
        if line == self.name:
            self.get_track_block(block).track_failure = new_failure

    @pyqtSlot(str, int)
    def handle_switch_position_updated(self, line: str, switch: int) -> None:
        
        """
        Handles the switch position updated signal from a track switch.
        
        Args:
            line (str): The name of the line.
            switch (int): The switch number.
        """
        
        if line == self.name:
            self.get_switch(switch).toggle()
    

if __name__ == "__main__":

    # Create a line object
    line_name = 'Red'
    line = Line(line_name)
    line.load_defaults()

    # Create a second line object
    line2 = Line(line_name)
    line2.load_defaults()

    # Connect the signals between the two lines
    line.track_block_suggested_speed_updated.connect(line2.handle_suggested_speed_updated)

    # Test the signal connection
    block_number = 1
    new_speed = 30
    line.get_track_block(block_number).suggested_speed = new_speed
    print(f"Changed block {block_number} suggested speed to {new_speed} and got {line2.get_track_block(block_number).suggested_speed}")

    # target = 15
    # path = line.get_path(line.yard, line.yard, target)
    # print(f"Path from yard to block {target}: {path}")

    # a = 17
    # b = 16
    # next_block = line.get_next_block(a, b)
    # print(f"Block sequence: {a} -> {b} -> {next_block}")