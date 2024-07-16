# train_system/track_controller/track_controller.py

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
import sys

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
                    "switch": self.switch_states,
                    "light": self.signal_states,
                    "cross": self.crossing_states,
                    "track_occupancies": self.track_occupancies
                }
            exec(code, {}, local_vars)

            self.switch_states = local_vars["switch"]
            self.signal_states = local_vars["light"]
            self.crossing_states = local_vars["cross"]
            self.track_occupancies = local_vars["track_occupancies"]

    def emergency_stop(self):
        """
        Performs an emergency stop of a train if notices two trains are going to crash into eachother
        
        """
