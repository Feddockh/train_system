from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from train_system.common.line import Line
from train_system.track_model.live_map import LiveMap

class BuilderUI(QWidget):

    def __init__(self, line: Line):

        super().__init__()

        self.big_layout = QHBoxLayout()
        self.live_map = LiveMap(line)
        self.upload_button = QPushButton('Upload Track')
        self.murphy_button = QPushButton('Murphy View')

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.upload_button)
        self.button_layout.addWidget(self.murphy_button)

        self.big_layout.addLayout(self.button_layout)
        self.big_layout.addWidget(self.live_map)
        self.setLayout(self.big_layout)