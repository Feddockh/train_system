from PyQt6.QtCore import Qt
from PyQt6.QtGui import * 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from random import choice
from datetime import datetime
import sys


from PyQt6.QtWidgets import QWidget

from mbo_manager import MBOController
from gui_features import CustomTable

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
        
        
        MBO = MBOController()
        #displaying current dispatch mode
        self.dispatch_label = QLabel('Dispatch Mode:') 
        self.dispatch_label.setFont(QFont('Times',15))
        self.dispatch_label.setFixedSize(200,50)
        self.dispatch_mode = QLabel(str(MBO.dispatch_mode))
        self.dispatch_mode.setFont(QFont('Times',15))
        self.dispatch_mode.setFixedSize(200,50)
        
        
        #lable to prompt/dircetion for user to enter information
        self.enter_label = QLabel('Please enter the date and time for the new schedules.')
        self.enter_label.setFont(QFont('Times', 18))
        self.enter_label.setFixedHeight(50)
        
        #creating calendar pop up and time
        self.schedule_date_time = QDateTimeEdit(datetime.now(),self)
        self.schedule_date_time.setFixedSize(400,50)
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
        self.dispatch_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
      
       
        
        #setting layout of the page
        self.schedule_layout = QVBoxLayout()
        self.schedule_layout.addWidget(self.MBO_mode_view)
        self.schedule_layout.addLayout(self.dispatch_layout)
        self.schedule_layout.addWidget(self.enter_label)
        self.schedule_layout.addWidget(self.schedule_date_time)
        self.schedule_layout.addWidget(self.create_schedules)

        
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
    
        
    

class MBOModeView(QMainWindow):
    def __init__(self):
        super(MBOModeView, self).__init__()
        
        self.setWindowTitle("MBO Mode View")
        self.setFixedSize(1222, 702)
        
        
        m = MBOController()
         
        #displaying current dispatch mode
        self.dispatch_label = QLabel('Dispatch Mode:') 
        self.dispatch_label.setFont(QFont('Times',12))
        self.dispatch_label.setFixedSize(150,50)
        self.dispatch_mode = QLabel(str(m.dispatch_mode))
        self.dispatch_mode.setFont(QFont('Times',12))
        self.dispatch_mode.setFixedSize(150,50)
        
        
        self.title = QLabel('Current Commanded Speed and Authority')
        self.title.setFont(QFont('Times',12))
        
        self.test_bench_window = None
        #button to navigate to test bench view 
        self.test_bench_view = QPushButton('Test Bench')
        self.test_bench_view.setFont(QFont('Times', 12))
        self.test_bench_view.setFixedSize(100,50)
        self.test_bench_view.clicked.connect(self.open_test_bench_view)
        
        self.headers = ['Trains', 'Line', 'Station', 'Position [ft from yard]', 'Authority [ft]', 'Commanded Speed [mph]']
        self.table = QTableWidget(3,6)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(6):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch
            )
    

        self.table.setStyleSheet("""
            QHeaderView::section { 
                background-color: #C8C8C8;
                color: #333333;
                font-size: 12pt;
            }
            QTableWidget::item {
                background-color: #FDFDFD;
                border: 1px solid #333333; 
            }
            QTableWidget {
                gridline-color: #333333; 
            }
        """)

        # Set the palette for the table to control the background and text colors
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0xd9d9d9))
        palette.setColor(QPalette.ColorRole.Text, QColor(0x333333))
        self.table.setPalette(palette)
        
        
        self.demo_data_positions = m.testing_positions_1
        self.demo_data_destination = m.destinations_1
        self.demo_data_block = m.block_maint_1
        
        self.demo_data_authority = m.authority(self.demo_data_positions, self.demo_data_destination, self.demo_data_block)
        self.demo_data_speed = m.commanded_speed(1)
        
        self.row1 = ["Train1", "Blue", self.demo_data_destination['Train1'], str(m.m_to_ft(self.demo_data_positions['Train1'])), str(m.m_to_ft(self.demo_data_authority['Train1'])), str(m.ms_to_mph(self.demo_data_speed)) ]
        self.row2 = ["Train2", "Blue", self.demo_data_destination['Train2'], str(m.m_to_ft(self.demo_data_positions['Train2'])), str(m.m_to_ft(self.demo_data_authority['Train2'])), str(m.ms_to_mph(self.demo_data_speed))]
        self.row3 = ["Train3", "Blue", self.demo_data_destination['Train3'], str(m.m_to_ft(self.demo_data_positions['Train3'])), str(m.m_to_ft(self.demo_data_authority['Train3'])), str(m.ms_to_mph(self.demo_data_speed))]

        
        
        for col in range(0,6):
            table_item = QTableWidgetItem(self.row1[col])
            table_item.setFont(QFont('Times',13))
            table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table_item.setFlags(
            table_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(0, col, table_item)
        
        for col in range(0,6):
            table_item = QTableWidgetItem(self.row2[col])
            table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table_item.setFont(QFont('Times',13))
            table_item.setFlags(
            table_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(1, col, table_item)
        
        for col in range(0,6):
            table_item = QTableWidgetItem(self.row3[col])
            table_item.setFont(QFont('Times',13))
            table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table_item.setFlags(
            table_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )
            self.table.setItem(2, col, table_item)
        
        
        self.dispatch_lay = QHBoxLayout()
        self.dispatch_lay.addWidget(self.dispatch_label)
        self.dispatch_lay.addWidget(self.dispatch_mode)
        self.dispatch_lay.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        
        self.lay = QVBoxLayout()
        self.lay.addLayout(self.dispatch_lay)
        self.lay.addWidget(self.title)
        self.lay.addWidget(self.table)
        self.lay.addWidget(self.test_bench_view)
        
        widget = QWidget()
        widget.setLayout(self.lay)
        self.setCentralWidget(widget)
        
    #opening test bench view for MBO mode view window 
    def open_test_bench_view(self):
        if self.test_bench_window is None:
            self.test_bench_window = TestBench()
            self.test_bench_window.show()
        else:
            self.test_bench_window.close()
            self.test_bench_window = None
        
        
 
        

class TestBench(QMainWindow):
    def __init__(self):
        super(TestBench,self).__init__()
        
        #label for page window 
        self.setWindowTitle("MBO Test Bench")
        self.setFixedSize(1222, 702)
        
        
        self.block_label = QLabel('Select a block to put under maint.')
        self.block_label.setFont(QFont('Times',12))
        self.block_label.setFixedSize(300,100)
        
        self.block_select = QComboBox()
        self.block_select.addItems(['None','1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'])
        self.block_select.setFixedSize(200,75)
        self.block_select.setFont(QFont('Times',12))
        
        self.block_layout = QHBoxLayout()
        self.block_layout.addWidget(self.block_label)
        self.block_layout.addWidget(self.block_select)
        self.block_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.title = QLabel('Test Commanded Speed and Authority')
        self.title.setFont(QFont('Times',12))
        self.direction = QLabel('Please Selcect a Station destination and current Position for each train')
        self.direction.setFont(QFont('Times',12))
        
        self.headers = ['Trains', 'Line', 'Station', 'Position [m from yard]', 'Authority [m]', 'Commanded Speed [m/s]']
        
        self.table = QTableWidget(3,6)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(6):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch
            )
    

        self.table.setStyleSheet("""
            QHeaderView::section { 
                background-color: #C8C8C8;
                color: #333333;
                font-size: 12pt;
            }
            QTableWidget::item {
                background-color: #FDFDFD;
                border: 1px solid #333333; 
            }
            QTableWidget {
                gridline-color: #333333; 
            }
        """)

        # Set the palette for the table to control the background and text colors
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0xd9d9d9))
        palette.setColor(QPalette.ColorRole.Text, QColor(0x333333))
        self.table.setPalette(palette)
       
       
       #train id
        self.train1_id = QLabel("Train1")
        self.train1_id.setFont(QFont('Times',15))
        self.train2_id = QLabel("Train2")
        self.train2_id.setFont(QFont('Times',15))
        self.train3_id = QLabel("Train3")
        self.train3_id.setFont(QFont('Times',15))
        
        self.table.setCellWidget(0, 0, self.train1_id)
        self.table.setCellWidget(1, 0, self.train2_id)
        self.table.setCellWidget(2, 0, self.train3_id)
        
        
        #line 
        self.line1 = QLabel("Blue")
        self.line1.setFont(QFont('Times',15))
        self.line2 = QLabel("Blue")
        self.line2.setFont(QFont('Times',15))
        self.line3 = QLabel("Blue")
        self.line3.setFont(QFont('Times',15))
        self.table.setCellWidget(0, 1, self.line1)
        self.table.setCellWidget(1, 1, self.line2)
        self.table.setCellWidget(2, 1, self.line3)
        
        
        #stations(for blue line)
        self.train1_station = QComboBox()
        self.train1_station.addItems(['Station B', 'Station C', 'Yard'])
        self.train1_station.setFont(QFont('Times',15))
        self.train2_station = QComboBox()
        self.train2_station.addItems(['Station B', 'Station C', 'Yard'])
        self.train2_station.setFont(QFont('Times',15))
        self.train3_station = QComboBox()
        self.train3_station.addItems(['Station B', 'Station C', 'Yard'])
        self.train3_station.setFont(QFont('Times',15))
        
        self.table.setCellWidget(0,2, self.train1_station)
        self.table.setCellWidget(1,2, self.train2_station)
        self.table.setCellWidget(2,2, self.train3_station)

        
        #text boxes to edit train position
        self.train1_position = QTextEdit('0')
        self.train1_position.setFont(QFont('Times',15))
        self.train2_position = QTextEdit('0')
        self.train2_position.setFont(QFont('Times',15))
        self.train3_position = QTextEdit('0')
        self.train3_position.setFont(QFont('Times',15))
        
        self.table.setCellWidget(0, 3, self.train1_position)
        self.table.setCellWidget(1, 3, self.train2_position)
        self.table.setCellWidget(2, 3, self.train3_position)

       
       
        #place holders for authority 
        self.train1_authority = QLabel('---')
        self.train1_authority.setFont(QFont('Times',15))
        self.train2_authority = QLabel('---')
        self.train2_authority.setFont(QFont('Times',15))
        self.train3_authority = QLabel('---')
        self.train3_authority.setFont(QFont('Times',15))

        self.table.setCellWidget(0, 4, self.train1_authority)
        self.table.setCellWidget(1, 4, self.train2_authority)
        self.table.setCellWidget(2, 4, self.train3_authority)
       
       
        #place holders for commanded speed 
        self.train1_commanded_speed = QLabel('---')
        self.train1_commanded_speed.setFont(QFont('Times',15))
        self.train2_commanded_speed = QLabel('---')
        self.train2_commanded_speed.setFont(QFont('Times',15))
        self.train3_commanded_speed = QLabel('---')
        self.train3_commanded_speed.setFont(QFont('Times',15))

        self.table.setCellWidget(0, 5, self.train1_commanded_speed)
        self.table.setCellWidget(1, 5, self.train2_commanded_speed)
        self.table.setCellWidget(2, 5, self.train3_commanded_speed)
       
        #button to run test bench
        self.test = QPushButton("Run Test")
        self.test.setFixedSize(200,100)
        self.test.setStyleSheet("background-color : lime") 
        self.test.setFont(QFont('Times', 14))
        self.test.clicked.connect(self.run_test_bench)
       
       
        #aligning labels and text edit boxes 
        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(self.block_layout)
        self.window_layout.addWidget(self.title)
        self.window_layout.addWidget(self.direction)
        self.window_layout.addWidget(self.table)
        self.window_layout.addWidget(self.test)
        
        main_widget = QWidget()
        main_widget.setLayout(self.window_layout)
        self.setCentralWidget(main_widget)
        
        #enter in dispatch mode? 
        #show authority and commanded speed being enabled and disabled?
    
    def run_test_bench(self):
        x = MBOController() 
        
        x.enable_s_and_a = 1
        
        #send out positions 
        test_trains_positions = {"Train1": int(self.train1_position.toPlainText()), "Train2": int(self.train2_position.toPlainText()), "Train3": int(self.train3_position.toPlainText())}
        destinations = {"Train1" : str(self.train1_station.currentText()), "Train2" : str(self.train2_station.currentText()), "Train3": str(self.train3_station.currentText())}
        
        c =x.commanded_speed(x.enable_s_and_a)
        self.train1_commanded_speed.setText(str(c))
        self.train2_commanded_speed.setText(str(c))
        self.train3_commanded_speed.setText(str(c))
        
        x.emergency_breaking_distance()
        
        if (self.block_select.currentText() == 'None'):
            block = {}
        else:
            block = str(self.block_select.currentText())
        
        authorities = x.authority(test_trains_positions, destinations, block)
        
        self.train1_authority.setText(str(authorities['Train1']))
        self.train2_authority.setText(str(authorities['Train2']))
        self.train3_authority.setText(str(authorities['Train3']))
        

app = QApplication(sys.argv)

window = MBOWindow()
window.show()
app.exec()