import csv
from csv import writer
import datetime
from datetime import timedelta
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
import json

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.train_dispatch import TrainDispatchUpdate
from train_system.mbo_manager.mbo_train_dispatch import MBOTrainDispatch


class MBOOffice(QObject):
    train_dispatch_updated = pyqtSignal(TrainDispatchUpdate)
    
    def __init__(self):
        super().__init__()
        """
        Initialize the MBO Office
        """
        self.green_line = Line('Green')
        self.green_line.load_track_blocks()
        
        # Create a list of train objects
        self.trains: Dict[int, MBOTrainDispatch] = {}
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
            
    def compute_commanded_speed(self, train_position):
        """
        Calculate trains commanded speed based on current block 
        
        return commanded_speed, equal to the speed limit 
        """ 
        
        block_num = train_position.get("block")
        block = self.green_line.get_track_block(block_num)
        
        print("calculating commanded speed for train in block ", block_num)

        if block: 
            self.block_speed = self.kmhr_to_ms(block.speed_limit)
            
        return(self.block_speed)
    
    def compute_authority(self, train_id, position, current_block):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        self.authority = 0
        
        #decrease authority!! 
        #compare two positions along the line
        
        #want to take in signal that has trains_id, position, and block number??
        
        if not self.train_exists(train_id):
            return 0
        
        train = self.get_train(train_id)
        #get trains current block from satellite not train dispatch 
        next_stop_block = train.get_next_stop()
        
        print(f"calculating authority for {train_id} at position {position} at block {current_block} and going to {next_stop_block} ")
        
        #list of blocks to next stop, including start and end 
        path = train.get_route_to_next_stop()
        
        #if next stop block has not changed 
        path_length = 0
        
        for blocks in path:
            path_length_m += blocks.length 
        
        #set authority to next station stop 
        self.authority = path_length - (next_stop_block.length / 2) ##NEED TO FIX TO TAKE INTO ACCOUNT TRAINS CURRENT POSITION AND ASSUMPTION THAT THE TRAIN POSITION IS FROM THE FRONT OF THE TRAIN AND WANT MIDDLE OF TRAIN TO STOP AT THE MIDDLE OF THE BLOCK 
        
        #change authority to service break distance if... 
        
        #next block is under maint or next block != path[1]
        
        
        #conditions to change authority 
            #to close to next train on path
            # next block is under maint (next_block.under_mainenance = True)
            # switch is not in the right position (next_block != next_block_path)
            #going to yard (next_stop_block = self.line.yard then authority is negative)
            #1Mil to show open doors, for a minute while at stop 
                #train is within 1 trains length of middle of block AND has been at the same position for two ticks in a row
                #train_dispatch compute_departure_time
                #pop next stop??
            #if minute has passed, start authority to next stop 
                #if time_keeper = departure time 
                    #authority = path to next station 
        
        return (self.authority)
               
    #incorporate time keeper here, every tick call load in posotions, calculate speed and authority, check if can send, if so encypt and emit data   
    class Satellite(QObject):
        
        send_data_signal = pyqtSignal(str, float, float)
        
        #want way to connect train positions to send
        
        def __init__(self):
            super().__init__()
            self.mbo_mode = True
            self.mbo_office = MBOOffice()
            
            self.train_positions = {}
            self.train_id = 'Train1'
        
        @pyqtSlot(str, float, int)
        def satellite_recieve(self, train_id: str, position: float, block: int) -> None:
            """
            Recieve train position
            
            Args:
                train_id (str): _description_
                position (float): _description_
                blcok (int): _description_
            """
            self.train_positions[train_id] = {'position' : position, 'block' : block}
            self.satellite_send(train_id)
        
        def satellite_send(self, train_id: str):
            """
            gathering info to send over satellite, authority and speed
            
            """
            self.train_info = self.train_positions[train_id]
            self.authority = self.mbo_office.compute_authority(self.train_info)
            self.commanded_speed = self.mbo_office.compute_commanded_speed(self.train_info)
             
            if (self.mbo_mode == True):
                """
                send speed and authority 
                """ 
                print('mbo mode is true')
                #pass encrypted_data = self.encrypty(data)
                
                #will emit encrypt
                self.send_data_signal.emit(self.train_id, self.authority, self.commanded_speed)
                  
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
            
            self.green_line = Line('Green')
            self.green_line.load_track_blocks()
            
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
            
            i = 65
            block = self.green_line.get_track_block(i)
            station = block.station
            print(station)
            print("in create schedules")
            
            
            
            
            
            
            
            
#pass if __name__ == "__main__":

    
    
    