# train_system.common.train.py

import heapq
from typing import List, Tuple
from collections import deque

from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper


class Train:
    def __init__(self, train_id: int, line: Line, 
                 time_keeper: TimeKeeper) -> None:

        self.train_id = train_id
        self.line = line
        self.time_keeper = time_keeper

        self.route: deque[int] = deque([self.line.yard])
        self.stop_priority_queue: List[Tuple[int, int]] = []

        self.suggested_speed: float = 0
        self.authority: float = 0

    def __repr__(self) -> str:

        """
        String representation of the Train object.

        Returns:
            str: The string representation of the Train object.
        """

        return (
            f"Train:          {self.train_id}\n"
            f"Line:           {self.line.name}\n"
            f"Current Block:  {self.current_block}\n"
            f"SuggestedSpeed: {self.suggested_speed}\n"
            f"Authority:      {self.authority}\n"
        )

    def add_stop(self, block_number: int, arrival_time: int) -> None:
        heapq.heappush(self.stop_priority_queue, (arrival_time, block_number))
        
        # Update the route if the new stop was added within the current route
        _, last_stop = self.get_last_stop()
        if last_stop != block_number:
            self.update_route()
    
    def pop_stop(self) -> None:
        if self.stop_priority_queue:
            heapq.heappop(self.stop_priority_queue)

    def get_next_stop(self) -> Tuple[int, int]:
        if self.stop_priority_queue:
            return self.stop_priority_queue[0]
        return None

    def get_last_stop(self) -> Tuple[int, int]:
        if self.stop_priority_queue:
            return self.stop_priority_queue[-1]
        return None

    def add_route_blocks(self, route: List[int]) -> None:
        self.route.extend(route)

    def pop_route_block(self) -> None:
        last_block = None
        if self.route:
            last_block = self.route.popleft()

        # Send train back to yard if no more blocks in route
        if not self.route and (last_block != self.line.yard):
            path_to_yard = self.line.get_path(last_block, self.line.yard)
            travel_time = self.line.get_travel_time(path_to_yard)
            current_time = self.time_keeper.current_second
            self.add_stop(self.line.yard, current_time + travel_time)
            self.add_route_blocks(path_to_yard[1:])

    def get_current_block(self) -> int:
        if self.route:
            return self.route[0]
        return None
    
    def update_route(self, reset: bool = False) -> None:

        if reset:
            self.route.clear()
            self.route.append(self.line.yard)

            # Plan the route to the next stop
            last_stop = self.line.yard
            for _, next_stop in self.stop_priority_queue:
                path = self.line.get_path(last_stop, next_stop)
                self.add_route_blocks(path[1:])
                last_stop = next_stop

        else:
            last_stop = self.route[-1]
            _, next_stop = self.get_last_stop()
            path = self.line.get_path(last_stop, next_stop)
            self.add_route_blocks(path[1:])

