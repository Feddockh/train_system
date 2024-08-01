# train_system/ctc_manager/ctc_manager.py

import sys
from typing import List, Dict, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QApplication

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.train_dispatch import TrainRouteUpdate
from train_system.ctc_manager.ctc_train_dispatch import CTCTrainDispatch
from train_system.ctc_manager.dispatcher_ui import DispatcherUI
from train_system.common.authority import Authority


class CTCOffice(QObject):
    mbo_train_info = pyqtSignal(TrainRouteUpdate)
    train_dispatched = pyqtSignal(int, str)
    throughput_updated = pyqtSignal(int)

    def __init__(self, time_keeper: TimeKeeper) -> None:

        """
        Initialize the CTC Office.

        Args:
            time_keeper (TimeKeeper): The time keeper for managing time updates.
        """

        super().__init__()
        self.time_keeper = time_keeper
        
        # Create the line objects
        self.lines: List[Line] = []

        # Create the green line object
        self.green_line = Line("green", time_keeper)
        self.green_line.load_defaults()
        self.green_line.track_block_occupancy_updated.connect(self.handle_occupancy_update)
        self.green_line.switch_position_updated.connect(self.handle_switch_position_update)
        self.green_line.enable_signal_queue = True
        self.lines.append(self.green_line)

        # Create the red line object
        self.red_line = Line("red", time_keeper)
        self.red_line.load_defaults()
        self.red_line.track_block_occupancy_updated.connect(self.handle_occupancy_update)
        self.red_line.switch_position_updated.connect(self.handle_switch_position_update)
        self.red_line.enable_signal_queue = True
        self.lines.append(self.red_line)

        # Create a list of train objects indexed by the train ID and the line name
        self.trains: Dict[Tuple[int, str], CTCTrainDispatch] = {}

        # Initialize the toggle switch states
        self.test_bench_mode: bool = False
        self.maintenance_mode: bool = False
        self.mbo_mode: bool = False
        self.automatic_mode: bool = False
        self.dispatching_line_name: str = self.lines[0].name

        self.green_line_throughput = 0
        self.red_line_throughput = 0

    def line_exists(self, line_name: str) -> bool:

        """
        Check if the line exists in the CTC Office.
        
        Args:
            line_name (str): The name of the line.

        Returns:
            bool: True if the line exists, False otherwise.
        """

        for line in self.lines:
            if line.name == line_name:
                return True
        return False
    
    def get_line(self, line_name: str) -> Line:

        """
        Get the line object from the CTC Office.

        Args:
            line_name (str): The name of the line.

        Returns:
            Line: The line object.
        """

        for line in self.lines:
            if line.name == line_name:
                return line
        return None

    def train_exists(self, train_id: int, line_name: str) -> bool:

        """
        Check if the train exists in the CTC Office.

        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.

        Returns:
            bool: True if the train exists, False otherwise.
        """

        return (train_id, line_name) in self.trains

    def add_train(self, train_id: int, line_name: str) -> CTCTrainDispatch:

        """
        Add a train to the CTC Office.

        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.

        Returns:
            CTCTrainDispatch: The train dispatch object.
        """
        
        # Check if the line is valid
        if not self.line_exists(line_name):
            raise ValueError(f"Line {line_name} does not exist.")
        
        # Create the train dispatch object and add to the dictionary
        train = CTCTrainDispatch(self.time_keeper, train_id, self.get_line(line_name))
        self.trains[(train_id, line_name)] = train
        return train

    def remove_train(self, train_id: int, line_name: str) -> None:

        """
        Remove a train from the CTC Office.

        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.

        Returns:
            None
        """

        if self.train_exists(train_id, line_name):
            del self.trains[(train_id, line_name)]

    def get_train(self, train_id: int, line_name: str) -> CTCTrainDispatch:

        """
        Get the train dispatch object from the CTC Office.

        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.

        Returns:
            CTCTrainDispatch: The train dispatch object.
        """

        if self.train_exists(train_id, line_name):
            return self.trains[(train_id, line_name)]
        return None

    def get_trains(self, line_name: str) -> List[CTCTrainDispatch]:

        """
        Get a list of trains on the line.
        
        Args:
            line_name (str): The name of the line.
        
        Returns:
            List[CTCTrainDispatch]: A list of train dispatch objects on the line.
        """

        return [train for (train_id, _), train in self.trains.items() if train.line.name.lower() == line_name.lower()]

    def get_trains_ordered_by_lag(self, trains: Optional[List[CTCTrainDispatch]] = None) -> List[CTCTrainDispatch]:

        """
        Get a list of trains ordered by lag (latest first).

        Args:
            trains (Optional[List[CTCTrainDispatch]]): A list of train dispatch objects to order by lag.

        Returns:
            List[CTCTrainDispatch]: A list of train dispatch objects ordered by lag.
        """

        if trains is None:
            trains = list(self.trains.values())

        # Filter trains with lag not None
        filtered_trains = [train for train in trains if train.lag is not None]

        # Order the trains by lag in descending order (latest first)
        ordered_trains = sorted(filtered_trains, key=lambda train: train.lag, reverse=True)
        return ordered_trains

    def send_mbo_train_info(self, train_id: int, line_name: str) -> None:

        """
        Send the MBO train information to the MBO Office.
        
        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.
        """

        if self.train_exists(train_id, line_name):
            train = self.get_train(train_id, line_name)
            line = self.get_line(line_name)
            update = TrainRouteUpdate(train.train_id, line, train.route, train.stop_priority_queue)
            self.mbo_train_info.emit(update)

    def update_train_authority(self, train_id: int, line_name: str) -> None:

        """
        Update the authority of the train based on the current block and next stop.
        
        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.
        """

        # Check if the train exists
        if not self.train_exists(train_id, line_name):
            return 0 
        
        # Get the train and line objects
        train = self.get_train(train_id, line_name)
        line = self.get_line(line_name)

        # If the train is boarding, do not update the authority
        if not train.departed and train.departure_time > self.time_keeper.current_second:
            return

        # Get the current block and next stop
        next_stop_id = train.get_next_stop()[1]

        # Get the unobstructed path to the next stop
        path = train.get_route_to_next_stop()
        unobstructed_path = line.get_unobstructed_path(path)
        
        # Compute the distance by summing the lengths of the blocks in the path and half the length of the stop block
        _distance = line.get_path_length(unobstructed_path)
        _distance += line.get_track_block(next_stop_id).length / 2

        # Update the train's authority
        train.authority = Authority(_distance, next_stop_id)

        # Get the current block of the train
        current_block_id = train.get_current_block_id()
        current_block = line.get_track_block(current_block_id)

        # Set the Authority of the block
        current_block.authority = Authority(_distance, next_stop_id)

    def update_train_suggested_speed(self, train_id: int, line_name: str) -> None:
        
        """
        Update the suggested speed of the train based on the current block speed limit.
        
        Args:
            train_id (int): The train ID.
            line_name (str): The name of the line.
        """

        # Check if the train exists
        if not self.train_exists(train_id, line_name):
            print(f"Train {train_id} on line {line_name} does not exist, cannot set speed.")
            return
        
        # Get the train and line objects
        train = self.get_train(train_id, line_name)
        line = self.get_line(line_name)      
        
        # Get the current block of the train
        current_block_id = train.get_current_block_id()
        current_block = line.get_track_block(current_block_id)

        # If the train is not boarding, then set the suggested speed to speed limit (min between train or block)
        _suggested_speed = 0
        if train.departed or train.departure_time < self.time_keeper.current_second:
            _suggested_speed = min(train.max_speed, current_block.speed_limit)

        # Set the speed of the train dispatch object
        train.suggested_speed = _suggested_speed

        # Set the speed of the block
        current_block.suggested_speed = _suggested_speed
    
    def update_all_trains_speed_authority(self, line_name: str) -> None:
        
        """
        Update the suggested speed and authority of all trains on the line.
        
        Args:
            line_name (str): The name of the line.
        """

        # Update the authority and suggested speed of each train (on the line)
        for (train_id, _line_name), train in self.trains.items():
            if train.dispatched and _line_name == line_name:

                # Update the suggested speed and authority
                self.update_train_suggested_speed(train_id, line_name)
                self.update_train_authority(train_id, line_name)

    def test_bench_simulation(self) -> None:
        
        """
        Run the test bench simulation.
        This method is called every second to simulate the test bench mode.
        """

        # Get the sorted list of trains by lag
        ordered_trains = self.get_trains_ordered_by_lag()

        # Check through all the trains to see if they are ready to move
        for train in ordered_trains:

            if train.dispatched and (train.departed or self.time_keeper.current_second >= train.departure_time):

                # Get the current and next block of the train
                current_block_id = train.get_current_block_id()
                current_block = train.line.get_track_block(current_block_id)
                next_block_id = train.get_next_block_id()
                next_block = train.line.get_track_block(next_block_id)
        
                # Check if the train is dispatched and sitting at the yard
                move_train = False
                if current_block_id == train.line.yard:
                    move_train = True

                # Check if the train has exceeded the time per block
                elif train.suggested_speed != 0 and train.time_in_block >= current_block.length / train.suggested_speed:
                    move_train = True

                # Check if the next block is clear and not under maintenance
                if next_block.occupancy or next_block.under_maintenance:
                    move_train = False

                # Check if the current block is a switch and if the train can move to the next block
                elif current_block.switch is not None and next_block.switch is not None:
                    if not current_block.switch.is_connected(current_block_id, next_block_id):
                        move_train = False

                # Move the train to the next block using the occupancies if all conditions are met
                if move_train:
                    current_block.occupancy = False
                    next_block.occupancy = True

    def connect_dispatcher_ui(self, dispatcher_ui: DispatcherUI):

        """
        Connect the signals from the GUI to the CTC Manager slots.
        This method should be called after the GUI has been initialized.
        This does not make the ctc_manager object dependent on the
        dispatcher_ui object or vice versa. The dispatcher_ui object is
        passed as an argument to the method and is not stored into the 
        ctc_manager object.
        
        Args:
            dispatcher_ui (DispatcherUI): The dispatcher UI object.
        """

        # Connect the time keeper signal to the CTC Manager slot
        self.time_keeper.tick.connect(self.handle_time_update)

        # Connect the GUI switch signals to the CTC Manager slots
        dispatcher_ui.test_bench_toggle_switch.toggled.connect(self.handle_test_bench_toggle)
        dispatcher_ui.maintenance_toggle_switch.toggled.connect(self.handle_maintenance_toggle)
        dispatcher_ui.mbo_toggle_switch.toggled.connect(self.handle_mbo_toggle)
        dispatcher_ui.automatic_toggle_switch.toggled.connect(self.handle_automatic_toggle)
        dispatcher_ui.line_toggle_switch.toggled.connect(self.handle_line_toggle)

        # Connect the GUI dispatch signals to the CTC Manager slots
        dispatcher_ui.dispatch_command_widget.dispatched_train.connect(self.handle_dispatcher_command)
        dispatcher_ui.schedule_selection_widget.dispatched_train.connect(self.handle_dispatcher_command)

        # Connect the Line signals to the DispatcherUI slots
        self.lines[0].track_block_occupancy_updated.connect(dispatcher_ui.handle_occupancy_update)
        self.lines[1].track_block_occupancy_updated.connect(dispatcher_ui.handle_occupancy_update)
        self.lines[0].track_block_under_maintenance_updated.connect(dispatcher_ui.handle_maintenance_update)
        self.lines[1].track_block_under_maintenance_updated.connect(dispatcher_ui.handle_maintenance_update)

        # Connect the throughput signal to the DispatcherUI slot
        self.throughput_updated.connect(dispatcher_ui.throughput_widget.handle_throughput_update)

    @pyqtSlot(int)
    def handle_time_update(self, tick: int) -> None:
        
        """
        Handle the time update signal from the time keeper.
        This method is called every second to update the CTC Office.
        
        Args:
            tick (int): The current tick value.
        """
        
        # Check if it is time to depart or dispatch any trains
        # Add trains to dispatch to a list because we can only dispatch one train at a time (from yard conflict)
        trains_to_dispatch = []
        for (train_id, line_name), train in self.trains.items():

            # Check for departing trains (must be dispatched, not departed, and the departure time has passed)
            if train.dispatched and not train.departed and self.time_keeper.current_second >= train.departure_time:
                
                # Update the speed and authority of the train
                self.update_train_suggested_speed(train_id, line_name)
                self.update_train_authority(train_id, line_name)
            
            # Check for dispatching trains (must be dispatched, have a stop, and the dispatch time has passed)
            if not train.dispatched and train.stop_priority_queue and self.time_keeper.current_second >= train.dispatch_time:
                trains_to_dispatch.append(train)

        # Dispatch the train with the highest lag if there are trains to dispatch
        if trains_to_dispatch:
            train = self.get_trains_ordered_by_lag(trains_to_dispatch)[0]
            self.update_train_suggested_speed(train_id, train.line.name)
            self.update_train_authority(train_id, train.line.name)
            self.train_dispatched.emit(train.train_id, train.line.name)
            train.dispatched = True

        # Run the test bench simulation if the test bench mode is enabled
        if self.test_bench_mode:
            self.test_bench_simulation()

        # Update the throughput of the line (demo)
        self.green_line_throughput = len(self.get_trains("green")) * 50
        self.red_line_throughput = len(self.get_trains("red")) * 25
        if self.dispatching_line_name == "green":
            self.throughput_updated.emit(self.green_line_throughput)
        else:
            self.throughput_updated.emit(self.red_line_throughput)

    @pyqtSlot(bool)
    def handle_test_bench_toggle(self, state: bool) -> None:
        
        """
        Handle the test bench toggle switch signal from the GUI.
        
        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.test_bench_mode = True
        else:
            self.test_bench_mode = False

    @pyqtSlot(bool)
    def handle_maintenance_toggle(self, state: bool) -> None:
        
        """
        Handle the maintenance toggle switch signal from the GUI.
        
        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.maintenance_mode = True
        else:
            self.maintenance_mode = False

    @pyqtSlot(bool)
    def handle_mbo_toggle(self, state: bool) -> None:
        
        """
        Handle the MBO toggle switch signal from the GUI.
        
        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.mbo_mode = True
        else:
            self.mbo_mode = False

    @pyqtSlot(bool)
    def handle_automatic_toggle(self, state: bool) -> None:
        
        """
        Handle the automatic toggle switch signal from the GUI.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.automatic_mode = True
        else:
            self.automatic_mode = False
    
    @pyqtSlot(bool)
    def handle_line_toggle(self, state: bool) -> None:
        
        """
        Handle the line toggle switch signal from the GUI.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.dispatching_line_name = self.lines[1].name
        else:
            self.dispatching_line_name = self.lines[0].name

    @pyqtSlot(str, int, bool)
    def handle_occupancy_update(self, line_name: str, block_number: int, occupancy: bool) -> None:
        
        """
        Handle the occupancy update signal from the line object.
        
        Args:
            line_name (str): The name of the line.
            block_number (int): The block number.
            occupancy (bool): The occupancy status of the block.
        """

        # Check if it is CTC's responsibility to update the speed and authority of the trains
        if self.mbo_mode:
            return

        # Get the line object
        if not self.line_exists(line_name):
            raise ValueError(f"Line {line_name} does not exist.")
        line = self.get_line(line_name)
        
        # Update train position when incoming occupancy is true (this helps with multi-block occupancies)
        if occupancy:

            # Get the next block candidate of the train (newly occupied block)
            candidate_block = line.get_track_block(block_number)

            # If the candidate block is the yard, remove the train from the list of trains
            if block_number == line.yard:
                for (train_id, _), train in self.trains.items():
                    if train.get_next_block_id() == line.yard:
                        self.remove_train(train_id, line_name)
                        break

            # If the candidate block is not under maintenance, find the train that can move to that block
            elif not candidate_block.under_maintenance:
                for (train_id, _), train in self.trains.items():

                    # Check that the train was dispatched and train's next block was the candidate block
                    if train.dispatched and train.get_next_block_id() == candidate_block.number:

                        # Get the train's current block and check if the train can move to the candidate block
                        current_block = line.get_track_block(train.get_current_block_id())
                        if (current_block.switch is None or 
                                candidate_block.switch is None or
                                current_block.switch.is_connected(current_block.number, candidate_block.number)):
                            train.move_train_to_next_block()
                            break

        # Update the speed and authority of the trains (this is done on positive and negative occupancy signals)
        self.update_all_trains_speed_authority(line_name)

    @pyqtSlot(str, int, int)
    def handle_switch_position_update(self, line_name: str, switch_number: int, new_position: int) -> None:
        
        """
        Handle the switch position update signal from the line object.
        
        Args:
            line_name (str): The name of the line.
            switch_number (int): The switch number.
            new_position (int): The new position of the switch.
        """

        self.update_all_trains_speed_authority(line_name)

    @pyqtSlot(int, int, int)
    def handle_dispatcher_command(self, train_id: int, target_block: int, arrival_time: int) -> None:
        
        """
        Handle the dispatcher command signal from the GUI.

        Args:
            train_id (int): The train ID.
            target_block (int): The target block number.
            arrival_time (int): The arrival time at the target block.
        """

        # If the train does not yet exist, add it and add the stop
        if not self.train_exists(train_id, self.dispatching_line_name):
            train = self.add_train(train_id, self.dispatching_line_name)
            train.add_stop(arrival_time, target_block)
        
        # If the train exists, add the stop and update the authority and suggested speed
        else:
            train = self.get_train(train_id, self.dispatching_line_name)
            train.add_stop(arrival_time, target_block)
            self.update_train_suggested_speed(train_id, self.dispatching_line_name)
            self.update_train_authority(train_id, self.dispatching_line_name)

    @pyqtSlot(TrainRouteUpdate)
    def handle_train_route_update(self, update: TrainRouteUpdate):
        
        """
        Handle the train route update signal from the MBO Office.
        
        Args:
            update (TrainRouteUpdate): The train route update object.
        """

        if self.mbo_mode:
            if not self.train_exists(update.train_id, update.line_name):
                self.add_train(update.train_id, update.line_name)
            train = self.get_train(update.train_id, update.line_name)
            train.handle_route_update(update)

    @pyqtSlot(str, int)
    def handle_throughput_update(self, line_name: str, throughput: int) -> None:
        
        """
        Handle the throughput update signal from the line object.

        Args:
            line_name (str): The name of the line.
            throughput (int): The throughput value.
        """

        if line_name.lower() == "green":
            self.green_line_throughput = throughput
        else:
            self.red_line_throughput = throughput
        
        if self.dispatching_line_name.lower() == line_name.lower():
            self.throughput_updated.emit(throughput)
        

if __name__ == "__main__":

    app = QApplication(sys.argv)

    time_keeper = TimeKeeper()
    time_keeper.start_timer()

    ctc_manager = CTCOffice(time_keeper)
    dispatcher_ui = DispatcherUI(time_keeper, ctc_manager.lines, ctc_manager.trains)
    ctc_manager.connect_dispatcher_ui(dispatcher_ui)

    dispatcher_ui.show()
    sys.exit(app.exec())