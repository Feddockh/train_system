from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import * 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from random import choice
from datetime import datetime
import sys


from PyQt6.QtWidgets import QWidget
from train_system.common.time_keeper import TimeKeeper
from train_system.common.time_keeper import TimeKeeperWidget
from train_system.common.line import Line
from train_system.common.gui_features import CustomTable
from train_system.mbo_manager.mbo_schedule import Schedules

class MBOWindow(QMainWindow):
    
    schedule_created = pyqtSignal(QDateTime, str, list, list)
    
    def __init__(self):
        super(MBOWindow, self).__init__()
        
        self.MBO_mode_window = None
        
        #name window
        self.setWindowTitle("MBO Planner")
        self.setFixedSize(1222, 702)
        
        #button to navigate to MBO mode view, see trains postitions, commanded speed and authority in real time? 
        self.MBO_mode_view_button = QPushButton('MBO Mode View', self)
        self.MBO_mode_view_button.setFixedSize(150,50)
        self.MBO_mode_view_button.setFont(QFont('Times', 12))
        self.MBO_mode_view_button.clicked.connect(self.open_MBO_mode_view)
        
        #lable to prompt/dircetion for user to enter date and time
        self.enter_label = QLabel('Please enter the date and time for the new schedules, then select the button.')
        self.enter_label.setFont(QFont('Times', 15))
        self.enter_label.setFixedHeight(50)
        
        #Creating calendar pop up to enter date and time
        self.schedule_date_time = QDateTimeEdit(datetime.now(),self)
        self.schedule_date_time.setFixedSize(400,50)
        self.schedule_date_time.setFont(QFont('Times', 15))
        self.schedule_date_time.setCalendarPopup(True)
        
        #create combo box to select train throughput for the given day 
        self.throughput_label = QLabel('Select the train throughput for the given day.')
        self.throughput_label.setFont(QFont('Times', 15))
        self.throughput_label.setFixedHeight(50)
        self.througput_options = ["Low", "Medium", "High"]
        self.train_throughput_selection = QComboBox()
        self.train_throughput_selection.setFixedSize(100,50)
        self.train_throughput_selection.setFont(QFont('Times', 12))
        self.train_throughput_selection.addItems(self.througput_options)
        
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Add checkable items to the layout
        self.green_checkboxes = []
        items = ["Glenbury 1", "Dormont 1", "Mt. Lebanon 1", "Poplar", "Castle Shannon", "Mt. Lebanon 2", "Dormont 2", "Glenbury 2", 
                 "Overbrook 1", "Inglewood", "Central 1", "Whited 1", "Edgebrook", "Pioneer", "Station", "Whited 2", "South Bank", 
                 "Central 2", "Overbrook 2" ]
        for item_text in items:
            green_checkbox = QCheckBox(item_text)
            self.green_checkboxes.append(green_checkbox)
            scroll_layout.addWidget(green_checkbox)
        
        
        scroll_area2 = QScrollArea()
        scroll_widget2 = QWidget()
        scroll_layout2 = QVBoxLayout(scroll_widget2)
        scroll_area2.setWidget(scroll_widget2)
        scroll_area2.setWidgetResizable(True)

        # Add checkable items to the layout
        self.green_checkboxes2 = []
        """items = ["Glenbury 1", "Dormont 1", "Mt. Lebanon 1", "Poplar", "Castle Shannon", "Mt. Lebanon 2", "Dormont 2", "Glenbury 2", 
                 "Overbrook 1", "Inglewood", "Central 1", "Whited 1", "Edgebrook", "Pioneer", "Station", "Whited 2", "South Bank", 
                 "Central 2", "Overbrook 2" ]"""
        
        for item_text in items:
            green_checkbox2 = QCheckBox(item_text)
            self.green_checkboxes2.append(green_checkbox2)
            scroll_layout2.addWidget(green_checkbox2)
        
        
        scroll_area3 = QScrollArea()
        scroll_widget3 = QWidget()
        scroll_layout3 = QVBoxLayout(scroll_widget3)
        scroll_area3.setWidget(scroll_widget3)
        scroll_area3.setWidgetResizable(True)

        # Add checkable items to the layout
        self.red_checkboxes = []
        items_red = ["Herron", "Swissville" ,"Penn Station", "Steel Plaza", "First Ave", "Station Square", "South Hills Junction", "Shadyside"]
        for item_text in items_red:
            red_checkbox = QCheckBox(item_text)
            self.red_checkboxes.append(red_checkbox)
            scroll_layout3.addWidget(red_checkbox)
        
        scroll_area4 = QScrollArea()
        scroll_widget4 = QWidget()
        scroll_layout4 = QVBoxLayout(scroll_widget4)
        scroll_area4.setWidget(scroll_widget4)
        scroll_area4.setWidgetResizable(True)

        # Add checkable items to the layout
        self.red_checkboxes2 = []
        for item_text in items_red:
            red_checkbox2 = QCheckBox(item_text)
            self.red_checkboxes2.append(red_checkbox2)
            scroll_layout4.addWidget(red_checkbox2)
        
        
        
        #Creat New Schedules Button, when clicked calls handle slot 
        self.create_schedules = QPushButton('Create New Schedules', self)
        self.create_schedules.setFixedSize(300,80)
        self.create_schedules.setFont(QFont('Times', 18))
        self.create_schedules.setStyleSheet("background-color : lime") 
        self.create_schedules.clicked.connect(self.handle_schedule)
        
        #page layout 
        self.select_label = QLabel("Please select the stations you would like the each schedule option to include")
        self.select_label.setFont(QFont('Times', 15))
        
        self.option1 = QLabel("Schedule Option 1")
        self.option1.setFont(QFont('Times', 11))
        self.option2 = QLabel("Schedule Option 2")
        self.option2.setFont(QFont('Times', 11))
        
        self.green_option1 = QLabel("Green Stations 1")
        self.green_option1.setFont(QFont('Times', 8))
        self.green_option2 = QLabel("Green Stations 2")
        self.green_option2.setFont(QFont('Times', 8))
        
        self.red_option1 = QLabel("Red Stations 1")
        self.red_option1.setFont(QFont('Times', 8))
        self.red_option2 = QLabel("Red Stations 2")
        self.red_option2.setFont(QFont('Times', 8))
        
        self.horizontal_layout_option = QHBoxLayout()
        self.horizontal_layout_option.addWidget(self.option1)
        self.horizontal_layout_option.addWidget(self.option2)
        
        self.line_layout_option = QHBoxLayout()
        self.line_layout_option.addWidget(self.green_option1)
        self.line_layout_option.addWidget(self.red_option1)
        self.line_layout_option.addWidget(self.green_option2)
        self.line_layout_option.addWidget(self.red_option2)
        
        self.horizontal_layout_scrolls = QHBoxLayout()
        self.horizontal_layout_scrolls.addWidget(scroll_area)
        self.horizontal_layout_scrolls.addWidget(scroll_area3)
        self.horizontal_layout_scrolls.addWidget(scroll_area2)
        self.horizontal_layout_scrolls.addWidget(scroll_area4)
        
        self.vertical_layout = QVBoxLayout()

        self.vertical_layout.addWidget(self.MBO_mode_view_button)
        self.vertical_layout.addWidget(self.enter_label)
        self.vertical_layout.addWidget(self.schedule_date_time)
        self.vertical_layout.addWidget(self.throughput_label)
        self.vertical_layout.addWidget(self.train_throughput_selection)
        self.vertical_layout.addWidget(self.select_label)
        self.vertical_layout.addLayout(self.horizontal_layout_option)
        self.vertical_layout.addLayout(self.line_layout_option)
        self.vertical_layout.addLayout(self.horizontal_layout_scrolls)
        self.vertical_layout.addWidget(self.create_schedules)
        
        main_widget = QWidget()
        main_widget.setLayout(self.vertical_layout)
        self.setCentralWidget(main_widget)

    #opening MBO mode view window
    def open_MBO_mode_view(self):
        if self.MBO_mode_window is None:
            self.MBO_mode_window = MBOModeView()
            self.MBO_mode_window.show()
        else:
            self.MBO_mode_window.close()
            self.MBO_mode_window = None
        
    @pyqtSlot()
    def handle_schedule(self) -> None:
        """
        emit date and start time selected 
        """   
        #checked stations for green line 
        checked_items = []
        checked_items2 = []
        
        #checked stations for red line
        checked_items3 = []
        checked_items4 = []
        
        for checkbox in self.green_checkboxes:
            if checkbox.isChecked():
                checked_items.append(checkbox.text())
        
        for checkbox2 in self.green_checkboxes2:
            if checkbox2.isChecked():
                checked_items2.append(checkbox2.text())
        
        for checkbox3 in self.red_checkboxes:
            if checkbox3.isChecked():
                checked_items3.append(checkbox3.text())
        
        for checkbox4 in self.red_checkboxes2:
            if checkbox4.isChecked():
                checked_items4.append(checkbox4.text())
                
        throughput = self.train_throughput_selection.currentText()
        selected_datetime = self.schedule_date_time.dateTime()
        schedules = Schedules()
        schedules.create_schedules_green(selected_datetime, throughput, checked_items, checked_items2)
        schedules.create_schedules_red(selected_datetime, throughput, checked_items3, checked_items4)
        #self.schedule_created.emit(selected_datetime, throughput, checked_items, checked_items2)
        
    
    #slot to disable MBO Mode View button (not clickable) when in fixed block mode

class MBOModeView(QMainWindow):
    def __init__(self):
        
        super(MBOModeView, self).__init__()
            #name window
        self.setWindowTitle("MBO Mode View")
        self.setFixedSize(1222, 702)
        
        
        self.title = QLabel('Current Commanded Speed and Authority')
        self.title.setFont(QFont('Times',12))
        
        self.test_bench_window = None
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
        
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.test_bench_view)
        self.main_layout.addWidget(self.table)
        
        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)
    

    def update_table(self, train_data):
        self.table_widget.setRowCount(len(train_data))
        for row, train in enumerate(train_data):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(train["train_id"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(train["line"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(train["station"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(train["position"])))
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(train["commanded_speed"])))
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(train["authority"])))

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
        self.line1 = QLabel("Green")
        self.line1.setFont(QFont('Times',15))
        self.line2 = QLabel("Green")
        self.line2.setFont(QFont('Times',15))
        self.line3 = QLabel("Green")
        self.line3.setFont(QFont('Times',15))
        self.table.setCellWidget(0, 1, self.line1)
        self.table.setCellWidget(1, 1, self.line2)
        self.table.setCellWidget(2, 1, self.line3)
        
        
        #stations(for blue line)
        self.train1_station = QComboBox()

        self.train1_station.addItems(['Glenbury', 'Dormont', 'Mt Lebanon', 'Poplar'])
        self.train1_station.setFont(QFont('Times',15))
        self.train2_station = QComboBox()
        self.train2_station.addItems(['Glenbury', 'Dormont', 'Mt Lebanon', 'Poplar'])
        self.train2_station.setFont(QFont('Times',15))
        self.train3_station = QComboBox()
        self.train3_station.addItems(['Glenbury', 'Dormont', 'Mt Lebanon', 'Poplar'])
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
        """will run a test for commanded speed and authority
        """
        



app = QApplication(sys.argv)

window = MBOWindow()
window.show()
app.exec()


        

        