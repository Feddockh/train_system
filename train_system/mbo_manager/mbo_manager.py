import csv
from csv import writer
import datetime
from datetime import timedelta



class MBOController:
    def __init__(self):
        """
        Initialize the MBO Controller
        """
        
        self.enable_s_and_a = 1
        
        #create file for drivers and crew? 
        self.drivers = ["Alejandro", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"]
        self.crew = ["Alice", "Barbra", "Cole", "Dan", "Earl", "Fern", "George", "Hank", "Ian", "Jack",
                "Karen", "Leo", "Morgan", "Niel", "Ophelia", "Paul", "Quinn", "Roger", "Stacy", "Terry"]
        
        self.route_schedule_green = {'Glenbury Down' : timedelta(seconds=20) , 'Dormont Down' : timedelta(minutes=1, seconds=13), 'Mt Lebanon Down' : timedelta(seconds=39), 
                               'Poplar' : timedelta(minutes=2, seconds=45), 'Castle Shannon' : timedelta(minutes=1, seconds=28), 'Mt Lebanon Up' : timedelta(minutes=2, seconds=59), 
                               'Dormont Up' : timedelta(seconds= 17), 'Glenbury Up' : timedelta(minutes=1, seconds=54), 'Overbrook Up' : timedelta(minutes= 1, seconds=35), 
                               'Inglewood' : timedelta(minutes=1, seconds=21), 'Central Up' : timedelta(minutes=1, seconds=21), 'Edgebrook' : timedelta(minutes=4, seconds=50), 
                               'Pioneer' : timedelta(minutes=1, seconds=4), 'Station' : timedelta(seconds=39), 'Whited' : timedelta(minutes=1, seconds=1), 
                               'South Bank' : timedelta(minutes=1, seconds=21),'Central Down' : timedelta(seconds=48), 'Overbrook Down' : timedelta(minutes= 1, seconds=48), 
                               'Yard' : timedelta(seconds=15)}
        
        self.route_authority_green = {'Glenbury Down' : 400 , 'Dormont Down' : 950, 'Mt Lebanon Down' : 500, 'Poplar' : 2786.6, 'Castle Shannon' : 612.5, 
                      'Mt Lebanon Up' : 2887.5 , 'Dormont Up' : 515, 'Glenbury Up' : 921, 'Overbrook Up' : 546, 'Inglewood' : 450, 
                      'Central Up' : 450, 'Edgebrook' : 3684, 'Pioneer' : 700, 'Station' : 675, 'Whited' : 1125, 'South Bank' : 1275,
                      'Central Down' : 400, 'Overbrook Down' : 900, 'Yard' : -125}
        
        self.route_schedule_red = {}
        self.route_authority_red = {}
        
        self.shift_length = timedelta(hours= 8, minutes= 30)
        self.drive_length = timedelta(hours=4)
        self.break_length = timedelta(minutes=30)
       
        #for testing for it 2 and MBO Mode View 
        self.train_ids = list(range(1,11))
        
        self.testing_positions_1 = {'Train1': 0, 'Train2': 150, 'Train3': 300}
        self.testing_positions_2 = {'Train1': 100, 'Train2': 335, 'Train3': 350, 'Train4': 420}
        
        self.destinations_1 = {'Train1': 'Yard', 'Train2': 'Station B', 'Train3': 'Station C'}
        self.destinations_2 = {'Train1': 'Station B', 'Train2': 'Station B', 'Train3': 'Station B', 'Train4': 'Station B'}
        
        self.block_maint_1 = {}
        self.block_maint_2 = {'4': 150,'9': 400 }
        
        self.low_trains = ["Train1"]
        self.med_trains = ["Train1", "Train2"]
        self.high_trains = ["Train1", "Train2", "Train3"]
        
        self.lines = ["Green", "Red"]
        self.blue_speed_limit = 50.0 #km/hr, convert to m/s
        self.blocks = {'1' : 0 , "2" : 50, "3" : 100, "4" :150, "5" :200, "6" : 250, "7" : 300, "8" : 350, "9" : 400, "10": 450, "11": 250, "12" : 300, "13" : 350, "14" : 400, "15" : 450}
        
        
       
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
            
    def commanded_speed(self):
        """
        Calculate trains commanded speed
        
        return commanded_speed, equal to the speed limit 
        """ 
        
        #change to use track_block.py 
            #to do this is there a way to figure out and set the positions for each block? Since I do not know which block trains are in just there positions 
            #set range of distance of block length from the yard? 
        
        # set equal to speed limit of block 
        self.speed = self.kmhr_to_ms(self.blue_speed_limit)
            
        return(self.speed)
    
    def authority(self, trains_positions, destinations, block_maint):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        trains = list(trains_positions.keys())
        number_of_trains = len(trains)
        
        number_of_block_maint = len(block_maint)
        
        authorities = {}
        
        for i in range(number_of_trains):
            train_1 = trains[i]
            position_1 = trains_positions[train_1]
            destination_1 = self.route_authority_green[destinations[0]]
            
            authorities[train_1] = destination_1
            
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
       
    def create_schedules(self, date_time):
        """
        Create schedule options 
        """
        
        print(f"making schedule for: {date_time}")
        
       
                 
    def enable_speed_authority(self):
        """
        Enable or Disable sending Speed and Authority through satellite
        Enable when in MBO Manual or MBO Automatice, Disable otherwise 
        Enable = 1, Disable = 0
        """
        
    
    def satellite_send():
        """
        gathering info to send over satellite, authority and speed
        
        """
        #call authories and sat for each train, send info for each train 
        #set as signals? 
                                  

if __name__ == "__main__":
    MBO = MBOController()
      
    time1 = timedelta(minutes = 1, seconds= 48)
    time2 = timedelta(minutes = 2, seconds= 12)
    print(time1 + time2)
    
    for x in MBO.route:
        print(x)
        print(MBO.route[x])
    
    
    