import csv
from csv import writer
import datetime
from datetime import timedelta
from train_system.common.dispatch_mode import DispatchMode


class MBOController:
    def __init__(self):
        """
        Initialize the MBO Controller
        """
        self.dispatch_mode = DispatchMode.AUTOMATIC_MBO_OVERLAY
        
        self.enable_s_and_a = 1
        
        self.lines = ["Green", "Red"]
        self.blue_speed_limit = 50.0 #km/hr, convert to m/s
        
        self.blocks = {'1' : 0 , "2" : 50, "3" : 100, "4" :150, "5" :200, "6" : 250, "7" : 300, "8" : 350, "9" : 400, "10": 450, "11": 250, "12" : 300, "13" : 350, "14" : 400, "15" : 450}
   
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
        
        self.route_schedule_green = {"Glenbury Down" : timedelta(seconds=20) , "Dormont Down" : timedelta(minutes=1, seconds=13), "Mt Lebanon Down" : timedelta(seconds=39), 
                               "Poplar" : timedelta(minutes=2, seconds=45), "Castle Shannon" : timedelta(minutes=1, seconds=28), "Mt Lebanon Up" : timedelta(minutes=2, seconds=59), 
                               "Dormont Up" : timedelta(seconds= 17), "Glenbury Up" : timedelta(minutes=1, seconds=54), "Overbrook Up" : timedelta(minutes= 1, seconds=35), 
                               "Inglewood" : timedelta(minutes=1, seconds=21), "Central Up" : timedelta(minutes=1, seconds=21), "Edgebrook" : timedelta(minutes=4, seconds=50), 
                               "Pioneer" : timedelta(minutes=1, seconds=4), "Station" : timedelta(seconds=39), "Whited" : timedelta(minutes=1, seconds=1), 
                               "South Bank" : timedelta(minutes=1, seconds=21),"Central Down" : timedelta(seconds=48), "Overbrook Down" : timedelta(minutes= 1, seconds=48), 
                               "Yard" : timedelta(seconds=15)}
        
        self.route_authority_green = {"Glenbury Down" : 400 , "Dormont Down" : 950, "Mt Lebanon Down" : 500, "Poplar" : 2786.6, "Castle Shannon" : 612.5, 
                      "Mt Lebanon Up" : 2887.5 , "Dormont Up" : 515, "Glenbury Up" : 921, "Overbrook Up" : 546, "Inglewood" : 450, 
                      "Central Up" : 450, "Edgebrook" : 3684, "Pioneer" : 700, "Station" : 675, "Whited" : 1125, "South Bank" : 1275,
                      "Central Down" : 400, "Overbrook Down" : 900, "Yard" : -125}
        
        #testin for MBO Mode View 
        self.testing_positions_1 = {'Train1': 100, 'Train2': 300, 'Train3': 310}
        self.testing_positions_2 = {'Train1': 100, 'Train2': 335, 'Train3': 350, 'Train4': 420}
        
        self.destinations_1 = {'Train1': 'Yard', 'Train2': 'Station B', 'Train3': 'Station B'}
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
    
    def service_breaking_distance(self):
     """
     distance the train will travel after emergency break is pulled
        (+ some wiggle room? )
     """ 
     service_brake_acceleration = 1.2
     v = self.kmhr_to_ms(70)
     breaking_distance = -1* (1/2)*(v)*(-1 * service_brake_acceleration)
    
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
    
        
    def commanded_speed(self):
        """
        Calculate trains commanded speed
        
        return commanded_speed, equal to the speed limit 
        """ 
        # set equal to speed limit of block 
        self.speed = self.kmhr_to_ms(self.blue_speed_limit)
            
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
                
                if(distance_from_train <= float(self.service_breaking_distance())):
                    authorities[train_1] = round(self.service_breaking_distance())
                
                else: 
                    if(number_of_block_maint > 0 ):
                        for x in range(number_of_block_maint):
                            block_position = self.blocks[block_maint]
                            to_block = abs(position_1 - block_position)
                            if (to_block <= 50):
                                authorities[train_1] = round(self.service_breaking_distance())
                              
        
        return (authorities)
       

    def create_schedules(self, selected_day, selected_start_time):
        """
        Create schedule options 
        """
        
        print('making schedule for: ', selected_day)
        print('starting schedule at ', selected_start_time)
        
        start_time = datetime.datetime.strptime(selected_day + ' ' + selected_start_time, '%m-%d-%Y %H:%M:%S')
        
        current_time = start_time
        end_time = start_time + timedelta(hours= 24)
        number_low_trains = len(self.low_trains)
        crew_index = 0
        driver_index = 0
        schedule = []
        current_time = start_time
        
        for train_id in self.train_ids:
            driver = self.drivers[driver_index]
            crew1 = self.crew[crew_index]
            crew2 = self.crew[crew_index + 1]
            crew_index += 2
            driver_index += 1
            
            shift_end_time = current_time + self.shift_length
            shift_start = current_time
            
            while current_time < shift_end_time and current_time < end_time:

                for i in self.route_schedule:
                    travel_time = self.route_schedule[i]
                    arrival_time = current_time + travel_time
                    if arrival_time > shift_end_time:
                        break
                    
                    schedule.append([f"Train{train_id}", f"{i}", self.lines[0] ,arrival_time, driver, crew1, crew2])
                    
                    #adding time to stop at station for 1 minute
                    current_time = arrival_time + timedelta(minutes=1)
                
                if (current_time - shift_start) >= self.drive_length:
                    current_time += self.break_length
                    if current_time >= shift_end_time or current_time >= end_time:
                        break
                    
            current_time = shift_end_time
            if current_time >= end_time:
                break
    
        low_throughput_file = selected_day + '_green_low.csv'
        with open(low_throughput_file, 'w', newline='') as csvfile:
            schedule_writer = csv.writer(csvfile)
            schedule_writer.writerow(["Train", "Line", "Station", "Arrival Time", "Driver", "Crew 1", "Crew 2"])
            
            for t in schedule:
                schedule_writer.writerow(t)
                
    
    def enable_speed_authority(self):
        """
        Enable or Disable sending Speed and Authority through satellite
        Enable when in MBO Manual or MBO Automatice, Disable otherwise 
        Enable = 1, Disable = 0
        """
        if (self.dispatch_mode == DispatchMode.AUTOMATIC_MBO_OVERLAY or self.dispatch_mode == DispatchMode.MANUAL_MBO_OVERLAY):
            self.enable_s_and_a = 1
        else:
            self.enable_s_and_a = 0 
    
    def satellite_send():
        """
        gathering info to send over satellite, authority and speed
        
        """
        #call authories and sat for each train, send info for each train 
        
                           

if __name__ == "__main__":
    MBO = MBOController()
      
    time1 = timedelta(minutes = 1, seconds= 48)
    time2 = timedelta(minutes = 2, seconds= 12)
    print(time1 + time2)
    
    for x in MBO.route:
        print(x)
        print(MBO.route[x])
    
    
    