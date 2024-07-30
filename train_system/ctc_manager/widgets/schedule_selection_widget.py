import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QPushButton,
                             QFileDialog, QApplication, QMainWindow)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List
import pandas as pd
import os

from train_system.common.schedule import Schedule
from train_system.common.line import Line
from train_system.common.conversions import time_to_seconds

class ScheduleSelectionWidget(QWidget):
    dispatched_train = pyqtSignal(int, int, int)

    def __init__(self, line: Line, parent: Optional[QWidget] = None) -> None:

        """
        Initializes the ScheduleSelectionWidget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Schedule Selection"
        self.line = line
        self.schedules: List[Schedule] = []
        self.current_schedule_index = -1
        self.rows = 0
        self.cols = 3
        self.headers = ["Train ID", "Block", "Arrival Time"]
        self.init_ui()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the ScheduleSelectionWidget.
        """

        layout = QVBoxLayout()

        # Create table title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "background-color: #333333;"
            "color: #fdfdfd;"
            "font-size: 16pt;"
            "font-weight: 600;"
        )
        layout.addWidget(title_label)

        # Create table widget
        self.table = QTableWidget(self.rows, self.cols)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)

        # Set the style for the table headers and cells
        self.table.setStyleSheet("""
            QHeaderView::section { 
                background-color: #C8C8C8;
                color: #333333;
                font-size: 14pt;
            }
            QTableWidget::item {
                background-color: #FDFDFD;
                border: 1px solid #333333; 
            }
            QTableWidget {
                gridline-color: #333333; 
            }
        """)

        # Set the palette for the table to control the background and text colors
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0xd9d9d9))
        palette.setColor(QPalette.ColorRole.Text, QColor(0x333333))
        self.table.setPalette(palette)

        # Adjust column widths to fit contents
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(self.cols):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch
            )

        layout.addWidget(self.table)

        # Create a layout for the buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Load schedules button
        self.load_button = QPushButton("Load Schedules")
        self.load_button.clicked.connect(self.load_schedules)
        button_layout.addWidget(self.load_button)

        # Next schedule button
        self.next_schedule_button = QPushButton("Next Schedule")
        self.next_schedule_button.clicked.connect(self.next_schedule)
        button_layout.addWidget(self.next_schedule_button)

        # Add dispatch button
        self.dispatch_button = QPushButton("Dispatch")
        self.dispatch_button.clicked.connect(self.dispatch_trains)
        button_layout.addWidget(self.dispatch_button)

        self.setLayout(layout)

    def load_schedules(self) -> None:

        """
        Loads schedules from Excel files in a selected folder.
        """

        folder = QFileDialog.getExistingDirectory(self, "Select Schedule Folder")
        if folder:
            schedules = []
            for filename in os.listdir(folder):
                if filename.endswith('.xlsx'):
                    schedule = Schedule()
                    schedule.load_schedule(os.path.join(folder, filename))
                    schedules.append(schedule)
            self.schedules = schedules
            self.next_schedule()

    def next_schedule(self) -> None:

        """
        Displays the next schedule in the list.
        """

        if not self.schedules:
            return
        self.current_schedule_index = (self.current_schedule_index + 1) % len(self.schedules)
        self.update_table_data()

    def update_table_data(self) -> None:

        """
        Updates the table with the current schedule data.
        """

        if (self.current_schedule_index < 0 or
                self.current_schedule_index >= len(self.schedules)):
            return
        schedule = self.schedules[self.current_schedule_index]
        self.rows = len(schedule.trains)
        self.table.setRowCount(self.rows)
        for i in range(self.rows):
            train_id_item = QTableWidgetItem(str(schedule.trains[i]))
            train_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            train_id_item.setFlags(
                train_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 0, train_id_item)

            stop_item = QTableWidgetItem(str(schedule.stops[i]))
            stop_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stop_item.setFlags(
                stop_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 1, stop_item)

            arrival_item = QTableWidgetItem(schedule.arrival_times[i].strftime('%H:%M'))
            arrival_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            arrival_item.setFlags(
                arrival_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 2, arrival_item)

    def clear_table(self) -> None:

        """
        Clears the table of all entries.
        """

        self.rows = 0
        self.table.setRowCount(self.rows)

    def dispatch_trains(self) -> None:

        """
        Dispatches the trains based on the table entries.
        """

        current_schedule = self.schedules[self.current_schedule_index]
        for i in range(len(current_schedule.trains)):
            train_id = int(current_schedule.trains[i])
            arrival_time = time_to_seconds(current_schedule.arrival_times[i].strftime('%H:%M'))

            target_block_text = str(current_schedule.stops[i])
            target_block = int(''.join(filter(str.isdigit, target_block_text[:2])))

            self.dispatched_train.emit(train_id, target_block, arrival_time)

        self.clear_table()

    def set_line(self, line: Line) -> None:

        """
        Sets the line for the ScheduleSelectionWidget.

        Args:
            line (Line): The line object.
        """

        self.line = line
        self.clear_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    schedule_widget = ScheduleSelectionWidget()
    window.setCentralWidget(schedule_widget)
    window.setWindowTitle("Schedule Selection")
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec())
