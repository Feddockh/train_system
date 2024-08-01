from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import * 
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from random import choice
from datetime import datetime
import sys
from typing import List, Dict, Tuple

from PyQt6.QtWidgets import QWidget
from train_system.common.time_keeper import TimeKeeper
from train_system.common.time_keeper import TimeKeeperWidget
from train_system.common.line import Line
from train_system.common.gui_features import CustomTable
from train_system.mbo_manager.mbo_schedule import Schedules
from train_system.common.train_dispatch import TrainRouteUpdate
from train_system.mbo_manager.mbo_train_dispatch import MBOTrainDispatch
from train_system.mbo_manager.mbo_manager import MBOOffice

class TestBench(QMainWindow):
    def __init__(self, time_keeper: TimeKeeper, lines: List[Line], trains: Dict[Tuple[int, str], MBOTrainDispatch]):
        
        super(TestBench,self).__init__()
        
        self.mbo = MBOOffice(time_keeper)
        self.satellite = MBOOffice.Satellite()
        
        self.time_keeper = time_keeper
        
        self.timer_keeper_widget = TimeKeeperWidget(time_keeper)
        #label for page window 
        self.setWindowTitle("MBO Test Bench")
        self.setFixedSize(1222, 702)
        
        
        self.block_label = QLabel('Select a block to put under maint.')
        self.block_label.setFont(QFont('Times',12))
        self.block_label.setFixedSize(300,100)
        
        
        self.green_line = Line("Green")
        self.green_line.load_defaults()
        self.blocks_from_yard_to_yard = self.green_line.get_path(152, 152, 151)
        string_blocks = [str(block) for block in self.blocks_from_yard_to_yard]
        
        self.block_select = QComboBox()
        self.block_select.addItem('None')
        self.block_select.addItems(string_blocks)
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
        self.train1_id = QLabel("0")
        self.train1_id.setFont(QFont('Times',15))
        self.train2_id = QLabel("1")
        self.train2_id.setFont(QFont('Times',15))
        self.train3_id = QLabel("2")
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
        
        self.green_station_names = ['Yard', 'Glenbury 1', 'Dormont 1', 'Mt. Lebanon 1', 'Poplar', 'Castle Shannon', 'Mt. Lebanon 2', 'Dormont 2', 'Glenbury 2','Overbrook 1',
                                    'Inglewood', 'Central 1', 'Whited 1', 'Edgebrook', 'Pioneer', 'Station', 'Whited 2', 'South Bank', 'Central 2', 'Overbrook 2']
        
        self.train0_station = QComboBox()
        self.train0_station.addItems(self.green_station_names)
        self.train0_station.setFont(QFont('Times',15))
        self.train1_station = QComboBox()
        self.train1_station.addItems(self.green_station_names)
        self.train1_station.setFont(QFont('Times',15))
        self.train2_station = QComboBox()
        self.train2_station.addItems(self.green_station_names)
        self.train2_station.setFont(QFont('Times',15))
        
        self.table.setCellWidget(0,2, self.train0_station)
        self.table.setCellWidget(1,2, self.train1_station)
        self.table.setCellWidget(2,2, self.train2_station)

        #text boxes to edit train position
        self.train0_position = QTextEdit('0')
        self.train0_position.setFont(QFont('Times',15))
        self.train1_position = QTextEdit('0')
        self.train1_position.setFont(QFont('Times',15))
        self.train2_position = QTextEdit('0')
        self.train2_position.setFont(QFont('Times',15))
        
        self.table.setCellWidget(0, 3, self.train0_position)
        self.table.setCellWidget(1, 3, self.train1_position)
        self.table.setCellWidget(2, 3, self.train2_position)

        #place holders for authority 
        self.train0_authority = QLabel('---')
        self.train0_authority.setFont(QFont('Times',15))
        self.train1_authority = QLabel('---')
        self.train1_authority.setFont(QFont('Times',15))
        self.train2_authority = QLabel('---')
        self.train2_authority.setFont(QFont('Times',15))

        self.table.setCellWidget(0, 4, self.train0_authority)
        self.table.setCellWidget(1, 4, self.train1_authority)
        self.table.setCellWidget(2, 4, self.train2_authority)
       
       
        #place holders for commanded speed 
        self.train0_commanded_speed = QLabel('---')
        self.train0_commanded_speed.setFont(QFont('Times',15))
        self.train1_commanded_speed = QLabel('---')
        self.train1_commanded_speed.setFont(QFont('Times',15))
        self.train2_commanded_speed = QLabel('---')
        self.train2_commanded_speed.setFont(QFont('Times',15))

        self.table.setCellWidget(0, 5, self.train0_commanded_speed)
        self.table.setCellWidget(1, 5, self.train1_commanded_speed)
        self.table.setCellWidget(2, 5, self.train2_commanded_speed)
       
        #button to run test bench
        self.test = QPushButton("Run Test")
        self.test.setFixedSize(200,100)
        self.test.setStyleSheet("background-color : lime") 
        self.test.setFont(QFont('Times', 14))
        self.test.clicked.connect(self.run_test_bench)
       
       
        #aligning labels and text edit boxes 
        self.window_layout = QVBoxLayout()
        self.window_layout.addWidget(self.timer_keeper_widget)
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
        """ 
            Running test bench with information the user input 
        """

        self.station_blocks_green = {'Yard': 152, 'from_yard' : 153, 'Glenbury 1': 65, 'Dormont 1': 73, 'Mt. Lebanon 1': 77,
                                    'Poplar': 88, 'Castle Shannon': 96, 'Mt. Lebanon 2' : 77, 'Dormont 2' : 105, 'Glenbury 2' : 114,'Overbrook 1': 123,
                                    'Inglewood': 132, 'Central 1': 141, 'Whited 1' : 22, 'Edgebrook': 9,
                                    'Pioneer': 2, 'Station': 16, 'Whited 2': 22,
                                    'South Bank': 31, 'Central 2' : 39, 'Overbrook 2' : 57, 'past_yard': 62, 'to_yard': 151}
        
        
        train_0 = MBOTrainDispatch(self.time_keeper, 0, self.green_line)
        train_1 = MBOTrainDispatch(self.time_keeper, 1, self.green_line)
        train_2 = MBOTrainDispatch(self.time_keeper, 2, self.green_line)
      
    
        
        print("inital train 0 position ", train_0.position)
        #float entered by user
        train_0.position = int(self.train0_position.toPlainText())
        print("updated train 0 position ", train_0.position)
        
        route = self.green_line.get_path(152, 152, 151)
        
        train_0_block = []
        for blocks in route:
            train_0_block.append(blocks)
            length = self.green_line.get_path_length(train_0_block)
            if length > train_0.position:
                num_blocks = len(train_0_block)
                train_0.current_block = train_0_block[num_blocks-1]
                break
                
        print("train 0 is in track block ", train_0.current_block)
        train_0_destination = self.station_blocks_green[str(self.train0_station.currentText())]
        print("train 0 destination block ", train_0_destination  )
        print("")
        
        print("inital train 1 position ", train_1.position)        
        #float entered by user
        train_1.position = int(self.train1_position.toPlainText())
        print("updated train position ", train_1.position)
        train_1_block = []
        for blocks in route:
            train_1_block.append(blocks)
            length = self.green_line.get_path_length(train_1_block)
            if length > train_1.position:
                num_blocks = len(train_1_block)
                train_1.current_block = train_1_block[num_blocks-1]
                break
        print("train 1 is in track block", train_1.current_block)
        train_1_destination = self.station_blocks_green[str(self.train1_station.currentText())]
        print("train 1 destination block ", train_1_destination  )
        print("")
        
        
        print("inital train 2 position ", train_2.position)
        #float entered by user
        train_2.position = int(self.train2_position.toPlainText())
        print("updated train 2 position ", train_2.position)
        train_2_block = []
        for blocks in route:
            train_2_block.append(blocks)
            length = self.green_line.get_path_length(train_2_block)
            if length > train_2.position:
                num_blocks = len(train_2_block)
                train_2.current_block = train_2_block[num_blocks-1]
                break
        print("train 2 is in track block", train_2.current_block)
        train_2_destination = self.station_blocks_green[str(self.train2_station.currentText())]
        print("train 2 destination block ", train_2_destination  )
        print("")
        
        
        train_0.velocity = self.mbo.compute_commanded_speed(train_0.current_block)
        train_1.velocity = self.mbo.compute_commanded_speed(train_1.current_block)
        train_2.velocity = self.mbo.compute_commanded_speed(train_2.current_block) 
        
        check_0 = [train_1.position, train_2.position]
        check_1 = [train_0.position, train_2.position]
        check_2 = [train_0.position, train_1.position]
        
        train_0_authority = self.mbo.test_authority(0, train_0.position, train_0.velocity, train_0.current_block, train_0_destination, check_0)
        train_1_authority = self.mbo.test_authority(0, train_1.position, train_1.velocity, train_1.current_block, train_1_destination, check_1)
        train_2_authority = self.mbo.test_authority(0, train_2.position, train_2.velocity, train_2.current_block, train_2_destination, check_2)
        
        
        self.train0_commanded_speed.setText(str(train_0.velocity))
        self.train1_commanded_speed.setText(str(train_1.velocity))
        self.train2_commanded_speed.setText(str(train_2.velocity))
        
        self.train0_authority.setText(str(train_0_authority))
        self.train1_authority.setText(str(train_1_authority))
        self.train2_authority.setText(str(train_2_authority))
        #station = destination block for the train 
        
        #create line object? if block is under maint. update it in my line object? 
        
        #use this line object to find unobstructed path to stop 
        #send this as init authority and assume train is leaving from the yard?? 
            #yard to destination to yard?
        
        #assume each tick the train is moving for 1 sec at its set commanded speed and send this back encrypted 
        #print encrypted value 
        #show decrypt on UI
    
        
        



if __name__ == '__main__':
    app = QApplication(sys.argv)

    time_keeper = TimeKeeper()
    time_keeper.start_timer()

    lines = []

    green_line = Line("Green")
    green_line.load_defaults()
    lines.append(green_line)

    red_line = Line("Red")
    red_line.load_defaults()
    lines.append(red_line)

    trains = {}

    widget = TestBench(time_keeper, lines, trains)
    widget.show()
    sys.exit(app.exec())