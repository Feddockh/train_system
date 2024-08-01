import os
import sys
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QMainWindow, QWidget, QStackedWidget, QApplication)
from train_system.common.line import Line
from train_system.common.track_failures import TrackFailure
from train_system.track_model.live_map import LiveMap
from train_system.track_model.murphy_view import MurphyUI
from train_system.track_model.builder_view import BuilderUI

class TrackModelUI(QMainWindow):

    update_track_failure = pyqtSignal(str, int, TrackFailure) # line, block, failure -> TrackModel
    update_temp = pyqtSignal(int) # temperature -> TrackModel
    pass_at_station = pyqtSignal(str) # station -> TrackModel

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Track Model UI")
        self.setGeometry(100, 100, 1000, 600)

        self.views = QStackedWidget()
        self.murphy = MurphyUI()
        self.builder = BuilderUI()
        self.views.addWidget(self.murphy)
        self.views.addWidget(self.builder)

        self.views.setCurrentWidget(self.builder)
        self.setCentralWidget(self.views)

        self.builder.to_murphy_view.connect(self.switch_to_murphy_view)
        self.murphy.temp_changed.connect(self.handle_temp_update)
        self.murphy.failure_changed.connect(self.track_failure_updated)
        self.murphy.ask_pass.connect(self.handle_ask_for_pass)

    @pyqtSlot(Line)
    def switch_to_murphy_view(self, line: Line):
        self.views.setCurrentWidget(self.murphy)
        self.murphy.add_line(line)
        self.murphy.select_line(line.name)
        

    @pyqtSlot(str, int, TrackFailure)
    def track_failure_updated(self, line: str, block: int, failure: TrackFailure):
        self.update_track_failure.emit(line, block, failure)

    @pyqtSlot(bool)
    def handle_heater_update(self, status: bool):
        self.murphy.heater_update(status)

    @pyqtSlot(int)
    def handle_temp_update(self, temp: int):
        self.update_temp.emit(temp)
        print(str(temp))

    @pyqtSlot(str)
    def handle_ask_for_pass(self, station: str):
        self.pass_at_station.emit(station)

    @pyqtSlot(int)
    def handle_pass_to_ui(self, num: int):
        self.murphy.update_station_passengers(num)


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    ui = TrackModelUI()
    ui.show()
    sys.exit(app.exec())