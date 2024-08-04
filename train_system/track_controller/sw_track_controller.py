# train_system/track_controller/track_controller.py

import copy
import sys
import paramiko
import time
from typing import List
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.authority import Authority
from train_system.common.time_keeper import TimeKeeper


class TrackController(QObject):
    plc_ran = pyqtSignal(bool)

    def __init__(self, time_keeper: TimeKeeper, track_blocks: List[TrackBlock], wayside_name: str, num_blocks: int) -> None:

        """
        Initialize variables of the Track Controller.

        Args:
            time_keeper(TimeKeeper): Time keeper used in modules to share tick
            track_blocks(list): List of track blocks
            wayside_name(str): Name of the wayside
            num_blocks(int): Number of blocks in the wayside
        """

        super().__init__()

        #Saving time_keeper to variables
        self.time_keeper = time_keeper
        time_keeper.tick.connect(self.handle_tick)

        #Variables needed for track controller
        self.track_blocks = track_blocks
        self.prev_track_blocks = copy.deepcopy(track_blocks)
        self.plc_program_uploaded = False
        self.plc_program = ""
        self.wayside_name = wayside_name
        self.numBlocks = num_blocks

        #Initialize variables needed for pi
        self.hostname = 'raspberrypi'
        self.username = 'garrett'
        self.password = 'Cornell@26'
        self.port = 22


    def get_block(self, block_number: int) -> TrackBlock:

        """
        Get the block object given the block number.

        Args:
            block_number(int): The block number

        Returns:
            TrackBlock: The block object
        """

        for block in self.track_blocks:
            if block.number == block_number:
                return block
        return None

    def update_block(self, prev_block_instance: TrackBlock, block_instance: TrackBlock) -> bool:

        """
        Uses the setter functions to send signals for the block object when the block parameters are updated.
        Also updated the previous block instance without triggering the signal.

        Args:
            prev_block_instance(TrackBlock): The previous block object
            block_instance(TrackBlock): The new block object

        Returns:
            bool: True if the block parameters are updated, False otherwise
        """

        updated = False

        # Send the authority signal if the authority has changed
        if block_instance.authority != prev_block_instance.authority:
            prev_block_instance._authority = block_instance.authority
            block_instance.authority_updated.emit(block_instance.number, block_instance.authority)
            updated = True

        # Send the light signal if the light signal has changed
        if block_instance.light_signal != prev_block_instance.light_signal:
            prev_block_instance._light_signal = block_instance.light_signal
            block_instance.light_signal_updated.emit(block_instance.number, block_instance.light_signal)
            updated = True

        # Send the crossing signal if the crossing signal has changed
        if block_instance.crossing_signal != prev_block_instance.crossing_signal:
            prev_block_instance._crossing_signal = block_instance.crossing_signal
            block_instance.crossing_signal_updated.emit(block_instance.number, block_instance.crossing_signal)
            updated = True

        # Send the switch signal if the switch signal has changed (only on parent block)
        if block_instance.switch is not None and block_instance.number == block_instance.switch.parent_block:
            if block_instance.switch.position != prev_block_instance.switch.position:
                prev_block_instance.switch._position = block_instance.switch.position
                block_instance.switch.position_updated.emit(block_instance.switch.number, block_instance.switch.position)
                updated = True
                # print(f"Switch {block_instance.switch.number} toggled to: {block_instance.switch.position}")

        return updated

    def update_blocks(self, prev_block_instances: List[TrackBlock], block_instances: List[TrackBlock]) -> bool:

        """
        Uses the setter functions to send signals for the block objects when the block parameters are updated.

        Args:
            prev_block_instances(list): The previous block objects
            block_instances(list): The new block objects

        Returns:
            bool: True if the block parameters are updated, False otherwise
        """

        updated = False
        for prev_block, block in zip(prev_block_instances, block_instances):
            _updated = self.update_block(prev_block, block)
            updated = updated or _updated
        return updated

    @pyqtSlot(int)
    def handle_tick(self, tick: int):    
        """
        Uses the time keeper to run plc program and update track block variables each tick. 

        Args:
            tick(int): Timestep

        """   

        # Run the plc code every tick if a program is loaded
        if self.plc_program_uploaded == True:
            self.run_PLC_program()
            self.plc_ran.emit(True)

        # Update the last known states of the track blocks
        updated = self.update_blocks(self.prev_track_blocks, self.track_blocks)
        

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

    def run_PLC_program(self) -> None:
        """
        Runs the PLC program & alters track block variables if necessary. 
        
        """

        # Check if the plc program has been uploaded
        if(self.plc_program_uploaded == False):
            print(f"ERROR: No PLC program uploaded")
            return None
        
        # Opening & running PLC code
        with open (self.plc_program, mode = "r", encoding="utf-8") as plc_code:
            code = plc_code.read()
        local_vars = {"track_blocks": self.track_blocks}
        exec(code, {}, local_vars)
        #self.send_to_pi()

    def check_PLC_program_switch(self, x, old_pos, new_pos):
        """
        Runs the PLC program  to check if changing switch is safe & alters track block variables if necessary. 
        
        """

        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Disabling signals
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x].switch.position = self.track_blocks[x].switch.child_blocks[new_pos]

            old_authority = [track_block._authority for track_block in self.track_blocks]
            old_bool_unsafe = [track_block._plc_unsafe for track_block in self.track_blocks]

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

            #Emergency brake enabled - not safe
            if(test_track_blocks[x]._plc_unsafe == True):
                self.track_blocks[x].switch.position = self.track_blocks[x].switch.child_blocks[old_pos]
                print("Unsafe Decision")
            #Emergency brake not enabled - safe
            else:
                print(new_pos)
                self.track_blocks[x].switch_position = self.track_blocks[x].switch.child_blocks[new_pos]
                print("Safe Decision")

            for i, track_block in enumerate(self.track_blocks):
                track_block._authority = old_authority[i]
                track_block._plc_unsafe = old_bool_unsafe[i]
    
    def check_PLC_program_signal(self, x, curr_signal, new_signal):
        """
        Runs the PLC program  to check if changing signal is safe & alters track block variables if necessary. 
        
        """

        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Disabling signals
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x]._light_signal = new_signal

            old_authority = [track_block._authority for track_block in self.track_blocks]
            old_bool_unsafe = [track_block._plc_unsafe for track_block in self.track_blocks]

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

            #Emergency brake enabled - not safe
            if(test_track_blocks[x]._plc_unsafe == True):
                self.track_blocks[x]._light_signal = curr_signal
                print("Unsafe Decision")
            #Emergency brake not enabled - safe
            else:
                print(new_signal)
                self.track_blocks[x]._light_signal = new_signal
                print("Safe Decision")

            for i, track_block in enumerate(self.track_blocks):
                track_block._authority = old_authority[i]
                track_block._plc_unsafe = old_bool_unsafe[i]

    def check_PLC_program_crossing(self, x, curr_crossing, new_crossing):
        """
        Runs the PLC program  to check if changing crossing is safe & alters track block variables if necessary. 
        
        """

        #Will only run if PLC program has been uploaded
        if (self.plc_program_uploaded == True):
            #Disabling signals
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x]._crossing_signal = new_crossing

            old_authority = [track_block._authority for track_block in self.track_blocks]
            old_bool_unsafe = [track_block._plc_unsafe for track_block in self.track_blocks]

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
            
            #Emergency brake enabled - not safe
            if(test_track_blocks[x]._plc_unsafe == True):
                self.track_blocks[x]._crossing_signal = curr_crossing
                print("Unsafe Decision")
            #Emergency brake not enabled - safe
            else:
                print(new_crossing)
                self.track_blocks[x]._crossing_signal = new_crossing
                print("Safe Decision")

            for i, track_block in enumerate(self.track_blocks):
                track_block._authority = old_authority[i]
                track_block._plc_unsafe = old_bool_unsafe[i]
    

    def convert_to_strings(self):
    # Message for Switch 13
        self.message_switch13 = (
            "#Switch at Block 13\n"
            "Switch 13 Information:\n"
            f"Switch Position: {self.track_blocks[12].switch.position}\n"
            f"Light Signal: {self.track_blocks[12]._light_signal}\n"
            f"Authority: {self.track_blocks[12].authority}\n\n"
        
            "# Block 1\n"
            "Block 1 Information:\n"
            f"Light Signal: {self.track_blocks[0]._light_signal}\n"
            f"Authority: {self.track_blocks[0].authority}\n\n"

            "# Block 12\n"
            "Block 12 Information:\n"
            f"Light Signal: {self.track_blocks[11]._light_signal}\n"
            f"Authority: {self.track_blocks[11].authority}\n"
        )

        # Message for Switch 29
        self.message_switch29 = (
            "#Switch at Block 29\n"
            "Switch 29 Information:\n"
            f"Switch Position: {self.track_blocks[28].switch.position}\n"
            f"Light Signal: {self.track_blocks[28]._light_signal}\n"
            f"Authority: {self.track_blocks[28].authority}\n\n"
        
            "# Block 30\n"
            "Block 30 Information:\n"
            f"Light Signal: {self.track_blocks[29]._light_signal}\n"
            f"Authority: {self.track_blocks[29].authority}\n\n"

            "# Block 150\n"
            "Block 150 Information:\n"
            f"Light Signal: {self.track_blocks[32]._light_signal}\n"
            f"Authority: {self.track_blocks[32].authority}\n"
        )

    # Print consolidated messages for error checking
 

    def send_to_pi(self):
        if self.wayside_name == "Wayside 1":
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)

                # Once the pi is connected, converts all outputs to strings, then displays them in pi
                self.convert_to_strings()

                command = [
                    "echo 'RUNNING PLC ON PI' > /home/garrett/pi_monitor.log",
                    f"echo '{self.wayside_name}' >> /home/garrett/pi_monitor.log",
                    f"echo '{self.message_switch13}' >> /home/garrett/pi_monitor.log",
                    #f"echo '{self.message_switch16}' >> /home/garrett/pi_monitor.log",
                    f"echo '{self.message_switch29}' >> /home/garrett/pi_monitor.log"
                ]

                for cmd in command:
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    stdout.channel.recv_exit_status()  # Ensure the command completes
                    error = stderr.read().decode('utf-8').strip()
                    if error:
                        print(f"Error: {error}")

            except Exception as e:
                print(f"Exception: {str(e)}")
            
            finally:
                ssh.close()

