import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSlot
from train_system.track_controller.sw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.track_controller.sw_ui import ProgrammerUI
from train_system.common.time_keeper import TimeKeeper

class TrackControllerManager(QObject):
    def __init__(self, time_keeper: TimeKeeper) -> None:
        super().__init__()

        """
        Initialize the Track Controller
        """
        
        # Creating Green Line
        self.green_line = Line("Green")
        self.green_line.load_track_blocks()
        self.green_line.load_switches()

        # Create the track blocks for the green line
        track_blocks1 = self.green_line.track_blocks[:32] + self.green_line.track_blocks[149:150]
        track_blocks2 = self.green_line.track_blocks[28:85] + self.green_line.track_blocks[100:153]
        track_blocks3 = self.green_line.track_blocks[73:101]

        # Creating Red Line
        self.red_line = Line("Red")
        self.red_line.load_track_blocks()
        self.red_line.load_switches()

        # Create the track blocks for the red line 
        track_blocks4 = self.red_line.track_blocks[0:34] + self.red_line.track_blocks[71:78]
        track_blocks5 = self.red_line.track_blocks[23:45] + self.red_line.track_blocks[67:75]
        track_blocks6 = self.red_line.track_blocks[39:68]

        # Create the Wayside objects
        Wayside_1 = TrackController(time_keeper, track_blocks1, "Wayside 1", 33)
        Wayside_2 = TrackController(time_keeper, track_blocks2, "Wayside 2", 110)
        Wayside_3 = TrackController(time_keeper, track_blocks3, "Wayside 3", 28)
        Wayside_4 = TrackController(time_keeper, track_blocks4, "Wayside 4", 40)
        Wayside_5 = TrackController(time_keeper, track_blocks5, "Wayside 5", 30)
        Wayside_6 = TrackController(time_keeper, track_blocks6, "Wayside 6", 29)

        # Add waysides to be sent to UI
        self.waysides = [Wayside_1, Wayside_2, Wayside_3, Wayside_4, Wayside_5, Wayside_6]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    time_keeper = TimeKeeper()
    time_keeper.start_timer()
    track_controller_manager = TrackControllerManager(time_keeper)
    window = ProgrammerUI(track_controller_manager.waysides)
    window.show()
    app.exec()