import csv
from csv import writer
import datetime
from datetime import timedelta
from datetime import datetime
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
import json
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.train_dispatch import TrainDispatchUpdate

class MBOOffice(QObject):
    train_dispatch_updated = pyqtSignal(TrainDispatchUpdate)
    
    def __init__(self, time_keeper: TimeKeeper):
        super().__init__()
        """
        Initialize the MBO Office
        """
        self.time_keeper = time_keeper
        self.green_line = Line('Green')
        self.green_line.load_track_blocks()
        
        # Create a list of train objects
        self.trains: Dict[int, TrainDispatchUpdate] = {}
        self.last_train_dispatched = None
                
        self.route_authority_green = {'Glenbury Down' : 400 , 'Dormont Down' : 950, 'Mt Lebanon Down' : 500, 'Poplar' : 2786.6, 'Castle Shannon' : 612.5, 
                      'Mt Lebanon Up' : 2887.5 , 'Dormont Up' : 515, 'Glenbury Up' : 921, 'Overbrook Up' : 546, 'Inglewood' : 450, 
                      'Central Up' : 450, 'Edgebrook' : 3684, 'Pioneer' : 700, 'Station' : 675, 'Whited' : 1125, 'South Bank' : 1275,
                      'Central Down' : 400, 'Overbrook Down' : 900, 'Yard' : -125}
        
        self.previous_position = {}
              
    def kmhr_to_ms(self, km_hr):
        """convert km/hr to m/s

        Args:
            km_hr (float?): km/hr that needs to be converted to m/s, mostly for setting commanded speed based of speed limit 
        """
        ms = km_hr * (1000.00/3600.00)
        return(ms)
    
    def ms_to_mph(self, ms):
        """
        convert m/s to mph for UI display 
        """
        
        return(ms * 2.237)
    
    def m_to_ft(self, m):
        """
        convert meters to feet for UI display 
        Args:
            m (_type_): _description_
        """
        return(m * 3.28084)
    
    def service_breaking_distance(self):
     """
     distance the train will travel after service break is pulled - using for if two trains are to close together 
     """ 
     service_brake_acceleration = 1.2
     v = self.kmhr_to_ms(70)
     breaking_distance = -1* (1/2)*(v)*(-1 * service_brake_acceleration)
    
     return (breaking_distance)
            
    def compute_commanded_speed(self, train_id, block):
        """
        Calculate trains commanded speed based on current block 
        
        return commanded_speed, equal to the speed limit 
        """ 
        
        """block_num = position.get("block")
        block = self.green_line.get_track_block(block_num)
        
        print(f"calculating commanded speed for {train_id} in block ", block_num)

        if block: 
            self.block_speed = self.kmhr_to_ms(block.speed_limit)
            """
        
        current_block = 63
        block_info = self.green_line.get_track_block(current_block)
        
        if current_block:
            self.block_speed = self.kmhr_to_ms(block.speed_limit) 
            
        return(self.block_speed)
    
    def compute_authority(self, train_id, position, block):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        #initialize to 0
        self.authority = 0
        
        #get block info
        current_block = self.green_line.get_track_block(block)
        
        #update
        #next_blocks = current_block.next_blocks()
        
        #if train does not exist return 0 (not dispatched)
        if not self.train_exists(train_id):
            return 0
        
        #get info about dispatched train
        train = self.get_train(train_id)
        #finding the block the train is supposed to stop in for station 
        next_stop_block = train.get_next_stop()
        
        print(f"calculating authority for {train_id} at position {position} at block {current_block} and going to {next_stop_block} ")
        
        #list of blocks to next stop, including start and end 
        path = train.get_route_to_next_stop()
        
        path_length = 0
        for blocks in path:
            path_length_m += blocks.length 
        
        #set authority to next station stop 
        
        #TODO NEED TO FIX TO ACCOUNT FOR TRAIN CURRENT POSITION 
        self.authority = path_length - ((next_stop_block.length / 2) + (32.2/2))
        
        #change authority to service break distance if... 
        
        #TODO
        #Should check if trains are gonna crash first 
        #for ids in self.trains:
            #distance_between = ids.get_position() -  position
        
        #if (distance_between < self.service_breaking_distance) and (distance_between > 0) #if negative train behind is to close
        
        #if next block is under maint or switch is not in right position 
        if (path[1].under_maintenance) or (path[1]): # not in next_blocks):
            self.authority = self.service_breaking_distance()
        
        #going to yard
        elif next_stop_block == self.green_line.yard:
            self.authority = -(self.authority)
        
        #resetting authority to next station
        elif (self.time_keeper.current_second >= train.departure_time):
            #pop next stop 
            #then authority = path_length to new next station 
            self.authority = 1
        
        #checking if train is at full stop at station, signalling to open doors with authority 
        elif (current_block == next_stop_block):
            #should keep authority big while only resetting departure time once
            if (position == self.previous_position[{train_id}]):
                self.authority = 1,000,000 
                if(train.departure_time < self.time_keeper.current_second):
                    #train to stop for 1 minute at station
                    train.departure_time = self.time_keeper.current_second + 30
                #pop next stop?
                
        #conditions to change authority 
            # to close to next train on path
            # next block is under maint (next_block.under_mainenance = True)
            # switch is not in the right position (next_block != next_block_path)
            # going to yard (next_stop_block = self.line.yard then authority is negative)
            # 1Mil to show open doors, for a minute while at stop 
                #train is within 1 trains length of middle of block AND has been at the same position for two ticks in a row
                #train_dispatch compute_departure_time
                #pop next stop??
            # if minute has passed, start authority to next stop 
                #if time_keeper = departure time 
                    #authority = path to next station 
        
        
        #need to remove next block 
        return (self.authority)
    
               
    class Satellite(QObject):
        
        send_data_signal = pyqtSignal(str, float, float)
        
        #want way to connect train positions to send
        
        def __init__(self):
            super().__init__()
            self.mbo_mode = True
            #pass self.mbo_office = MBOOffice()
            
            self.train_positions = {}
            self.train_id = ''
            
            time_keeper = TimeKeeper()
            
            self.mbo_office = MBOOffice(time_keeper)
        
        @pyqtSlot(str, float, int)
        def satellite_recieve(self, train_id: str, position: float, block: int) -> None:
            """
            Recieve train position
            
            Args:
                train_id (str): _description_
                position (float): _description_
                blcok (int): _description_
            """
            #pass self.train_positions[train_id] = {'position' : position, 'block' : block}
            self.satellite_send(train_id, position, float)
        
        def satellite_send(self, train_id: str, position: float, block: int):
            """
            gathering info to send over satellite, authority and speed
            
            """
            #pass self.train_info = self.train_positions[train_id]
            #####
            self.authority = self.mbo_office.compute_authority(train_id, position, block, 65)
            self.commanded_speed = self.mbo_office.compute_commanded_speed(train_id, block)
             
            if (self.mbo_mode == True):
                """
                send speed and authority 
                """ 
                print('mbo mode is true')
                #pass encrypted_id = self.encrypty(train_id)
                #pass encrypted_authority = self.encrypt(authority)
                #pass encrypted_speed = self.(commanded_speed)
                
                #will emit encrypt
                self.send_data_signal.emit(self.train_id, self.authority, self.commanded_speed)
                  
            else: 
                """
                do not send information, information will be sent to train through CTC office
                """ 
                self.update_satellite({})
        
        def encrypty(self):
            """
            encryption to send vital information
            """
            #will generate key in top level main to use here, and encrypt the speed and authority 
            
        
        def decrypt(self):
            """
            decryption to recieve position(s)
            """
            #will generate key in top level main to use here, and decrypt the speed and authority 
            
    class Schedules:
        def __init__(self):
            super().__init__()
            """
            Initialize Schedule
            """
            # Create set of drivers and crew
            self.drivers = ["Alejandro", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"]
            self.crew = ["Alice", "Barbra", "Cole", "Dan", "Earl", "Fern", "George", "Hank", "Ian", "Jack",
                        "Karen", "Leo", "Morgan", "Niel", "Ophelia", "Paul", "Quinn", "Roger", "Stacy", "Terry"]

            # Info about shifts
            self.shift_length = timedelta(hours=8, minutes=30)
            self.drive_length = timedelta(hours=4)
            self.break_length = timedelta(minutes=30)

            # Loading in line blocks
            self.green_line = Line('Green')
            self.green_line.load_track_blocks()

            # Route blocks for the green line
            self.route_blocks_green = {'yard': 152, 'from_yard' : 153, 'Glenbury 1': 65, 'Dormont 1': 73, 'Mt. Lebanon 1': 77,
                                    'Poplar': 88, 'Castle Shannon': 96, 'Mt. Lebanon 2' : 77, 'Dormont 2' : 105, 'Glenbury 2' : 114,'Overbrook 1': 123,
                                    'Inglewood': 132, 'Central 1': 141, 'Whited 1' : 22, 'Edgebrook': 9,
                                    'Pioneer': 2, 'Station': 16, 'Whited 2': 22,
                                    'South Bank': 31, 'Central 2' : 39, 'Overbrook 2' : 57, 'past_yard': 62, 'to_yard': 151}
            
            #prev block the train would have passed to get to station 
            self.route_prev_blocks_green = {'yard': 152, 'from_yard' : 152, 'Glenbury 1': 64, 'Dormont 1': 72, 'Mt. Lebanon 1': 76,
                                    'Poplar': 87, 'Castle Shannon': 95, 'Mt. Lebanon 2' : 78, 'Dormont 2' : 104, 'Glenbury 2' : 113, 'Overbrook 1': 122,
                                    'Inglewood': 131, 'Central 1': 140, 'Whited 1' : 23, 'Edgebrook': 1,
                                    'Pioneer': 3, 'Station': 15, 'Whited 2': 21,
                                    'South Bank': 30, 'Central 2' : 38, 'Overbrook 2' : 56, 'past_yard': 62, 'to_yard': 57}

        def create_schedules(self, date_time, train_throughput, checked_items1, checked_items2):
            """Create schedules for trains based on selected stations."""
            # Set the number of trains based on throughput
            if train_throughput == "Low":
                num_of_trains = 1
            #elif train_throughput == 'Medium':
                #num_of_trains = 15
            elif train_throughput == "High":
                num_of_trains = 20

            selected_day = date_time.toString('MM-dd-yyyy')
            selected_start_time = date_time.toString('HH:mm:ss')
            print(f"making schedule for: {date_time}, with a {train_throughput} throughput")
            print("schedule option 1 has stations: ", checked_items1)
            print("schedule option 2 has stations: ", checked_items2)

            # Filter route schedule based on checked items
            filtered_route_blocks1 = {station: self.route_blocks_green[station] for station in checked_items1}
            filtered_route_blocks2 = {station: self.route_blocks_green[station] for station in checked_items2}
            
            filtered_prev_blocks1 = {station: self.route_prev_blocks_green[station] for station in checked_items1}
            filtered_prev_blocks2 = {station: self.route_prev_blocks_green[station] for station in checked_items2}

            start_time = datetime.strptime(selected_day + ' ' + selected_start_time, '%m-%d-%Y %H:%M:%S')
            end_time = start_time + timedelta(hours=24)

            train_departure_interval = timedelta(minutes=20) if train_throughput == "High" else timedelta(hours=1)

            def create_schedule(filtered_route_blocks, filtered_prev_blocks ,file_suffix):
                print("making schedules")
                current_time = start_time
                crew_index = 0
                driver_index = 0
                schedule = []

                for train_id in range(1, num_of_trains + 1):
                    train_current_time = start_time + (train_id - 1) * train_departure_interval

                    while train_current_time < end_time:
                        driver = self.drivers[driver_index % len(self.drivers)]
                        crew1 = self.crew[crew_index % len(self.crew)]
                        crew2 = self.crew[(crew_index + 1) % len(self.crew)]
                        crew_index += 2
                        driver_index += 1

                        shift_end_time = train_current_time + self.shift_length
                        shift_start = train_current_time

                        # Always start from yard
                        start_block = self.route_blocks_green['yard']
                        stations = list(filtered_route_blocks.keys())

                        while train_current_time < shift_end_time and train_current_time < end_time:
                            for i in range(len(stations)):
                                end_station = stations[i]
                                end_block = filtered_route_blocks[end_station]
                                
                                if (start_block == self.route_blocks_green['yard']):
                                    prev_block = 152
                                else:
                                    prev_block = stations[i-1]
                                
                                path = self.green_line.get_path(prev_block, start_block, end_block)
                                travel_time = timedelta(seconds=self.green_line.get_travel_time(path))
                                arrival_time = train_current_time + travel_time

                                if arrival_time > shift_end_time:
                                    break

                                schedule.append([f"Train{train_id}", f"{end_station}", prev_block ,start_block, end_block, arrival_time, driver, crew1, crew2])

                                # Adding time to stop at station for 1 minute
                                train_current_time = arrival_time + timedelta(seconds=30)

                                if (train_current_time - shift_start) >= self.drive_length:
                                    train_current_time += self.break_length
                                    if train_current_time >= shift_end_time or train_current_time >= end_time:
                                        break

                                start_block = end_block

                            if train_current_time >= shift_end_time or train_current_time >= end_time:
                                break

                            # Loop from the last station to the first, passing the yard
                            end_block = filtered_route_blocks[stations[0]]
                            path = self.green_line.get_path(prev_block,start_block, end_block)
                            travel_time = timedelta(seconds=self.green_line.get_travel_time(path))
                            train_current_time += travel_time + timedelta(seconds=30)  # Time to pass yard and stop

                        train_current_time = shift_end_time
                        if train_current_time >= end_time:
                            break
                
                print("printing schedule")            
                file_name = f"{selected_day}_green_{file_suffix}.csv"
                with open(file_name, 'w', newline='') as csvfile:
                    schedule_writer = csv.writer(csvfile)
                    schedule_writer.writerow(["Train", "Station", "Prev Block", "Start Block", "End Block","Arrival Time", "Driver", "Crew 1", "Crew 2"])
                
                    for t in schedule:
                        schedule_writer.writerow(t)

         # Create schedules for both sets of checked items
            print("calling create sched")
            create_schedule(filtered_route_blocks1, filtered_prev_blocks1 ,f"1_{train_throughput.lower()}")
            create_schedule(filtered_route_blocks2, filtered_prev_blocks2 ,f"2_{train_throughput.lower()}")


                    
                               
            
# pass if __name__ == "__main__":
    
    

    
    
    