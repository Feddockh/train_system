import csv
from csv import writer
import datetime
from datetime import timedelta


class MBOController:
    def __init__(self):
        """
        Initialize the MBO Controller
        """
        self.dispatch_mode = "AUTOMATIC MBO"
        
        self.enable_s_and_a = 1
        
        self.lines = ["Blue"]
        self.blue_speed_limit = 50.0 #km/hr, convert to m/s
        
        self.blocks = {'1' : 0 , "2" : 50, "3" : 100, "4" :150, "5" :200, "6" : 250, "7" : 300, "8" : 350, "9" : 400, "10": 450, "11": 250, "12" : 300, "13" : 350, "14" : 400, "15" : 450}
   
        self.stations = {"Yard" : 0, "Station B": 500, "Station C" :500}
        self.drivers = ["Alejandro", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"]
        self.crew = ["Alice", "Barbra", "Cole", "Dan", "Earl", "Fern", "George", "Hank", "Ian", "Jack",
                "Karen", "Leo", "Morgan", "Niel", "Ophelia", "Paul", "Quinn", "Roger", "Stacy", "Terry"]
        
        self.low_trains = ["Train1"]
        self.med_trains = ["Train1", "Train2"]
        self.high_trains = ["Train1", "Train2", "Train3"]
        
        self.train_ids = list(range(1,11))
        
        self.shift_length = timedelta(hours= 8, minutes= 30)
        self.drive_length = timedelta(hours=4)
        self.break_length = timedelta(minutes=30)
        
        
        
        #testin for MBO Mode View 
        self.testing_positions_1 = {'Train1': 100, 'Train2': 300, 'Train3': 310}
        self.testing_positions_2 = {'Train1': 100, 'Train2': 335, 'Train3': 350, 'Train4': 420}
        
        self.destinations_1 = {'Train1': 'Yard', 'Train2': 'Station B', 'Train3': 'Station C'}
        self.destinations_2 = {'Train1': 'Station B', 'Train2': 'Station B', 'Train3': 'Station B', 'Train4': 'Station B'}
        
        self.block_maint_1 = {}
        self.block_maint_2 = {'4': 150,'9': 400 }
       
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
    
    def emergency_breaking_distance(self):
     """
     distance the train will travel after emergency break is pulled
        (+ some wiggle room? )
     """ 
     emergency_brake_acceleration = 2.73
     v = 0.0
     v = self.commanded_speed(self.enable_s_and_a)
     breaking_distance = -1* (1/2)*(v)*(-1 * emergency_brake_acceleration)
    
     return (breaking_distance)
    
    def enable_mbo_mode(self, dispatch_mode, enable_s_and_a):
        """
        If dispatcher selects MBO mode, enable sending speed and authority 
        """  
        #print in command prompt for test bench purposes? 
        
        if self.dispatch_mode == 'MBO': 
            self.enable_s_and_a = 1  
        
        else:
            self.enable_s_and_a = 0
    
    def travel_time(self, distance):
        """Time to travel a certain distance, for schedule 

        Args:
            distance (_type_): _description_
        """
        return(timedelta(seconds=distance/self.commanded_speed(1)))
        
    def commanded_speed(self, enable_s_and_a ):
        """
        Calculate trains commanded speed
        Arg = enable_s_and_a to know if MBO has control to send speed
         
        return commanded_speed which is just equal to the speed limit 
                (will need to be the speed limit for the section/block)
        """
        if(enable_s_and_a):
        #do i need to adjust speed when train needs to stop? 
            self.speed = self.kmhr_to_ms(self.blue_speed_limit)
        else:
            self.speed = 0
            
        return(self.speed)
    
    
    def authority(self, trains_positions, destinations, block_maint):
        """
        Calculate trains authority such that more than one train can be in a block 
        """
        trains = list(trains_positions.keys())
        number_of_trains = len(trains)
        
        number_of_block_maint = len(block_maint)
        
        authorities = {}
        
        for i in range(number_of_trains):
            train_1 = trains[i]
            position_1 = trains_positions[train_1]
            destination_1 = self.stations[destinations[train_1]]
            
            authorities[train_1] = abs(position_1-destination_1)
            
            
            for j in range(i+1, number_of_trains):
                train_2 = trains[j]
                position_2 = trains_positions[train_2]
                distance_from_train = abs(position_1 - position_2)
                
                if(distance_from_train <= float(self.emergency_breaking_distance())):
                    authorities[train_1] = round(self.emergency_breaking_distance())
                
                else: 
                    if(number_of_block_maint > 0 ):
                        for x in range(number_of_block_maint):
                            block_position = self.blocks[block_maint]
                            to_block = abs(position_1 - block_position)
                            if (to_block <= 50):
                                authorities[train_1] = round(self.emergency_breaking_distance())
                    
                
        
        return (authorities)
                    
       
        #for each train 
            #if train is within emerg braking distance of another train 
                #then authority = emerg breaking distance 
            #elif train is a block away from block under maint
                #then authority = emerg breaking distance 
            #else
                #distance to next stop (station or yard)
     
       

    def create_schedules(self, selected_day, selected_start_time):
        """
        Create schedule options 
        
        return bool to ensure schedules were made - make pop up window in UI to confirm they were made successfully 
                                                        give file path for them
        """
        
        print('making schedule for: ', selected_day)
        print('starting schedule at ', selected_start_time)
        
        start_time = datetime.datetime.strptime(selected_day + ' ' + selected_start_time, '%m-%d-%Y %H:%M:%S')
        
        #creating all 3 schedule options 
        pass # low_throughput_filename = selected_day + '_low.csv'
        pass # med_throughput_filename = selected_day + '_med.csv'
        pass # high_throughput_filename = selected_day + '_high.csv'
        
        
        current_time = start_time
        end_time = start_time + timedelta(hours= 24)
        number_low_trains = len(self.low_trains)
        crew_index = 0
        driver_index = 0
        schedule = []
        current_time = start_time
        travel_time = self.travel_time(500)
        
        for train_id in self.train_ids:
            driver = self.drivers[driver_index]
            crew1 = self.crew[crew_index]
            crew2 = self.crew[crew_index + 1]
            crew_index += 2
            driver_index += 1
            
            shift_end_time = current_time + self.shift_length
            shift_start = current_time
            
            while current_time < shift_end_time and current_time < end_time:
                route = [("Yard","Station B"),("Station B","Yard"),("Yard","Station C"),("Station C","Yard")]

                for start,end in route:
                    arrival_time = current_time + travel_time
                    if arrival_time > shift_end_time:
                        break
                    
                    schedule.append([f"Train{train_id}", f"{end}", self.lines[0] ,arrival_time, driver, crew1, crew2])
                    current_time = arrival_time + timedelta(minutes=1)
                
                if (current_time - shift_start) >= self.drive_length:
                    current_time += self.break_length
                    if current_time >= shift_end_time or current_time >= end_time:
                        break
                    
            current_time = shift_end_time
            if current_time >= end_time:
                break
    
        low_throughput_file = selected_day + '_low.csv'
        with open(low_throughput_file, 'w', newline='') as csvfile:
            schedule_writer = csv.writer(csvfile)
            schedule_writer.writerow(["Train", "Line", "Station", "Arrival Time", "Driver", "Crew 1", "Crew 2"])
            
            for t in schedule:
                schedule_writer.writerow(t)
                    

         

if __name__ == "__main__":
    MBO = MBOController()
    
    
    MBO.create_schedules('06-19-2024', '00:00:00')
    
    
    MBO.enable_s_and_a = 1
    testing_positions_1 = {'Train1': 100, 'Train2': 300, 'Train3': 310}
    testing_positions_2 = {'Train1': 100, 'Train2': 335, 'Train3': 350, 'Train4': 420}
    
    destinations_1 = {'Train1': 'Yard', 'Train2': 'Station B', 'Train3': 'Station B'}
    destinations_2 = {'Train1': 'Station B', 'Train2': 'Station B', 'Train3': 'Station B', 'Train4': 'Station B'}
    
    block_maint_1 = {}
    block_maint_2 = '4'
    
    print('\n\nSpeed Limit: ', MBO.blue_speed_limit,'km/hr')
    print('Emergency Breaking Distance At Speed Limit: ', MBO.emergency_breaking_distance(), 'm/s \n')
    
    print('----TEST 1: MBO MODE, NO MAINT.----')
    print('Train Positions: ', testing_positions_1, '[m]')
    print('No Blocks Under Maint.')
    test_1_author = MBO.authority(testing_positions_1, destinations_1,block_maint_1)
    print('Authorities: ', test_1_author)
    print(' -Train1 authority = distance to station')
    print(' -Train2 authority = emergency braking distance, train is an unsafe distance away from the train infront of it')
    print(' -Train3 authority = distance to station\n')
    
    print('----TEST 2: MBO MODE, BLOCK MAINT.----')  
    print('Train Positions: ',testing_positions_2, '[m]')
    print('Block 4 Under Maint, Position 150 m')
    test_2_author = MBO.authority(testing_positions_2, destinations_2,block_maint_2)
    print('Authorities: ', test_2_author)
    print(' -Train1 authority = emergency braking distance, must stop before block under maint.')
    print(' -Train2 authority = emergency braking distance, train is an unsafe distance away from the train infront of it')
    print(' -Train3 authority = emergency braking distance, must stop before block under maint.')
    print(' -Train4 authority = distance to station\n')
    
    
    