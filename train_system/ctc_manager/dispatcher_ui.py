import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.widgets.switch_widget import SwitchWidget
from train_system.ctc_manager.widgets.train_visual_widget import TrainVisualWidget
from train_system.ctc_manager.widgets.dispatch_command_widget import DispatchCommandWidget


class DispatcherUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the CTC Manager
        ctc_manager = CTCOffice()

        # Create the UI
        self.setWindowTitle("Dispatcher UI")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the UI
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create layouts for the top layout and bottom layout
        top_layout = QHBoxLayout()
        layout.addLayout(top_layout)
        bottom_layout = QHBoxLayout()
        layout.addLayout(bottom_layout)

        # Switch Layout
        switch_layout = QVBoxLayout()
        top_layout.addLayout(switch_layout)

        # Maintenance Mode Toggle Switch
        maintenance_toggle_layout = QVBoxLayout()
        maintenance_toggle_label = QLabel("Maintenance Mode")
        maintenance_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        maintenance_toggle = SwitchWidget()
        maintenance_toggle_layout.addWidget(maintenance_toggle_label)
        maintenance_toggle_layout.addWidget(maintenance_toggle)
        switch_layout.addLayout(maintenance_toggle_layout)

        # MBO Mode Toggle Switch
        mbo_toggle_layout = QVBoxLayout()
        mbo_toggle_label = QLabel("MBO Mode")
        mbo_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mbo_toggle = SwitchWidget()
        mbo_toggle_layout.addWidget(mbo_toggle_label)
        mbo_toggle_layout.addWidget(mbo_toggle)
        switch_layout.addLayout(mbo_toggle_layout)

        # Automatic Mode Toggle Switch
        automatic_toggle_layout = QVBoxLayout()
        automatic_toggle_label = QLabel("Automatic Mode")
        automatic_toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        automatic_toggle = SwitchWidget()
        automatic_toggle_layout.addWidget(automatic_toggle_label)
        automatic_toggle_layout.addWidget(automatic_toggle)
        switch_layout.addLayout(automatic_toggle_layout)

        # Train Visual Widget
        train_visual_widget = TrainVisualWidget(ctc_manager.line)
        top_layout.addWidget(train_visual_widget)

        # Dispatch Command Widget
        dispatch_command_widget = DispatchCommandWidget(ctc_manager.line, ctc_manager.trains)
        bottom_layout.addWidget(dispatch_command_widget)

        # Train Information Widget
        # train_info_widget = TrainInfoWidget(ctc_manager.line)


        # # Create the dispatcher command data table and add to the layout
        # self.dispatch_table_headers = [
        #     "Train ID", 
        #     "Set Block (Station)",
        #     "Dispatch"
        # ]
        # self.dispatch_table_data = [
        #     ["1", "7", ""],
        #     ["2", "18 (Union Station)", ""]
        # ]
        # self.dispatch_table = CustomTable(
        #     "Dispatcher Command",
        #     len(self.dispatch_table_data),
        #     len(self.dispatch_table_headers),
        #     self.dispatch_table_headers,
        #     self.dispatch_table_data
        # )
        # self.bottom_layout.addWidget(self.dispatch_table)

        # # Create the train information data table
        # self.train_table_headers = [
        #     "Train ID", 
        #     "Block (Station)",
        #     "Suggested Speed"
        # ]
        # self.train_table_data = [
        #     ["1", "7", "-- mph"],
        #     ["2", "18 (Union Station)", "-- mph"]
        # ]
        # self.train_table = CustomTable(
        #     "Train Information",
        #     len(self.train_table_data),
        #     len(self.train_table_headers),
        #     self.train_table_headers,
        #     self.train_table_data
        # )
        # self.table_layout.addWidget(self.train_table)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DispatcherUI()
    window.show()
    sys.exit(app.exec())
