# train_system/ctc_manager/ctc_manager.py

import bisect
from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.dispatch_mode import DispatchMode
from train_system.common.line import Line
from train_system.common.train_dispatch import TrainDispatchUpdate
from train_system.ctc_manager.ctc_train_dispatch import CTCTrainDispatch

class CTCOffice(QObject):
    train_dispatch_updated = pyqtSignal(TrainDispatchUpdate)

    def __init__(self, time_keeper: TimeKeeper, line_name: str) -> None:

        """
        Initialize the CTC Office.
        """

        super().__init__()
        self.time_keeper = time_keeper
        
        # Create the line object
        self.line = Line(line_name)
        self.line.load_defaults()

        # Connect the Line signals to the CTC Manager slots
        self.line.track_block_occupancy_updated.connect(self.handle_occupancy_update)
        self.line.track_block_crossing_signal_updated.connect(self.handle_crossing_signal_update)
        self.line.switch_position_updated.connect(self.handle_switch_position_update)

        # Create a list of train objects
        self.trains: Dict[int, CTCTrainDispatch] = {}
        self.last_train_dispatched = None

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

    def get_trains_ordered_by_lag(self, trains: Optional[List[CTCTrainDispatch]] = None) -> List[CTCTrainDispatch]:
        if trains is None:
            trains = list(self.trains.values())

        # Filter trains with lag not None
        filtered_trains = [train for train in trains if train.lag is not None]

        # Order the trains by lag in descending order (latest first)
        ordered_trains = sorted(filtered_trains, key=lambda train: train.lag, reverse=True)
        return ordered_trains

    def send_train_dispatch_update(self, train_id: int) -> None:
        if self.train_exists(train_id):
            train = self.get_train(train_id)
            update = TrainDispatchUpdate(train_id, self.line.name, train.route, train.stop_priority_queue)
            self.train_dispatch_updated.emit(update)

    def compute_train_authority(self, train_id: int) -> float:

        # Check if the train exists
        if not self.train_exists(train_id):
            return 0
        
        # Get the train object, current block, and next stop
        train = self.get_train(train_id)
        current_block_id = train.get_current_block_id()
        next_stop_id = train.get_next_stop()[1]

        # Get the unobstructed path to the next stop
        path = train.get_route_to_next_stop()
        unobstructed_path = self.line.get_unobstructed_path(path)
        
        # Compute the authority by summing the lengths of the blocks in the path
        authority = 0
        for i in range(1, len(unobstructed_path)):
            next_block_id = unobstructed_path[i]
            next_block = self.line.get_track_block(next_block_id)
            authority += next_block.length

            # If we are reaching the stop, set authority to half the distance, else add the full distance
            if next_block.number == next_stop_id:
                authority += next_block.length / 2
            else:
                authority += next_block.length

        # If the next stop is the yard negate authority
        if next_stop_id == self.line.yard:
            authority = -abs(authority)
        
        return authority

    def compute_train_suggested_speed(self, train_id: int) -> int:

        # TODO: Consider lag in the computation

        # Check if the train exists
        if not self.train_exists(train_id):
            return 0
        
        # Get the train object, current block, and next stop
        train = self.get_train(train_id)
        current_block_id = train.get_current_block_id()
        next_stop_id = train.get_next_stop()
        
        # Get the path to the next stop
        block = self.line.get_track_block(current_block_id)

        # Set the suggested speed as 1 when it reaches the next stop, otherwsie use the block speed limit
        if current_block_id == next_stop_id:
            suggested_speed = 1
        else:
            suggested_speed = block.speed_limit

        return suggested_speed

    def update_all_trains_speed_authority(self) -> None:

        # Update the authority and suggested speed of each train
        for train_id, train in self.trains.items():
            if train.dispatched:

                # Compute the suggested speed and authority
                suggested_speed = self.compute_train_suggested_speed(train_id)
                authority = self.compute_train_authority(train_id)

                # Update the train object
                train.update(suggested_speed, authority)

    def test_bench_simulation(self) -> None:

        # Get the sorted list of trains by lag
        ordered_trains = self.get_trains_ordered_by_lag()

        # Check through all the trains to see if they are ready to move
        for train in ordered_trains:

            if train.dispatched:

                # Get the current and next block of the train
                current_block_id = train.get_current_block_id()
                current_block = self.line.get_track_block(current_block_id)
                next_block_id = train.get_next_block_id()
                next_block = self.line.get_track_block(next_block_id)
        
                # Check if the train is dispatched and sitting at the yard
                move_train = False
                if current_block_id == self.line.yard:
                    move_train = True

                # Check if the train has exceeded the time per block
                elif train.time_in_block >= current_block.length / train.suggested_speed:
                    move_train = True

                # Check if the next block is clear and not under maintenance
                if next_block.occupancy or next_block.under_maintenance:
                    move_train = False

                # Check if the current block is a switch and if the train can move to the next block
                if current_block.switch is not None and next_block.switch is not None:
                    if not current_block.switch.is_connected(current_block_id, next_block_id):
                        move_train = False

                # Move the train to the next block using the occupancies if all conditions are met
                if move_train:
                    current_block.occupancy = False
                    next_block.occupancy = True

    @pyqtSlot(int)
    def handle_time_update(self, tick: int) -> None:
        
        # Check if it is time to depart or dispatch any trains
        # Add trains to dispatch to a list because we can only dispatch one train at a time
        trains_to_dispatch = []
        for train_id, train in self.trains.items():

            # Check for departing trains
            if train.dispatched and not train.departed and self.time_keeper.current_second >= train.departure_time:
                
                # Update the speed and authority of the train
                train.suggested_speed = self.compute_train_suggested_speed(train_id)
                train.authority = self.compute_train_authority(train_id)
            
            # Check for dispatching trains
            if not train.dispatched and self.time_keeper.current_second >= train.dispatch_time:
                trains_to_dispatch.append(train)

        # Dispatch the train with the highest lag if there are trains to dispatch
        if trains_to_dispatch:
            train = self.get_trains_ordered_by_lag(trains_to_dispatch)[0]
            suggested_speed = self.compute_train_suggested_speed(train_id)
            authority = self.compute_train_authority(train_id)
            train.dispatch(suggested_speed, authority)

        # Run the test bench simulation if the test bench mode is enabled
        if self.test_bench_mode:
            self.test_bench_simulation()

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
    def handle_occupancy_update(self, block_number: int, occupancy: bool) -> None:
        
        # Check if it is CTC's responsibility to update the speed and authority of the trains
        if not self.mbo_mode:

            # Update train position when incoming occupancy is true
            if occupancy:
                next_block = self.line.get_track_block(block_number)

                # Check if the block is not under maintenance
                if not next_block.under_maintenance:
                    for train_id, train in self.trains.items():

                        # Check that the train was dispatched and train's next block was the now occupied block
                        if train.dispatched and train.get_next_block_id() == next_block.number:

                            # Get the train's current block and check if the train can move to the now occupied block
                            current_block = self.line.get_track_block(train.get_current_block_id())
                            if current_block.switch is None or next_block.switch is None:
                                train.move_train_to_next_block()
                                self.send_train_dispatch_update(train_id)
                                break
                            elif current_block.switch.is_connected(current_block.number, next_block.number):
                                train.move_train_to_next_block()
                                self.send_train_dispatch_update(train_id)
                                break

            # Update the speed and authority of the trains
            self.update_all_trains_speed_authority()

        # print(f"Block {block_number} occupancy updated to {occupancy}")

    @pyqtSlot(int, int)
    def handle_crossing_signal_update(self, block_number: int, new_signal: int) -> None:
        print(f"Block {block_number} crossing signal updated to {new_signal}")
    
    @pyqtSlot(int)
    def handle_switch_position_update(self, switch_number: int) -> None:
        print(f"Switch {switch_number} position updated")

    @pyqtSlot(int, int, int)
    def handle_dispatcher_command(self, train_id: int, target_block: int, arrival_time: int) -> None:

        # Check if the train id is already in the list of trains
        if not self.train_exists(train_id):
            self.add_train(train_id, self.line)
        train = self.get_train(train_id)
        train.add_stop(arrival_time, target_block)

    @pyqtSlot(TrainDispatchUpdate)
    def handle_train_dispatch_update(self, train_update: TrainDispatchUpdate):
        if self.mbo_mode:
            if not self.train_exists(train_update.train_id):
                self.add_train(train_update.train_id, self.line) # TODO: Change this to check for line
            train_dispatch = self.get_train(train_update.train_id)
            train_dispatch.process_update_message(train_update)
