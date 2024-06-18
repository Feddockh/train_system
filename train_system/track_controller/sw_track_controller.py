# train_system/track_controller/track_controller.py

import pandas as pd
import sys

class TrackController:
    def __init__(self):
        """
        Initialize the Track Controller.
        """
        
        self.track_occupancies = {}
        self.train_speeds = {}
        self.train_authorities = {}
        self.switch_states = {};
        self.signal_states = {};
        self.crossing_states = {};
        self.plc_program_uploaded = False;
        self.switch_positions = {};
    
    
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

    def send_speed(self):
        """
        Sends track speeds to Track Model
        
        Returns:
            array(float): List of floats representing authorities
        """
        return self.train_speeds;


    """     
    def get_track_model(self, trackModel):
        
        Used for test bench - Takes in Excel file and reads data from it
        
        Args:
            trackModel(file): Excel file of track model data
        
        trackModel = "C:\\Users\\Isabella\\Downloads\\Track Layout & Vehicle Data vF2.xlsx";
        require_cols = [2,6];

        datasheet = pd.read_excel(trackModel, sheet_name = 1, usecols = require_cols);


        print(datasheet);
    """


    def get_PLC_program(self, plc_program):
        """
        Recieves PLC program

        Args:
            plc_program(file): Python file containting PLC program code
        
        """

    def run_PLC_program(self):
        """
        Runs the PLC program
        
        """

    def emergency_stop(self):
        """
        Performs an emergency stop of a train if notices two trains are going to crash into eachother
        
        """
     