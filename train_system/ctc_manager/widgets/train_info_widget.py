from typing import Dict, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSlot

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.ctc_manager.ctc_train_dispatch import CTCTrainDispatch
from train_system.common.conversions import seconds_to_time, meters_to_miles, kph_to_mph

class TrainInfoWidget(QWidget):
    def __init__(self, time_keeper: TimeKeeper, line: Line, trains: Dict[int, CTCTrainDispatch], 
                 parent: Optional[QWidget] = None) -> None:
        
        """
        Initializes the TrainInfoWidget.

        Args:
            line (Line): The line object containing track blocks.
            trains (list[Train]): List of trains to display.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Train Information"
        self.line = line
        self.trains = trains
        self.rows = len(line.track_blocks)
        self.cols = 6
        self.headers = ["ID", "Current Block", "Dest. Block (Station)", "Arrival Time",
                        "Speed", "Authority"]
        self.init_ui()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the TrainInfoWidget.
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
        self.update_table_data()

        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_table_data(self) -> None:

        """
        Updates the table data based on the current state of trains.
        """
        
        self.rows = len(self.trains)
        self.table.setRowCount(self.rows)

        for row, (train_id, train) in enumerate(self.trains.items()):

            # Create cell for train ID
            train_id_cell = QTableWidgetItem(str(train_id))
            train_id_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            train_id_cell.setFlags(
                train_id_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 0, train_id_cell)

            # Create cell for current block or station
            if train.dispatched:
                block_id = train.get_current_block_id()
                block_name = str(block_id)
                station_name = self.line.get_track_block(block_id).station
                if station_name is not None:
                    block_name += f" ({station_name})"
                current_block_cell = QTableWidgetItem(block_name)
            else:
                current_block_cell = QTableWidgetItem("Yard")
            current_block_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            current_block_cell.setFlags(
                current_block_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 1, current_block_cell)

            # Create cell for block or station if the train is active
            arrival_time, next_stop_id = train.get_next_stop()
            if next_stop_id is not None:
                block_name = str(next_stop_id)
                station_name = self.line.get_track_block(next_stop_id).station
                if station_name is not None:
                    block_name += f" ({station_name})"
                dest_block_cell = QTableWidgetItem(block_name)
            else:
                dest_block_cell = QTableWidgetItem("NA")
            dest_block_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            dest_block_cell.setFlags(
                dest_block_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 2, dest_block_cell)

            # Create cell for arrival time
            if arrival_time is not None:
                arrival_time_text = seconds_to_time(arrival_time)
                arrival_time_cell = QTableWidgetItem(f"{arrival_time_text}")
            else:
                arrival_time_cell = QTableWidgetItem("NA")
            arrival_time_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            arrival_time_cell.setFlags(
                arrival_time_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 3, arrival_time_cell)

            # Create cell for suggested speed
            speed_mph = round(kph_to_mph(train.suggested_speed), 2)
            speed_cell = QTableWidgetItem(f"{speed_mph} mph")
            speed_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            speed_cell.setFlags(
                speed_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 4, speed_cell)

            # Create cell for authority
            authority_miles = round(meters_to_miles(train.authority), 2)
            authority_cell = QTableWidgetItem(f"{authority_miles} miles")
            authority_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            authority_cell.setFlags(
                authority_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(row, 5, authority_cell)

    @pyqtSlot()
    def handle_time_update(self) -> None:
        self.update_table_data()
