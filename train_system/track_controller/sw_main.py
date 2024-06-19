import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from sw_track_controller import TrackController
from sw_ui import ProgrammerUI

def main():
    #Creating instance of Track Controller
    tc = TrackController()

    app = QApplication(sys.argv)
    window = ProgrammerUI(tc)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()