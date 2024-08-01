import copy
import os
from dataclasses import dataclass
from random import randint
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from train_system.common.authority import Authority
from train_system.common.station import Station
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.track_failures import TrackFailure
from train_system.train_controller.train_controller import TrainSystem
from train_system.train_model.train_model import TrainModel

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

    track_to_train = pyqtSignal(int, float, str, float, int) # train id, speed, authority, grade, temperature -> TrainManager -> TrainModel
    passengers_to_train = pyqtSignal(int, int) # train id, number of passengers -> TrainManager -> TrainModel
    pass_auth_back = pyqtSignal(int, Authority) # block, authority -> TrackController
    heater_status = pyqtSignal(bool) # heater status -> TrackModelUI
    station_passengers = pyqtSignal(int) # people on platform -> TrackModelUI

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

    @pyqtSlot(str, int, object)
    def handle_s_a_update(self, line: str, block: int, _: object):
        for train in self.trains:
            if train.line == line and train.block == block:
                trk_block = self.lines[train.line].get_track_block(train.block)
                if trk_block.track_failure != TrackFailure.CIRCUIT:
                    self.track_to_train.emit(train.id, trk_block.suggested_speed, trk_block.authority, trk_block.grade, self._temperature)

    @pyqtSlot(int, float)
    def handle_position(self, id: int, position: float):
        self.move_train(id, position)

    @pyqtSlot(str, int, TrainSystem)
    def handle_new_train(self, line: str, id: int, train: TrainSystem):
        self.create_train(id, line)
        train.train_model.position_updated.connect(self.handle_position)

    @pyqtSlot(int, Authority)
    def handle_mbo_authority(self, id: int, authority: Authority):
        for train in self.trains:
            if train.id == id:
                self.pass_auth_back.emit(train.block, authority)
                return
            
    @pyqtSlot(str, int, TrackFailure)
    def handle_failure_update(self, line: str, block: int, failure: TrackFailure):
        self.lines[line].get_track_block(block).track_failure = failure

    @pyqtSlot(int)
    def handle_temperature_update(self, temp: int):
        self.temperature = temp

    @pyqtSlot(str)
    def handle_passengers_to_ui(self, station: str):
        self.station_passengers.emit(self.tickets_by_station[station])
    
    def update_heaters(self) -> None:

        """
        Update heater state based on temperature.
        """

        if self._temperature <= 36:
            self.heaters = True
        else:
            self.heaters = False
        
        self.heater_status.emit(self.heaters)

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
        train.passengers_to_train.emit(train.id, train.passengers)

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