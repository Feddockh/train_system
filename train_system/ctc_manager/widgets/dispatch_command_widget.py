import sys
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QPushButton,
                             QApplication)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal

from train_system.common.palette import Colors
from train_system.common.line import Line
from train_system.common.conversions import time_to_seconds

class DispatchCommandWidget(QWidget):
    dispatched_train = pyqtSignal(int, int, int)

    def __init__(self, line: Line, parent: Optional[QWidget] = None):

        """
        Initializes the DispatchCommandWidget.
        
        Args:
            line (Line): The line object.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Dispatch Command"
        self.line = line
        self.rows = 0
        self.cols = 3
        self.headers = ["Train ID", "Block", "Arrival Time"]
        self.init_ui()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the DispatchCommandWidget.
        """

        layout = QVBoxLayout()

        # Create table title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"background-color: {Colors.BLACK};"
            f"color: {Colors.WHITE};"
            "font-size: 16pt;"
            "font-weight: 600;"
        )
        layout.addWidget(title_label)

        # Create table widget
        self.table = QTableWidget(self.rows, self.cols)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)

        # Set the style for the table headers and cells
        self.table.setStyleSheet(f"""
            QHeaderView::section {{ 
                background-color: {Colors.GREY};
                color: {Colors.BLACK};
                font-size: 14pt;
            }}
            QTableWidget::item {{
                background-color: {Colors.WHITE};
                color: {Colors.BLACK};
                border: 1px solid {Colors.BLACK}; 
            }}
            QTableWidget {{
                background-color: {Colors.GREY};
                gridline-color: {Colors.BLACK};
            }}
        """)

        # Set the palette for the table to control the background and text colors
        palette = self.table.palette()
        self.table.setPalette(palette)

        # Adjust column widths to fit contents
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(self.cols):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch
            )

        # Add data to the table
        self.add_table_entry()
        layout.addWidget(self.table)

        # Create a layout for the buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Add new entry button
        self.add_entry_button = QPushButton("Add Entry")
        self.add_entry_button.clicked.connect(self.add_table_entry)
        self.add_entry_button.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        button_layout.addWidget(self.add_entry_button)

        # Add a clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_table)
        self.clear_button.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        button_layout.addWidget(self.clear_button)

        # Add dispatch button
        self.dispatch_button = QPushButton("Dispatch")
        self.dispatch_button.clicked.connect(self.dispatch_trains)
        self.dispatch_button.setStyleSheet(f"background-color: {Colors.GREY}; color: {Colors.BLACK};")
        button_layout.addWidget(self.dispatch_button)

        self.setLayout(layout)

    def add_table_entry(self) -> None:

        """
        Adds a new row to the table for entering dispatch commands.
        """

        # Increase the number of rows in the table
        row_num = self.rows
        self.rows += 1
        self.table.setRowCount(self.rows)
        
        # Create combo box for train IDs
        train_id_cell = QComboBox()
        trains_ids = self.generate_train_ids()
        train_id_cell.addItems(trains_ids)
        train_id_cell.setStyleSheet(f"color: {Colors.BLACK}; background-color: {Colors.WHITE};")
        self.table.setCellWidget(row_num, 0, train_id_cell)

        # Create combo box for track block inputs
        track_block_cell = QComboBox()
        block_numbers = self.generate_stops()
        track_block_cell.addItems(block_numbers)
        track_block_cell.setStyleSheet(f"color: {Colors.BLACK}; background-color: {Colors.WHITE};")
        self.table.setCellWidget(row_num, 1, track_block_cell)

        # Create combo box for arrival times
        time_cell = QComboBox()
        times = self.generate_time_slots()
        time_cell.addItems(times)
        time_cell.setStyleSheet(f"color: {Colors.BLACK}; background-color: {Colors.WHITE};")
        self.table.setCellWidget(row_num, 2, time_cell)

    def generate_train_ids(self) -> list[str]:

        """
        Generates a list of train IDs.

        Returns:
            list[str]: A list of train IDs as strings.
        """

        if self.line.name.lower() == "red":
            return [str(i) for i in range(20, 40)]
        else:
            return [str(i) for i in range(0, 20)]
    
    def generate_stops(self) -> list[str]:

        """
        Generates a list of stops with station names if available.

        Returns:
            list[str]: A list of block numbers as strings.
        """
        
        stops = []
        for block in self.line.track_blocks:
            if block.station:
                stops.append(f"{block.number} ({block.station.name})")
            else:
                stops.append(f"{block.number}")
        return stops

    def generate_time_slots(self) -> list[str]:

        """
        Generates a list of time slots in 1-minute increments.

        Returns:
            list[str]: A list of time slots as strings.
        """

        times = []
        for hour in range(24):
            for minute in range(0, 60):
                times.append(f"{hour:02d}:{minute:02d}")
        return times

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
        
        for row in range(self.rows):
            train_id = int(self.table.cellWidget(row, 0).currentText())
            arrival_time = time_to_seconds(self.table.cellWidget(row, 2).currentText())

            target_block_text = self.table.cellWidget(row, 1).currentText()
            target_block = int(''.join(filter(str.isdigit, target_block_text[:2])))

            self.dispatched_train.emit(train_id, target_block, arrival_time)

        self.clear_table()

    def set_line(self, line: Line) -> None:

        """
        Sets the line for the DispatchCommandWidget.

        Args:
            line (Line): The line object.
        """

        self.line = line
        self.clear_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    line = Line("Red")
    line.load_defaults()

    widget = DispatchCommandWidget(line)
    widget.show()
    sys.exit(app.exec())