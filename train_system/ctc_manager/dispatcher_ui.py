import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QLabel, QHBoxLayout, QStackedWidget)
from PyQt6.QtCore import Qt

from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.widgets.switch_widget import SwitchWidget
from train_system.ctc_manager.widgets.train_visual_widget import TrainVisualWidget
from train_system.ctc_manager.widgets.dispatch_command_widget import DispatchCommandWidget
from train_system.ctc_manager.widgets.train_info_widget import TrainInfoWidget
from train_system.ctc_manager.widgets.schedule_selection_widget import ScheduleSelectionWidget
from train_system.ctc_manager.widgets.maintenance_widget import MaintenanceWidget
from train_system.ctc_manager.widgets.test_bench_widget import TestBenchWidget

class DispatcherUI(QMainWindow):
    def __init__(self):

        """
        Initializes the DispatcherUI object, setting up the main window 
        and its components.
        """

        super().__init__()

        # Create the CTC Manager
        self.ctc_manager = CTCOffice()

        # Create the UI
        self.setWindowTitle("Dispatcher UI")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the UI
        central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Create layouts for the top layout and bottom layout
        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)
        self.bottom_layout = QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)

        # Switch Layout
        switch_layout = QVBoxLayout()
        self.top_layout.addLayout(switch_layout)

        # Test Bench Mode Toggle Switch
        test_bench_toggle_layout = QVBoxLayout()
        self.test_bench_toggle_label = QLabel("Test Bench Mode")
        self.test_bench_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.test_bench_toggle = SwitchWidget()
        test_bench_toggle_hlayout = QHBoxLayout()
        test_bench_toggle_hlayout.addWidget(self.test_bench_toggle)
        test_bench_toggle_layout.addWidget(self.test_bench_toggle_label)
        test_bench_toggle_layout.addLayout(test_bench_toggle_hlayout)
        switch_layout.addLayout(test_bench_toggle_layout)

        # Maintenance Mode Toggle Switch
        maintenance_toggle_layout = QVBoxLayout()
        self.maintenance_toggle_label = QLabel("Maintenance Mode")
        self.maintenance_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.maintenance_toggle = SwitchWidget()
        maintenance_toggle_hlayout = QHBoxLayout()
        maintenance_toggle_hlayout.addWidget(self.maintenance_toggle)
        maintenance_toggle_layout.addWidget(self.maintenance_toggle_label)
        maintenance_toggle_layout.addLayout(maintenance_toggle_hlayout)
        switch_layout.addLayout(maintenance_toggle_layout)

        # MBO Mode Toggle Switch
        mbo_toggle_layout = QVBoxLayout()
        self.mbo_toggle_label = QLabel("MBO Mode")
        self.mbo_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mbo_toggle = SwitchWidget()
        mbo_toggle_hlayout = QHBoxLayout()
        mbo_toggle_hlayout.addWidget(self.mbo_toggle)
        mbo_toggle_layout.addWidget(self.mbo_toggle_label)
        mbo_toggle_layout.addLayout(mbo_toggle_hlayout)
        switch_layout.addLayout(mbo_toggle_layout)

        # Automatic Mode Toggle Switch
        automatic_toggle_layout = QVBoxLayout()
        self.automatic_toggle_label = QLabel("Automatic Mode")
        self.automatic_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.automatic_toggle = SwitchWidget()
        automatic_toggle_hlayout = QHBoxLayout()
        automatic_toggle_hlayout.addWidget(self.automatic_toggle)
        automatic_toggle_layout.addWidget(self.automatic_toggle_label)
        automatic_toggle_layout.addLayout(automatic_toggle_hlayout)
        switch_layout.addLayout(automatic_toggle_layout)

        # Connect toggle signals to methods
        self.test_bench_toggle.toggled.connect(self.toggle_test_bench_mode)
        self.maintenance_toggle.toggled.connect(self.toggle_maintenance_mode)
        self.mbo_toggle.toggled.connect(self.toggle_mbo_mode)
        self.automatic_toggle.toggled.connect(self.toggle_automatic_mode)

        # Train Visual Widget
        self.train_visual_widget = TrainVisualWidget(self.ctc_manager.line)
        self.top_layout.addWidget(self.train_visual_widget)

        # Create Stacked Widget for bottom layout to switch between widgets
        self.bottom_stacked_widget = QStackedWidget()
        self.bottom_layout.addWidget(self.bottom_stacked_widget)

        # Dispatch Command Widget
        self.dispatch_command_widget = DispatchCommandWidget(
            self.ctc_manager.line, self.ctc_manager.trains)
        self.bottom_stacked_widget.addWidget(self.dispatch_command_widget)

        # Schedule Widget
        self.schedule_selection_widget = ScheduleSelectionWidget()
        self.bottom_stacked_widget.addWidget(self.schedule_selection_widget)

        # Train Information Widget
        self.train_info_widget = TrainInfoWidget(
            self.ctc_manager.line, self.ctc_manager.trains)
        self.bottom_layout.addWidget(self.train_info_widget)

        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def toggle_test_bench_mode(self, state):

        """
        Toggles the Test Bench mode.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.show_test_bench_screen()
        else:
            self.show_main_screen()

    def toggle_maintenance_mode(self, state):

        """
        Toggles the Maintenance mode.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.show_maintenance_screen()
        else:
            self.show_main_screen()

    def toggle_mbo_mode(self, state):

        """
        Toggles the MBO mode.

        Args:
            state (bool): The state of the toggle switch.
        """

        self.set_widgets_enabled(not state)

    def toggle_automatic_mode(self, state):

        """
        Toggles the Automatic mode.

        Args:
            state (bool): The state of the toggle switch.
        """

        if state:
            self.bottom_stacked_widget.setCurrentWidget(
                self.schedule_selection_widget)
        else:
            self.bottom_stacked_widget.setCurrentWidget(
                self.dispatch_command_widget)

    def show_test_bench_screen(self):

        """
        Shows the Test Bench screen and hides other widgets.
        """

        self.train_visual_widget.hide()
        self.train_info_widget.hide()
        self.bottom_stacked_widget.hide()
        self.maintenance_toggle.hide()
        self.mbo_toggle.hide()
        self.automatic_toggle.hide()
        self.maintenance_toggle_label.hide()
        self.mbo_toggle_label.hide()
        self.automatic_toggle_label.hide()
        self.test_bench_screen = TestBenchWidget(self.ctc_manager.line)
        self.top_layout.addWidget(self.test_bench_screen)

    def show_maintenance_screen(self):

        """
        Shows the Maintenance screen and hides other widgets.
        """

        self.train_visual_widget.hide()
        self.train_info_widget.hide()
        self.bottom_stacked_widget.hide()
        self.test_bench_toggle.hide()
        self.mbo_toggle.hide()
        self.automatic_toggle.hide()
        self.test_bench_toggle_label.hide()
        self.mbo_toggle_label.hide()
        self.automatic_toggle_label.hide()
        self.maintenance_screen = MaintenanceWidget(self.ctc_manager.line)
        self.top_layout.addWidget(self.maintenance_screen)

    def show_main_screen(self):

        """
        Shows the main screen and displays all widgets.
        """

        self.train_visual_widget.show()
        self.train_info_widget.show()
        self.bottom_stacked_widget.show()
        self.test_bench_toggle.show()
        self.maintenance_toggle.show()
        self.mbo_toggle.show()
        self.automatic_toggle.show()
        self.test_bench_toggle_label.show()
        self.maintenance_toggle_label.show()
        self.mbo_toggle_label.show()
        self.automatic_toggle_label.show()
        if hasattr(self, 'maintenance_screen'):
            self.top_layout.removeWidget(self.maintenance_screen)
            self.maintenance_screen.deleteLater()
            del self.maintenance_screen
        if hasattr(self, 'test_bench_screen'):
            self.top_layout.removeWidget(self.test_bench_screen)
            self.test_bench_screen.deleteLater()
            del self.test_bench_screen

    def set_widgets_enabled(self, enabled):

        """
        Enables or disables the dispatch command and schedule selection widgets.

        Args:
            enabled (bool): Whether to enable or disable the widgets.
        """

        self.dispatch_command_widget.setEnabled(enabled)
        self.schedule_selection_widget.setEnabled(enabled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DispatcherUI()
    window.show()
    sys.exit(app.exec())