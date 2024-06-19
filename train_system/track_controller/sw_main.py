import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from sw_track_controller import TrackController
from sw_ui import ProgrammerUI
from sw_widgets import *

def main():
    #Creating instance of Track Controller
    Wayside_1 = TrackController()
    Wayside_1.get_track_occupancy([True, False, False, False, False, False, False, False, False, False, False, False, False, False, False])
    Wayside_1.get_speed([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])
    Wayside_1.get_authority([20, 25, 25, 25, 20, 25, 30, 25, 25, 25, 25, 30, 30, 25, 20])

    app = QApplication(sys.argv)
    window = ProgrammerUI(Wayside_1)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()