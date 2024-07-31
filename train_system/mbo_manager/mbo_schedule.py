import csv
from csv import writer
import os
import datetime
from datetime import timedelta
from datetime import datetime
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
import json
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

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
            
            #TODO update red line block info 
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
           
            # Set the number of trains based on throughput (trains/line/hour)
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

                                schedule.append([train_id, f"{end_station}", prev_block ,start_block, end_block, arrival_time, driver, crew1, crew2])
                                
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
                file_path = 'system_data/schedules/green_line_schedules'            
                file_name = f"{selected_day}_green_{file_suffix}.csv"
                
                folder_path = os.path.join(file_path, file_name)
                
                with open(folder_path, 'w', newline='') as csvfile:
                    schedule_writer = csv.writer(csvfile)
                    schedule_writer.writerow(["Train", "Station", "Prev Block", "Start Block", "End Block","Arrival Time", "Driver", "Crew 1", "Crew 2"])
                
                    for t in schedule:
                        schedule_writer.writerow(t)

         # Create schedules for both sets of checked items
            print("calling create sched")
            create_schedule(filtered_route_blocks1, filtered_prev_blocks1 ,f"1_{train_throughput.lower()}")
            create_schedule(filtered_route_blocks2, filtered_prev_blocks2 ,f"2_{train_throughput.lower()}")