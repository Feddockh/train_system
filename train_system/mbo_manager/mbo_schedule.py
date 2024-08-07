import csv
from csv import writer
import os
import pandas as pd
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
            self.drivers = []
            self.crew_members = []
            
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
            self.route_blocks_red = {'Herron': 16, 'Swissville' : 21,'Penn Station' : 25, 'Steel Plaza': 35, 'First Ave': 45, 'Station Square': 48,
                                    'South Hills Junction': 60, 'Shadyside': 7, 'yard': 78 }
            
            #prev block the train would have passed to get to station 
            self.route_prev_blocks_red = {'Herron': 15, 'Swissville' : 20,'Penn Station' : 24, 'Steel Plaza': 34, 'First Ave': 44, 'Station Square': 47,
                                    'South Hills Junction': 59, 'Shadyside': 8, 'yard': 78}

        def load_crew_profiles(self):
            
            driver_file_path = 'system_data/employees/drivers.xlsx'
            df = pd.read_excel(driver_file_path, header=None)
            # Convert the column to a list
            self.drivers = df[0].tolist()
            
            crew_file_path = 'system_data/employees/crew_members.xlsx'
            df = pd.read_excel(crew_file_path, header=None)
            # Convert the column to a list
            self.crew_members = df[0].tolist()
            
        
        def create_schedules_green(self, date_time, train_throughput, checked_items1, checked_items2):
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

                for train_id in range(0, num_of_trains):
                    train_current_time = start_time + (train_id - 1) * train_departure_interval

                    while train_current_time < end_time:
                        driver = self.drivers[driver_index % len(self.drivers)]
                        crew1 = self.crew_members[crew_index % len(self.crew_members)]
                        crew2 = self.crew_members[(crew_index + 1) % len(self.crew_members)]
                        crew_index += 2
                        driver_index += 1

                        shift_end_time = train_current_time + self.shift_length
                        shift_start = train_current_time
                        break_taken = False
                        
                        # Always start from yard
                        start_block = self.route_blocks_green['yard']
                        stations = list(filtered_route_blocks.keys())
                        first_trip = True

                        while train_current_time < shift_end_time and train_current_time < end_time:
                            for i in range(len(stations)):
                                end_station = stations[i]
                                end_block = filtered_route_blocks[end_station]

                                if first_trip:
                                    prev_block = self.route_prev_blocks_green['yard']
                                    first_trip = False
                                else:
                                    prev_block = filtered_prev_blocks[stations[i-1]] if i > 0 else start_block

                                path = self.green_line.get_path(prev_block, start_block, end_block)
                                travel_time = timedelta(seconds=self.green_line.get_travel_time(path))
                                arrival_time = train_current_time + travel_time

                                if arrival_time > shift_end_time:
                                    break

                                schedule.append([train_id, end_block, arrival_time, f"{end_station}",driver, crew1, crew2])

                                # Adding time to stop at station for 30s
                                train_current_time = arrival_time + timedelta(seconds=30)

                                if ((train_current_time - shift_start) >= self.drive_length) and (break_taken == False):
                                    # Add yard stop for break
                                    schedule.append([train_id, self.route_blocks_green['yard'], train_current_time, "Yard",driver, crew1, crew2])
                                    train_current_time += self.break_length
                                    break_taken = True
                                    start_block = self.route_blocks_green['yard']  # Reset start_block to yard
                                    first_trip = True  # After break, reset first_trip to True

                                    if train_current_time >= shift_end_time or train_current_time >= end_time:
                                        break
                                else:
                                    start_block = end_block

                            if train_current_time >= shift_end_time or train_current_time >= end_time:
                                break

                            # Loop from the last station to the first, passing the yard
                            if train_current_time < shift_end_time and train_current_time < end_time:
                                end_block = filtered_route_blocks[stations[0]]
                                path = self.green_line.get_path(prev_block, start_block, end_block)
                                travel_time = timedelta(seconds=self.green_line.get_travel_time(path))
                                train_current_time += travel_time # Time to pass yard and stop

                        # Add yard stop at the end of the shift
                        schedule.append([train_id, self.route_blocks_green['yard'], train_current_time, "Yard" ,driver, crew1, crew2])
                        train_current_time = shift_end_time
                        
                        if train_current_time >= end_time:
                            break
                        
                print("printing schedule")
                file_path = 'system_data/schedules/green_line_schedules'            
                file_name = f"{selected_day}_green_{file_suffix}.xlsx"  

                folder_path = os.path.join(file_path, file_name)

                # Convert your schedule to a DataFrame
                schedule_df = pd.DataFrame(schedule, columns=["Train", "End Block", "Arrival Time", "Station", "Driver", "Crew 1", "Crew 2"])

                # Write the DataFrame to an Excel file
                schedule_df.to_excel(folder_path, index=False)

         # Create schedules for both sets of checked items
            print("calling create sched")
            create_schedule(filtered_route_blocks1, filtered_prev_blocks1 ,f"1_{train_throughput.lower()}")
            create_schedule(filtered_route_blocks2, filtered_prev_blocks2 ,f"2_{train_throughput.lower()}")
          
            
        def create_schedules_red(self, date_time, train_throughput, checked_items1, checked_items2):
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
            filtered_route_blocks1 = {station: self.route_blocks_red[station] for station in checked_items1}
            filtered_route_blocks2 = {station: self.route_blocks_red[station] for station in checked_items2}
            
            filtered_prev_blocks1 = {station: self.route_prev_blocks_red[station] for station in checked_items1}
            filtered_prev_blocks2 = {station: self.route_prev_blocks_red[station] for station in checked_items2}

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

                for train_id in range(20, num_of_trains + 20):
                    train_current_time = start_time + (train_id - 1) * train_departure_interval

                    
                    while train_current_time < end_time:
                        driver = self.drivers[driver_index % len(self.drivers)]
                        crew1 = self.crew_members[crew_index % len(self.crew_members)]
                        crew2 = self.crew_members[(crew_index + 1) % len(self.crew_members)]
                        crew_index += 2
                        driver_index += 1

                        shift_end_time = train_current_time + self.shift_length
                        shift_start = train_current_time
                        break_taken = False
                        
                        # Always start from yard
                        start_block = self.route_blocks_red['yard']
                        stations = list(filtered_route_blocks.keys())
                        first_trip = True

                        while train_current_time < shift_end_time and train_current_time < end_time:
                            for i in range(len(stations)):
                                end_station = stations[i]
                                end_block = filtered_route_blocks[end_station]

                                if first_trip:
                                    prev_block = self.route_prev_blocks_red['yard']
                                    first_trip = False
                                else:
                                    prev_block = filtered_prev_blocks[stations[i-1]] if i > 0 else start_block
                                    
                                path = self.red_line.get_path(prev_block, start_block, end_block)
                                travel_time = timedelta(seconds=self.red_line.get_travel_time(path))
                                arrival_time = train_current_time + travel_time

                                if arrival_time > shift_end_time:
                                    break

                                schedule.append([train_id, end_block, arrival_time, f"{end_station}", driver, crew1, crew2])

                                # Adding time to stop at station for 30s
                                train_current_time = arrival_time + timedelta(seconds=30)

                                if ((train_current_time - shift_start) >= self.drive_length) and (break_taken == False):
                                    # Add yard stop for break
                                    schedule.append([train_id, self.route_blocks_red['yard'], train_current_time, "Yard", driver, crew1, crew2])
                                    train_current_time += self.break_length
                                    break_taken = True
                                    start_block = self.route_blocks_red['yard']  # Reset start_block to yard
                                    first_trip = True  # After break, reset first_trip to True

                                    if train_current_time >= shift_end_time or train_current_time >= end_time:
                                        break
                                else:
                                    start_block = end_block

                            if train_current_time >= shift_end_time or train_current_time >= end_time:
                                break

                            # Loop from the last station to the first, passing the yard
                            if train_current_time < shift_end_time and train_current_time < end_time:
                                end_block = filtered_route_blocks[stations[0]]
                                path = self.red_line.get_path(prev_block, start_block, end_block)
                                travel_time = timedelta(seconds=self.red_line.get_travel_time(path))
                                train_current_time += travel_time # Time to pass yard and stop

                        # Add yard stop at the end of the shift
                        schedule.append([train_id, self.route_blocks_red['yard'], train_current_time, "Yard", driver, crew1, crew2])
                        
                        train_current_time = shift_end_time + timedelta(minutes=5)
                        
                        if train_current_time >= end_time:
                            break
                        
                        
                print("printing schedule")
                file_path = 'system_data/schedules/red_line_schedules'            
                file_name = f"{selected_day}_red_{file_suffix}.xlsx"  

                folder_path = os.path.join(file_path, file_name)

                # Convert your schedule to a DataFrame
                schedule_df = pd.DataFrame(schedule, columns=["Train", "End Block", "Arrival Time", "Station", "Driver", "Crew 1", "Crew 2"])

                # Write the DataFrame to an Excel file
                schedule_df.to_excel(folder_path, index=False)

         # Create schedules for both sets of checked items
            print("calling create sched")
            create_schedule(filtered_route_blocks1, filtered_prev_blocks1 ,f"1_{train_throughput.lower()}")
            create_schedule(filtered_route_blocks2, filtered_prev_blocks2 ,f"2_{train_throughput.lower()}")    