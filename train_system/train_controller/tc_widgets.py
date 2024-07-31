import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor, QPalette, QIntValidator
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from typing import List, Optional


TRAIN_COL = 0
KP_COL = 1
KI_COL = 2 

class CircleWidget(QWidget):


    def __init__(self, x, y):
        super().__init__()

        self.x = x
        self.y = y
        self.color = QColor(Qt.GlobalColor.white)
        
        ##self.setWindowTitle('Solid Green Circle')
        ##self.setGeometry(100, 100, 300, 300)  # Set initial size and position

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Optional: smooth edges
        
        pen = QtGui.QPen()
        pen.setWidth(0)

        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(self.color))
        brush.setStyle(Qt.BrushStyle.Dense1Pattern)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self.x, self.y, 50, 50)

    def setColor(self,color):
        self.color = QColor(color)
        self.update()
        
class TinyCircleWidget(QWidget):


    def __init__(self, x, y, color):
        super().__init__()

        self.x = x
        self.y = y
        self.color = color
        
        ##self.setWindowTitle('Solid Green Circle')
        ##self.setGeometry(100, 100, 300, 300)  # Set initial size and position

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Optional: smooth edges
        
        pen = QtGui.QPen()
        pen.setWidth(0)

        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(self.color))
        brush.setStyle(Qt.BrushStyle.Dense1Pattern)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self.x, self.y, 10, 10)

class EngineerTrains:
    def __init__(self):
        self.edit_kp = QLineEdit()
        self.edit_ki = QLineEdit()

class TableCellDelegate(QStyledItemDelegate):
    def __init__(self, validator, parent=None):
        super().__init__(parent)
        self.validator = validator

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(self.validator)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        text = editor.text()
        # Validate the input
        if self.validator.validate(text, 0)[0] == QIntValidator.State.Acceptable:
            model.setData(index, text)
        else:
            QMessageBox.warning(editor, "Invalid Input", "Please enter a valid number.")

class EngineerTable(QWidget):
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
        self.cols = 3
        self.headers = headers
        self.data = data
        self.trains_list =[]
        
        self.init_ui()

    def init_ui(self) -> None:

        """
        Initializes the user interface for the CustomTable.

        Returns:
            None
        """

        for i in range(20):
            self.trains_list.append(EngineerTrains())

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
                background-color: #BDB4BF;
                color: #071013;
                font-size: 14pt;
            }
            QTableWidget::item {
                background-color: #FCF7FF;
                border: 1px solid #071013; 
            }
            QTableWidget {
                gridline-color: #071013; 
            }
        """)

        # Set the palette for the table to control the background and text colors
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0xBDB4BF))
        palette.setColor(QPalette.ColorRole.Text, QColor(0x071013))
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

                #train number cannot be edited
                if(col_idx == 0):
                    table_item.setFlags(
                        table_item.flags() & ~Qt.ItemFlag.ItemIsEditable # Remove to make editable
                    )

                self.table.setItem(row_idx, col_idx, table_item)

            