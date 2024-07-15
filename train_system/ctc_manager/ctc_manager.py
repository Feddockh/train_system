# train_system/ctc_manager/ctc_manager.py

import os
from typing import List
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.dispatch_mode import DispatchMode
from train_system.common.line import Line
from train_system.common.train import Train, time_to_seconds

class CTCOffice(QObject):
    trains_updated = pyqtSignal()

    def __init__(self, time_keeper: TimeKeeper, line_name: str) -> None:

        """
        Initialize the CTC Office.
        """

        super().__init__()
        self.time_keeper = time_keeper
        
        # Create the line object
        self.line = Line(line_name)
        self.file_path = os.path.abspath(os.path.join("system_data\\tracks", f"{self.line.name.lower()}_line.xlsx"))
        print(f"Loading track blocks from {self.file_path}")
        self.line.load_track_blocks(self.file_path)

        # Connect the Line signals to the CTC Manager slots
        self.line.track_block_occupancy_updated.connect(self.handle_occupancy_update)
        self.line.track_block_switch_position_updated.connect(self.handle_switch_position_update)
        self.line.track_block_crossing_signal_updated.connect(self.handle_crossing_signal_update)

        # Create a list of train objects
        self.trains: List[Train] = []

        # Initialize the mode
        self.test_bench_mode = False
        self.maintenance_mode = False
        self.mbo_mode = False
        self.automatic_mode = False

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
        print(f"Block {block_number} occupancy updated to {new_occupancy}")

        # TODO: This should recompute train authorities, speeds, dispatch new trains, and update estimated train positions

    @pyqtSlot(int, int)
    def handle_switch_position_update(self, block_number: int, new_position: int) -> None:
        print(f"Block {block_number} switch position updated to {new_position}")

    @pyqtSlot(int, int)
    def handle_crossing_signal_update(self, block_number: int, new_signal: int) -> None:
        print(f"Block {block_number} crossing signal updated to {new_signal}")
    
    @pyqtSlot(int, int, str)
    def handle_dispatched_trains(self, train_id: int, target_block: int, arrival_time: str) -> None:

        # TODO: Sort the trains by arrival time

        # Check if the train id is already in the list of trains
        train_exists = False
        dispatched_train: Train = None
        for train in self.trains:
            if train_id == train.train_id:
                train_exists = True
                dispatched_train = train
                break
                
        if train_exists:
            self.insert_sorted(dispatched_train, target_block, arrival_time)
        else:
            dispatched_train = Train(train_id)
            dispatched_train.stops.append(target_block)
            dispatched_train.arrival_times.append(arrival_time)
            self.trains.append(dispatched_train)

        print(f"Dispatched trains: {train_id} to block {target_block} at {arrival_time}")

        # Compute the initial authority for the train
        distance = self.line.get_distance(1, target_block)
        dispatched_train.authority = distance
        print(f"Initial Authority: {distance}")

        # Compute the initial suggested speed for the train
        if distance == 0:
            speed = 0
        else:
            speed = 50
        dispatched_train.speed = speed
        print(f"Initial Suggested Speed: {speed}")

        # Update the trains table
        self.trains_updated.emit()

    def insert_sorted(self, train: Train, target_block: int, arrival_time: str) -> None:
        inserted = False
        for i in range(len(train.arrival_times)):
            if time_to_seconds(arrival_time) < time_to_seconds(train.arrival_times[i]):
                train.arrival_times.insert(i, arrival_time)
                train.stops.insert(i, target_block)
                inserted = True
                break
        if not inserted:
            train.arrival_times.append(arrival_time)
            train.stops.append(target_block)


