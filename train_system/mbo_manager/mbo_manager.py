import csv
from csv import writer
import datetime
from datetime import timedelta
from datetime import datetime
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
import json
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.conversions import *
from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock


class MBOOffice(QObject):
    #pass train_dispatch_updated = pyqtSignal(TrainDispatchUpdate)
    
    def __init__(self, time_keeper: TimeKeeper):
        super().__init__()
        """
        Initialize the MBO Office
        """
        self.time_keeper = time_keeper
        self.green_line = Line('Green')
        self.green_line.load_defaults()
        
        self.red_line = Line('Red')
        self.red_line.load_defaults()
        
        # Create a list of train objects
        #pass self.trains: Dict[int, TrainDispatchUpdate] = {}
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
        """Commanded speed for a train based off of the block it is currently in 

        Args:
            train_id (_type_): _description_
            block (_type_): _description_
        """
        
        current_block = self.green_line.get_track_block(block)
        print(f"calculating commanded speed for {train_id} in block ", block)

        if block: 
            self.block_speed = self.kmhr_to_ms(current_block.speed_limit)
            
        return(self.block_speed)
    
    def compute_authority(self, train_id, position, velocity, block):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        # "authority:destination_block"
        #initial authority will be unobtructed path to destination 
            #looking for blocks under maint, switch positions 
        #if train infront is within certain distance of the train then set authority tooooo
            # service breaking distance? 
        
        #use mbo_train_dispatch to adjust the departure time and next stop for the train once it reaches it's destination 

        
        
        
        #need to remove next block 
        return (self.authority)
    
               
    class Satellite(QObject):
        
        #trainid, authority, speed
        send_data_signal = pyqtSignal(str, float, float)
        
        def __init__(self):
            super().__init__()
            self.mbo_mode = True
            #pass self.mbo_office = MBOOffice()
            
            self.train_positions = {}
            self.train_id = ''
            
            time_keeper = TimeKeeper()
            
            self.mbo_office = MBOOffice(time_keeper)
            
            #is key int or string? think string
            key = 0
        
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
            
            self.authority = self.mbo_office.compute_authority(train_id, position, block)
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
                #TODO what train model wants me to send when in fixed block? 
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
            Init Schedules class
            """
            
            # Create set of drivers and crew - make excel file
            self.drivers = ["Alejandro", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"]
            self.crew = ["Alice", "Barbra", "Cole", "Dan", "Earl", "Fern", "George", "Hank", "Ian", "Jack",
                        "Karen", "Leo", "Morgan", "Niel", "Ophelia", "Paul", "Quinn", "Roger", "Stacy", "Terry"]

            # Info about shifts
            self.shift_length = timedelta(hours=8, minutes=30)
            self.drive_length = timedelta(hours=4)
            self.break_length = timedelta(minutes=30)

            # Loading in line blocks/routes
            self.green_line = Line('Green')
            self.green_line.load_defaults()
            self.red_line = Line('Red')
            self.red_line.load_defaults()

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
            
            # Route blocks for the red line
            self.route_blocks_red = {'yard': 152, 'from_yard' : 153, 'Glenbury 1': 65, 'Dormont 1': 73, 'Mt. Lebanon 1': 77,
                                    'Poplar': 88, 'Castle Shannon': 96, 'Mt. Lebanon 2' : 77, 'Dormont 2' : 105, 'Glenbury 2' : 114,'Overbrook 1': 123,
                                    'Inglewood': 132, 'Central 1': 141, 'Whited 1' : 22, 'Edgebrook': 9,
                                    'Pioneer': 2, 'Station': 16, 'Whited 2': 22,
                                    'South Bank': 31, 'Central 2' : 39, 'Overbrook 2' : 57, 'past_yard': 62, 'to_yard': 151}
            
            #prev block the train would have passed to get to station 
            self.route_prev_blocks_red = {'yard': 152, 'from_yard' : 152, 'Glenbury 1': 64, 'Dormont 1': 72, 'Mt. Lebanon 1': 76,
                                    'Poplar': 87, 'Castle Shannon': 95, 'Mt. Lebanon 2' : 78, 'Dormont 2' : 104, 'Glenbury 2' : 113, 'Overbrook 1': 122,
                                    'Inglewood': 131, 'Central 1': 140, 'Whited 1' : 23, 'Edgebrook': 1,
                                    'Pioneer': 3, 'Station': 15, 'Whited 2': 21,
                                    'South Bank': 30, 'Central 2' : 38, 'Overbrook 2' : 56, 'past_yard': 62, 'to_yard': 57}

        
        def create_schedules(self, date_time, train_throughput, checked_items1, checked_items2):
            """ Create schedule options with various station stops 
                Schedules trains, driver, and crew 

            Args:
                date_time (_type_): _description_
                train_throughput (_type_): _description_
                checked_items1 (_type_): _description_
                checked_items2 (_type_): _description_
            """
           
            # Set the number of trains based on throughput 
            if train_throughput == "Low":
                num_of_trains = 4
                train_departure_interval = timedelta(minutes=15)
            elif train_throughput == 'Medium':
                num_of_trains = 10
                train_departure_interval = timedelta(minutes=6)
            elif train_throughput == "High":
                num_of_trains = 20
                train_departure_interval = timedelta(minutes=3)

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

            # pass train_departure_interval = timedelta(minutes=20) if train_throughput == "High" else timedelta(hours=1)

            def create_schedule(filtered_route_blocks, filtered_prev_blocks ,file_suffix):
                """ Making a schedule option 

                Args:
                    filtered_route_blocks (_type_): _description_
                    filtered_prev_blocks (_type_): _description_
                    file_suffix (_type_): _description_
                """
                
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
                                
                                if (i == 0):
                                    prev_block = self.route_prev_blocks_green['yard']
                                else:
                                    prev_block = filtered_prev_blocks[stations[i-1]]
                                
                                path = self.green_line.get_path(int(prev_block), int(start_block), int(end_block))
                                travel_time = timedelta(seconds=self.green_line.get_travel_time(path))
                                arrival_time = train_current_time + travel_time

                                if arrival_time > shift_end_time:
                                    break

                                schedule.append([f"Train{train_id}", f"{end_station}", prev_block ,start_block, end_block, arrival_time, driver, crew1, crew2])
                                
                                # Adding time to stop at station for 30s
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
    
    

    
    
    