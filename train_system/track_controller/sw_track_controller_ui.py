import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

def window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(0, 0, 1900, 1080)
    win.setWindowTitle("SW Programmer UI")

    

    win.show();
    sys.exit(app.exec())

window()