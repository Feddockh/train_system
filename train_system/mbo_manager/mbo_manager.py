
class MBOController:
    def __init__(self):
        """
        Initialize the MBO Controller
        """
        
        self.dispatch_mode = {} #manual and mbo 
        self.mbo_mode = {}  #fixed block or mbo 
        self.enable_s_and_a = 0
        
        self.lines = {'Blue'}
        self.blue_speed_limit = 50 #km/hr, convert to m/s
        
        self.trains_positions = {"Train1" : 0}
   
        self.stations = ["Yard", "Station B", "Station C"]
        self.drivers = ["Driver 1", "Driver 2", "Driver 3"]
        self.crew = ["Crew 1", "Crew 2", "Crew 3", "Crew 4", "Crew 5", "Crew 6"]
        
       
    def kmhr_to_ms(self, km_hr):
        """convert km/hr to m/s

        Args:
            km_hr (float?): km/hr that needs to be converted to m/s, mostly for setting commanded speed based of speed limit 
        """
        return(km_hr * (1000/3600))
    
    def emergency_breaking_distance(self):
     """
     distance the train will travel after emergency break is pulled
        (+ some wiggle room? )
     """ 
     emergency_brake_acceleration = 2.73 #m/s^2
     v = self.commanded_speed(self.enable_s_and_a)
     breaking_distance = -1* (1/2)*(v)*(-1 * emergency_brake_acceleration)
    
     print(breaking_distance)
     return (breaking_distance)
    
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
        Arg = enable_s_and_a to know if MBO has control to send speed
         
        return commanded_speed which is just equal to the speed limit 
                (will need to be the speed limit for the section/block)
        """
        if(enable_s_and_a):
        #do i need to adjust speed when train needs to stop? 
            self.speed = self.kmhr_to_ms(self.blue_speed_limit)
            return(self.speed)
    
    
    def authorirty(self):
        """
        Calculate trains authority such that more than one train can be in a block 
        """
        print(self.trains_positions)
        
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
        
    
            
    
        

if __name__ == "__main__":
    MBO = MBOController()
    speed_limit = MBO.blue_speed_limit
    m = MBO.kmhr_to_ms(speed_limit)
    print(m)
    