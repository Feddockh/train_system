# train_system/ctc_manager/ctc_manager.py

from train_system.common.dispatch_mode import DispatchMode

class CTCOffice:
    def __init__(self):
        """
        Initialize the CTC Office.
        """
        self.dispatch_mode = DispatchMode.MANUAL
        self.ticket_sales = 0
        self.passenger_throughput = 0
        self.track_occupancies = {}
        self.train_suggested_speeds = {}
        self.train_authorities = {}
    
    def compute_passenger_throughput(self):
        """
        Compute passenger throughput.
        
        Returns:
            int: Passenger throughput over the past hour.
        """
    
    def compute_suggested_speed(self):
        """
        Compute the suggested speed for each train based on track occupancy.

        Returns:
            float: Suggested speed for the train.
        """
    
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

