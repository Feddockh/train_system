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
        #self.time_keeper.tick.connect(self.handle_time_update)
        
        self.green_line = Line("green", time_keeper)
        self.green_line.load_defaults()
        
        self.red_line = Line("red", time_keeper)
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
        """Compute authority for trains such that 2 trains can be in the same block 

        Args:
            train_id (int): identifier of the train
            line_name (str): the line the train is one
            position (float): the current distance the train has traveld since leaving from yard
            velocity (float): current velocity of the train
            block (int): the current block the train is in

        Returns:
            str: authority and destination block packed together to send to train
        """
        
        #load in train info and trains destination
        train = self.get_train(train_id, line_name)
        destination_block = train.get_next_stop()[1]
        
        #load in line info
        if line_name == "Green":
            line = self.green_line
        elif line_name == "Red":
            line = self.red_line    
        
        #if train has not left yard or station = 0 
        if train.departed == False or train.dispatched == False:
            authority_distance = 0
            
        #find path and unobstructed path
        path = train.get_route_to_next_stop()
        path_length = line.get_path_length(path)
        
        unobstructed_path = line.get_unobstructed_path(path)
        unobstructed_path_length = line.get_path_length(unobstructed_path)
        
        path_current_block = line.get_path(152, 152, block)
        distance_to_block = line.get_path_length(path_current_block)
        
        #if no line obstacle to destination, else unobstructed path
        if(unobstructed_path == path):
            #path length - distance traveled in current block - distance needed to stop at station
            authority_distance = path_length - ( (destination_block.get_length / 2) - (.5 * 32.2) ) - (position - distance_to_block)
        else:
            authority_distance = unobstructed_path_length 
        
        #for trains in train 
        for (train_id, line_name), train_1 in self.trains.items():
            if train_1.line == line_name:
                #greean line to yard check
                if(block == 57 or block == 58 or block == 59 or block == 61):
                    #allow wiggle room for switch to go back into position and when position is off regular count
                    if(train_1.current_block == path[1] or train_1.current_block == unobstructed_path[1]):
                        authority_distance = 0
                    #extra authority to make sure train gets back to the yard
                    elif (destination_block == line.yard):
                        authority_distance += 50
                
                elif(0 <= train_1.position - position <= 65):
                    #trains are to close together back one needs to slow down/stop
                    authority_distance = 0
                
                elif(0 <= train_1 - position <= 125):
                    #train behind has authority to back of next train w/ some wiggle room 
                    authority_distance = (train_1.position - position) - 65
                                     
        # authority = "authority_distance:destination_block"     
        authority = str(authority_distance) + ":" + str(destination_block)

        return (authority)
             
    class Satellite(QObject):
        
        #train_id, "authority:destination_block", "commanded_speed"
        send_data_signal = pyqtSignal(int, str, str)
        
        def __init__(self):
            super().__init__()
            
            self.mbo_mode = True
            self.key = ''
            
        @pyqtSlot(int, str, str, str)
        def satellite_recieve(self, train_id: int, encrypt_block: str, encrypt_position: str, encrypt_velocity:str ) -> None:
            """get updated information regarding the trains current position, velocity, and current block 

            Args:
                encrypted_train_id (str): identifier of which train is being updating 
                "
            """
            
            #decrypt information sent from the train model
            new_position = self.decrypt(encrypt_position)
            new_velocity = self.decrypt(encrypt_velocity)
            new_block = self.decrypt(encrypt_block)
            
            #update the information for each train
            train = self.get_train(train_id)
            train.position = float(new_position)
            train.velocity = float(new_velocity)
            train.current_block = int(new_block)
            
            if new_block != train.current_block :
                train.move_train_to_next_block()   
            
        def satellite_send(self, train_id: int):
            """send information about authority and commanded speed to the train model 
                when in MBO mode else send nothing 

            Args:
                train_id (int): _description_
            """
            train = self.get_train(train_id)
            position = train.position
            velocity = train.velocity
            block = train.block
            
            authority = self.compute_authority(train_id, position, velocity, block)
            commanded_speed = self.compute_commanded_speed(train_id, block)
            
            encrypt_train_id = self.encrypt(str(train_id))
            encrypt_authority = self.encryt(authority)
            encrypt_speed = self.encrypt(commanded_speed)
             
            if (self.mbo_mode == True):
                self.send_data_signal.emit(encrypt_train_id, encrypt_authority, encrypt_speed)
            
        def encrypt(self, plain_text):
            """_summary_

            Args:
                key (_type_): _description_
                plain_text (_type_): _description_

            Returns:
                _type_: _description_
            """
             
            cipher_text = self.cipher_suite.encrypt(plain_text.encode())
            
            return (cipher_text)
            
        def decrypt(self, cipher_text):
            """_summary_

            Args:
                key (_type_): _description_
                cipher_text (_type_): _description_

            Returns:
                _type_: _description_
            """
            
            plain_text = self.cipher_suite.decrypt(cipher_text.decode())
            
            return (plain_text)
            
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
               
        @pyqtSlot(bool)
        def switch_modes(self, mbo: bool):
            """Know when CTC switched between FBO and MBO mode

            Args:
                mbo (bool): track current overlay mode
            """
            if mbo == True:
                self.mbo_mode == True
            else:
                self.mbo_mode == False 
        
        @pyqtSlot(str)
        def key_recieved(self, key_value: str):
            """receive key to encrypt and decrypt vital information

            Args:
                key_value (str): _description_
            """
            self.key = key_value 
            self.cipher_suite = Fernet(self.key)
                                
            
# pass if __name__ == "__main__":
    
    

    
    
    