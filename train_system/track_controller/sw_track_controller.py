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
            track_blocks(list): List of track blocks
            wayside_name(str): Name of the wayside
            num_blocks(int): Number of blocks in the wayside
        """

        super().__init__()

        self.time_keeper = time_keeper
        time_keeper.tick.connect(self.handle_tick)

        self.track_blocks = track_blocks
        self.plc_program_uploaded = False
        self.plc_program = ""
        self.wayside_name = wayside_name
        self.numBlocks = num_blocks

        #Initialize variables needed for pi
        self.hostname = 'raspberrypi'
        self.username = 'garrett'
        self.password = 'Cornell@26'
        self.port = 22

        for block in self.track_blocks:

            # Connect the block signal with the number to the handler
            block.authority_updated.connect(self.handle_authority_update)


            #block.authority_updated.connect(self.handle_authority_update)
            # block.occupancy_updated.connect(self.handle_occupancy_update)
            # block.suggested_speed_updated.connect(self.handle_speed_update)

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

    def update_block(self, new_block: TrackBlock) -> None:

        """
        Update the block object in the track controller.

        Args:
            block(TrackBlock): The block object
        """

        # Find the block in our list of track blocks
        block = self.get_block(new_block.number)

        # Check if the block's authority has changed
        if block.authority != new_block.authority:
            block.authority = new_block.authority

        # Check if the light signal has changed
        if block.light_signal != new_block.light_signal:
            block.light_signal = new_block.light_signal

        # Check if the crossing signal has changed
        if block.crossing_signal != new_block.crossing_signal:
            block.crossing_signal = new_block.crossing_signal

        # Check if the switch position has changed
        if block.switch.get_child_index != new_block.switch.get_child_index:
            block.switch.toggle()

    def update_blocks(self, new_blocks: List[TrackBlock]) -> None:

        """
        Update the block objects in the track controller.

        Args:
            blocks(list): List of block objects
        """

        for new_block in new_blocks:
            self.update_block(new_block)


    @pyqtSlot(int, bool)
    def handle_occupancy_update(self, block_number: int, new_occupancy: bool) -> None:

        # Run the PLC program to update the track blocks
        # self.run_PLC_program()
        print("occupancy updated")

    @pyqtSlot(int)
    def handle_authority_update(self, block_number: int, new_authority: Authority) -> None:

        # Get the block object
        block = self.get_block(block_number)

        # Set the authority of the block without triggering the signal
        block._authority = new_authority

        # Run the PLC program to update the track blocks
        # self.run_PLC_program()
        print("authority updated")

        # Check if the authority is unchanged, set it and such that the signal is propagated
        if block.authority == new_authority:
            block.authority = new_authority

    @pyqtSlot(int)
    def handle_tick(self, tick: int):

        # Run the plc code every tick if a program is loaded
        if self.plc_program_uploaded == True:
            self.run_PLC_program()
            self.plc_ran.emit(True)


        

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

        # Check if the plc program has been uploaded
        if(self.plc_program_uploaded == False):
            print(f"ERROR: No PLC program uploaded")
            return None
        
        # Opening & running PLC code
        with open (self.plc_program, mode = "r", encoding="utf-8") as plc_code:
            code = plc_code.read()
        local_vars = {"track_blocks": self.track_blocks}
        exec(code, {}, local_vars)

    def check_PLC_program_switch(self, x, old_pos, new_pos):
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
    
    """
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
    """

    """
    def convert_to_strings(self):
        # Check block 58 Switch Position
        self.message_switch9 = (
            "Wayside 4\n"
            "#Switch at Block 9\n"
            "Switch 9: \n"
            f"Switch Position: {track_blocks[8].switch.position}\n"
            f"Light Signal: {track_blocks[8]._light_signal}\n"
            f"Authority: {track_blocks[8].authority}\n\n"
    
            "# Block 10\n"
            "Block 16 Information: \n"
            f"Light Signal: {track_blocks[9]._light_signal}\n"
            f"Authority: {track_blocks[9].authority}\n\n"
    
            "# Block 27\n"
            "Block 77 Information: \n"
            f"Light Signal: {track_blocks[38]._light_signal}\n"
            f"Authority: {track_blocks[38].authority}\n"
        )

        self.message_switch16 = (
            "#Switch at BLOCK 16\n"
            "Switch 16 Information: \n"
            f"Switch Position: {track_blocks[15].switch.position}\n"
            f"Light Signal: {track_blocks[15]._light_signal}\n"
            f"Authority: {track_blocks[15].authority}\n\n"
    
            "# Block 1\n"
            "Block 1 Information: \n"
            f"Light Signal: {track_blocks[0]._light_signal}\n"
            f"Authority: {track_blocks[0].authority}\n\n"
    
            "# Block 15\n"
            "Block 15 Information: \n"
            f"Light Signal: {track_blocks[14]._light_signal}\n"
            f"Authority: {track_blocks[14].authority}\n"
        )

        self.message_switch29 = (
            "#Switch at Block 29\n"
            "Switch 27 Information: \n"
            f"Switch Position: {track_blocks[26].switch.position}\n"
            f"Light Signal: {track_blocks[26]._light_signal}\n"
            f"Authority: {track_blocks[26].authority}\n\n"
    
            "# Block 28\n"
            "Block 28 Information: \n"
            f"Light Signal: {track_blocks[27]._light_signal}\n"
            f"Authority: {track_blocks[27].authority}\n\n"
    
            "# Block 76\n"
            "Block 76 Information: \n"
            f"Light Signal: {track_blocks[37]._light_signal}\n"
            f"Authority: {track_blocks[37].authority}\n"
        )

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
"""
