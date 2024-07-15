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
        self.line = line
        self.title = f"{line.name} Line Visual"
        self.setGeometry(100, 100, 800, 600)
        
        # Load in the line visual data
        filename = os.path.join(os.path.dirname(__file__), f"lines\\{line.name.lower()}.json")
        with open(filename, "r") as file:
            self.block_visuals = json.load(file)

        # Set the scaling values
        self.max_x = self.find_max_x()
        self.max_y = self.find_max_y()
        self.x_scale = self.width() // (self.max_x + 2)
        self.y_scale = self.height() // (self.max_y + 2)
        self.padding = self.x_scale // 10

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
        self.padding = self.x_scale // 10

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        font_metrics = QFontMetrics(painter.font())
        
        # Place the blocks on the visual
        for block in self.block_visuals:

            # Set the pen color based on the status of the block
            line_width = 2
            if self.line.get_track_block(block['block_number']).occupancy:
                pen = QPen(Qt.GlobalColor.red, line_width)
            elif self.line.get_track_block(block['block_number']).under_maintenance:
                pen = QPen(Qt.GlobalColor.yellow, line_width)
            else:
                pen = QPen(Qt.GlobalColor.white, line_width)
                painter.setPen(pen)

            # Set the visual block coordinates
            x1, y1 = block['x1'] * self.x_scale, block['y1'] * self.y_scale
            x2, y2 = block['x2'] * self.x_scale, block['y2'] * self.y_scale

            # Draw the line
            painter.drawLine(QPoint(x1 + self.padding, y1), QPoint(x2 - self.padding, y2))

            # Get the block number
            block_number = str(block['block_number'])

            # Compute text width and height
            text_width = font_metrics.horizontalAdvance(block_number)
            text_height = font_metrics.height()

            # Compute the x position of the text
            if block["y1"] < block["y2"]:
                text_x = x1 + (x2 - x1) // 2
            elif block["y1"] > block["y2"]:
                text_x = x1 + (x2 - x1) // 2 - text_width
            else:
                text_x = x1 + (x2 - x1) // 2 - text_width // 2
                
            # Compute the y position of the text
            if block["branch"] > 0:
                text_y = max(y1, y2) - abs(y1 - y2) // 2 - line_width - 1
            else:
                text_y = y1 + text_height

            painter.drawText(text_x, text_y, block_number)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)

    line = Line("Green")
    file_path = os.path.abspath(os.path.join("system_data\\tracks", f"{line.name.lower()}_line.xlsx"))
    line.load_track_blocks(file_path)

    widget = TrainVisualWidget(line)
    widget.show()
    sys.exit(app.exec())