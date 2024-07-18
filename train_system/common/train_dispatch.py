# train_system.common.train_dispatch.py

from dataclasses import dataclass
import heapq
from typing import List, Tuple
from collections import deque
from PyQt6.QtCore import pyqtSlot, QObject

from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper


@dataclass
class TrainDispatchUpdate:
    train_id: int
    line_name: str
    route: deque[int]
    stop_priority_queue: List[Tuple[int, int]]

class TrainDispatch(QObject):
    def __init__(self, train_id: int, line: Line, 
                 time_keeper: TimeKeeper) -> None:
        super().__init__()

        self.train_id = train_id
        self.line = line

        self.time_keeper = time_keeper
        self.time_keeper.tick.connect(self.handle_time_update)

        self.boarding_time: int = 30
        self.departed: bool = False
        self.departure_time: int = None

        self.dispatched: bool = False
        self.dispatch_time: int = None
        self.eta: int = 0
        self.lag: int = 0
        self.time_in_block: int = 0
        
        self.route: deque[int] = deque([self.line.yard])
        self.stop_priority_queue: List[Tuple[int, int]] = []

        self.authority: float = 0

    def __repr__(self) -> str:

        """
        String representation of the Train object.

        Returns:
            str: The string representation of the Train object.
        """

        return (
            f"Train ID:            {self.train_id}\n"
            f"Line:                {self.line.name}\n"
            f"Departured:          {self.departed}\n"
            f"Departure Time:      {self.departure_time}\n"
            f"Dispatched:          {self.dispatched}\n"
            f"Dispatch Time:       {self.dispatch_time}\n"
            f"ETA:                 {self.eta}\n"
            f"Lag:                 {self.lag}\n"
            f"Current Block:       {self.get_current_block_id()}\n"
            f"Next Stop:           {self.get_next_stop()}\n"
            f"Route:               {self.route}\n"
            f"Stop Priority Queue: {self.stop_priority_queue}\n"
            f"Authority:           {self.authority}\n"
        )

    def add_stop(self, arrival_time: int, block_number: int) -> None:
        if not self.dispatched:
            _, prev_last_stop = self.get_last_stop()
            heapq.heappush(self.stop_priority_queue, (arrival_time, block_number))
        
            # Reset the route and times if the new stop was added within the current route
            if prev_last_stop != block_number:
                self.compute_route(True)
                self.compute_dispatch_time()
                self.compute_departure_time()
                self.update_eta_lag()
            else:
                self.compute_route(False)

        else:
            print("ERROR: Train has already been dispatched")
    
    def pop_stop(self) -> None:

        # Pop the previous stop from the priority queue
        # This function should be called as soon as the train arrives at the stop
        if self.stop_priority_queue:
            heapq.heappop(self.stop_priority_queue)

    def get_next_stop(self) -> Tuple[int, int]:
        if self.stop_priority_queue:
            return self.stop_priority_queue[0]
        return (None, None)

    def get_route_to_next_stop(self) -> List[int]:
        _, next_stop = self.get_next_stop()
        if next_stop:
            return self.line.get_path(self.get_current_block_id(), next_stop)
        return None

    def get_last_stop(self) -> Tuple[int, int]:
        if self.stop_priority_queue:
            return self.stop_priority_queue[-1]
        return (None, None)

    def add_route_blocks(self, route: List[int]) -> None:
        if not self.dispatched:
            self.route.extend(route)
        else:
            print("ERROR: Train has already been dispatched")

    def move_train_to_next_block(self) -> None:

        # Pop the previous block from route
        # Should be called after the train leaves the block
        prev_block_id = None
        if self.route:
            prev_block_id = self.route.popleft()

        # Send train back to yard if no more blocks in route
        if not self.route and (prev_block_id != self.line.yard):
            path_to_yard = self.line.get_path(prev_block_id, self.line.yard)
            travel_time = self.line.get_travel_time(path_to_yard)
            current_time = self.time_keeper.current_second
            arrival_time = current_time + travel_time
            heapq.heappush(self.stop_priority_queue, (arrival_time, self.line.yard))
            self.route.extend(path_to_yard[1:])
        
        # TODO: Else the train is at the yard, remove

        # Update the departed status
        if self.route:
            self.departed = True

        # If the now current block is the stop, pop the stop
        current_block_id = self.get_current_block_id()
        _, next_stop_id = self.get_next_stop()
        if current_block_id == next_stop_id:
            self.pop_stop()
            
            # Update the departure time and reset departed flag
            self.compute_departure_time()
            self.departed = False

        # Reset the time in block
        self.time_in_block = 0

    def get_current_block_id(self) -> int:
        if self.route:
            return self.route[0]
        return None
    
    def get_next_block_id(self) -> int:
        if len(self.route) > 1:
            return self.route[1]
        return None

    def compute_dispatch_time(self) -> int:
        
        # Get the travel time to the first stop
        route_to_first_stop = self.get_route_to_next_stop()
        travel_time = self.line.get_travel_time(route_to_first_stop)

        # Get the first arrival time from the priority queue
        arrival_time, _ = self.get_next_stop()
        
        # Compute the dispatch time
        self.dispatch_time = arrival_time - travel_time

        return self.dispatch_time
    
    def compute_departure_time(self) -> int:

        # TODO: Consider time it takes to get to station from block entry
        
        # Get the current time
        current_time = self.time_keeper.current_second

        # Compute the departure time
        self.departure_time = current_time + self.boarding_time

        return self.departure_time

    def update_eta_lag(self, tick: int = None) -> None:

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
        arrival_time, _ = self.get_next_stop() # 300s
        self.lag = self.eta - arrival_time # 100 - 300 = -200

    def compute_route(self, reset: bool = False) -> None:

        # Replan the route from the yard if reset is True
        if reset:
            self.route.clear()
            self.route.append(self.line.yard)

            # Plan the route to the next stop
            last_stop = self.line.yard
            for _, next_stop in self.stop_priority_queue:
                path = self.line.get_path(last_stop, next_stop)
                self.add_route_blocks(path[1:])
                last_stop = next_stop

        # Plan the route to the next stop
        else:
            last_stop = self.route[-1]
            _, next_stop = self.get_last_stop()
            path = self.line.get_path(last_stop, next_stop)
            self.add_route_blocks(path[1:])

    def process_update_message(self, update: TrainDispatchUpdate) -> None:
        if self.train_id != update.train_id or self.line.name != update.line_name:
            print("ERROR: Train ID or Line Name mismatch for update")
            return
        self.route = update.route
        self.stop_priority_queue = update.stop_priority_queue
    
    def get_position (self) -> None:
        current_block = self.get_current_block
        path = current_block.get

    @pyqtSlot(int)
    def handle_time_update(self, tick: int) -> None:
        self.update_eta_lag(tick)
        self.time_in_block += 1
        