import csv
from csv import writer
import datetime
from datetime import timedelta

from cryptography.fernet import Fernet
import json

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

#assuming recieving train_positions as {'train_id' : train_id, 'position' : m, 'block' : #}
#sending speed and authority as data = {'train_id' : train_id, 'authority' : m, 'commanded_speed' : m/s}

class MBOOffice:
    
    def __init__(self):
        """
        Initialize the MBO Office
        """
        
        self.enable_speed_authority = 0
        
        self.green_line = Line('Green')
        self.green_line.load_track_blocks()
                
        self.route_authority_green = {'Glenbury Down' : 400 , 'Dormont Down' : 950, 'Mt Lebanon Down' : 500, 'Poplar' : 2786.6, 'Castle Shannon' : 612.5, 
                      'Mt Lebanon Up' : 2887.5 , 'Dormont Up' : 515, 'Glenbury Up' : 921, 'Overbrook Up' : 546, 'Inglewood' : 450, 
                      'Central Up' : 450, 'Edgebrook' : 3684, 'Pioneer' : 700, 'Station' : 675, 'Whited' : 1125, 'South Bank' : 1275,
                      'Central Down' : 400, 'Overbrook Down' : 900, 'Yard' : -125}
        
           
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
            
    def commanded_speed(self, train_position):
        """
        Calculate trains commanded speed based on current block 
        
        return commanded_speed, equal to the speed limit 
        """ 
        #set up to read in dictionary of trains for now, similar to 
        # set equal to speed limit of block 
        block_num = train_position.get("block")
        block = self.green_line.get_track_block(block_num)
        
        print("calculating commanded speed for train in block ", block_num)

        if block: 
            self.block_speed = self.kmhr_to_ms(block.speed_limit)
            
        return(self.block_speed)
    
    def authority(self, train_position):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        #pass trains = list(trains_positions.keys())
        #pass number_of_trains = len(trains)
        
        #pass number_of_block_maint = len(block_maint)
        position = train_position.get("position")
        print("calculating authority for train at position ", position)
        authorities = 100
        
        """for i in range(number_of_trains):
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
                                authorities[train_1] = round(self.service_breaking_distance())"""
                              
        
        return (authorities)
               
    #incorporate time keeper here, every tick call load in posotions, calculate speed and authority, check if can send, if so encypt and emit data   
    class Satellite(QObject):
        
        send_data_signal = pyqtSignal(dict)
        
        #want way to connect train positions to send
        
        def __init__(self):
            super().__init__()
            self.mbo_mode = True
            self.mbo_office = MBOOffice()
            
            self.train_positions = {'train_id' : 'Train1', 'position' : 100, 'block' : 15}
        
        def satellite_send(self):
            """
            gathering info to send over satellite, authority and speed
            
            """
            authority = self.mbo_office.authority(self.train_positions)
            commanded_speed = self.mbo_office.commanded_speed(self.train_positions)
            
            data = {'train_id' : self.train_positions['train_id'], 'authority' : authority, 'commanded_speed' : commanded_speed}
             
            if (self.mbo_mode == True):
                """
                send speed and authority 
                """ 
                print('mbo mode is true')
                #pass encrypted_data = self.encrypty(data)
                
                #will emit encrypt
                self.send_data_signal.emit(data)
                
                 
            else: 
                """
                do not send information, information will be sent to train through CTC office
                """ 
                self.update_satellite({})
        
        def encrypty(self):
            """
            encryption to send vital information
            """
            
        
        def decrypt(self):
            """
            decryption to recieve position(s)
            """
                
    #create schedules from planners selected date and time on UI
    class Schedules:
        def __init__(self):
            super().__init__()
            """
            Initialize the MBO Controller
            """
            #create set of drivers and crew
            self.drivers = ["Alejandro", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"]
            self.crew = ["Alice", "Barbra", "Cole", "Dan", "Earl", "Fern", "George", "Hank", "Ian", "Jack",
                    "Karen", "Leo", "Morgan", "Niel", "Ophelia", "Paul", "Quinn", "Roger", "Stacy", "Terry"]
            
            #info about shifts
            self.shift_length = timedelta(hours= 8, minutes= 30)
            self.drive_length = timedelta(hours=4)
            self.break_length = timedelta(minutes=30)
            
            #time to travel from one station to another 
            self.route_schedule_green = {'Glenbury Down' : timedelta(seconds=20) , 'Dormont Down' : timedelta(minutes=1, seconds=13), 'Mt Lebanon Down' : timedelta(seconds=39), 
                                'Poplar' : timedelta(minutes=2, seconds=45), 'Castle Shannon' : timedelta(minutes=1, seconds=28), 'Mt Lebanon Up' : timedelta(minutes=2, seconds=59), 
                                'Dormont Up' : timedelta(seconds= 17), 'Glenbury Up' : timedelta(minutes=1, seconds=54), 'Overbrook Up' : timedelta(minutes= 1, seconds=35), 
                                'Inglewood' : timedelta(minutes=1, seconds=21), 'Central Up' : timedelta(minutes=1, seconds=21), 'Edgebrook' : timedelta(minutes=4, seconds=50), 
                                'Pioneer' : timedelta(minutes=1, seconds=4), 'Station' : timedelta(seconds=39), 'Whited' : timedelta(minutes=1, seconds=1), 
                                'South Bank' : timedelta(minutes=1, seconds=21),'Central Down' : timedelta(seconds=48), 'Overbrook Down' : timedelta(minutes= 1, seconds=48), 
                                'Yard' : timedelta(seconds=15)}
        
        
        def create_schedules(self, date_time):
            """_summary_

            Args:
                date_time (_type_): _description_
            """
            print(f"making schedule for: {date_time}")
            print("in shcedules class") 
                                  


#pass if __name__ == "__main__":
    
    
    
    