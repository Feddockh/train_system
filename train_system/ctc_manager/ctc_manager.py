# train_system/ctc_manager/ctc_manager.py

from PyQt6.QtCore import QObject, pyqtSlot

from train_system.common.dispatch_mode import DispatchMode
from train_system.common.line import Line
from train_system.common.train import Train

class CTCOffice(QObject):
    def __init__(self):

        """
        Initialize the CTC Office.
        """

        super().__init__()

        # Initialize the dispatch mode
        self.dispatch_mode = DispatchMode.MANUAL_FIXED_BLOCK

        # Initialize the line and track blocks
        
        
    @pyqtSlot(bool)
    def handle_test_bench_toggle(self, state):

        """
        Handle the test bench mode toggle.
        
        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("Test Bench Mode ON in CTCManager")
        else:
            print("Test Bench Mode OFF in CTCManager")

    @pyqtSlot(bool)
    def handle_maintenance_toggle(self, state):

        """
        Handle the Maintenance mode toggle.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("Maintenance Mode ON in CTCManager")
        else:
            print("Maintenance Mode OFF in CTCManager")

    @pyqtSlot(bool)
    def handle_mbo_toggle(self, state):

        """
        Handle the MBO mode toggle.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("MBO Mode ON in CTCManager")
        else:
            print("MBO Mode OFF in CTCManager")

    @pyqtSlot(bool)
    def handle_automatic_toggle(self, state):

        """
        Handle the Automatic mode toggle.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("Automatic Mode ON in CTCManager")
        else:
            print("Automatic Mode OFF in CTCManager")
    