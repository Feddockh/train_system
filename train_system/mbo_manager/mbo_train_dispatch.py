# train_system/mbo_manager/mbo_train_dispatch.py
import heapq
from train_system.common.train_dispatch import TrainDispatch
from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper

class MBOTrainDispatch(TrainDispatch):
    def __init__(self, time_keeper: TimeKeeper, train_id: int,
                 line: Line) -> None:
        super().__init__(time_keeper, train_id, line)

        self.position = 0
        self.current_block = 0
        self.velocity = 0
        
    def move_train_to_next_block(self) -> None:
        
        current_block_id = self.get_current_block_id()
        next_block_id = self.get_next_stop()
        destination_block = self.get_next_stop()[1]
        
        #Case 0: train not dispatched 
        if current_block_id == self.line.yerd and self.dispatched == False:
            print("ERROR: train not dispatched yet")
        
        #Case 1: Train is en route to next stop
        elif self.route and next_block_id != destination_block:    
            self.prev_block_id = self.route.popleft()
            self.departed = True
        
        #TODO fix with exact train position to the station it is at?? 
        #Case 2: Train is at a stop on route (not going back to yard)
        elif self.route and next_block_id == destination_block and len(self.stop_priority_queue) > 1: 
            self.prev_block_id = self.route.popleft()
            self.pop_stop()
            self.compute_departure_time()
            
            #flase until train departs after 30s wait
            self.departed == False
        
        #Case 3: Train is at last stop on route (is at the yard)
        elif self.route and next_block_id == destination_block and len(self.stop_priority_queue) == 1 and destination_block == self.line.yard:
            self.prev_block_id = self.route.popleft()
            self.pop_stop()
            self.departed = False
            self.dispatched = False
        
        #safety incase train is not being sent back to yard? would be a case if in manual mbo? 
        #Case 4:
        elif self.route and next_block_id == destination_block and len(self.stop_priority_queue) == 1 and destination_block != self.line.yard:
            
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
    