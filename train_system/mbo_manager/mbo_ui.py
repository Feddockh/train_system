from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import * 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from random import choice
from datetime import datetime
import sys


from PyQt6.QtWidgets import QWidget

from train_system.mbo_manager.gui_features import CustomTable


class MBOWindow(QMainWindow):
    
    schedule_created = pyqtSignal(QDateTime)
    
    def __init__(self):
        super(MBOWindow, self).__init__()
        
        #name window
        self.setWindowTitle("MBO Planner")
        self.setFixedSize(1222, 702)
        
        #lable to prompt/dircetion for user to enter date and time
        self.enter_label = QLabel('Please enter the date and time for the new schedules, then select the button.')
        self.enter_label.setFont(QFont('Times', 18))
        self.enter_label.setFixedHeight(50)
        
        #Creating calendar pop up to enter date and time
        self.schedule_date_time = QDateTimeEdit(datetime.now(),self)
        self.schedule_date_time.setFixedSize(400,50)
        self.schedule_date_time.setFont(QFont('Times', 12))
        self.schedule_date_time.setCalendarPopup(True)
        
        #Creat New Schedules Button, when clicked calls handle slot 
        self.create_schedules = QPushButton('Create New Schedules', self)
        self.create_schedules.setFixedSize(300,100)
        self.create_schedules.setFont(QFont('Times', 18))
        self.create_schedules.setStyleSheet("background-color : lime") 
        self.create_schedules.clicked.connect(self.handle_schedule)
        
        #page layout 
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.enter_label)
        vertical_layout.addWidget(self.schedule_date_time)
        vertical_layout.addWidget(self.create_schedules)
        
        
    @pyqtSlot()
    def handle_schedule(self) -> None:
        """
        emit date and start time selected 
        """      
        selected_datetime = self.schedule_date_time.dateTime()
        self.schedule_created.emit(selected_datetime)
        

        