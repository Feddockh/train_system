
import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic

class RectangleWidget(QtWidgets.QWidget):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.setFixedSize(width, height)
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.color)))
        painter.drawRect(self.x, self.y, self.width, self.height)