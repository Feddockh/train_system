# train_system/ctc_manager/ctc_manager.py

from typing import List, Dict
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.dispatch_mode import DispatchMode
from train_system.common.line import Line
from train_system.common.train_dispatch import TrainDispatchUpdate
from train_system.ctc_manager.ctc_train_dispatch import CTCTrainDispatch

class CTCOffice(QObject):
    train_updated = pyqtSignal(TrainDispatchUpdate)

    def __init__(self, time_keeper: TimeKeeper, line_name: str) -> None:

        """
        Initialize the CTC Office.
        """

        super().__init__()
        self.time_keeper = time_keeper
        
        # Create the line object
        self.line = Line(line_name)
        self.line.load_track_blocks()
        self.line.load_routes()

        # Connect the Line signals to the CTC Manager slots
        self.line.track_block_occupancy_updated.connect(self.handle_occupancy_update)
        self.line.track_block_switch_position_updated.connect(self.handle_switch_position_update)
        self.line.track_block_crossing_signal_updated.connect(self.handle_crossing_signal_update)

        # Create a list of train objects
        self.trains: Dict[CTCTrainDispatch] = {}

        # Initialize the mode
        self.test_bench_mode = False
        self.maintenance_mode = False
        self.mbo_mode = False
        self.automatic_mode = False

    def train_exists(self, train_id: int) -> bool:
        return train_id in self.trains

    def add_train(self, train_id: int, line: Line) -> None:
        self.trains[train_id] = CTCTrainDispatch(train_id, line, self.time_keeper)

    def get_train(self, train_id: int) -> CTCTrainDispatch:
        if self.train_exists(train_id):
            return self.trains[train_id]
        return None

    def compute_train_authority(self, train_id: int) -> float:

        # Check if the train exists
        if not self.train_exists(train_id):
            return 0
        
        # Get the train object, current block, and next stop
        train = self.get_train(train_id)
        current_block_id = train.get_current_block()
        next_stop_id = train.get_next_stop()
        
        # Get the path to the next stop
        path = train.line.get_path(current_block_id, next_stop_id)

        # Check if the path is clear (excluding the current block and including next stop block)
        authority = 0
        last_block = self.line.get_track_block(current_block_id)
        for i in range(1, len(path) + 1):
            block = self.line.get_track_block(path[i])

            # Check if the block is occupied, under maintenance, or not in the next blocks of the last block
            if block.occupancy or block.under_maintenance or (block.number not in last_block.next_blocks):
                break
            
            # If the next stop is a station, set authority to half the distance
            if block.station and (block.number == next_stop_id):
                authority += block.length / 2
                break
            else:
                authority += block.length

            # Update the last block
            last_block = block

        # If the next stop is the yard negate authority
        if next_stop_id == self.line.yard:
            authority = -abs(authority)
        
        return authority

    def compute_train_suggested_speed(self, train_id: int) -> int:

        # Check if the train exists
        if not self.train_exists(train_id):
            return 0
        
        # Get the train object, current block, and next stop
        train = self.get_train(train_id)
        current_block_id = train.get_current_block()
        next_stop_id = train.get_next_stop()
        
        # Get the path to the next stop
        block = self.line.get_track_block(current_block_id)

        # Determine the suggested speed based on the block
        if current_block_id == next_stop_id:
            suggested_speed = 1
        else:
            suggested_speed = block.speed_limit

        return suggested_speed

    @pyqtSlot(int)
    def handle_time_update(self, tick: int) -> None:
        updateAuthority = True
        # TODO: This should check for the next train to be sent out

    @pyqtSlot(bool)
    def handle_test_bench_toggle(self, state: bool) -> None:
        if state:
            self.test_bench_mode = True
        else:
            self.test_bench_mode = False

    @pyqtSlot(bool)
    def handle_maintenance_toggle(self, state: bool) -> None:
        if state:
            self.maintenance_mode = True
        else:
            self.maintenance_mode = False

    @pyqtSlot(bool)
    def handle_mbo_toggle(self, state: bool) -> None:
        if state:
            self.mbo_mode = True
        else:
            self.mbo_mode = False

    @pyqtSlot(bool)
    def handle_automatic_toggle(self, state: bool) -> None:
        if state:
            self.automatic_mode = True
        else:
            self.automatic_mode = False
    
    @pyqtSlot(int, bool)
    def handle_occupancy_update(self, block_number: int, new_occupancy: bool) -> None:

        # If the block changes to occupied, update the trains
        if new_occupancy:

            # Determine which train is affected by the occupancy update
            for train_id, train in self.trains.items():

                # Get the next block of the train
                next_block = train.get_next_block()

                # If the updated block is the next block of the train, update the train's block, authority, and speed
                if next_block == block_number:
                    train.pop_route_block()

                    break


        print(f"Block {block_number} occupancy updated to {new_occupancy}")

        # TODO: This should recompute train authorities, speeds, dispatch new trains, and update estimated train positions

    @pyqtSlot(int, int)
    def handle_switch_position_update(self, block_number: int, new_position: int) -> None:
        print(f"Block {block_number} switch position updated to {new_position}")

    @pyqtSlot(int, int)
    def handle_crossing_signal_update(self, block_number: int, new_signal: int) -> None:
        print(f"Block {block_number} crossing signal updated to {new_signal}")
    
    @pyqtSlot(int, int, str)
    def handle_dispatched_trains(self, train_id: int, target_block: int, arrival_time: int) -> None:

        # Check if the train id is already in the list of trains
        if not self.train_exists(train_id):
            self.add_train(train_id, self.line)
        dispatched_train = self.get_train(train_id)
        dispatched_train.add_stop(target_block, arrival_time)
        
        # Compute the initial authority for the train

        # Compute the initial suggested speed for the train

        # print(f"Dispatched trains: {train_id} to block {target_block} at {arrival_time}")

        # # Compute the initial authority for the train
        # distance = self.line.get_distance(1, target_block)
        # dispatched_train.authority = distance
        # print(f"Initial Authority: {distance}")

        # # Compute the initial suggested speed for the train
        # if distance == 0:
        #     speed = 0
        # else:
        #     speed = 50
        # dispatched_train.suggested_speed = speed
        # print(f"Initial Suggested Speed: {speed}")

        # # Update the trains table
        # self.trains_updated.emit()\

    @pyqtSlot(TrainDispatchUpdate)
    def handle_train_dispatch_update(self, train_update: TrainDispatchUpdate):
        if self.mbo_mode:
            if not self.train_exists(train_update.train_id):
                self.add_train(train_update.train_id, self.line) # TODO: Change this to check for line
            train_dispatch = self.get_train(train_update.train_id)
            train_dispatch.update(train_update)
