import copy
import os
from dataclasses import dataclass
from random import randint
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.track_failures import TrackFailure

@dataclass
class Train:
    id: int
    line: str
    block: int
    pos: int = 0
    passengers: int = 0

class TrackModel:

    def __init__(self, lines: list[Line]) -> None:

        self.lines = lines
        self.trains: list[Train] = []
        self.dispatch_blocks: dict[str, int] = {}   #line, block num
        self._temperature: int = 85
        self.heaters: bool = False
        self.stations_by_line: dict[str, dict[str, int]] = {}

        for line in self.lines:
            stations: dict[str, int] = {}
            for block in line.track_blocks:
                if block.section == 'Yard':
                    self.dispatch_blocks[line.name] = block.next_blocks[0]
                elif block.station.isascii():
                    stations[block.station] = randint(0, 50)
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

        self.trains.append(Train(id, line, self.dispatch_blocks[line]))
        for l in self.lines:
            if l.name == line:
                l.get_track_block(self.dispatch_blocks[line]).occupancy = True
                break

    def move_train(self, id: int, distance: float) -> None:

        """
        Update a train's position on the track based on a traveled distance.
        
        Args:
            id (int): The train's ID.
            distance (float): Distance the train has traveled since last call of this function.
        """

        for train in self.trains:
            if train.id == id:
                moving_train = train
                break

        new_pos = distance + train.pos
        
        for l in self.lines:
            if l.name == train.line:
                curr_block = l.get_track_block(train.block)
                curr_line = l
                break

        if new_pos > curr_block.length:

            #Determine which block train moves into
            if len(curr_block.next_blocks) < 2:
                new_block = curr_block.next_blocks[0]
            else:
                new_block = curr_block.switch_position

            curr_line.get_track_block(new_block).occupancy = True
            moving_train.block = new_block
            moving_train.pos = new_pos - curr_block.length

            #Update occupancy of departed block
            curr_block_occ = False
            for train in self.trains:
                if train.block == curr_block.number:
                    curr_block_occ = True
                    break
            curr_block.occupancy = curr_block_occ

            

        else:
            moving_train.pos = new_pos

            #Determine if train is boarding from a station (stopped within 15 meters of center of station block)
            if distance == 0 and curr_block.station.isascii() and (abs(moving_train.pos - curr_block.length/2) < 32.2):
                self.board_at_station(curr_block.station, moving_train)


    def board_at_station(self, station: str, train: Train) -> None:

        """
        Board passengers from a station.
        
        Args:
            station (str): Name of the station to board at.
            train (Train): The train being boarded.
        """

        train.passengers -= randint(0, train.passengers)
        num_boarding = randint(0, self.stations_by_line[train.line][station])
        self.stations_by_line[train.line][station] -= num_boarding
        train.passengers += num_boarding
    

    @property
    def temperature(self) -> int:
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: int):
        self._temperature = value
        self.update_heaters()
  

if __name__ == "__main__":
    line = Line('Green')
    file_path = os.path.abspath(os.path.join("system_data/lines", "green_line.xlsx"))
    line.load_track_blocks(file_path)

    model = TrackModel([line])
    print(model.get_tickets('Green'))
    print(model.dispatch_blocks)

    model.create_train(1, 'Green')
    model.create_train(2, 'Green')
    model.move_train(2, 70)
    model.move_train(1, 20)
    model.move_train(2, 100)
    model.move_train(1, 50)

    print('Occupied:')
    for block in model.lines[0].track_blocks:
        if(block.occupancy):
            print(block.number)

    print(model.trains)