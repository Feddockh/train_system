from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSlot
from typing import Optional

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.station import Station
from train_system.ctc_manager.train import Train

class TrainInfoWidget(QWidget):
    def __init__(self, line: Line, trains: list[Train], 
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
        self.cols = 4
        self.headers = ["Train ID", "Block (Station)", "Suggested Speed", 
                        "Authority"]
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

        for i, train in enumerate(self.trains):
            # Create cell for train ID
            train_id_cell = QTableWidgetItem(str(train.train_id))
            train_id_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            train_id_cell.setFlags(
                train_id_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 0, train_id_cell)

            # Create cell for block or station if the train is active
            if train.block is not None:
                track_block = train.block
                track_block_name = str(track_block.number)
                if track_block.station is not None:
                    track_block_name += f" ({track_block.station.name})"
                track_block_cell = QTableWidgetItem(track_block_name)
                track_block_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                track_block_cell.setFlags(
                    track_block_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
            else:
                track_block_cell = QTableWidgetItem("N/A")
                track_block_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                track_block_cell.setFlags(
                    track_block_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
            self.table.setItem(i, 1, track_block_cell)

            # Create cell for suggested speed
            speed_cell = QTableWidgetItem(f"{train.speed} mph")
            speed_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            speed_cell.setFlags(
                speed_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 2, speed_cell)

            # Create cell for authority
            authority_cell = QTableWidgetItem(str(train.authority))
            authority_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            authority_cell.setFlags(
                authority_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 3, authority_cell)

    @pyqtSlot()
    def handle_train_update(self) -> None:
        self.update_table_data()
