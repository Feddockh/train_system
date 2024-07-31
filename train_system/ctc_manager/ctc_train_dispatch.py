# train_system/ctc_manager/ctc_train_dispatch.py

import heapq
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.train_dispatch import TrainDispatch
from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper

class CTCTrainDispatch(TrainDispatch):
    def __init__(self, time_keeper: TimeKeeper, train_id: int, 
                 line: Line) -> None:
        super().__init__(time_keeper, train_id, line)

        """
        Initialize the CTC train dispatch object.
        
        Args:
            time_keeper (TimeKeeper): The time keeper for managing time updates.
            train_id (int): The unique identifier for the train.
            line (Line): The line on which the train is operating.
        """

        self.suggested_speed = 0

    def update_speed_authority(self, suggested_speed: int, authority: int) -> None:

        """
        Update the suggested speed and authority of the train.
        
        Args:
            suggested_speed (int): The suggested speed of the train.
            authority (int): The authority level of the train.
        """

        self.suggested_speed = suggested_speed
        self.authority = authority

    def dispatch(self, suggested_speed: int, authority: int) -> None:

        """
        Dispatch the train with the suggested speed and authority.
        
        Args:
            suggested_speed (int): The suggested speed of the train.
            authority (int): The authority level of the train.
        """

        self.update_speed_authority(suggested_speed, authority)
        self.dispatched = True

    def move_train_to_next_block(self) -> None:

        """
        Move the train to the next block in the route. This function should be called
        as soon as the train leaves the block.
        """

        # Get the previous and current block id and the next stop id
        current_block_id = self.get_current_block_id()
        next_block_id = self.get_next_block_id()
        next_stop_id = self.get_next_stop()[1]

        # Case 0: Train is at the yard
        if current_block_id == self.line.yard and self.dispatched == False:
            print("ERROR: Train cannot move because it has not been dispatched yet.")

        # Case 1: Train is en route to next stop
        elif self.route and next_block_id != next_stop_id:
            self.prev_block_id = self.route.popleft()
            self.departed = True

        # Case 2: Train is at the stop (which is not the last stop)
        elif self.route and next_block_id == next_stop_id and len(self.stop_priority_queue) > 1:
            self.prev_block_id = self.route.popleft()
            self.pop_stop()
            self.compute_departure_time()
            self.update_eta_lag()
            self.departed = False

        # Case 3: Train is at the last stop (which is the yard)
        elif self.route and next_block_id == next_stop_id and \
                len(self.stop_priority_queue) == 1 and \
                next_stop_id == self.line.yard:
            self.prev_block_id = self.route.popleft()
            self.pop_stop()
            self.departed = False
            self.dispatched = False

        # Case 4: Train is at the last stop (which is not the yard)
        elif self.route and next_block_id == next_stop_id and \
                len(self.stop_priority_queue) == 1 and \
                next_stop_id != self.line.yard:
            self.prev_block_id = self.route.popleft()
            self.pop_stop()

            # Send train back to yard if no more blocks in route
            path_to_yard = self.line.get_path(current_block_id, next_block_id, self.line.yard)
            travel_time = self.line.get_travel_time(path_to_yard)
            current_time = self.time_keeper.current_second
            arrival_time = current_time + travel_time
            heapq.heappush(self.stop_priority_queue, (arrival_time, self.line.yard))
            self.route.extend(path_to_yard[1:])

            self.compute_departure_time()
            self.departed = False
            self.dispatched = False

        # Reset the time in block
        self.time_in_block = 0

    def update_eta_lag(self, tick: int = None) -> None:

        """
        Update the estimated time of arrival and lag time based on the current time.
        
        Args:
            tick (int): The current time in seconds.
        """

        # If the route is empty, return None
        if not self.route:
            self.eta = None
            self.lag = None
            return
        
        # If the tick is None, get the current time from the time keeper
        if not tick:
            tick = self.time_keeper.current_second

        # Compute the estimated time of arrival based on the travel time to the next stop
        route_to_next_stop = self.get_route_to_next_stop()
        self.eta = tick + self.line.get_travel_time(route_to_next_stop) # 100s

        # Compute the lag time
        arrival_time = self.get_next_stop()[0] # 300s
        if arrival_time is not None:
            self.lag = self.eta - arrival_time # 100 - 300 = -200
        else:
            self.lag = 0


