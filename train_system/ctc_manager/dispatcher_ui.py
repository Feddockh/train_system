from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem)
import sys, os

from train_system.common.gui_features import CustomTable


class DispatcherUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dispatcher UI")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the UI
        self.layout = QVBoxLayout()

        # Create layouts for the top (track layout) and bottom (table layout)
        self.track_layout = QHBoxLayout()
        self.table_layout = QHBoxLayout()

        # Nest the track and table layouts inside the main layout
        self.layout.addLayout(self.track_layout)
        self.layout.addLayout(self.table_layout)

        # Create the dispatcher command data table and add to the layout
        self.dispatch_table_headers = [
            "Train ID", 
            "Set Block (Station)",
            "Dispatch"
        ]
        self.dispatch_table_data = [
            ["1", "7", ""],
            ["2", "18 (Union Station)", ""]
        ]
        self.dispatch_table = CustomTable(
            "Dispatcher Command",
            len(self.dispatch_table_data),
            len(self.dispatch_table_headers),
            self.dispatch_table_headers,
            self.dispatch_table_data
        )
        self.table_layout.addWidget(self.dispatch_table)

        # Create the train information data table
        self.train_table_headers = [
            "Train ID", 
            "Block (Station)",
            "Suggested Speed"
        ]
        self.train_table_data = [
            ["1", "7", "-- mph"],
            ["2", "18 (Union Station)", "-- mph"]
        ]
        self.train_table = CustomTable(
            "Train Information",
            len(self.train_table_data),
            len(self.train_table_headers),
            self.train_table_headers,
            self.train_table_data
        )
        self.table_layout.addWidget(self.train_table)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DispatcherUI()
    window.show()
    sys.exit(app.exec())
