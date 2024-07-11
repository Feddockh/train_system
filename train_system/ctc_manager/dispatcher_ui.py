# train_system/ctc_manager/dispatcher_ui.py

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QLabel, QHBoxLayout, QStackedWidget)
from PyQt6.QtCore import pyqtSignal, Qt

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.ctc_manager.widgets.switch_widget import SwitchWidget
from train_system.ctc_manager.widgets.train_visual_widget import TrainVisualWidget
from train_system.ctc_manager.widgets.dispatch_command_widget import DispatchCommandWidget
from train_system.ctc_manager.widgets.train_info_widget import TrainInfoWidget
from train_system.ctc_manager.widgets.schedule_selection_widget import ScheduleSelectionWidget
from train_system.ctc_manager.widgets.maintenance_widget import MaintenanceWidget
from train_system.ctc_manager.widgets.test_bench_widget import TestBenchWidget


class DispatcherUI(QMainWindow):
    def __init__(self, line: Line):

        """
        Initializes the DispatcherUI object, setting up the main window 
        and its layout/widgets.
        """

        super().__init__()

        ### LAYOUT THE UI ###

        # Create the UI
        self.setWindowTitle("Dispatcher UI")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the UI
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Create layouts for the top half and bottom half of the UI
        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)
        self.bottom_layout = QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)

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

        ### ARRANGE THE TRAIN VISUAL WIDGET ###

        # Train visual widget
        self.line = line
        self.train_visual_widget = TrainVisualWidget(self.line)
        self.top_layout.addWidget(self.train_visual_widget)

        # Set the central widget and layout
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def handle_test_bench_toggle(self, state):

        """
        Handle the test bench mode toggle.
        
        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("Test Bench Mode ON")
        else:
            print("Test Bench Mode OFF")

    def handle_maintenance_toggle(self, state):

        """
        Handle the Maintenance mode toggle.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("Maintenance Mode ON")
        else:
            print("Maintenance Mode OFF")

    def handle_mbo_toggle(self, state):

        """
        Handle the MBO mode toggle.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("MBO Mode ON")
        else:
            print("MBO Mode OFF")

    def handle_automatic_toggle(self, state):

        """
        Handle the Automatic mode toggle.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            print("Automatic Mode ON")
        else:
            print("Automatic Mode OFF")

