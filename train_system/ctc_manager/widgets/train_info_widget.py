from typing import Dict, Optional, Tuple, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSlot

from train_system.common.palette import Colors
from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.ctc_manager.ctc_train_dispatch import CTCTrainDispatch
from train_system.common.conversions import seconds_to_time, meters_to_miles, kph_to_mph
from train_system.common.authority import Authority


class TrainInfoWidget(QWidget):
    def __init__(self, time_keeper: TimeKeeper,
                 trains: Dict[Tuple[int, str], CTCTrainDispatch], 
                 parent: Optional[QWidget] = None) -> None:
        
        """
        Initializes the TrainInfoWidget.

        Args:
            time_keeper (TimeKeeper): The time keeper object to track time.
            trains (Dict[Tuple[int, str], CTCTrainDispatch]): Dictionary of train dispatch objects keyed by train ID and line name.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Train Information"
        self.time_keeper = time_keeper
        self.trains = trains
        self.rows = 0
        self.cols = 6
        self.headers = ["ID", "Block", "Destination", "Arrival",
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

        # Adjust column widths to fit contents and stretch all columns
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

        for row, ((train_id, line_name), train) in enumerate(self.trains.items()):
            self.set_table_item(row, 0, f"{train_id} - {line_name.capitalize()}")

            if train.dispatched:
                block_id = train.get_current_block_id()
                block_name = str(block_id)
                station_name = train.line.get_track_block(block_id).station
                if station_name is not None:
                    block_name += f" ({station_name})"
                self.set_table_item(row, 1, block_name)
            else:
                self.set_table_item(row, 1, "Yard")

            arrival_time, next_stop_id = train.get_next_stop()
            if next_stop_id is not None:
                block_name = str(next_stop_id)
                station_name = train.line.get_track_block(next_stop_id).station
                if station_name is not None:
                    block_name += f" ({station_name})"
                self.set_table_item(row, 2, block_name)
            else:
                self.set_table_item(row, 2, "NA")

            if arrival_time is not None:
                arrival_time_text = seconds_to_time(arrival_time)
                self.set_table_item(row, 3, arrival_time_text)
            else:
                self.set_table_item(row, 3, "NA")

            speed_mph = round(kph_to_mph(train.suggested_speed), 2)
            self.set_table_item(row, 4, f"{speed_mph} mph")

            authority = train.authority
            if authority is not None:
                authority_miles = round(meters_to_miles(train.authority.get_distance()), 2)
            else :
                authority_miles = 0
            self.set_table_item(row, 5, f"{authority_miles} miles")

    def set_table_item(self, row: int, col: int, text: str) -> None:

        """
        Helper method to create a non-editable, center-aligned table item with optional background color.

        Args:
            row (int): The row in which to place the item.
            col (int): The column in which to place the item.
            text (str): The text for the table item.
        """

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)        
        self.table.setItem(row, col, item)

    @pyqtSlot()
    def handle_time_update(self) -> None:
        self.update_table_data()
