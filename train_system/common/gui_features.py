# train_system/common/gui_features.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from typing import List, Optional

class CustomTable(QWidget):
    def __init__(self, title: str, rows: int, cols: int, headers: List[str],
                 data: List[List[str]], parent: Optional[QWidget] = None) -> None:
        
        """
        Initializes the CustomTable object.

        Args:
            title (str): The title of the table.
            rows (int): The number of rows in the table.
            cols (int): The number of columns in the table.
            headers (List[str]): The headers for the table columns.
            data (List[List[str]]): The data to be displayed in the table.
            parent (Optional[QWidget]): The parent widget, if any.

        Returns:
            None
        """

        super().__init__(parent)
        self.title = title
        self.rows = rows
        self.cols = cols
        self.headers = headers
        self.data = data
        self.init_ui()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the CustomTable.

        Returns:
            None
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
        self.update_table_data(self.data)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_table_data(self, data: List[List[str]]) -> None:

        """
        Updates the table with new data.

        Args:
            data (List[List[str]]): The data to be displayed in the table.

        Returns:
            None
        """
        
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, item in enumerate(row_data):
                table_item = QTableWidgetItem(item)
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_item.setFlags(
                    table_item.flags() & ~Qt.ItemFlag.ItemIsEditable # Remove to make editable
                )
                self.table.setItem(row_idx, col_idx, table_item)

# Demonstrate the usage of the CustomTable class
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    headers = ["Column 1", "Column 2", "Column 3"]
    data = [
        ["1", "A", "X"],
        ["2", "B", "Y"],
        ["3", "C", "Z"]
    ]

    table = CustomTable("Custom Table", 3, 3, headers, data)
    table.show()

    sys.exit(app.exec())
