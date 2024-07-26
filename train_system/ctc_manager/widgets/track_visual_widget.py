import os
import sys
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QApplication,
                             QMainWindow)
from PyQt6.QtGui import QColor, QPaintEngine, QPaintEvent, QPalette, QPainter, QPen, QFontMetrics
from PyQt6.QtCore import Qt, QPoint
from typing import Optional

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock


class TrackVisualTableWidget(QWidget):
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

class TrackVisualWidget(QWidget):
    def __init__(self, line: Line):
        super().__init__()

        # Line parameters
        self.line = line
        self.title = f"{line.name} Line Visual"
        self.setGeometry(100, 100, 800, 600)
        
        # Load in the line visual data
        filename = os.path.join(os.path.dirname(__file__), f"line_visuals\\{line.name.lower()}_visual.json")
        with open(filename, "r") as file:
            self.block_visuals = json.load(file)

        # Set the scaling values
        self.max_x = self.find_max_x()
        self.max_y = self.find_max_y()
        self.x_scale = self.width() // (self.max_x + 2)
        self.y_scale = self.height() // (self.max_y + 2)

        self.line_width = 3

    def find_max_y(self):
        max_y = 0
        for block in self.block_visuals:
            if block['y2'] > max_y:
                max_y = block['y2']
        return max_y
    
    def find_max_x(self):
        max_x = 0
        for block in self.block_visuals:
            if block['x2'] > max_x:
                max_x = block['x2']
        return max_x

    def resizeEvent(self, event):

        # Update the scaling values
        self.x_scale = self.width() // (self.max_x + 2)
        self.y_scale = self.height() // (self.max_y + 2)

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        font_metrics = QFontMetrics(painter.font())
        
        # Place the blocks on the visual
        for block in self.block_visuals:

            # Get the block number
            block_text = str(block["block_number"])

            # Set the visual block coordinates
            x1, y1 = block["x1"] * self.x_scale, block["y1"] * self.y_scale
            x2, y2 = block["x2"] * self.x_scale, block["y2"] * self.y_scale

            # Set the pen color based on the status of the block
            if self.line.get_track_block(block["block_number"]).occupancy:
                pen = QPen(Qt.GlobalColor.red, self.line_width)
            elif self.line.get_track_block(block["block_number"]).under_maintenance:
                pen = QPen(Qt.GlobalColor.yellow, self.line_width)
            else:
                pen = QPen(Qt.GlobalColor.white, self.line_width)

            # Check if the block is part of the yard
            if block["attribute"] == "Yard":
                pen = QPen(Qt.GlobalColor.white, self.line_width, Qt.PenStyle.DotLine)
                block_text = "Yard"
            
            # Check if the block is part of the station
            if block["attribute"] != "":
                block_text = block["attribute"]
            
            # Set the pen and draw the line
            painter.setPen(pen)
            painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))

            # Compute text width and height
            text_width = font_metrics.horizontalAdvance(block_text)
            text_height = font_metrics.height()
            
            # Position the center of the text on the center of the line (default cursor is bottom left)
            center_x = x1 + (x2 - x1) // 2 - text_width // 2
            center_y = y1 + (y2 - y1) // 2 + text_height // 2
            
            # Compute the x and y position of the text based on the text position
            # The text position is based on the following grid:
            # 1 | 2 | 3
            # 4 | 5 | 6
            # 7 | 8 | 9
            text_position = block["text_position"]
            if text_position == 0:
                continue
            if text_position == 1:
                text_x = center_x - text_width // 2
                text_y = center_y - text_height // 2 - self.line_width
            elif text_position == 2:
                text_x = center_x
                text_y = center_y - text_height // 2 - self.line_width
            elif text_position == 3:
                text_x = center_x + text_width // 2
                text_y = center_y - text_height // 2 - self.line_width
            elif text_position == 4:
                text_x = center_x - text_width // 2
                text_y = center_y
            elif text_position == 5:
                text_x = center_x
                text_y = center_y
            elif text_position == 6:
                text_x = center_x + text_width // 2
                text_y = center_y
            elif text_position == 7:
                text_x = center_x - text_width // 2
                text_y = center_y + text_height // 2 - self.line_width
            elif text_position == 8:
                text_x = center_x
                text_y = center_y + text_height // 2 - self.line_width
            elif text_position == 9:
                text_x = center_x + text_width // 2
                text_y = center_y + text_height // 2 - self.line_width
            else:
                print("Invalid text position")

            painter.drawText(text_x, text_y, block_text)

    def set_line(self, line: Line) -> None:

        """
        Sets the line for the visual.

        Args:
            line (Line): The line object.
        """

        self.line = line
        filename = os.path.join(os.path.dirname(__file__), f"line_visuals\\{line.name.lower()}_visual.json")
        with open(filename, "r") as file:
            self.block_visuals = json.load(file)

        self.max_x = self.find_max_x()
        self.max_y = self.find_max_y()
        self.x_scale = self.width() // (self.max_x + 2)
        self.y_scale = self.height() // (self.max_y + 2)
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    line = Line("Red")
    line.load_defaults()

    widget = TrackVisualWidget(line)
    widget.show()
    sys.exit(app.exec())