import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic

class CircleWidget(QWidget):


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
        painter.drawEllipse(self.x, self.y, 50, 50)

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
