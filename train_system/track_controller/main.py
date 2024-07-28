import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from train_system.track_controller.sw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.line import Line
from train_system.track_controller.sw_ui import ProgrammerUI

def main():

    """
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
    test.switch_position = 0
    test._occupancy = True
    test2 = TrackBlock("", "", 2, 2, 2, 2, 2, 2, 2, "")
    test3.switch_options = [1]
    test2.switch_options = [1]

    line = Line("")

    line.add_track_block(test)
    #line.add_track_block(test)
    line.add_track_block(test2)
    line.add_track_block(test3)
    line.add_track_block(test4)
    line.add_track_block(test5)
    line.add_track_block(test6)
    line.add_track_block(test7)
    line.add_track_block(test7)

    track_blocks1 = line.track_blocks[0:3]
    track_blocks2 = line.track_blocks[3:4]
    track_blocks3 = line.track_blocks[4:5]
    track_blocks5 = line.track_blocks[5:6]
    track_blocks6 = line.track_blocks[6:8]
    """

    #Creating Green Line
    line = Line("Green")
    line.load_track_blocks()
    line.load_switches()

    track_blocks1 = line.track_blocks[:32] + line.track_blocks[149:150]
                         
    track_blocks2 = line.track_blocks[28:85] + line.track_blocks[100:153]

    track_blocks3 = line.track_blocks[73:101]
    track_blocks3[2]._light_signal = True
    track_blocks3[11]._light_signal = True
    print(track_blocks3[26].number)

    #Creating Red Line
    line2 = Line("Red")
    line2.load_track_blocks()
    line2.load_switches()

    track_blocks4 = line2.track_blocks[0:23] + line2.track_blocks[72:76]

    track_blocks5 = line2.track_blocks[23:45] + line2.track_blocks[67:75]

    track_blocks6 = line2.track_blocks[39:68]


    #Creating Waysides
    Wayside_1 = TrackController(track_blocks1, "Wayside 1", 33)

    Wayside_2 = TrackController(track_blocks2, "Wayside 2", 110)

    Wayside_3 = TrackController(track_blocks3, "Wayside 3", 28)
    
    Wayside_4 = TrackController(track_blocks4, "Wayside 4", 27)

    Wayside_5 = TrackController(track_blocks5, "Wayside 5", 30)
    
    Wayside_6 = TrackController(track_blocks6, "Wayside 6", 29)


    #Add waysides to be sent to UI
    waysides = [Wayside_1, Wayside_2, Wayside_3,Wayside_4, Wayside_5, Wayside_6]

    #Create application
    app = QApplication(sys.argv)
    window = ProgrammerUI(waysides)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()