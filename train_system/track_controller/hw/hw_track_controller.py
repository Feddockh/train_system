import copy
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
import sys
import paramiko
import time

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
            if block_number == self.track_blocks[x].number:
                print(f"Block {block_number} occupancy updated to {new_occupancy}")
                self.track_blocks[x]._occupancy = new_occupancy
                if self.plc_program_uploaded:
                    self.run_PLC_program()

    @pyqtSlot(int)
    def handle_speed_update(self, new_speed: int) -> None:
        block_number = self.sender().number
        for x in range(len(self.track_blocks)):
            if block_number == self.track_blocks[x].number:
                print(f"Block {block_number} speed updated to {new_speed}")
                self.track_blocks[x].suggested_speed = new_speed

    @pyqtSlot(int)
    def handle_authority_update(self, new_authority: int) -> None:
        block_number = self.sender().number
        for x in range(len(self.track_blocks)):
            if block_number == self.track_blocks[x].number:
                print(f"Block {block_number} authority updated to {new_authority}")
                self.track_blocks[x].authority = new_authority

    def get_PLC_program(self, plc_program):
        """
        Receives PLC program & updates self values - Only allows upload once

        Args:
            plc_program(file): File path of a Python program
        """
        if not self.plc_program_uploaded or not self.plc_program:
            self.plc_program_uploaded = True
            self.plc_program = plc_program
            print(self.plc_program)

    def run_PLC_program(self):
        """
        Continuously runs the PLC program.
        """
        if self.plc_program_uploaded:
            while True:
                with open(self.plc_program, mode="r", encoding="utf-8") as plc_code:
                    code = plc_code.read()

                local_vars = {"track_blocks": self.track_blocks}
                exec(code, {}, local_vars)

                self.track_blocks = local_vars["track_blocks"]
                
                self.send_to_pi()

                time.sleep(1)

    def check_PLC_program_switch(self, x, old_pos, new_pos):
        if self.plc_program_uploaded:
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x].switch.position = self.track_blocks[x].switch.child_blocks[new_pos]

            old_Auth = self.track_blocks[x]._authority

            with open(self.plc_program, mode="r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {"track_blocks": test_track_blocks}
            exec(code, {}, local_vars)

            test_track_blocks = local_vars["track_blocks"]

            for block in self.track_blocks:
                block.signal_updates_enabled = True

            if test_track_blocks[x].authority == 0:
                self.track_blocks[x].switch.position = self.track_blocks[x].switch.child_blocks[old_pos]
                print("Unsafe Decision")
            else:
                print(new_pos)
                self.track_blocks[x].switch_position = self.track_blocks[x].switch.child_blocks[new_pos]
                print("Safe Decision")

            self.track_blocks[x]._authority = old_Auth

    def check_PLC_program_signal(self, x, curr_signal, new_signal):
        if self.plc_program_uploaded:
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x]._light_signal = new_signal

            old_Auth = self.track_blocks[x]._authority

            with open(self.plc_program, mode="r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {"track_blocks": test_track_blocks}
            exec(code, {}, local_vars)

            test_track_blocks = local_vars["track_blocks"]

            for block in self.track_blocks:
                block.signal_updates_enabled = True

            if test_track_blocks[x].authority == 0:
                self.track_blocks[x]._light_signal = curr_signal
                print("Unsafe Decision")
            else:
                print(new_signal)
                self.track_blocks[x]._light_signal = new_signal
                print("Safe Decision")

            self.track_blocks[x]._authority = old_Auth

    def check_PLC_program_crossing(self, x, curr_crossing, new_crossing):
        if self.plc_program_uploaded:
            for block in self.track_blocks:
                block.signal_updates_enabled = False

            test_track_blocks = self.track_blocks
            test_track_blocks[x]._crossing_signal = new_crossing

            old_Auth = self.track_blocks[x]._authority

            with open(self.plc_program, mode="r", encoding="utf-8") as plc_code:
                code = plc_code.read()
            local_vars = {"track_blocks": test_track_blocks}
            exec(code, {}, local_vars)

            test_track_blocks = local_vars["track_blocks"]

            for block in self.track_blocks:
                block.signal_updates_enabled = True

            if test_track_blocks[x].authority == 0:
                self.track_blocks[x]._crossing_signal = curr_crossing
                print("Unsafe Decision")
            else:
                print(new_crossing)
                self.track_blocks[x]._crossing_signal = new_crossing
                print("Safe Decision")

            self.track_blocks[x]._authority = old_Auth

    def convert_to_strings(self):
    # Message for Switch 13
        self.message_switch13 = (
            "#Switch at Block 13\n"
            "Switch 13 Information:\n"
            f"Switch Position: {track_blocks[12].switch.position}\n"
            f"Light Signal: {track_blocks[12]._light_signal}\n"
            f"Authority: {track_blocks[12].authority}\n\n"
        
            "# Block 1\n"
            "Block 1 Information:\n"
            f"Light Signal: {track_blocks[0]._light_signal}\n"
            f"Authority: {track_blocks[0].authority}\n\n"

            "# Block 12\n"
            "Block 12 Information:\n"
            f"Light Signal: {track_blocks[11]._light_signal}\n"
            f"Authority: {track_blocks[11].authority}\n"
        )

        # Message for Switch 29
        self.message_switch29 = (
            "#Switch at Block 29\n"
            "Switch 29 Information:\n"
            f"Switch Position: {track_blocks[28].switch.position}\n"
            f"Light Signal: {track_blocks[28]._light_signal}\n"
            f"Authority: {track_blocks[28].authority}\n\n"
        
            "# Block 30\n"
            "Block 30 Information:\n"
            f"Light Signal: {track_blocks[29]._light_signal}\n"
            f"Authority: {track_blocks[29].authority}\n\n"

            "# Block 150\n"
            "Block 150 Information:\n"
            f"Light Signal: {track_blocks[32]._light_signal}\n"
            f"Authority: {track_blocks[32].authority}\n"
        )

    # Print consolidated messages for error checking

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
"""
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
                    "echo 'TESTING' >> /home/garrett/pi_monitor.log",
                    f"echo '{self.wayside_name}' >> /home/garrett/pi_monitor.log",
                    f"echo '{self.message_switch9}' >> /home/garrett/pi_monitor.log",
                    f"echo '{self.message_switch16}' >> /home/garrett/pi_monitor.log",
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

                
#Original Pi Code   
"""
    def send_to_pi(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)

            #once pi is connected, converts all outputs to strings, then displays them in pi
            self.convert_to_strings()

            command = "echo 'RUNNING PLC ON PI' > /home/garrett/pi_monitor.log\n"
            command += f"echo 'TESTING' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.wayside_name}' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.message_switch9}' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.message_switch16}' >>/home/garrett/pi_monitor.log\n"
            command += f"echo '{self.message_switch29}' >>/home/garrett/pi_monitor.log\n"

            stdin, stdout, stderr = ssh.exec_command(command)

            response = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if error:
                response += f"\nError: {error}"

        except Exception as e:
            response = str(e)

        finally:
            ssh.close()

        return response
"""