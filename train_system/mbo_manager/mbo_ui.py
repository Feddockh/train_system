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
        self.vertical_layout = QVBoxLayout()

        self.vertical_layout.addWidget(self.MBO_mode_view_button)
        self.vertical_layout.addWidget(self.enter_label)
        self.vertical_layout.addWidget(self.schedule_date_time)
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
        selected_datetime = self.schedule_date_time.dateTime()
        self.schedule_created.emit(selected_datetime)
    
    #slot to disable MBO Mode View button (not clickable) when in fixed block mode

class MBOModeView(QMainWindow):
    def __init__(self):
        super(MBOModeView, self).__init__()
            #name window
        self.setWindowTitle("MBO Mode View")
        self.setFixedSize(1222, 702)
        
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Train ID", "Line", "Station", "Position", "Commanded Speed", "Authority"])

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_table(self, train_data):
        self.table_widget.setRowCount(len(train_data))
        for row, train in enumerate(train_data):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(train["train_id"])))
            self.table_widget.setItem(row, 1, QTableWidgetItem(train["line"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(train["station"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(train["position"])))
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(train["commanded_speed"])))
            self.table_widget.setItem(row, 5, QTableWidgetItem(str(train["authority"])))

app = QApplication(sys.argv)

window = MBOWindow()
window.show()
app.exec()


        

        