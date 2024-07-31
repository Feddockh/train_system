import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSlot
from train_system.track_controller.sw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.track_controller.sw_ui import ProgrammerUI

class TrackControllerManager(QObject):


    def __init__(self) -> None:
        """
        Initialize the Track Controller
        """
        super().__init__()
        self.initialize_track_controller()

    def initialize_track_controller():
        # Creating Green Line
        green_line = Line("Green")
        green_line.load_track_blocks()
        green_line.load_switches()

        track_blocks1 = green_line.track_blocks[:32] + green_line.track_blocks[149:150]
        track_blocks2 = green_line.track_blocks[28:85] + green_line.track_blocks[100:153]
        track_blocks3 = green_line.track_blocks[73:101]
        track_blocks3[2]._light_signal = True
        track_blocks3[11]._light_signal = True

        # Creating Red Line
        red_line = Line("Red")
        red_line.load_track_blocks()
        red_line.load_switches()

        track_blocks4 = red_line.track_blocks[0:34] + red_line.track_blocks[71:78]
        track_blocks5 = red_line.track_blocks[23:45] + red_line.track_blocks[67:75]
        track_blocks6 = red_line.track_blocks[39:68]

        # Creating Waysides
        wayside_1 = TrackController(track_blocks1, "Wayside 1", 33)
        wayside_2 = TrackController(track_blocks2, "Wayside 2", 110)
        wayside_3 = TrackController(track_blocks3, "Wayside 3", 28)
        wayside_4 = TrackController(track_blocks4, "Wayside 4", 40)
        wayside_5 = TrackController(track_blocks5, "Wayside 5", 30)
        wayside_6 = TrackController(track_blocks6, "Wayside 6", 29)

        # Add waysides to be sent to UI
        waysides = [wayside_1, wayside_2, wayside_3, wayside_4, wayside_5, wayside_6]

        # Create application
        app = QApplication(sys.argv)
        window = ProgrammerUI(waysides)
        window.show()

        app.exec()

    @pyqtSlot(str, int, str)
    def handle_authority_update(self, line_name: str, block_number: int, authority: str):



# suggest speed will be tied to line handler
# maintenance will be tied line handler