from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, QPushButton)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from typing import Optional

from train_system.common.line import Line
from train_system.common.train import Train
from train_system.ctc_manager.ctc_manager import CTCOffice

class DispatchCommandWidget(QWidget):
    def __init__(self, line: Line, trains: list[Train], 
                 parent: Optional[QWidget] = None) -> None:
        
        """
        Initializes the DispatchCommandWidget.

        Args:
            line (Line): The line object containing track blocks.
            trains (list[Train]): The list of train objects.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Dispatch Command"
        self.line = line
        self.trains = trains
        self.rows = 0
        self.cols = 3
        self.headers = ["Train ID", "Set Block (Station)", "Arrival Time"]
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

        # Add data to the table
        self.add_table_entry()
        layout.addWidget(self.table)

        # Create a layout for the buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Add new entry button
        self.add_entry_button = QPushButton("Add Entry")
        self.add_entry_button.clicked.connect(self.add_table_entry)
        button_layout.addWidget(self.add_entry_button)

        # Add dispatch button
        self.dispatch_button = QPushButton("Dispatch")
        self.dispatch_button.clicked.connect(self.dispatch_trains)
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
        self.table.setCellWidget(row_num, 0, train_id_cell)

        # Create combo box for track block inputs
        track_block_cell = QComboBox()
        block_numbers = self.generate_block_numbers()
        track_block_cell.addItems(block_numbers)
        self.table.setCellWidget(row_num, 1, track_block_cell)

        # Create combo box for arrival times
        time_cell = QComboBox()
        times = self.generate_time_slots()
        time_cell.addItems(times)
        self.table.setCellWidget(row_num, 2, time_cell)

    def generate_train_ids(self) -> list[str]:

        """
        Generates a list of train IDs.

        Returns:
            list[str]: A list of train IDs as strings.
        """

        return [str(train.train_id) for train in self.trains]
    
    def generate_block_numbers(self) -> list[str]:

        """
        Generates a list of block numbers with station names if available.

        Returns:
            list[str]: A list of block numbers as strings.
        """

        block_numbers = []
        for block in self.line.track_blocks.values():
            if block.station is not None:
                block_numbers.append(f"{block.number} ({block.station.name})")
            else:
                block_numbers.append(str(block.number))
        return block_numbers

    def generate_time_slots(self) -> list[str]:

        """
        Generates a list of time slots in 15-minute increments.

        Returns:
            list[str]: A list of time slots as strings.
        """

        times = []
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                times.append(f"{hour:02d}:{minute:02d}")
        return times

    def dispatch_trains(self) -> None:

        """
        Dispatches the trains based on the table entries.
        """
        
        for row in range(self.rows):
            train_id = self.table.cellWidget(row, 0).currentText()
            target_block = self.table.cellWidget(row, 1).currentText()
            arrival_time = self.table.cellWidget(row, 2).currentText()
            print(f"Train {train_id} dispatched to block {target_block} at {arrival_time}")

            # Compute the distance from the train to the first stop
            distance = self.line.get_distance(1, int(target_block))
            if distance == 0:
                print("Suggest Initial Speed: 0")
            else:
                print("Suggest Initial Speed: 50")

            # Compute the authority for the train
            print("Initial Authority: ", distance)

        self.rows = 0
        self.table.setRowCount(self.rows)
            
