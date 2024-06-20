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
        self.MBO_mode_view.setFixedSize(150,50)
        self.MBO_mode_view.setFont(QFont('Times', 12))
        self.MBO_mode_view.clicked.connect(self.open_MBO_mode_view)
        
        self.test_bench_window = None
        #button to navigate to test bench view 
        self.test_bench_view = QPushButton('Test Bench')
        self.test_bench_view.setFont(QFont('Times', 12))
        self.test_bench_view.setFixedSize(100,50)
        self.test_bench_view.clicked.connect(self.open_test_bench_view)
        
    
        
        MBO = MBOController()
        #displaying current dispatch mode
        self.dispatch_label = QLabel('Dispatch Mode:') 
        self.dispatch_label.setFont(QFont('Times',10))
        self.dispatch_label.setFixedSize(100,50)
        self.dispatch_mode = QLabel(str(MBO.dispatch_mode))
        self.dispatch_mode.setFont(QFont('Times',10))
        self.dispatch_mode.setFixedSize(100,50)
        
        
        #displaying current overlay mode 
        self.overlay_label = QLabel('Overlay Mode:')
        self.overlay_label.setFont(QFont('Times',10))
        self.overlay_label.setFixedSize(100,50)
        self.overlay_mode = QLabel(str(MBO.overlay_mode))
        self.overlay_mode.setFont(QFont('Times',10))
        self.overlay_mode.setFixedSize(100,50)
        
        
        #lable to prompt/dircetion for user to enter information
        self.enter_label = QLabel('Please enter the date and time for the new schedules.')
        self.enter_label.setFont(QFont('Times', 18))
        self.enter_label.setFixedHeight(50)
        
        #creating calendar pop up and time
        self.schedule_date_time = QDateTimeEdit(datetime.now(),self)
        self.schedule_date_time.setFixedSize(300,50)
        self.schedule_date_time.setFont(QFont('Times', 12))
        self.schedule_date_time.setCalendarPopup(True)
        
        #Creat New Schedules Button, when clicked calls create sched function 
        self.create_schedules = QPushButton('Create New Schedules', self)
        self.create_schedules.setFixedSize(300,100)
        self.create_schedules.setFont(QFont('Times', 18))
        self.create_schedules.setStyleSheet("background-color : lime") 
        self.create_schedules.clicked.connect(self.save_schedule_date_time)
        
        #setting dispatch mode layout 
        self.dispatch_layout = QHBoxLayout()
        self.dispatch_layout.addWidget(self.dispatch_label)
        self.dispatch_layout.addWidget(self.dispatch_mode)
        
        #setting overlay mode layout
        self.overlay_layout = QHBoxLayout()
        self.overlay_layout.addWidget(self.overlay_label)
        self.overlay_layout.addWidget(self.overlay_mode)
        
        #setting layout of the page
        self.schedule_layout = QVBoxLayout()
        self.schedule_layout.addWidget(self.MBO_mode_view)
        self.schedule_layout.addLayout(self.dispatch_layout)
        self.schedule_layout.addLayout(self.overlay_layout)
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
        self.selected_start_time = self.schedule_date_time.dateTime().toString('HH:mm:ss')
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
        self.trains_header = QLabel('Train')
        self.trains_header.setFixedSize(200,75)
        self.trains_header.setFont(QFont('Times',12))
        self.line_header = QLabel('Line')
        self.line_header.setFixedSize(200,75)
        self.line_header.setFont(QFont('Times',12))
        self.station_header = QLabel('Station')
        self.station_header.setFixedSize(200,75)
        self.station_header.setFont(QFont('Times',12))
        self.position_header = QLabel('Position [m]')
        self.position_header.setFixedSize(200,75)
        self.position_header.setFont(QFont('Times',12))
        self.authority_header = QLabel('Authority [ft]')
        self.authority_header.setFixedSize(200,75)
        self.authority_header.setFont(QFont('Times',12))
        self.speed_header = QLabel('Commanded Speed [mph]')
        self.speed_header.setFixedSize(200,75)
        self.speed_header.setFont(QFont('Times',12))
        
        #aligning header
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.trains_header)
        self.header_layout.addWidget(self.line_header)
        self.header_layout.addWidget(self.station_header)
        self.header_layout.addWidget(self.position_header)
        self.header_layout.addWidget(self.authority_header)
        self.header_layout.addWidget(self.speed_header)
        
        
        #labels for train positions 
        self.train1_position_label = QLabel("Train 1")
        self.train1_position_label.setFixedSize(200,75)
        self.train1_position_label.setFont(QFont('Times',10))
        self.train2_position_label = QLabel("Train 2")
        self.train2_position_label.setFixedSize(200,75)
        self.train2_position_label.setFont(QFont('Times',10))
        self.train3_position_label = QLabel("Train 3")
        self.train3_position_label.setFixedSize(200,75)
        self.train3_position_label.setFont(QFont('Times',10))
        
        #text boxes to edit train position
        self.train1_position = QTextEdit('0')
        self.train1_position.setFixedSize(200,75)
        self.train1_position.setFont(QFont('Times',10))
        self.train2_position = QTextEdit('0')
        self.train2_position.setFixedSize(200,75)
        self.train2_position.setFont(QFont('Times',10))
        self.train3_position = QTextEdit('0')
        self.train3_position.setFixedSize(200,75)
        self.train3_position.setFont(QFont('Times',10))
        
        #line (all blue lol)
        self.train1_line = QLabel("Blue")
        self.train1_line.setFixedSize(200,75)
        self.train1_line.setFont(QFont('Times',10))
        self.train2_line = QLabel("Blue")
        self.train2_line.setFixedSize(200,75)
        self.train2_line.setFont(QFont('Times',10))
        self.train3_line = QLabel("Blue")
        self.train3_line.setFixedSize(200,75)
        self.train3_line.setFont(QFont('Times',10))
        
        
        #stations (for blue line)
        self.train1_station = QComboBox()
        self.train1_station.addItems(['Station B', 'Station C', 'Yard'])
        self.train1_station.setFixedSize(200,75)
        self.train1_station.setFont(QFont('Times',10))
        self.train2_station = QComboBox()
        self.train2_station.addItems(['Station B', 'Station C', 'Yard'])
        self.train2_station.setFixedSize(200,75)
        self.train2_station.setFont(QFont('Times',10))
        self.train3_station = QComboBox()
        self.train3_station.addItems(['Station B', 'Station C', 'Yard'])
        self.train3_station.setFixedSize(200,75)
        self.train3_station.setFont(QFont('Times',10))
        
    
        #place holders for commanded speed 
        self.train1_commanded_speed = QLabel('---')
        self.train1_commanded_speed.setFixedSize(200,75)
        self.train1_commanded_speed.setFont(QFont('Times',10))
        self.train2_commanded_speed = QLabel('---')
        self.train2_commanded_speed.setFixedSize(200,75)
        self.train2_commanded_speed.setFont(QFont('Times',10))
        self.train3_commanded_speed = QLabel('---')
        self.train3_commanded_speed.setFixedSize(200,75)
        self.train3_commanded_speed.setFont(QFont('Times',10))
        
        #place holders for authority 
        self.train1_authority = QLabel('---')
        self.train1_authority.setFixedSize(200,75)
        self.train1_authority.setFont(QFont('Times',10))
        self.train2_authority = QLabel('---')
        self.train2_authority.setFixedSize(200,75)
        self.train2_authority.setFont(QFont('Times',10))
        self.train3_authority = QLabel('---')
        self.train3_authority.setFixedSize(200,75)
        self.train3_authority.setFont(QFont('Times',10))
        
          
        #button to run test bench
        self.test = QPushButton("Run Test")
        self.test.setFixedSize(200,100)
        self.test.setStyleSheet("background-color : lime") 
        self.test.setFont(QFont('Times', 14))
        self.test.clicked.connect(self.run_test_bench)
        
        #setting up layout to align position labels 
        self.layout_position_labels = QVBoxLayout()
        self.layout_position_labels.addWidget(self.train1_position_label)
        self.layout_position_labels.addWidget(self.train2_position_label)
        self.layout_position_labels.addWidget(self.train3_position_label)
        
        #setting up layout to align text edit boxes 
        self.layout_position_text = QVBoxLayout()
        self.layout_position_text.addWidget(self.train1_position)
        self.layout_position_text.addWidget(self.train2_position)
        self.layout_position_text.addWidget(self.train3_position)
        
        #vert aligning of line
        self.layout_line = QVBoxLayout()
        self.layout_line.addWidget(self.train1_line)
        self.layout_line.addWidget(self.train2_line)
        self.layout_line.addWidget(self.train3_line)
        
        #vert aligining of stations 
        self.layout_station = QVBoxLayout()
        self.layout_station.addWidget(self.train1_station)
        self.layout_station.addWidget(self.train2_station)
        self.layout_station.addWidget(self.train3_station)
        
        #vert aligning layout of commanded speeds 
        self.layout_speed = QVBoxLayout()
        self.layout_speed.addWidget(self.train1_commanded_speed)
        self.layout_speed.addWidget(self.train2_commanded_speed)
        self.layout_speed.addWidget(self.train3_commanded_speed)
        
        #vert aligning layout of author
        self.layout_authority = QVBoxLayout()
        self.layout_authority.addWidget(self.train1_authority)
        self.layout_authority.addWidget(self.train2_authority)
        self.layout_authority.addWidget(self.train3_authority)
        
        #horz aligning columns in table 
        self.column_layout = QHBoxLayout()
        self.column_layout.addLayout(self.layout_position_labels)
        self.column_layout.addLayout(self.layout_line)
        self.column_layout.addLayout(self.layout_station)
        self.column_layout.addLayout(self.layout_position_text)
        self.column_layout.addLayout(self.layout_authority)
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
        test_trains_positions = {"Train1": int(self.train1_position.toPlainText()), "Train2": int(self.train2_position.toPlainText()), "Train3": int(self.train3_position.toPlainText())}
        
        c =x.ms_to_mph( x.commanded_speed(x.enable_s_and_a) )
        self.train1_commanded_speed.setText(str(c))
        self.train2_commanded_speed.setText(str(c))
        self.train3_commanded_speed.setText(str(c))
        
        x.emergency_breaking_distance()
        block = {}
        authorities = x.authority(test_trains_positions, block)
        
        self.train1_authority.setText(str(x.m_to_ft(authorities['Train1'])))
        self.train2_authority.setText(str(x.m_to_ft(authorities['Train2'])))
        self.train3_authority.setText(str(x.m_to_ft(authorities['Train3'])))
        
        
       

app = QApplication(sys.argv)

window = MBOWindow()
window.show()
app.exec()