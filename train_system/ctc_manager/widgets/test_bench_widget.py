from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox, 
                             QAbstractItemView)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from typing import Optional

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

class TestBenchWidget(QWidget):
    def __init__(self, line: Line, parent: Optional[QWidget] = None) -> None:

        """
        Initializes the TestBenchWidget.

        Args:
            line (Line): The line object containing track blocks.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Test Bench"
        self.line = line
        self.rows = len(line.track_blocks)
        self.cols = 2
        self.headers = ["Block ID", "Status"]
        self.init_ui()
        self.connect_signals()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the TestBenchWidget.
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

    def connect_signals(self) -> None:

        """
        Connects signals for track block occupancy changes.
        """

        for track_block in self.line.track_blocks.values():
            track_block.occupancyChanged.connect(self.update_table_data)

    def update_table_data(self) -> None:

        """
        Updates the table data with the current track block statuses.
        """

        self.rows = len(self.line.track_blocks)
        self.table.setRowCount(self.rows)
        for i, track_block in enumerate(self.line.track_blocks.values()):
            track_block_cell = QTableWidgetItem(str(track_block.number))
            track_block_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            track_block_cell.setFlags(
                track_block_cell.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 0, track_block_cell)

            # ComboBox for occupancy status
            status_cell = QComboBox()
            status_cell.addItems(["Available", "Occupied"])
            status_cell.setCurrentText(
                "Occupied" if track_block.occupancy else "Available"
            )
            status_cell.currentTextChanged.connect(
                lambda state, tb=track_block: self.update_occupancy_status(tb, state)
            )
            self.table.setCellWidget(i, 1, status_cell)

            self.update_cell_color(i, 1, track_block.occupancy)

    def update_occupancy_status(self, track_block: TrackBlock, state: str) -> None:

        """
        Updates the occupancy status of a track block.

        Args:
            track_block (TrackBlock): The track block to update.
            state (str): The new state ("Available" or "Occupied").
        """

        track_block.occupancy = state == "Occupied"
        self.update_table_data()

    def update_cell_color(self, row: int, col: int, occupancy: bool) -> None:

        """
        Updates the color of a cell based on its occupancy status.

        Args:
            row (int): The row of the cell.
            col (int): The column of the cell.
            occupancy (bool): Whether the track block is occupied.
        """
        
        widget = self.table.cellWidget(row, col)
        if widget:
            color = QColor("#FFCCCC") if occupancy else QColor("#FFFFFF")
            widget.setStyleSheet(f"background-color: {color.name()}; color: black;")
