import os
import sys
import networkx as nx
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QApplication,
                             QMainWindow)
from PyQt6.QtGui import QColor, QPalette, QPainter, QPen
from PyQt6.QtCore import Qt
from typing import Optional

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock


class TrainVisualTableWidget(QWidget):
    def __init__(self, line: Line, parent: Optional[QWidget] = None) -> None:

        """
        Initializes the TrainVisualWidget.

        Args:
            line (Line): The line object containing track blocks.
            parent (Optional[QWidget]): The parent widget.
        """

        super().__init__(parent)
        self.title = "Train Visual"
        self.line = line
        self.rows = len(line.track_blocks)
        self.cols = 2
        self.headers = ["Block ID", "Status"]
        self.init_ui()
        self.connect_signals()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the TrainVisualWidget.
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
                border: 1px solid; 
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
        Connects signals for occupancy and maintenance changes.
        """

        for track_block in self.line.track_blocks.values():
            track_block.occupancyChanged.connect(self.update_table_data)
            track_block.maintenanceChanged.connect(self.update_table_data)
            
    def update_table_data(self) -> None:

        """
        Updates the table data based on the current state of track blocks.
        """
        
        self.rows = len(self.line.track_blocks)
        self.table.setRowCount(self.rows)
        for i, track_block in enumerate(self.line.track_blocks.values()):
            number_item = QTableWidgetItem(str(track_block.number))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            number_item.setFlags(
                number_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(i, 0, number_item)

            status_item = QTableWidgetItem()
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setFlags(
                status_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )

            if track_block.under_maintenance:
                status_item.setText("Under Maintenance")
                color = QColor("#FFFF00")
            elif track_block.occupancy:
                status_item.setText("Occupied")
                color = QColor("#FFCCCC")
            else:
                status_item.setText("Unoccupied")
                color = QColor("#CCFFCC")

            status_item.setBackground(color)
            status_item.setForeground(QColor("#000000"))
            self.table.setItem(i, 1, status_item)


class TrainVisualWidget(QWidget):

    def __init__(self, line: Line):
        super().__init__()

        # Line parameters
        self.title = f"{line.name} Line Layout"
        self.track_blocks = line.track_blocks

        # Scaling parameters
        self.y_block_padding = 0.1
        self.y_offset = 1
        self.y_scale = self.height() / 4
        self.main_branch_length = self.compute_main_branch_length()
        self.x_block_padding = 10
        self.x_total_padding = (len(self.track_blocks) + 2) * self.x_block_padding
        self.x_scale = self.width() / (self.main_branch_length + self.x_total_padding)
        self.relative_block_positions = self.find_relative_block_positions()

    def paintEvent(self, event):

        # Initialize the painter
        painter = QPainter(self)

        # Draw the track blocks
        for block in self.track_blocks:
            if block.occupancy:
                pen = QPen(Qt.GlobalColor.red, 6)
            elif block.under_maintenance:
                pen = QPen(Qt.GlobalColor.yellow, 6)
            else:
                pen = QPen(Qt.GlobalColor.white, 6)
            painter.setPen(pen)

            # Scale the block positions to the window size
            block_endpoints = self.relative_block_positions[block.number - 1]
            x1 = int(block_endpoints[0][0] * self.x_scale)
            x2 = int(block_endpoints[1][0] * self.x_scale)
            y1 = int((block_endpoints[0][1] + self.y_offset) * self.y_scale)
            y2 = int((block_endpoints[1][1] + self.y_offset) * self.y_scale)
            painter.drawLine(x1, y1, x2, y2)
            
    def resizeEvent(self, event):
        self.y_scale = self.height() / 4
        self.x_scale = self.width() / (self.main_branch_length + self.x_total_padding)
        self.update()  # Trigger repaint

    def compute_main_branch_length(self) -> int:
        main_branch_length = 0
        for block in self.track_blocks:
            if block.branch == 1:
                main_branch_length += block.length

        return main_branch_length

    def find_relative_block_positions(self) -> list:

        # Initialize the search parameters
        visited_blocks = {1}
        block_positions = [[[0, 1], [0, 1]] for _ in range(len(self.track_blocks))]
        starting_block = self.track_blocks[0]
        block_positions[0] = [[self.x_block_padding, 1], [starting_block.length, 1]]

        # Recursively search for the connections and their relative positions
        self.recursive_position_search(2, 1, visited_blocks, block_positions, self.track_blocks)

        return block_positions

    def recursive_position_search(self, block_id, prev_block_id, visited_blocks, positions, blocks):

        # If block is already visited, return
        if block_id in visited_blocks:
            return

        # Mark the block as visited
        visited_blocks.add(block_id)

        # Get the current and previous block objects
        block = blocks[block_id - 1]
        prev_block = blocks[prev_block_id - 1]
        
        # Compute the x-coordinates of the current block
        x1 = positions[prev_block_id - 1][1][0] + self.x_block_padding
        x2 = x1 + block.length

        # Case 1: The current block is on the same branch as the previous block
        if block.branch == prev_block.branch:
            y1 = y2 = prev_block.branch

        # Case 2: The current block is branching upwards off the previous block
        elif block.branch < 1 and prev_block.branch == 1:
            y1 = 1 - self.y_block_padding
            y2 = block.branch + self.y_block_padding

        # Case 3: The current block is merging downwards onto the main branch
        elif block.branch == 1 and prev_block.branch < 1:
            y1 = 1 + self.y_block_padding
            y2 = block.branch - self.y_block_padding

            # Adjust the y-coordinates of the previous block
            positions[prev_block_id - 1][1][1] = block.branch - self.y_block_padding

        # Case 4: The current block is branching downwards off the previous block
        elif block.branch > 1 and prev_block.branch == 1:
            y1 = 1 + self.y_block_padding
            y2 = block.branch - self.y_block_padding

        # Case 5: The current block is merging upwards onto the main branch
        elif block.branch == 1 and prev_block.branch > 1:
            y1 = 1 - self.y_block_padding
            y2 = block.branch + self.y_block_padding

            # Adjust the y-coordinates of the previous block
            positions[prev_block_id - 1][1][1] = block.branch + self.y_block_padding

        # Store the new block's position
        positions[block_id - 1] = [[x1, y1], [x2, y2]]

        # Recursively search for the connections
        for next_block_id in blocks[block_id - 1].connecting_blocks:
            # Skip the next block if it was already visited
            if next_block_id in visited_blocks:
                continue

            # Recursively search for the connections
            self.recursive_position_search(next_block_id, block_id, visited_blocks, positions, blocks)
            
# Demonstrate line generation
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    # Create a line
    line = Line("Blue")

    # Load in the track blocks
    file_path = os.path.abspath(os.path.join("tests", "blue_line.xlsx"))

    # Load the track blocks
    line.load_track_blocks(file_path)

    display = TrainVisualWidget(line)
    
    layout.addWidget(display)
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
