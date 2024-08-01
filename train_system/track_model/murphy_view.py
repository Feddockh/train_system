import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QButtonGroup, QRadioButton, QPushButton, QGridLayout, QCheckBox, QComboBox, QLineEdit, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.track_failures import TrackFailure
from train_system.track_model.live_map import LiveMap

class MurphyUI(QWidget):

    failure_changed = pyqtSignal(str, int, TrackFailure) # line, block, failure -> TrackModelUI -> TrackModel
    temp_changed = pyqtSignal(int) # temp -> TrackModelUI -> TrackModel
    ask_pass = pyqtSignal(str) # station -> TrackModelUI -> TrackModel
    
    def __init__(self):

        super().__init__()

        self.murphy_layout = QGridLayout()

        self.lines: dict[str, Line] = {}
        self.block_info = BlockInfoWidget()
        self.map = LiveMap()
        self.line_picker = QComboBox()
        self.block_picker = QComboBox()
        self.previous_block_picked = 1
        self.line_block_pickers = QHBoxLayout()
        self.line_block_pickers.addWidget(self.line_picker)
        self.line_block_pickers.addWidget(self.block_picker)

        self.heater_layout = QHBoxLayout()
        self.temp_label = QLabel('Temperature (F):')
        self.temp_edit = QLineEdit('80')
        self.heater_label = QLabel('Heater')
        self.heater_status = QLabel('OFF')
        self.heater_layout.addWidget(self.temp_label)
        self.heater_layout.addWidget(self.temp_edit)
        self.heater_layout.addWidget(self.heater_label)
        self.heater_layout.addWidget(self.heater_status)

        self.block_info_side = QVBoxLayout()
        self.block_info_side.addLayout(self.line_block_pickers)
        self.block_info_side.addWidget(self.block_info)
        self.block_info_side.addLayout(self.heater_layout)

        self.murphy_layout.addLayout(self.block_info_side, 0, 0, 1, 1)
        self.murphy_layout.addWidget(self.map, 0, 1, 1, 2)
        
        self.setLayout(self.murphy_layout)


        # self.temp_change.returnPressed.connect(self.temp_changed.emit)

        self.block_picker.currentTextChanged.connect(self.handle_block_picked)
        self.block_info.failure_updated.connect(self.handle_failure_updated)
        self.temp_edit.returnPressed.connect(self.handle_temp_updated)

    def add_line(self, line: Line):

        self.lines[line.name] = line
        self.line_picker.addItem(line.name)

    def select_line(self, line: str):
        
        self.map.set_line(self.lines[line])
        self.block_picker.clear()
        self.block_picker.addItems(str(block.number) for block in self.lines[line].track_blocks)
        self.handle_block_picked()

    def heater_update(self, status: bool):

        if status:
            self.heater_status.setText('ON')
        else:
            self.heater_status.setText('OFF')

    def update_station_passengers(self, num: int):

        self.block_info.waiting_passengers.setText(str(num))

    @pyqtSlot()
    def handle_block_picked(self):

        self.block_info.block_picked(self.lines[self.line_picker.currentText()].get_track_block(int(self.block_picker.currentText())))

    @pyqtSlot(TrackFailure)
    def handle_failure_updated(self, failure: TrackFailure):

        self.failure_changed.emit(self.line_picker.currentText(), int(self.block_picker.currentText()), failure)

    @pyqtSlot()
    def handle_temp_updated(self):

        self.temp_changed.emit(int(self.temp_edit.text()))

    @pyqtSlot(str)
    def handle_request_pass(self, station: str):

        self.ask_pass.emit(station)

class BlockInfoWidget(QWidget):

    failure_updated = pyqtSignal(TrackFailure) # failure -> MurphyUI -> TrackModelUI -> TrackModel
    request_passengers = pyqtSignal(str) # station -> MurphyUI -> TrackModelUI -> TrackModel

    def __init__(self):

        super().__init__()

        self.info_layout = QVBoxLayout()
        self.setLayout(self.info_layout)

        # Static info to display for any selected block
        self.static_info = QGridLayout()
        self.info_layout.addLayout(self.static_info)

        self.length_label = QLabel('Length (m):')
        self.speed_limit_label = QLabel('Speed Limit (km/h):')
        # self.direction_label = QLabel('Direction:')
        self.grade_label = QLabel('Grade (%):')
        self.elevation_label = QLabel('Elevation (m):')

        self.static_info.addWidget(self.length_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.speed_limit_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        # self.static_info.addWidget(self.direction_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.grade_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.elevation_label, 3, 0, Qt.AlignmentFlag.AlignLeft)

        self.length = QLabel('init')
        self.speed_limit = QLabel('init')
        self.direction = QLabel('init')
        self.grade = QLabel('init')
        self.elevation = QLabel('init')

        self.static_info.addWidget(self.length, 0, 1, Qt.AlignmentFlag.AlignRight)
        self.static_info.addWidget(self.speed_limit, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.static_info.addWidget(self.direction, 2, 1, Qt.AlignmentFlag.AlignRight)
        self.static_info.addWidget(self.grade, 3, 1, Qt.AlignmentFlag.AlignRight)
        self.static_info.addWidget(self.elevation, 4, 1, Qt.AlignmentFlag.AlignRight)

        # Dynamic info (occupancy and failure) to display for any selected block
        self.occupancy_info = QHBoxLayout()
        self.info_layout.addLayout(self.occupancy_info)

        self.occupancy_label = QLabel('Occupancy:')
        self.occupancy_info.addWidget(self.occupancy_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.occupancy = QLabel('init')
        self.occupancy_info.addWidget(self.occupancy, alignment=Qt.AlignmentFlag.AlignRight)

        self.failure_info = FailureWidget()
        self.info_layout.addWidget(self.failure_info)

        # Station info to display if block contains a station
        self.station_info = QGridLayout()
        self.info_layout.addLayout(self.station_info)
        
        self.station_label = QLabel('Station:')
        self.waiting_passengers_label = QLabel('Waiting Passengers:')
        self.beacon_label = QLabel('Beacon:')

        self.station_info.addWidget(self.station_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.station_info.addWidget(self.waiting_passengers_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.station_info.addWidget(self.beacon_label, 2, 0, Qt.AlignmentFlag.AlignLeft)

        self.station = QLabel('init')
        self.waiting_passengers = QLabel('init')
        self.beacon = QLabel('init')

        self.station_info.addWidget(self.station, 0, 1, Qt.AlignmentFlag.AlignRight)
        self.station_info.addWidget(self.waiting_passengers, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.station_info.addWidget(self.beacon, 2, 1, Qt.AlignmentFlag.AlignRight)

        # Switch info to display if block is parent or child of switch
        self.switch_info = QGridLayout()
        self.info_layout.addLayout(self.switch_info)

        self.switch_parent_label = QLabel('Switch Parent:')
        self.switch_children_label = QLabel('Switch Children:')
        self.switch_position_label = QLabel('Switch Position:')
        # self.signal_label = QLabel('Signal:')

        self.switch_info.addWidget(self.switch_parent_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.switch_info.addWidget(self.switch_children_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.switch_info.addWidget(self.switch_position_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        # self.switch_info.addWidget(self.signal_label, 3, 0, Qt.AlignmentFlag.AlignLeft)

        self.switch_parent = QLabel('init')
        self.switch_children = QLabel('init')
        self.switch_position = QLabel('init')
        # self.signal = QLabel('init')

        self.switch_info.addWidget(self.switch_parent, 0, 1, Qt.AlignmentFlag.AlignRight)
        self.switch_info.addWidget(self.switch_children, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.switch_info.addWidget(self.switch_position, 2, 1, Qt.AlignmentFlag.AlignRight)
        # self.switch_info.addWidget(self.signal, 3, 1, Qt.AlignmentFlag.AlignRight)

        self.failure_info.failure_buttons.buttonClicked.connect(self.failure_picked)

    def block_picked(self, block: TrackBlock):

        # self.lines[self.line_picker.currentText()].get_track_block(self.previous_block_picked).disconnect()
        
        self.length.setText(str(block.length))
        self.speed_limit.setText(str(block.speed_limit))
        # self.direction = block.direction
        self.grade.setText(str(block.grade))
        self.elevation.setText(str(block.elevation))

        if block.occupancy:
            self.occupancy.setText('Occupied')
        else:
            self.occupancy.setText('Not Occupied')
        
        if block.track_failure == TrackFailure.NONE:
            self.failure_info.no_failure.setChecked(True)
        elif block.track_failure == TrackFailure.TRACK:
            self.failure_info.track_failure.setChecked(True)
        elif block.track_failure == TrackFailure.CIRCUIT:
            self.failure_info.circuit_failure.setChecked(True)
        elif block.track_failure == TrackFailure.POWER:
            self.failure_info.power_failure.setChecked(True)

        if block.station:
            self.station_label.show()
            self.waiting_passengers_label.show()
            self.beacon_label.show()
            self.station.show()
            self.waiting_passengers.show()
            self.beacon.show()

            self.station.setText(block.station.name)
            self.request_passengers.emit(block.station.name)
            self.beacon.setText('None')
        else:
            self.station_label.hide()
            self.waiting_passengers_label.hide()
            self.beacon_label.hide()
            self.station.hide()
            self.waiting_passengers.hide()
            self.beacon.hide()

        if block.switch:
            self.switch_parent_label.show()
            self.switch_children_label.show()
            self.switch_position_label.show()
            self.switch_parent.show()
            self.switch_children.show()
            self.switch_position.show()

            self.switch_parent.setText(str(block.switch.parent_block))
            self.switch_children.setText(str(block.switch.child_blocks))
            self.switch_position.setText(str(block.switch.position))
        else:
            self.switch_parent_label.hide()
            self.switch_children_label.hide()
            self.switch_position_label.hide()
            self.switch_parent.hide()
            self.switch_children.hide()
            self.switch_position.hide()

        

    @pyqtSlot()
    def failure_picked(self):
        if self.failure_info.track_failure.isChecked():
            self.failure_updated.emit(TrackFailure.TRACK)
        elif self.failure_info.circuit_failure.isChecked():
            self.failure_updated.emit(TrackFailure.CIRCUIT)
        elif self.failure_info.power_failure.isChecked():
            self.failure_updated.emit(TrackFailure.POWER)
        else:
            self.failure_updated.emit(TrackFailure.NONE)

class FailureWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.failure_layout = QVBoxLayout()
        self.setLayout(self.failure_layout)

        self.failure_buttons = QButtonGroup()

        self.failure_label = QLabel('Toggle Failures')

        self.track_failure = QRadioButton('Broken Rail')
        self.circuit_failure = QRadioButton('Circuit Failure')
        self.power_failure = QRadioButton('Power Failure')
        self.no_failure = QRadioButton('No Failure')

        self.failure_buttons.addButton(self.track_failure)
        self.failure_buttons.addButton(self.circuit_failure)
        self.failure_buttons.addButton(self.power_failure)
        self.failure_buttons.addButton(self.no_failure)
        
        self.failure_layout.addWidget(self.failure_label)
        self.failure_layout.addWidget(self.track_failure)
        self.failure_layout.addWidget(self.circuit_failure)
        self.failure_layout.addWidget(self.power_failure)
        self.failure_layout.addWidget(self.no_failure)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    line = Line("Green")
    line.load_defaults()

    widget = MurphyUI()
    widget.add_line(line)
    widget.select_line('Green')
    widget.show()
    sys.exit(app.exec())