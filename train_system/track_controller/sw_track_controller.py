# train_system/track_controller/track_controller.py

import pandas as pd
import sys

class TrackController:
    def __init__(self):
        """
        Initialize variables of the Track Controller.
        """
        
        self.track_occupancies = []
        self.train_speeds = []
        self.train_authorities = []
        self.switch_states = False
        self.signal_states = False
        self.crossing_states = False
        self.plc_program_uploaded = False
        self.switch_positions = []
        self.plc_program = ""
        self.wayside_name = ""
    
    def get_track_occupancy(self, new_track_occupancies):
        """
        Receives track occupancy from Track Model & updates current occupancy list

         Args:
            new_track_occupancies(bool): List of bool values for track occupancies
        
        """
        self.track_occupancies = new_track_occupancies;

    def send_track_occupancy(self):
        """
        Sends track occupancies to CTC Office
        
        Returns:
            array(bool): List of bools representing track occupancies
        """
        return self.track_occupancies;

    def get_authority(self, new_authorities):
        """
        Recieves authority from CTC office & updates current authority list

        Args:
            new_authorities(float): List of float values for track authorities
        
        """
        self.train_authorities = new_authorities;

    def send_authority(self):
         """
        Sends track authorities to Track Model
        
        Returns:
            array(float): List of floats representing authorities
        """
         return self.train_authorities;


    def get_speed(self, new_speeds):
        """
        Recieves speed from CTC office & updates current speed list

        Args:
            new_speeds(float): List of float values for track speeds
        
        """
        self.train_speeds = new_speeds

    def send_speed(self):
        """
        Sends track speeds to Track Model
        
        Returns:
            array(float): List of floats representing authorities
        """
        return self.train_speeds

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

"""
#Testing program
test = TrackController();
test.plc_program_uploaded = True
test.plc_program = "C:/Users/Isabella/Trains/train_system/train_system/track_controller/sw_plc.py"
test.run_PLC_program()
test.get_track_occupancy([True, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
test.run_PLC_program()
test.get_track_occupancy(([False, False, False, False, True, False, False, False, False, False, False, False, False, False, False]))
test.run_PLC_program()
test.get_track_occupancy(([False, False, False, False, False, True, False, False, False, False, False, False, False, False, False]))
test.run_PLC_program()
test.get_track_occupancy(([False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]))
test.run_PLC_program()
"""