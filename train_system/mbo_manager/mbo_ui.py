from PyQt6.QtCore import Qt
from PyQt6.QtGui import * 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from random import choice
from datetime import datetime
import sys


from PyQt6.QtWidgets import QWidget

from mbo_manager import MBOController

class MBOWindow(QMainWindow):
    def __init__(self):
        super(MBOWindow, self).__init__()
        
        #name window
        self.setWindowTitle("MBO Controller")
        self.setFixedSize(1222, 702)
        
        self.MBO_mode_window = None
        #button to navigate to MBO mode view, see trains postitions, commanded speed and authority in real time? 
        self.MBO_mode_view = QPushButton('MBO Mode View', self)
        self.MBO_mode_view.clicked.connect(self.open_MBO_mode_view)
        
        self.test_bench_window = None
        #button to navigate to test bench view 
        self.test_bench_view = QPushButton('Test Bench')
        self.test_bench_view.clicked.connect(self.open_test_bench_view)
        
        #display txt file of schedule? 
        
        #test bench - button and page 
        
        
        #lable to prompt/dircetion for user to enter information
        self.enter_label = QLabel('Please enter the date and time for the new schedules.')
        
        #creating calendar pop up and time
        self.schedule_date_time = QDateTimeEdit(datetime.now(),self)
        self.schedule_date_time.setCalendarPopup(True)
        
        #Creat New Schedules Button, when clicked calls create sched function 
        self.create_schedules = QPushButton('Create New Schedules', self)
        self.create_schedules.clicked.connect(self.save_schedule_date_time)
        
        #init layout for creating schedule
        self.schedule_layout = QVBoxLayout()
        #setting layout of the page
        self.schedule_layout.addWidget(self.MBO_mode_view)
        self.schedule_layout.addWidget(self.enter_label)
        self.schedule_layout.addWidget(self.schedule_date_time)
        self.schedule_layout.addWidget(self.create_schedules)
        self.schedule_layout.addWidget(self.test_bench_view)
        
        widget = QWidget()
        widget.setLayout(self.schedule_layout)
        self.setCentralWidget(widget)
        
        
    #calling function to create schedules 
    def save_schedule_date_time(self):
        """
        Format and send user entered date and time to mbo_manager file to create schedule 
        """
        self.selected_day = self.schedule_date_time.dateTime().toString('MM-dd-yyyy')
        self.selected_start_time = self.schedule_date_time.dateTime().toString('HH:mm')
        x = MBOController()   
        x.create_schedules(self.selected_day, self.selected_start_time)
    
    #opening MBO mode view window
    def open_MBO_mode_view(self):
        if self.MBO_mode_window is None:
            self.MBO_mode_window = MBOModeView()
            self.MBO_mode_window.show()
        else:
            self.MBO_mode_window.close()
            self.MBO_mode_window = None
    
    #opening test bench view for MBO mode view window 
    def open_test_bench_view(self):
        if self.test_bench_window is None:
            self.test_bench_window = TestBench()
            self.test_bench_window.show()
        else:
            self.test_bench_window.close()
            self.test_bench_window = None
        
    

class MBOModeView(QWidget):
    def __init__(self):
        super(MBOModeView, self).__init__()
        
        self.setWindowTitle("MBO Mode View")
        self.setFixedSize(1222, 702)
        
        self.MBO_mode_view = QPushButton('MBO Mode View', self)
        self.MBO_mode_view.clicked.connect(self.close_MBO_mode_view)
    
    def close_MBO_mode_view(self):
        self.window = MBOModeView()
        #way to close window, back button!
        

class TestBench(QMainWindow):
    def __init__(self):
        super(TestBench,self).__init__()
        
        #label for page window 
        self.setWindowTitle("MBO Test Bench")
        self.setFixedSize(1222, 702)
        
        #labels for table header
        self.trains_header = QLabel('Trains')
        self.position_header = QLabel('Position')
        self.authority_header = QLabel('Authority')
        self.speed_header = QLabel('Commanded Speed')
        
        #aligning header
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.trains_header)
        self.header_layout.addWidget(self.position_header)
        self.header_layout.addWidget(self.authority_header)
        self.header_layout.addWidget(self.speed_header)
        
        
        #labels for train positions 
        self.train1_position_label = QLabel("Train 1")
        self.train2_position_label = QLabel("Train 2")
        self.train3_posotion_label = QLabel("Train 3")
        
        #text boxes to edit train position
        self.train1_position = QTextEdit()
        self.train2_position = QTextEdit()
        self.train3_position = QTextEdit()
    
        
        self.train1_commanded_speed = QLabel('-')
        self.train2_commanded_speed = QLabel('-')
        self.train3_commanded_speed = QLabel('-')
        
          
        #button to run test bench
        self.test = QPushButton("Run Test")
        self.test.clicked.connect(self.run_test_bench)
        
        #setting up layout to align position labels 
        self.layout_position_labels = QVBoxLayout()
        self.layout_position_labels.addWidget(self.train1_position_label)
        self.layout_position_labels.addWidget(self.train2_position_label)
        self.layout_position_labels.addWidget(self.train3_posotion_label)
        
        #setting up layout to align text edit boxes 
        self.layout_position_text = QVBoxLayout()
        self.layout_position_text.addWidget(self.train1_position)
        self.layout_position_text.addWidget(self.train2_position)
        self.layout_position_text.addWidget(self.train3_position)
        
        #vert aligning layout of commanded speeds 
        self.layout_speed = QVBoxLayout()
        self.layout_speed.addWidget(self.train1_commanded_speed)
        self.layout_speed.addWidget(self.train2_commanded_speed)
        self.layout_speed.addWidget(self.train3_commanded_speed)
        
        #horz aligning columns in table 
        self.column_layout = QHBoxLayout()
        self.column_layout.addLayout(self.layout_position_labels)
        self.column_layout.addLayout(self.layout_position_text)
        self.column_layout.addLayout(self.layout_speed)
        
        self.table_layout = QVBoxLayout()
        self.table_layout.addLayout(self.header_layout)
        self.table_layout.addLayout(self.column_layout)
        
        self.test_layout = QVBoxLayout()
        self.test_layout.addWidget(self.test)
        
        #aligning labels and text edit boxes 
        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(self.table_layout)
        self.window_layout.addLayout(self.test_layout)
        
        main_widget = QWidget()
        main_widget.setLayout(self.window_layout)
        self.setCentralWidget(main_widget)
        
    
        
        #enter in dispatch mode? 
        #show authority and commanded speed being enabled and disabled?
    
    def run_test_bench(self):
        x = MBOController() 
        
        x.enable_s_and_a = 1
        
        #need a check to make sure these text boxes are not empty! will crash! 
        
        #send out positions 
        x.trains_positions = {"Train1": int(self.train1_position.toPlainText()), "Train2": int(self.train2_position.toPlainText()), "Train3": int(self.train3_position.toPlainText())}
        
        c =x.ms_to_mph( x.commanded_speed(x.enable_s_and_a) )
        self.train1_commanded_speed.setText(str(c))
        self.train2_commanded_speed.setText(str(c))
        self.train3_commanded_speed.setText(str(c))
        
        x.emergency_breaking_distance()
        
        pass # x.authorirty()
        
        
        
        
       

app = QApplication(sys.argv)

window = MBOWindow()
window.show()
app.exec()