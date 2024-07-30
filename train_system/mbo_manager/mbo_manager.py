import csv
from csv import writer
import datetime
from datetime import timedelta
from datetime import datetime
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
import json
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.conversions import *
from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock


class MBOOffice(QObject):
    
    def __init__(self, time_keeper: TimeKeeper):
        super().__init__()
        """
        Initialize the MBO Office
        """
        self.time_keeper = time_keeper
        self.green_line = Line('Green')
        self.green_line.load_defaults()
        
        self.red_line = Line('Red')
        self.red_line.load_defaults()
        
        # Create a list of train objects
        #pass self.trains: Dict[int, TrainDispatchUpdate] = {}
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
            
    def compute_commanded_speed(self, train_id, block):
        """Commanded speed for a train based off of the block it is currently in 

        Args:
            train_id (_type_): _description_
            block (_type_): _description_
        """
        
        current_block = self.green_line.get_track_block(block)
        print(f"calculating commanded speed for {train_id} in block ", block)

        if block: 
            self.block_speed = self.kmhr_to_ms(current_block.speed_limit)
            
        return(self.block_speed)
    
    def compute_authority(self, train_id, position, velocity, block):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        # "authority:destination_block"
        #initial authority will be unobtructed path to destination 
            #looking for blocks under maint, switch positions 
        #if train infront is within certain distance of the train then set authority tooooo
            # service breaking distance? 
        
        #use mbo_train_dispatch to adjust the departure time and next stop for the train once it reaches it's destination 

        
        
        
        #need to remove next block 
        return (self.authority)
    
               
    class Satellite(QObject):
        
        #trainid, authority, speed
        send_data_signal = pyqtSignal(str, float, float)
        
        def __init__(self):
            super().__init__()
            self.mbo_mode = True
            #pass self.mbo_office = MBOOffice()
            
            self.train_positions = {}
            self.train_id = ''
            
            time_keeper = TimeKeeper()
            
            self.mbo_office = MBOOffice(time_keeper)
            
            #is key int or string? think string
            key = 0
        
        @pyqtSlot(str, float, int)
        def satellite_recieve(self, train_id: str, position: float, block: int) -> None:
            """
            Recieve train position
            
            Args:
                train_id (str): _description_
                position (float): _description_
                blcok (int): _description_
            """
            #pass self.train_positions[train_id] = {'position' : position, 'block' : block}
            self.satellite_send(train_id, position, float)
        
        def satellite_send(self, train_id: str, position: float, block: int):
            """
            gathering info to send over satellite, authority and speed
            
            """
            #pass self.train_info = self.train_positions[train_id]
            
            self.authority = self.mbo_office.compute_authority(train_id, position, block)
            self.commanded_speed = self.mbo_office.compute_commanded_speed(train_id, block)
             
            if (self.mbo_mode == True):
                """
                send speed and authority 
                """ 
                print('mbo mode is true')
                #pass encrypted_id = self.encrypty(train_id)
                #pass encrypted_authority = self.encrypt(authority)
                #pass encrypted_speed = self.(commanded_speed)
                
                #will emit encrypt
                self.send_data_signal.emit(self.train_id, self.authority, self.commanded_speed)
                  
            else: 
                """
                do not send information, information will be sent to train through CTC office
                """ 
                #TODO what train model wants me to send when in fixed block? 
                self.update_satellite({})
        
        def encrypty(self):
            """
            encryption to send vital information
            """
            #will generate key in top level main to use here, and encrypt the speed and authority 
            
        
        def decrypt(self):
            """
            decryption to recieve position(s)
            """
            #will generate key in top level main to use here, and decrypt the speed and authority 
            
 


                    
                               
            
# pass if __name__ == "__main__":
    
    

    
    
    