import csv
from csv import writer
import datetime
from datetime import timedelta
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from cryptography.fernet import Fernet
import json
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.conversions import *
from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

from train_system.common.train_dispatch import TrainRouteUpdate
from train_system.mbo_manager.mbo_train_dispatch import MBOTrainDispatch


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
        
        #list of trains 
        self.trains: Dict[Tuple[int, str], MBOTrainDispatch] = {}
        
              
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
            
    def compute_commanded_speed(self, line, block):
        """Commanded speed for a train based off of the block it is currently in 

        Args:
            line (_type_): _description_
            block (_type_): _description_
        """
        current_block = self.line.get_track_block(block)
        if block: 
            self.block_speed = self.kmhr_to_ms(current_block.speed_limit)
            
        return(self.block_speed)
    
    def compute_authority(self, train_id, line_name, position, velocity, block):
        """
        Calculate trains authority such that more than one train can be in a block 
        each train stops at it's desitnation and opens the doors, and stops before any block maintenance 
        """
        # "authority:destination_block"
            #where authority is the m to it needs to stop 
            #where destination block is next station 

        #if block is in 57 then train padding needs to be bigger
        #block  in red 

        #initial authority will be unobtructed path to destination 
            #looking for blocks under maint, switch positions then will change 
            
        #if train infront is within certain distance of the train then set authority tooooo
            # service breaking distance? 
            #set to back of train infront with some wiggle room 
        
        #use mbo_train_dispatch to adjust the departure time and next stop for the train once it reaches it's destination 

        train = self.get_train(train_id, line_name)
        line = self.get_line(line_name)
        
        destination_block = train.get_next_stop()[1]
        
        path = train.get_route_to_next_stop()
        unobstructed_path = line.get_unobstructed_path(path)
        
        authority_distance = line.get_path_length(unobstructed_path)
        #authority_distance -= distance traveled from previous station 
        #authority_distance += stop block length/2 +half of train ?? 
        
        #check 2 trains will not be to close 
            #if within 40m + 33m (back of train) to next train 
                #authority goes to 10m from back of next train 
                
            #if within 10m train
                #authoirity goes to 0? 
        
        #for trains on line in self.trains:
            #if (trains.position - train.position <= )  
            
            #if (line = green line) and block = 57?     
                #make padding bigger 
            #if (line = red line) and block = ? 
                #make padding bigger
                
        #if (current block == next_stop) and (velocity == 0) and (train.departed == False)    
        
        #make string 
        # authority = "authority_distance:destination_block"
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
        
        def satellite_send(self, train_id: str, position: float, velocity: float, block: int):
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
            
        @pyqtSlot(int)
        def handle_time_update(self, tick: int) -> None:
            """send speed and authority every step - IF in MBO mode 

            Args:
                tick (int): _description_
            """
            #every tick, send satellite info to train 
            for (train_id, line_name), train in self.trains.items():
                if train.dispathed :
                    self.satellite_send(train_id)
            
        @pyqtSlot(str, float, int)
        def satellite_recieve(self, train_id: str, position: float, velocity: float, block: int) -> None:
            """
            Recieve train position
            
            Args:
                train_id (str): _description_
                position (float): _description_
                blcok (int): _description_
            """
            #update train position, velocity, and current block in MBO train dispatch for each train??
             
              
        
        @pyqtSlot(bool)
        def switch_modes():
            """
            
            """  
            
 


                    
                               
            
# pass if __name__ == "__main__":
    
    

    
    
    