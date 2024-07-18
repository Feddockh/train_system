from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (QMainWindow, QWidget, QStackedWidget)
from train_system.track_model.murphy_view import MurphyUI
from train_system.track_model.builder_view import BuilderUI

class TrackModelUI(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Track Model UI")
        self.setGeometry(100, 100, 800, 600)

        self.views = QStackedWidget()
        self.murphy = MurphyUI(self.views)
        self.builder = BuilderUI(self.views)
        self.views.addWidget(self.murphy, self.builder)