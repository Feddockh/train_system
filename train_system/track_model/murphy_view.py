from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QButtonGroup, QRadioButton, QPushButton, QGridLayout, QCheckBox, QComboBox, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

from train_system.common.line import Line
from train_system.track_model.live_map import LiveMap

class MurphyUI(QWidget):

    temp_changed = pyqtSignal(int)
    
    def __init__(self):

        super().__init__()

        self.murphy_layout = QGridLayout()
        self.setLayout(self.murphy_layout)

        self.lines: dict[str, Line]
        self.block_info = BlockInfoWidget()
        self.map = LiveMap()
        self.line_picker = QComboBox()
        self.block_picker = QComboBox()
        self.line_block_pickers = QHBoxLayout()
        self.line_block_pickers.addWidget(self.line_picker)
        self.line_block_pickers.addWidget(self.block_picker)

        self.block_info_side = QVBoxLayout()
        self.block_info_side.addLayout(self.line_block_pickers)
        self.block_info_side.addWidget(self.block_info)

        self.murphy_layout.addLayout(self.block_info_side, 0, 0, 1, 1)
        self.murphy_layout.addWidget(self.map, 0, 1, 1, 2)

        # Temperature toggle and heater status
        self.temp_change = QLineEdit()
        self.heater_status = QLabel()

        self.temp_change.returnPressed.connect(self.temp_changed.emit)

    def add_line(self, line: Line):

        self.lines[line.name] = line
        self.line_picker.addItem(line.name)

    def select_line(self, line: str):
        
        self.map.set_line(self.lines[line])
        self.block_picker.clear()
        for block in self.lines[line].track_blocks:
            self.block_picker.addItem(block.section + block.number)

class BlockInfoWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.info_layout = QVBoxLayout()
        self.setLayout(self.info_layout)

        # Static info to display for any selected block
        self.static_info = QGridLayout()
        self.info_layout.addLayout(self.static_info)

        self.length_label = QLabel('Length (m):')
        self.speed_limit_label = QLabel('Speed Limit (km/h):')
        self.direction_label = QLabel('Direction:')
        self.grade_label = QLabel('Grade (%):')
        self.elevation_label = QLabel('Elevation (m):')

        self.static_info.addWidget(self.length_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.speed_limit_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.direction_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.grade_label, 3, 0, Qt.AlignmentFlag.AlignLeft)
        self.static_info.addWidget(self.elevation_label, 4, 0, Qt.AlignmentFlag.AlignLeft)

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
        self.signal_label = QLabel('Signal:')

        self.switch_info.addWidget(self.switch_parent_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.switch_info.addWidget(self.switch_children_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.switch_info.addWidget(self.switch_position_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.switch_info.addWidget(self.signal_label, 3, 0, Qt.AlignmentFlag.AlignLeft)

        self.switch_parent = QLabel('init')
        self.switch_children = QLabel('init')
        self.switch_position = QLabel('init')
        self.signal = QLabel('init')

        self.switch_info.addWidget(self.switch_parent, 0, 1, Qt.AlignmentFlag.AlignRight)
        self.switch_info.addWidget(self.switch_children, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.switch_info.addWidget(self.switch_position, 2, 1, Qt.AlignmentFlag.AlignRight)
        self.switch_info.addWidget(self.signal, 3, 1, Qt.AlignmentFlag.AlignRight)

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

        self.failure_buttons.addButton(self.track_failure)
        self.failure_buttons.addButton(self.circuit_failure)
        self.failure_buttons.addButton(self.power_failure)

        self.clear_failures = QPushButton('Repair Failure')
        
        self.failure_layout.addWidget(self.failure_label)
        self.failure_layout.addWidget(self.track_failure)
        self.failure_layout.addWidget(self.circuit_failure)
        self.failure_layout.addWidget(self.power_failure)
        self.failure_layout.addWidget(self.clear_failures)