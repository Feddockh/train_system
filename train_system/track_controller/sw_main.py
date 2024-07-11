import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from train_system.track_controller.sw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.crossing_signal import CrossingSignal
from train_system.track_controller.sw_ui import ProgrammerUI

def main():
    #Creating instances of Track Controller
    Wayside_1 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, "")
    test.authority = 3
    arr = [test, test]
    Wayside_1.track_blocks = arr
    Wayside_1.numBlocks = 2
    Wayside_1.wayside_name = "Wayside 1"



    Wayside_2 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, "")
    arr = [test]
    Wayside_2.track_blocks = arr
    Wayside_2.numBlocks = 1
    Wayside_2.wayside_name = "Wayside 2"

    Wayside_3 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, "")
    arr = [test]
    Wayside_3.track_blocks = arr
    Wayside_3.numBlocks = 1
    Wayside_3.wayside_name = "Wayside 3"

    Wayside_5 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, "")
    arr = [test]
    Wayside_5.track_blocks = arr
    Wayside_5.numBlocks = 1
    Wayside_5.wayside_name = "Wayside 5"

    Wayside_6 = TrackController()
    test = TrackBlock("", "", 1, 1, 1, 1, 1, 1, "")
    arr = [test]
    Wayside_6.track_blocks = arr
    Wayside_6.numBlocks = 1
    Wayside_6.wayside_name = "Wayside 6"


    '''
    Wayside_1.get_track_occupancy([False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
    Wayside_1.get_speed([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_1.get_authority([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_1.crossing_states = False
    Wayside_1.wayside_name = "Wayside 1"

    Wayside_2 = TrackController()
    Wayside_2.get_track_occupancy([False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
    Wayside_2.get_speed([10, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_2.get_authority([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_2.crossing_states = False
    Wayside_2.wayside_name = "Wayside 2"

    Wayside_3 = TrackController()
    Wayside_3.get_track_occupancy([False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
    Wayside_3.get_speed([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_3.get_authority([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_3.crossing_states = False
    Wayside_3.wayside_name = "Wayside 3"

    Wayside_5 = TrackController()
    Wayside_5.get_track_occupancy([False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
    Wayside_5.get_speed([5, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_5.get_authority([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_5.crossing_states = False
    Wayside_5.wayside_name = "Wayside 5"

    Wayside_6 = TrackController()
    Wayside_6.get_track_occupancy([False, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
    Wayside_6.get_speed([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_6.get_authority([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_6.crossing_states = False
    Wayside_6.wayside_name = "Wayside 6"
    '''

    waysides = [Wayside_1, Wayside_2, Wayside_3, Wayside_5, Wayside_6]

    app = QApplication(sys.argv)
    window = ProgrammerUI(waysides)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()