import os
import re
import sys
from PyQt6.QtWidgets import QWidget, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QApplication
from PyQt6.QtCore import QObject, pyqtSignal, Qt

from train_system.common.line import Line
from train_system.track_model.live_map import LiveMap

class BuilderUI(QWidget):

    to_murphy_view = pyqtSignal(Line)

    def __init__(self):

        super().__init__()


        self.big_layout = QHBoxLayout()
        self.live_map = LiveMap()
        self.upload_button = QPushButton('Upload Track')
        self.murphy_button = QPushButton('Murphy View')

        self.upload_button.setFixedSize(170, 45)
        self.murphy_button.setFixedSize(100, 30)

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.upload_button)
        self.button_layout.addWidget(self.murphy_button)
        self.button_layout.setAlignment(self.upload_button, Qt.AlignmentFlag.AlignCenter)
        self.button_layout.setAlignment(self.murphy_button, Qt.AlignmentFlag.AlignCenter)

        self.big_layout.addLayout(self.button_layout)
        self.big_layout.addWidget(self.live_map)
        self.setLayout(self.big_layout)

        self.line_imported = False

        self.upload_button.clicked.connect(self.open_file)
        self.murphy_button.clicked.connect(self.murphy_clicked)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, caption='Select Track Model', directory='./system_data/lines')

        self.line = Line(str.split(filename[0].split('/')[-1], '_')[0])
        self.line.load_track_blocks(filename[0])
        self.line.load_route()
        self.line.load_switches()
        self.line.load_stations()

        self.live_map.set_line(self.line)
        self.line_imported = True

    def murphy_clicked(self):
        if self.line_imported:
            self.to_murphy_view.emit(self.line)
        

if __name__ == "__main__":

    #line = Line('Green')
    #file_path = os.path.abspath(os.path.join("system_data/lines", "green_line.xlsx"))
    #line.load_track_blocks(file_path)
    
    app = QApplication(sys.argv)
    ui = BuilderUI()
    ui.show()
    sys.exit(app.exec())