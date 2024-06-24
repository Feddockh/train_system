# train_system/ctc_manager/ctc_manager.py

from train_system.common.dispatch_mode import DispatchMode
from train_system.common.line import Line
from train_system.common.train import Train

class CTCOffice:
    def __init__(self):

        """
        Initialize the CTC Office.
        """

        self.trains = [Train(i) for i in range(1, 11)]
        self.dispatch_mode = DispatchMode.MANUAL_FIXED_BLOCK
        self.ticket_sales = 0
        self.passenger_throughput = 0
        self.train_suggested_speeds = {}
        self.train_authorities = {}

        file_path = (
        'C:/Users/hayde/OneDrive/Pitt/2024_Summer_Term/ECE 1140/'
        'Project/train_system/tests/blue_line.xlsx'
        )
        self.line = Line("Blue")
        self.line.load_track_blocks(file_path)
    
    def compute_passenger_throughput(self):
        """
        Compute passenger throughput.
        
        Returns:
            int: Passenger throughput over the past hour.
        """
    
    def compute_suggested_speed(self, line: Line, train: Train, target_block: int):
        """
        Compute the suggested speed for each train based on track occupancy.

        Returns:
            float: Suggested speed for the train.
        """

        # Get the current block
        current_block = train.current_block

        # Get the distance to the target block
        distance = line.get_distance(current_block, target_block)
        print(f"Distance to target block: {distance}")


    
    def compute_authority(self, train_id: int):
        """
        Compute the authority for each train.
        
        Args:
            train_id (int): Identifier for the train.
        
        Returns:
            int: Authority for the train.
        """
    
    def send_maintenance_info(self):
        """
        Send maintenance information to the MBO Controller.
        
        Args:
            mbo_controller (MBOController): The MBO Controller instance to send information to.
        """

