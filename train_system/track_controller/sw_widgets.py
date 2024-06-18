import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic

class FileInputWidget(QWidget):

    def __init__(self, x, y, color):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        
        #If Upload File Clicked - allow upload file
        self.btn = QPushButton('Upload File')
        self.btn.setStyleSheet("""
        *{
        border: 2px solid '#000000';
        border-radius: 10px;
        background: '#0e7190';
        font-size: 20px;
        color: 'white';
        }
        *:hover{
        background: '#000000';
        color: 'white';            
        }
        """)
        self.btn.clicked.connect(self.getFileName)

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
        painter.drawRect(self.x, self.y, 10, 10)

    def getFileName(self):
        file_filter = 'Data File (*.py)'
        response = QFileDialog.getOpenFileName (
            parent = self,
            caption = 'Select a file',
            directory = os.getcwd(),
            filter = file_filter,
            initialFiler = 'Data File (*.py)'
        )
        
