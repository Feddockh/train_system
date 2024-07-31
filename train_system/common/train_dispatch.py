# train_system.common.train_dispatch.py

from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
import heapq
from PyQt6.sip import wrappertype as PyQtWrapperType
from typing import List, Tuple
from collections import deque
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal

from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper


class MetaQObjectABC(PyQtWrapperType, ABCMeta):
    pass

@dataclass
class TrainRouteUpdate:
    train_id: int
    line_name: str
    route: deque[int]
    stop_priority_queue: List[Tuple[int, int]]

class TrainDispatch(QObject, metaclass=MetaQObjectABC):
    def __init__(self, time_keeper: TimeKeeper, train_id: int,
                 line: Line) -> None:
        super().__init__()

        """
        Base class for train dispatch system.

        Attributes:
            time_keeper (TimeKeeper): The time keeper for managing time updates.
            train_id (int): The unique identifier for the train.
            line (Line): The line on which the train is operating.
            boarding_time (int): The boarding time in seconds.
            departed (bool): Indicates if the train has departed.
            departure_time (int): The departure time in seconds.
            dispatched (bool): Indicates if the train has been dispatched.
            dispatch_time (int): The dispatch time in seconds.
            eta (int): Estimated time of arrival in seconds.
            lag (int): Lag time in seconds.
            time_in_block (int): Time spent in the current block in seconds.
            route (deque[int]): The route of the train, with block IDs.
            prev_block_id (int): The previous block ID.
            stop_priority_queue (List[Tuple[int, int]]): A priority queue of stops,
                where each tuple contains:
                    - arrival time (int): The arrival time in seconds.
                    - block number (int): The block number of the stop.
            authority (float): The authority level of the train.
        """

        self.time_keeper = time_keeper
        self.time_keeper.tick.connect(self.handle_time_update)

        self.train_id = train_id
        self.line = line

        self.boarding_time: int = 30
        self.departed: bool = False
        self.departure_time: int = 0

        self.dispatched: bool = False
        self.dispatch_time: int = None
        self.eta: int = 0
        self.lag: int = 0
        self.time_in_block: int = 0
        
        self.route: deque[int] = deque([self.line.yard])
        self.prev_block_id: int = self.line.yard
        self.stop_priority_queue: List[Tuple[int, int]] = []

        self.authority: float = 0
        self.max_speed = 21.67 # m/s

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

        """
        Add a new stop to the priority queue. If the new stop is added within the
        current route, the entire route is recalculated.

        Args:
            arrival_time (int): The arrival time (in seconds) to reach the stop.
            block_number (int): The block number of the stop.
        """

        # Add a new stop to the priority queue
        prev_last_stop = self.get_last_stop()[1]
        heapq.heappush(self.stop_priority_queue, (arrival_time, block_number))
    
        # Reset the route and times if the new stop was added within the current route
        if prev_last_stop != block_number:
            self.compute_route(True)
            self.compute_dispatch_time()
            self.update_eta_lag()
        else:
            self.compute_route(False)
    
    def pop_stop(self) -> None:

        """
        Pop the previous stop from the priority queue. This function should be called
        as soon as the train arrives at the stop.
        """

        if self.stop_priority_queue:
            heapq.heappop(self.stop_priority_queue)

    def get_next_stop(self) -> Tuple[int, int]:

        """
        Get the next stop from the priority queue.
        
        Returns:
            Tuple[int, int]: The arrival time and block number of the next stop.
        """

        if self.stop_priority_queue:
            return self.stop_priority_queue[0]
        return (None, None)

    def get_route_to_next_stop(self) -> List[int]:

        """
        Get the route to the next stop.
        
        Returns:
            List[int]: The route to the next stop.
        """

        next_stop = self.get_next_stop()[1]
        if next_stop:
            return self.line.get_path(self.prev_block_id, self.get_current_block_id(), next_stop)
        return None

    def get_last_stop(self) -> Tuple[int, int]:

        """
        Get the last stop from the priority queue.
        
        Returns:
            Tuple[int, int]: The arrival time and block number of the last stop.
        """

        if self.stop_priority_queue:
            return self.stop_priority_queue[-1]
        return (None, None)

    def add_route_block_ids(self, route: List[int]) -> None:

        """
        Add a list of blocks to the route.
        
        Args:
            route (List[int]): A list of block IDs to add to the route.
        """

        self.route.extend(route)

    def get_current_block_id(self) -> int:

        """
        Get the current block ID.
        
        Returns:
            int: The current block ID.
        """

        if self.route:
            return self.route[0]
        return None
    
    def get_next_block_id(self) -> int:

        """
        Get the next block ID.

        Returns:
            int: The next block ID.
        """

        if len(self.route) > 1:
            return self.route[1]
        return None

    def compute_dispatch_time(self) -> int:

        """
        Compute the dispatch time based on the travel time to the first stop.
        
        Returns:
            int: The dispatch time in seconds.
        """
        
        # Get the travel time to the first stop
        route_to_first_stop = self.get_route_to_next_stop()
        travel_time = self.line.get_travel_time(route_to_first_stop)

        # Get the first arrival time from the priority queue
        arrival_time = self.get_next_stop()[0]
        
        # Compute the dispatch time
        self.dispatch_time = arrival_time - travel_time

        return self.dispatch_time
    
    def compute_departure_time(self) -> int:

        """
        Compute the departure time based on the boarding time.
        
        Returns:
            int: The departure time in seconds.
        """

        # TODO: Consider time it takes to get to station from block entry
        
        # Get the current time
        current_time = self.time_keeper.current_second

        # Compute the departure time
        self.departure_time = current_time + self.boarding_time

        return self.departure_time

    def compute_route(self, reset: bool = False) -> None:

        # If reset is True, plan the route from the current block to the first stop
        if reset:

            # Clear the current route
            self.route = deque([self.get_current_block_id()])

            # Check if there is a stop in the priority queue.
            # If so, plan the route to the first stop from current block
            if self.stop_priority_queue:
                path = self.line.get_path(self.prev_block_id, self.get_current_block_id(), self.get_next_stop()[1])
                self.add_route_block_ids(path[1:])

            # Plan the route from the previous stop to the next
            for _, next_stop in self.stop_priority_queue[1:]:
                path = self.line.get_path(self.route[-2], self.route[-1], next_stop)
                self.add_route_block_ids(path[1:])

        # Plan the route from the last stop to the next stop
        else:
            path = self.line.get_path(self.route[-2], self.route[-1], self.get_last_stop()[1])
            self.add_route_block_ids(path[1:])

    def handle_route_update(self, update: TrainRouteUpdate) -> None:
        if self.train_id != update.train_id or self.line.name != update.line_name:
            print("ERROR: Train ID or Line Name mismatch for update")
            return
        self.route = update.route
        self.stop_priority_queue = update.stop_priority_queue

    @pyqtSlot(int)
    def handle_time_update(self, tick: int) -> None:
        self.update_eta_lag(tick)
        self.time_in_block += 1

    @abstractmethod
    def move_train_to_next_block(self) -> None:

        """
        Move the train to the next block.
        """

        pass

    @abstractmethod
    def update_eta_lag(self, tick: int = None) -> None:
            
        """
        Update the estimated time of arrival and lag time.
        
        Args:
            tick (int): The current time in seconds.
        """

        pass

