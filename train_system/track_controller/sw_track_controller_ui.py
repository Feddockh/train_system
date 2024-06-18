import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class TestBenchWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test Bench")
        

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Programmer UI")



app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()