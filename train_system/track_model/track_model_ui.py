import os
import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import (QMainWindow, QWidget, QStackedWidget, QApplication)
from train_system.common.line import Line
from train_system.track_model.murphy_view import MurphyUI
from train_system.track_model.builder_view import BuilderUI

class TrackModelUI(QMainWindow):

    def __init__(self, line: Line):

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


if __name__ == "__main__":

    #line = Line('Green')
    #file_path = os.path.abspath(os.path.join("system_data/lines", "green_line.xlsx"))
    #line.load_track_blocks(file_path)
    
    app = QApplication(sys.argv)
    ui = TrackModelUI()
    ui.show()
    sys.exit(app.exec())