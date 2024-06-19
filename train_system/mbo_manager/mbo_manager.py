from csv import writer

class MBOController:
    def __init__(self):
        """
        Initialize the MBO Controller
        """
        
        self.dispatch_mode = {} #manual and mbo 
        self.mbo_mode = {}  #fixed block or mbo 
        self.enable_s_and_a = 0
        
        self.lines = {'Blue'}
        self.blue_speed_limit = 50.0 #km/hr, convert to m/s
        
        self.test_trains_positions = {"Train1" : 0}
   
        self.stations = ["Yard", "Station B", "Station C"]
        self.drivers = ["Driver 1", "Driver 2", "Driver 3"]
        self.crew = ["Crew 1", "Crew 2", "Crew 3", "Crew 4", "Crew 5", "Crew 6"]
        
       
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
    
    
    def authority(self, trains_positions, block_maint):
        """
        Calculate trains authority such that more than one train can be in a block 
        """
        trains = list(trains_positions.keys())
        number_of_trains = len(trains)
        
        blocks = list(block_maint.values())
        number_of_block_maint = len(block_maint)
        
        authorities = {}
        
        for i in range(number_of_trains):
            train_1 = trains[i]
            position_1 = trains_positions[train_1]
            
            authorities[train_1] = abs(position_1-500)
            
            
            for j in range(i+1, number_of_trains):
                train_2 = trains[j]
                position_2 = trains_positions[train_2]
                distance_from_train = abs(position_1 - position_2)
                
                if(distance_from_train <= float(self.emergency_breaking_distance())):
                    authorities[train_1] = round(self.emergency_breaking_distance())
                
                else: 
                    if(number_of_block_maint > 0 ):
                        for x in range(number_of_block_maint):
                            block_position = blocks[x]
                            to_block = abs(position_1 - block_position)
                            if (to_block <= 50):
                                authorities[train_1] = round(self.emergency_breaking_distance())
                    
                
        
        return (authorities)
                    
       
        #for each train 
            #if train is within emerg braking distance of another train 
                #then authority = emerg breaking distance + c
            #elif train is a block away from block under maint
                #then authority = emerg breaking distance + c 
            #else
                #distance to next stop (station or yard)
     
       

    def create_schedules(self, selected_day, selected_start_time):
        """
        Create schedule options 
        
        return bool to ensure schedules were made - make pop up window in UI to confirm they were made successfully 
                                                        give file path for them
        """
        #where does hayden want me to save these files? send to folder in ctc folder? label schedules? 
        #schedule as txt? cvs? excel? 
        
        #printing to command for demo 
        print('making schedule for: ', selected_day)
        print('starting schedule at ', selected_start_time)
        
        #creating all 3 schedule options 
        low_throughput_filename = selected_day + '_low.csv'
        med_throughput_filename = selected_day + '_med.csv'
        high_throughput_filename = selected_day + '_high.csv'
        
        #creating file names for all three schedule types  
        low_file = open(low_throughput_filename, 'w')
        med_file = open(med_throughput_filename, 'w')
        high_file = open(high_throughput_filename, 'w')
        
        low_writer = writer(low_file)
        med_writer = writer(med_file)
        high_writer = writer(high_file)
        
        
        #headers for each file 
        header = ['Train', 'Line', 'Station', 'Arrival Time', 'Driver', 'Crew 1', 'Crew 2']
        low_writer.writerow(header)
        med_writer.writerow(header)
        high_writer.writerow(header)
        
        
        
        #all crew need a break after 4 hours 
        #.5 hour break 
        #8.5 hour shifts total 
        #total schedule needs to go from start time + 24 hours 
        
        #low throughput schedule = 1 train 
        
        #med throughput schedule = 2 trains 
        
        #high throughput shcedule = 3 trains 
        
        
        
        #initial speed and authority on schedule for CTC? I think not necessary since CTC has ability to calculate this on their own? 
        
        for i in range(1,5):
            low_file.write('Train ' + repr(i) + '   ' + repr(self.lines) + '   Station B   ' + repr(selected_start_time) + '    ' + repr(selected_start_time) +'\n')
        
        
        #closing files when finished 
        low_file.close()
        med_file.close()
        high_file.close()
        
    
                 

if __name__ == "__main__":
    MBO = MBOController()
    MBO.enable_s_and_a = 1
    testing_positions_1 = {'Train1': 100, 'Train2': 300, 'Train3': 310}
    testing_positions_2 = {'Train1': 100, 'Train2': 335, 'Train3': 350, 'Train4': 420}
    block_maint_1 = {}
    block_maint_2 = {'4': 150,'9': 400 }
    
    print('\n\nSpeed Limit: ', MBO.blue_speed_limit,'km/hr')
    print('Emergency Breaking Distance At Speed Limit: ', MBO.emergency_breaking_distance(), 'm/s \n')
    
    print('----TEST 1: MBO MODE, NO MAINT.----')
    print('Train Positions: ', testing_positions_1, '[m]')
    print('No Blocks Under Maint.')
    test_1_author = MBO.authority(testing_positions_1, block_maint_1)
    print('Authorities: ', test_1_author)
    print(' -Train1 authority = distance to station')
    print(' -Train2 authority = emergency braking distance, train is an unsafe distance away from the train infront of it')
    print(' -Train3 authority = distance to station\n')
    
    print('----TEST 2: MBO MODE, BLOCK MAINT.----')  
    print('Train Positions: ',testing_positions_2, '[m]')
    print('Block 4 Under Maint, Position 150 m')
    test_2_author = MBO.authority(testing_positions_2, block_maint_2)
    print('Authorities: ', test_2_author)
    print(' -Train1 authority = emergency braking distance, must stop before block under maint.')
    print(' -Train2 authority = emergency braking distance, train is an unsafe distance away from the train infront of it')
    print(' -Train3 authority = emergency braking distance, must stop before block under maint.')
    print(' -Train4 authority = distance to station\n')
    
    
    