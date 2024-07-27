# train_system/ctc_manager/dispatcher_ui.py

import sys
from typing import List, Dict, Tuple
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QLabel, QHBoxLayout,
                             QStackedWidget, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.ctc_manager.ctc_train_dispatch import CTCTrainDispatch
from train_system.common.time_keeper import TimeKeeper, TimeKeeperWidget
from train_system.ctc_manager.widgets.switch_widget import SwitchWidget
from train_system.ctc_manager.widgets.track_visual_widget import TrackVisualWidget
from train_system.ctc_manager.widgets.throughput_widget import ThroughputWidget
from train_system.ctc_manager.widgets.dispatch_command_widget import DispatchCommandWidget
from train_system.ctc_manager.widgets.train_info_widget import TrainInfoWidget
from train_system.ctc_manager.widgets.schedule_selection_widget import ScheduleSelectionWidget
from train_system.ctc_manager.widgets.occupancy_widget import OccupancyWidget
from train_system.ctc_manager.widgets.track_switch_widget import TrackSwitchWidget
from train_system.ctc_manager.widgets.maintenance_widget import MaintenanceWidget


class DispatcherUI(QMainWindow):
    def __init__(self, time_keeper: TimeKeeper, lines: List[Line], trains: Dict[Tuple[int, str], CTCTrainDispatch]):
        super().__init__()

        """
        Initializes the DispatcherUI object, setting up the main window 
        and its layout/widgets.

        Args:
            time_keeper (TimeKeeper): The time keeper object.
            lines (List[Line]): A dictionary of the Line objects.
            trains (Dict[Tuple[int, str], CTCTrainDispatch]): A dictionary mapping the train IDs 
                and line names to CTCTrainDispatch objects.
        """

        # Check that there are exactly two lines
        if len(lines) != 2:
            raise ValueError("DispatcherUI requires exactly two lines.")

        # Store the time keeper, lines, and trains
        self.time_keeper = time_keeper
        self.lines = lines
        self.line = lines[0]
        self.trains = trains

        ### LAYOUT THE UI ###

        # Create the UI
        self.setWindowTitle("Dispatcher UI")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

        # Add the time keeper widget to the top of the central layout
        self.time_keeper_widget = TimeKeeperWidget(self.time_keeper)
        self.central_layout.addWidget(self.time_keeper_widget)

        # Create a horizontal layout for the top half
        self.top_layout = QHBoxLayout()
        self.central_layout.addLayout(self.top_layout)

        # Create a stacked widget with a horizontal layout for the bottom half (for the maintenance widget)
        self.bottom_stacked_widget = QStackedWidget()
        self.central_layout.addWidget(self.bottom_stacked_widget)
        self.bottom_widget = QWidget()
        self.bottom_stacked_widget.addWidget(self.bottom_widget)
        self.bottom_layout = QHBoxLayout()
        self.bottom_widget.setLayout(self.bottom_layout)

        ### ARRANGE AND CONNECT THE SWITCHES ###

        # Switch layout for holding toggle switches
        switch_layout = QVBoxLayout()
        self.top_layout.addLayout(switch_layout)

        # Toggle switch layouts
        self.test_bench_toggle_layout = QVBoxLayout()
        switch_layout.addLayout(self.test_bench_toggle_layout)
        self.maintenance_toggle_layout = QVBoxLayout()
        switch_layout.addLayout(self.maintenance_toggle_layout)
        self.mbo_toggle_layout = QVBoxLayout()
        switch_layout.addLayout(self.mbo_toggle_layout)
        self.automatic_toggle_layout = QVBoxLayout()
        switch_layout.addLayout(self.automatic_toggle_layout)
        self.line_toggle_layout = QVBoxLayout()
        switch_layout.addLayout(self.line_toggle_layout)

        # Test bench toggle label
        self.test_bench_toggle_label = QLabel("Test Bench Mode")
        self.test_bench_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.test_bench_toggle_layout.addWidget(self.test_bench_toggle_label)

        # Test bench toggle switch
        self.test_bench_toggle_switch = SwitchWidget()
        centered_test_bench_toggle = QHBoxLayout()
        centered_test_bench_toggle.addWidget(self.test_bench_toggle_switch)
        self.test_bench_toggle_layout.addLayout(centered_test_bench_toggle)
        self.test_bench_toggle_switch.toggled.connect(self.handle_test_bench_toggle)

        # Maintenance mode toggle label
        self.maintenance_toggle_label = QLabel("Maintenance Mode")
        self.maintenance_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.maintenance_toggle_layout.addWidget(self.maintenance_toggle_label)

        # Maintenance mode toggle switch
        self.maintenance_toggle_switch = SwitchWidget()
        centered_maintenance_toggle = QHBoxLayout()
        centered_maintenance_toggle.addWidget(self.maintenance_toggle_switch)
        self.maintenance_toggle_layout.addLayout(centered_maintenance_toggle)
        self.maintenance_toggle_switch.toggled.connect(self.handle_maintenance_toggle)

        # MBO mode toggle label
        self.mbo_toggle_label = QLabel("MBO Mode")
        self.mbo_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mbo_toggle_layout.addWidget(self.mbo_toggle_label)

        # MBO mode toggle switch
        self.mbo_toggle_switch = SwitchWidget()
        centered_mbo_toggle = QHBoxLayout()
        centered_mbo_toggle.addWidget(self.mbo_toggle_switch)
        self.mbo_toggle_layout.addLayout(centered_mbo_toggle)
        self.mbo_toggle_switch.toggled.connect(self.handle_mbo_toggle)

        # Automatic mode toggle label
        self.automatic_toggle_label = QLabel("Automatic Mode")
        self.automatic_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.automatic_toggle_layout.addWidget(self.automatic_toggle_label)

        # Automatic mode toggle switch
        self.automatic_toggle_switch = SwitchWidget()
        centered_automatic_toggle = QHBoxLayout()
        centered_automatic_toggle.addWidget(self.automatic_toggle_switch)
        self.automatic_toggle_layout.addLayout(centered_automatic_toggle)
        self.automatic_toggle_switch.toggled.connect(self.handle_automatic_toggle)

        # Line toggle label
        self.line_toggle_label = QLabel(f"{lines[0].name.capitalize()}      {lines[1].name.capitalize()}") 
        self.line_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_toggle_layout.addWidget(self.line_toggle_label)

        # Line toggle switch
        self.line_toggle_switch = SwitchWidget(bg_color=lines[0].name.lower(), active_color=lines[1].name.lower())
        centered_line_toggle = QHBoxLayout()
        centered_line_toggle.addWidget(self.line_toggle_switch)
        self.line_toggle_layout.addLayout(centered_line_toggle)
        self.line_toggle_switch.toggled.connect(self.handle_line_toggle)

        ### TRAIN VISUAL WIDGET ###

        # Create a layout that combines the train visual widget and thorughput widget
        self.visual_layout = QVBoxLayout()
        self.top_layout.addLayout(self.visual_layout)

        # Track visual widget
        self.track_visual_widget = TrackVisualWidget(self.line)
        self.visual_layout.addWidget(self.track_visual_widget, stretch=4)

        # Throughput widget
        self.throughput_widget = ThroughputWidget(self.line)
        self.visual_layout.addWidget(self.throughput_widget, stretch=0)

        ### DISPATCH COMMAND/SCHEDULE SELECTION STACKED WIDGET ###

        self.stacked_widget = QStackedWidget()
        self.bottom_layout.addWidget(self.stacked_widget, stretch=2)

        # Dispatch Command Widget
        self.dispatch_command_widget = DispatchCommandWidget(self.line)
        self.stacked_widget.addWidget(self.dispatch_command_widget)

        # Schedule Selection Widget
        self.schedule_selection_widget = ScheduleSelectionWidget(self.line)
        self.stacked_widget.addWidget(self.schedule_selection_widget)

        ### TRAIN INFORMATION WIDGET ###

        # Train Information Widget
        self.trains = trains
        self.train_info_widget = TrainInfoWidget(self.time_keeper, self.trains)
        self.bottom_layout.addWidget(self.train_info_widget, stretch=3)
        self.time_keeper.tick.connect(self.train_info_widget.handle_time_update)

        ### TEST BENCH WIDGET ###

        # Create and add the OccupancyWidget to the bottom stacked widget
        # self.set_occupancy_widget = OccupancyWidget(self.line)
        # self.bottom_stacked_widget.addWidget(self.set_occupancy_widget)

        # Create a track switch widget
        self.track_switch_widget = TrackSwitchWidget(self.line)
        self.bottom_layout.addWidget(self.track_switch_widget, stretch=1)
        self.track_switch_widget.hide()

        ### MAINTENANCE WIDGET ###

        # Create and add the MaintenanceWidget to the bottom stacked widget
        self.maintenance_widget = MaintenanceWidget(self.line)
        self.bottom_stacked_widget.addWidget(self.maintenance_widget)

    @pyqtSlot(bool)
    def handle_test_bench_toggle(self, state: bool) -> None:
        if state:
            # self.bottom_stacked_widget.setCurrentWidget(self.set_occupancy_widget)
            # self.dispatch_command_widget.setEnabled(False)
            self.track_switch_widget.show()
            self.schedule_selection_widget.setEnabled(False)
        else:
            # self.bottom_stacked_widget.setCurrentWidget(self.bottom_widget)
            self.track_switch_widget.hide()
            if not self.maintenance_toggle_switch.isChecked():
                self.dispatch_command_widget.setEnabled(True)
                self.schedule_selection_widget.setEnabled(True)

    @pyqtSlot(bool)
    def handle_maintenance_toggle(self, state: bool) -> None:
        if state:
            self.bottom_stacked_widget.setCurrentWidget(self.maintenance_widget)
            self.dispatch_command_widget.setEnabled(False)
            self.schedule_selection_widget.setEnabled(False)
        else:
            self.bottom_stacked_widget.setCurrentWidget(self.bottom_widget)
            if not self.test_bench_toggle_switch.isChecked():
                self.dispatch_command_widget.setEnabled(True)
                self.schedule_selection_widget.setEnabled(True)

    @pyqtSlot(bool)
    def handle_mbo_toggle(self, state: bool) -> None:
        self.dispatch_command_widget.setEnabled(not state)
        self.schedule_selection_widget.setEnabled(not state)

    @pyqtSlot(bool)
    def handle_automatic_toggle(self, state: bool) -> None:
        if state:
            self.stacked_widget.setCurrentWidget(
                self.schedule_selection_widget)
        else:
            self.stacked_widget.setCurrentWidget(
                self.dispatch_command_widget)

    @pyqtSlot(bool)
    def handle_line_toggle(self, state: bool) -> None:
        if state:
            self.line = self.lines[1]
        else:
            self.line = self.lines[0]
        self.track_visual_widget.set_line(self.line)
        self.throughput_widget.set_line(self.line)
        self.dispatch_command_widget.set_line(self.line)
        self.schedule_selection_widget.set_line(self.line)
        self.track_switch_widget.set_line(self.line)
        self.maintenance_widget.set_line(self.line)

    @pyqtSlot(str, int, bool)
    def handle_occupancy_update(self, line_name: str, block_number: int, occupancy: bool) -> None:
        self.track_visual_widget.update()

<<<<<<< HEAD
    # @pyqtSlot(int)
    # def handle_switch_position_update(self, switch_number: int) -> None:
    #     print(f"Switch {switch_number} position updated")
=======
    @pyqtSlot(int)
    def handle_switch_position_update(self, switch_number: int) -> None:
        print(f"Switch {switch_number} position updated")
>>>>>>> 5642103 (New and improved implementation of switches)

    # @pyqtSlot(int, int)
    # def handle_crossing_signal_update(self, block_number: int, signal: int) -> None:
    #     print(f"Block {block_number} crossing signal updated: {signal}")

    @pyqtSlot(str, int, bool)
    def handle_maintenance_update(self, line_name: str, block_number: int, maintenance: bool) -> None:
        self.track_visual_widget.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    time_keeper = TimeKeeper()
    time_keeper.start_timer()

    lines = []

    green_line = Line("Green")
    green_line.load_defaults()
    lines.append(green_line)

    red_line = Line("Red")
    red_line.load_defaults()
    lines.append(red_line)

    trains = {}

    widget = DispatcherUI(time_keeper, lines, trains)
    widget.show()
    sys.exit(app.exec())