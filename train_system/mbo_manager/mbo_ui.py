from PyQt6.QtGui import * 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from random import choice
from datetime import datetime
import sys


class MBOWindow(QMainWindow):
    def __init__(self):
        super(MBOWindow, self).__init__()
        
        self.setWindowTitle("MBO Controller")

        layout = QVBoxLayout()
        
        self.enter_label = QLabel('Please enter the date and time for the new schedules.')
        
        self.schedule_date_time = QDateTimeEdit(datetime.now(),self)
        self.schedule_date_time.setCalendarPopup(True)
        
        self.create_schedules = QPushButton('Create New Schedules', self)
        self.create_schedules.clicked.connect(self.save_schedule_date_time)
        
        
        layout.addWidget(self.enter_label)
        layout.addWidget(self.schedule_date_time)
        layout.addWidget(self.create_schedules)
    
        widget = QWidget()
        widget.setLayout(layout)   
        self.setCentralWidget(widget)     
        
    def save_schedule_date_time(self):
        selected_day_time = self.schedule_date_time.dateTime().toString('MM-dd-yyyy HH:mm')
        print('current date and time is', selected_day_time)       
       

app = QApplication(sys.argv)

window = MBOWindow()
window.show()
app.exec()