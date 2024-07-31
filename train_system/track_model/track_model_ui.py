import os
import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import (QMainWindow, QWidget, QStackedWidget, QApplication)
from train_system.common.line import Line
from train_system.track_model.live_map import LiveMap
from train_system.track_model.murphy_view import MurphyUI
from train_system.track_model.builder_view import BuilderUI

class TrackModelUI(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Track Model UI")
        self.setGeometry(100, 100, 800, 600)

        self.views = QStackedWidget()
        self.murphy = MurphyUI()
        self.builder = BuilderUI()
        self.views.addWidget(self.murphy)
        self.views.addWidget(self.builder)

        self.views.setCurrentWidget(self.builder)
        self.setCentralWidget(self.views)

        self.builder.to_murphy_view.connect(self.switch_to_murphy_view)
        self.murphy.temp_changed.connect(self.change_temp)

    def switch_to_murphy_view(self, line: Line):
        self.murphy.add_line(line)
        self.views.setCurrentWidget(self.murphy)

    def change_temp(self, temp: int):
        ###


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    ui = TrackModelUI()
    ui.show()
    sys.exit(app.exec())