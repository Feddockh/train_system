import copy
import os
from dataclasses import dataclass
from random import randint
from PyQt6.QtCore import pyqtSignal
from train_system.common.authority import Authority
from train_system.common.station import Station
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.track_failures import TrackFailure

@dataclass
class Train:
    id: int
    line: str
    block: int
    prev_block: int
    pos: int
    pos_in_block: int = 0
    passengers: int = 0

class TrackModel:

    track_to_train = pyqtSignal(int, float, str, float, int) # train id, speed, authority, grade, temperature
    passengers_to_train = pyqtSignal(int) # number of passengers
    pass_auth_back = pyqtSignal(int, Authority) # train id, authority

    def __init__(self, lines: list[Line]) -> None:

        self.lines: dict[str, Line] = {}
        self.trains: list[Train] = []
        self._temperature: int = 85
        self.heaters: bool = False
        self.tickets_by_station: dict[str, int] = {}

        # Prepare lines
        for line in lines:
            self.lines[line.name] = line
        for _, line in self.lines.items():
            line.load_defaults()
            line.track_block_authority_updated.connect(self.handle_s_a_update)
            line.track_block_suggested_speed_updated.connect(self.handle_s_a_update)

        # Sell tickets at stations
        for _, line in self.lines.items():
            for station in line.stations:
                self.tickets_by_station[station.name] = randint(0, 50)

    def handle_s_a_update(self):
        for train in self.trains:
            block = self.lines[train.line].get_track_block(train.block)
            self.track_to_train.emit(train.id, block.suggested_speed, block.authority, block.grade, self.temperature)

    def handle_position(self, id: int, position: float):
        self.move_train(id, position)

    def handle_new_train(self, id: int, line: str):
        self.create_train(id, line)

    def handle_mbo_authority(self, id: int, authority: Authority):
        for train in self.trains:
            if train.id == id:
                self.pass_auth_back.emit(train.block, authority)
                break

    def create_failure(self, block: TrackBlock, failure: TrackFailure) -> None:

        """
        Creates a track failure on a track block.

        Args:
            block (TrackBlock): The block to create a failure on.
            failure (TrackFailure): The type of failure to create on the track block.
        """

        block.track_failure = failure


    def fix_failure(self, block: TrackBlock) -> None:

        """
        Remove any failure from a track block.

        Args:
            block (TrackBlock): The block to remove a failure from.
        """

        block.track_failure = TrackFailure.NONE


    def sell_tickets(self, station: str, num: int) -> None:

        """
        Sell tickets at a station.

        Args:
            station (str): The name of the station to sell tickets from.
            num (int): The number of tickets to sell.
        """

        self.tickets_by_station[station]
    
    def update_heaters(self) -> None:

        """
        Update heater state based on temperature.
        """

        if self._temperature <= 36:
            self.heaters = True
        else:
            self.heaters = False

    def create_train(self, id: int, line: str) -> None:

        """
        Create a local train to track its location on the line.

        Args:
            id (int): The train's ID.
            line (str): The name of the line the train was dispatched onto.
        """

        l: Line

        for _, l in self.lines.items():
            if l.name == line:
                from_yard_block = l.get_track_block(l.route.from_yard[0])
                from_yard_block.occupancy = True
                break

        self.trains.append(Train(id, line, from_yard_block.number, l.yard, from_yard_block.length * -1))
        

    def move_train(self, id: int, position: float) -> None:

        """
        Update a train's position on the track.
        
        Args:
            id (int): The train's ID.
            position (float): Position of the train on the line.
        """

        for train in self.trains:
            if train.id == id:
                moving_train = train
                break

        # TODO Account for position resetting to 0 when train loops
        distance_delta = abs(position - moving_train.pos)
        moving_train.pos = position
        
        for name, l in self.lines.items():
            if name == train.line:
                curr_block = l.get_track_block(train.block)
                curr_line = name
                break

        # When train moves into next block
        if distance_delta + moving_train.pos_in_block > curr_block.length:

            # Determine which block train moves into
            new_block = self.lines[curr_line].get_next_block(moving_train.prev_block, moving_train.block)

            new_block.occupancy = True
            
            moving_train.prev_block = moving_train.block
            moving_train.block = new_block.number
            moving_train.pos_in_block -= curr_block.length

            # Update occupancy of departed block
            curr_block_occ = False
            for train in self.trains:
                if train.block == curr_block.number:
                    curr_block_occ = True
                    break
            curr_block.occupancy = curr_block_occ

            self.send_to_trains()

        else:
            moving_train.pos_in_block += distance_delta

            # Determine if train is boarding from a station (stopped within 32.5 meters of center of station block)
            if distance_delta == 0 and curr_block.station != None and (abs(moving_train.pos_in_block - curr_block.length/2) < 32.5):
                self.board_at_station(curr_block.station.name, moving_train)


    def board_at_station(self, station: str, train: Train) -> tuple[int, int]:

        """
        Board passengers from a station.
        
        Args:
            station (str): Name of the station to board at.
            train (Train): The train being boarded.
        Returns:
            tuple[int, int]: Number of passengers disembarked and boarded, respectively.
        """

        num_disembarked = randint(0, train.passengers)
        train.passengers -= num_disembarked
        num_boarding = randint(0, self.tickets_by_station[station])
        self.tickets_by_station[station] -= num_boarding
        train.passengers += num_boarding
        train.passengers_to_train.emit(train.passengers)

        return num_disembarked, num_boarding
    

    @property
    def temperature(self) -> int:
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: int):
        self._temperature = value
        self.update_heaters()
  

if __name__ == "__main__":
    
    line = Line('green')
    file_path = os.path.abspath(os.path.join("system_data/lines", "green_line.xlsx"))
    line.load_track_blocks(file_path)

    model = TrackModel([line])
    print(model.tickets_by_station)

    model.create_train(1, 'Green')
    model.create_train(2, 'Green')
    # model.move_train(2, 70)
    model.move_train(1, 20)
    # model.move_train(2, 100)
    model.move_train(1, 50)

    print('Occupied:')
    for block in model.lines[0].track_blocks:
        if(block.occupancy):
            print(block.number)

    print(model.trains)