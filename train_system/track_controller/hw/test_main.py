import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from train_system.track_controller.hw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.crossing_signal import CrossingSignal 
from train_system.track_controller.hwtrack_ui import ProgrammerUI

def main():
    #Creating instances of Track Controller
    print("Creating Track Controllers")

    #wayside 1
    Wayside_1 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, 1, "")
    test3 = TrackBlock("", "", 2, 1, 1, 1, 1, 1, 1, "")
    test4 = TrackBlock("", "", 3, 1, 1, 1, 1, 1, 1, "")
    test.authority = 3
    test.crossing_signal = CrossingSignal.OFF
    test._light_signal = False
    test.switch_options = [1, 2, 3]
    test.switch_position = 1
    test._occupancy = True
    test3._occupancy = True
    test3.switch_options = [1]
    test4.switch_options = [1]
    arr = [test, test3, test4]
    Wayside_1.track_blocks = arr
    Wayside_1.numBlocks = 3
    Wayside_1.wayside_name = "Wayside 1"


    #wayside 2
    Wayside_2 = TrackController()
    test2 = TrackBlock("", "", 2, 2, 2, 2, 2, 2, 2, "")
    arr2 = [test2]
    Wayside_2.track_blocks = arr2
    Wayside_2.numBlocks = 1
    Wayside_2.wayside_name = "Wayside 2"


    #wayside 3
    Wayside_3 = TrackController()
    test2 = TrackBlock("", "", 1, 1, 1, 1, 1, 1, 1, "")
    arr = [test2]
    Wayside_3.track_blocks = arr
    Wayside_3.numBlocks = 1
    Wayside_3.wayside_name = "Wayside 3"

    #wayside 5
    Wayside_5 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, 1, "")
    arr = [test]
    Wayside_5.track_blocks = arr
    Wayside_5.numBlocks = 1
    Wayside_5.wayside_name = "Wayside 5"

    #wayside 6
    Wayside_6 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, 1, "")
    arr = [test]
    Wayside_6.track_blocks = arr
    Wayside_6.numBlocks = 1
    Wayside_6.wayside_name = "Wayside 6"

    waysides = [Wayside_1, Wayside_2, Wayside_3, Wayside_5, Wayside_6]

    app = QApplication(sys.argv)
    window = ProgrammerUI(waysides)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()