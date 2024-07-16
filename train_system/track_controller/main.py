import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from train_system.track_controller.sw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.common.crossing_signal import CrossingSignal
from train_system.track_controller.sw_ui import ProgrammerUI

def main():

    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, 1, "")
    test3 = TrackBlock("", "", 3, 1, 1, 1, 1, 1, 1, "")
    test4 = TrackBlock("", "", 4, 1, 1, 1, 1, 1, 1, "")
    test5 = TrackBlock("", "", 5, 1, 1, 1, 1, 1, 1, "")
    test6 = TrackBlock("", "", 6, 1, 1, 1, 1, 1, 1, "")
    test7 = TrackBlock("", "", 7, 1, 1, 1, 1, 1, 1, "")
    test.authority = 3
    test.crossing_signal = CrossingSignal.OFF
    test._light_signal = False
    test.switch_options = [2, 3]
    test.switch_position = 1
    test._occupancy = True
    test3.switch_options = [1]
    test4.switch_options = [1]
    test2 = TrackBlock("", "", 2, 2, 2, 2, 2, 2, 2, "")


    #Creating a line
    #line = Line("Green")
    #line.load_track_blocks()
    line = Line("")

    line.add_track_block(test)
    line.add_track_block(test2)
    line.add_track_block(test3)
    line.add_track_block(test4)
    line.add_track_block(test5)
    line.add_track_block(test6)
    line.add_track_block(test7)

    track_blocks1 = line.track_blocks[0:3]
    track_blocks2 = line.track_blocks[3:4]
    track_blocks3 = line.track_blocks[4:5]
    track_blocks5 = line.track_blocks[5:6]
    track_blocks6 = line.track_blocks[6:7]


    """
    #Connect the Line signals to the Track Controller slots
    line.track_block_occupancy_updated.connect(TrackController.handle_occupancy_update)
    line.track_block_suggested_speed_updated.connect(TrackController.handle_speed_update)
    line.track_block_authority_updated.connect(TrackController.handle_authority_update)
    """

    #Creating Waysides
    Wayside_1 = TrackController(track_blocks1)
    Wayside_1.numBlocks = 3
    Wayside_1.wayside_name = "Wayside 1"

    
    Wayside_2 = TrackController(track_blocks2)
    Wayside_2.numBlocks = 1
    Wayside_2.wayside_name = "Wayside 2"

    
    Wayside_3 = TrackController(track_blocks3)
    Wayside_3.numBlocks = 1
    Wayside_3.wayside_name = "Wayside 3"

    
    Wayside_5 = TrackController(track_blocks5)
    Wayside_5.numBlocks = 1
    Wayside_5.wayside_name = "Wayside 5"

    
    Wayside_6 = TrackController(track_blocks6)
    Wayside_6.numBlocks = 1
    Wayside_6.wayside_name = "Wayside 6"

    #Add waysides to be sent to UI
    waysides = [Wayside_1, Wayside_2, Wayside_3, Wayside_5, Wayside_6]

    #Create application
    app = QApplication(sys.argv)
    window = ProgrammerUI(waysides)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()