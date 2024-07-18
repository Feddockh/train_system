
import copy
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.crossing_signal import CrossingSignal
import sys
import paramiko
import time

crossing_signal_map = {
    CrossingSignal.ON: True,
    CrossingSignal.OFF: False,
    CrossingSignal.NA: False
}

class TrackController(QObject):
    def __init__(self, track_blocks: list):
        """
        Initialize variables of the Track Controller.
        """
        super().__init__()

        
        self.track_blocks = track_blocks
        self.plc_program_uploaded = False
        self.plc_program = ""
        self.wayside_name = ""
        self.numBlocks = 0

        self.message_switch58 = ""
        self.message_switch63 = ""
        self.message_switch76 = ""
        
        self.hostname = 'raspberrypi'
        self.port = 22
        self.username = 'garrett'
        self.password = 'Cornell@26'
        
        
        for block in self.track_blocks:
                block.authority_updated.connect(self.handle_authority_update)
                block.occupancy_updated.connect(self.handle_occupancy_update)
                block.suggested_speed_updated.connect(self.handle_speed_update)

    
    @pyqtSlot(bool)
    def handle_occupancy_update(self, new_occupancy: bool) -> None:
        block_number = self.sender().number
        for x in range(len(self.track_blocks)):
            if(block_number) == self.track_blocks[x].number:
                print(f"Block {block_number} occupancy updated to {new_occupancy}")
                self.track_blocks[x]._occupancy = new_occupancy
                if(self.plc_program_uploaded == True):
                    self.run_PLC_program()

    @pyqtSlot(int)
    def handle_speed_update(self, new_speed: int) -> None:
        block_number = self.sender().number
        for x in range(len(self.track_blocks)):
            if(block_number) == self.track_blocks[x].number:
                print(f"Block {block_number} speed updated to {new_speed}")
                self.track_blocks[x].suggested_speed = new_speed

    @pyqtSlot(int)
    def handle_authority_update(self, new_authority: int) -> None:
        block_number = self.sender().number
        for x in range(len(self.track_blocks)):
            if(block_number) == self.track_blocks[x].number:
                print(f"Block {block_number} authority updated to {new_authority}")
                self.track_blocks[x].authority = new_authority

    def get_PLC_program(self, plc_program):
        """
        Recieves PLC program & updates self values - Only allows upload once

        Args:
            plc_program(file): File path of a Python program
        
        """
        #Updates that PLC program has been uploaded & file path
        if(self.plc_program_uploaded == False or self.plc_program == ""):
            self.plc_program_uploaded = True
            self.plc_program = plc_program
            print(self.plc_program)
            #self.send_to_pi()
            

    def run_PLC_program(self):
        """
        Continuously runs the PLC program.
        
        """
        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Opening & running PLC code
            with open (self.plc_program, mode = "r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {
                    "track_blocks": self.track_blocks
                }
            exec(code, {}, local_vars)

            self.track_blocks = local_vars["track_blocks"]


            #what i added to be able to utilize my pi

            self.convert_to_strings()
            self.send_to_pi()

    def check_PLC_program_switch(self, x, old_pos, new_pos):
        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Disabling signals
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            self.track_blocks[x].switch_position = new_pos

            old_Auth = self.track_blocks[x]._authority

            #Opening & running PLC code
            with open (self.plc_program, mode = "r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {
                    "track_blocks": test_track_blocks
                }
            exec(code, {}, local_vars)

            test_track_blocks = local_vars["track_blocks"]

            for block in self.track_blocks:
                block.signal_updates_enabled = True

            self.track_blocks[x]._authority = old_Auth

            #Emergency brake enabled - not safe
            if(test_track_blocks[x].authority == 0):
                self.track_blocks[x].switch_position = old_pos
                print("Unsafe Decision")
            #Emergency brake not enabled - safe
            else:
                print(new_pos)
                self.track_blocks[x].switch_position = new_pos
                print("Safe Decision")
    
    def check_PLC_program_signal(self, x, curr_signal, new_signal):
        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Disabling signals
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            self.track_blocks[x]._light_signal = new_signal

            old_Auth = self.track_blocks[x]._authority

            #Opening & running PLC code
            with open (self.plc_program, mode = "r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {
                    "track_blocks": test_track_blocks,
                }
            exec(code, {}, local_vars)

            test_track_blocks = local_vars["track_blocks"]

            for block in self.track_blocks:
                block.signal_updates_enabled = True

            self.track_blocks[x]._authority = old_Auth

            #Emergency brake enabled - not safe
            if(test_track_blocks[x].authority == 0):
                self.track_blocks[x]._light_signal = curr_signal
                print("Unsafe Decision")
            #Emergency brake not enabled - safe
            else:
                print(new_signal)
                self.track_blocks[x]._light_signal = new_signal
                print("Safe Decision")

    def check_PLC_program_crossing(self, x, curr_crossing, new_crossing):
        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Disabling signals
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x]._crossing_signal_bool = new_crossing

            old_Auth = self.track_blocks[x]._authority

            #Opening & running PLC code
            with open (self.plc_program, mode = "r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {
                    "track_blocks": test_track_blocks,
                }
            exec(code, {}, local_vars)

            test_track_blocks = local_vars["track_blocks"]

            for block in self.track_blocks:
                block.signal_updates_enabled = True
            
            self.track_blocks[x]._authority = old_Auth
            
            #Emergency brake enabled - not safe
            if(test_track_blocks[x].authority == 0):
                self.track_blocks[x]._crossing_signal_bool = curr_crossing
                print("Unsafe Decision")
            #Emergency brake not enabled - safe
            else:
                print(new_crossing)
                self.track_blocks[x]._crossing_signal_bool = new_crossing
                print("Safe Decision")


    def convert_to_strings(self):
    
    #Check block 58 Switch Position
        if(self.track_blocks[57]._switch_position == 0 and self.track_blocks[57].authority < 0):
            self.message_switch58 = f"Switch from 58 to yard is connected, all trains going into yard\nAuthority: {self.track_blocks[57].authority}"  
        
        #checks if the track to yard is not connected
        elif(self.track_blocks[57]._switch_position == 1):
            self.message_switch58 = "Switch from 58 to yard is not connected, all trains are continuing along section J"
        

        #checks if all signals are red
        elif(self.track_blocks[57]._light_signal == False 
             and self.track_blocks[56]._light_signal == False 
             and self.track_blocks[58]._light_signal == False):
            self.message_switch58 = "ALL Trains must stop, all tracks occupied.\nWait till tracks clear"


    #Check block 63 switch position
        if(self.track_blocks[62]._switch_position == 1):
            self.message_switch63 = "Switch from yard to Block 63 is open, Trains can leave the yard"
        else:
            self.message_switch63 = "Switch from yard is open, Trains cannot leave yard, Trains must wait for section J to be unoccupied"

#original send to pi
    def send_to_pi(self):
        # Initialize the SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	#convert to strings
        try:
            # Connect to the Raspberry Pi
            ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)

             
            # Prepare the command to be sent to Raspberry Pi
            command = ""
            
            #reset log
            command = "echo 'Log Reset' > /home/garrett/pi_monitor.log\n "

            #original code for pi
            
            command += "echo 'Running PLC Code' >>/home/garrett/pi_monitor.log\n"
            #testing only
            command += f"echo 'TESTING' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.wayside_name}' >>/home/garrett/pi_monitor.log\n"
		
            #actual outputs on pi  
            command += f"echo '{self.message_switch58}' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.message_switch63}' >>/home/garrett/pi_monitor.log\n"
           # command += f"echo '{self.message_switch76}' >> /home/garrett/pi_monitor.log\n"
            
            
            # Execute the command
            stdin, stdout, stderr = ssh.exec_command(command)

            # Read the response
            response = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            #Print for debugging purposes
            print("Response: ", response)
            print("Error: ", error)

            # Check for errors
            if error:
                response += f"\nError: {error}"

        except Exception as e:
            response = str(e)

        finally:
            # Close the connection
            ssh.close()

        return response


"""
    #Check block 76 switch position
        if(self.track_blocks[75]._switch_position == 1):
            self.message_switch76 = "Switch from 76 to 77 is connected"
        elif(self.track_blocks[75]._switch_position == 0):
            self.message_switch76 = "Switch from 76 to 101 is connected"
        #check if light colors are all red, all trains must stop
        elif(self.track_blocks[75]._light_signal == False
             and self.track_block[76]._light_signal == False
             and self.track_block[100]._light_signal == False):
            self.message_switch76 = "All Trains must stop, all tracks occupied.\nWait till tracks clear"
"""
