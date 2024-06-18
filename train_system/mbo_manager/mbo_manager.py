
class MBOController:
    def __init__(self):
        """
        Initialize the MBO Controller
        """
        self.train_commanded_speeds = {}
        self.train_authorities = {}
        self.block_maintanece = {}
        
        self.dispatch_mode = {} #manual and mbo 
        self.mbo_mode = {}  #fixed block or mbo 
        self.enable_s_and_a = 0
        
        self.lines = {'Blue'}
        self.blue_speed_limit = 50 #km/hr, convert to m/s
        
        self.trains_positions = {"Train1" : 0}
   
        self.stations = ["Yard", "Station B", "Station C"]
        self.drivers = ["Driver 1", "Driver 2", "Driver 3"]
        self.crew = ["Crew 1", "Crew 2", "Crew 3", "Crew 4", "Crew 5", "Crew 6"]
        
       
    def kmhr_to_ms(self, blue_speed_limit):
        return(self.blue_speed_limit * (1000/3600))
        
    def distance_between(self): #?? idk, or time to travel based of distance between?
        """
        finding the distance in bettween 
            stations?
            
        """ 
        #yard to b = 500m 
        #b to c = 
    
    def create_schedules(self, selected_day, selected_start_time):
        """
        Create schedule options 
        """
        #where does hayden want me to save these files? send to folder in ctc folder? label schedules? 
        #schedule as txt? cvs? excel? 
        
        #printing to command for demo 
        print('making schedule for: ', selected_day)
        print('starting schedule at ', selected_start_time)
        
        #creating all 3 schedule options 
        low_throughput_filename = selected_day + '_low.txt'
        med_throughput_filename = selected_day + '_med.txt'
        high_throughput_filename = selected_day + '_high.txt'
        
        #creating file names for all three schedule types  
        low_file = open(low_throughput_filename, 'w')
        med_file = open(med_throughput_filename, 'w')
        high_file = open(high_throughput_filename, 'w')
        
        #headers for each file 
        low_file.write('Train      Line    Station    Arrival Time    Departure Time    Driver    Crew 1    Crew 2    Crew 3\n')
        med_file.write('Train      Line    Station    Arrival Time    Departure Time    Driver    Crew 1    Crew 2    Crew 3\n')
        high_file.write('Train      Line    Station    Arrival Time    Departure Time    Driver    Crew 1    Crew 2    Crew 3\n')
        
        #all crew need a break after 4 hours 
        #.5 hour break 
        #8.5 hour shifts total 
        
        #total schedule needs to go from start time + 24 hours 
        
        #initial speed and authority on schedule for CTC? I think not necessary since CTC has ability to calculate this on their own? 
        
        for i in range(1,5):
            low_file.write('Train ' + repr(i) + '   ' + repr(self.lines) + '   Station B   ' + repr(selected_start_time) + '    ' + repr(selected_start_time) +'\n')
        
        
        #closing files when finished 
        low_file.close()
        med_file.close()
        high_file.close()
        
     
    def enable_mbo_mode(self, dispatch_mode, enable_s_and_a):
        """
        If dispatcher selects MBO mode, enable sending speed and authority 
        """  
        #print in command prompt for test bench purposes? 
        
        if self.dispatch_mode == 'MBO': 
            self.enable_s_and_a = 1;  
        
        else:
            self.enable_s_and_a = 0;
        
    def commanded_speed(self, enable_s_and_a ):
        """
        Calculate trains commanded speed 
        """
        if(enable_s_and_a):
        #do i need to adjust speed when train needs to stop? 
        
            return(self.blue_speed_limit)
        
    def authorirty(self):
        """
        Calculate trains authority such that more than one train can be in a block 
        """
        print(self.trains_positions)
        #leaving yard authorirty is 250 m 
        #station b to station c authority?
        #station c to yard is 250 m 
        
        #if entering a block and the next block is under maintance, authority = length of block 
        
        #if train is x meters away from the train infront of it, set authority to emergency breaking distance?
            #emergency break = 2.73m/s2
            #how far will train travel if break is applied while traveling 50km/hr 
            
    
        

if __name__ == "__main__":
    MBO = MBOController()
    speed_limit = MBO.blue_speed_limit
    m = MBO.kmhr_to_ms(speed_limit)
    print(m)
    