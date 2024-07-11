import os
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6 import QtCore, QtGui, QtWidgets, uic, QtWidgets
from train_system.track_controller.sw_track_controller import TrackController
from train_system.common.crossing_signal import CrossingSignal

#Colors
DARK_GREY = "#C8C8C8"
WHITE = "#FFFFFF"
RED = "#FF0000"
GREEN = "#00FF00"


class CenterDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignCenter

class CrossingSignalWidget(QTableWidgetItem):
    def __init__(self, text='', background_color=None):
        super().__init__(text)
        if background_color:
            self.setBackground(QtGui.QColor(background_color))
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)

class Rectangle(QWidget):

    def __init__(self, x, y, width, height, color, parent=None):
        super().__init__(parent)
        self.setGeometry(x, y, width, height)
        self.color = color

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        pen = QtGui.QPen()
        pen.setWidth(0)

        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(self.color))
        brush.setStyle(Qt.BrushStyle.Dense4Pattern)

        painter.setPen(pen)
        painter.setBrush(brush)
        rect = QRect(0, 0, self.width() - 1, self.height() - 1)
        painter.drawRect(rect)


"""
Programmer UI - Default Page
"""
class ProgrammerUI(QtWidgets.QMainWindow):

    #def setupUi(self, MainWindow):
    def __init__(self, track_controllers):
        super().__init__()

        #Setting track controller
        self.track_controllers = track_controllers

        #Programmer UI name & size
        self.setObjectName("Programmer UI")
        self.resize(1222, 702)

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)


        '''
        
        Central Time here
        
        '''
        #Creating a timer to update UI - updates every 3 seconds
        if(~self.isHidden()):
            self.timer = QTimer(self)
            
            #self.timer.timeout.connect(self.update_ui)
            self.timer.start(3000)

        #Used in multiple widgets
        waysides = [track_controllers[0].wayside_name, track_controllers[1].wayside_name, track_controllers[2].wayside_name,track_controllers[3].wayside_name, track_controllers[4].wayside_name]
        lines = ['Green Line', 'Red Line']
        
        #Creating universal font
        font = QtGui.QFont()
        font.setPointSize(15)

        #FileUpload button
        self.fileUploadPushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.fileUploadPushButton.setGeometry(QtCore.QRect(720, 100, 135, 40))
        self.fileUploadPushButton.setObjectName("pushButton")
        self.fileUploadPushButton.clicked.connect(self.getFileName)
        self.fileUploadPushButton.setFont(font)

        #Select PLC Program label
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(530, 100, 180, 40))
        self.label.setObjectName("label")
        self.label.setFont(font)

        #PLC Program uploaded label
        self.plcUploadedLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.plcUploadedLabel.setGeometry(QtCore.QRect(900, 100, 220, 40))
        self.label.setObjectName("plcUploadedLabel")
        self.plcUploadedLabel.setFont(font)
        self.plcUploadedLabel.setVisible(False)

        #Combobox for wayside selection
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(520, 35, 640, 35))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(waysides)
        self.comboBox.setFont(font)

        #Getting current combo box index
        waysideIndex = self.comboBox.currentIndex()

        #Create Rectangle for wayside selection
        self.waysideRec = Rectangle(520, 30, 640, 50, DARK_GREY, self.centralwidget)
        self.waysideRec.lower()
        self.backWaysideBlkRec = Rectangle(520, 80, 640, 80, WHITE, self.centralwidget)
        self.backWaysideBlkRec.lower()

        #Waysides and responsible blocks combo
        self.comboBox_3 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(60, 35, 415, 35))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItems(lines)
        self.comboBox_3.setFont(font)

        #Getting line index
        lineIndex = self.comboBox_3.currentIndex()

        #Create Rectangle for Waysides and responsible blocks rectangles
        self.waysideRec = Rectangle(60, 30, 415, 50, DARK_GREY, self.centralwidget)
        self.waysideRec.lower()
        self.backWaysideBlkRec = Rectangle(60, 80, 415, 130, WHITE, self.centralwidget)
        self.backWaysideBlkRec.lower()

        #Waysides and Blocks their responsible for table
        self.waysideBlkTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.waysideBlkTable.setGeometry(QtCore.QRect(60, 80, 415, 130))
        self.waysideBlkTable.setObjectName("waysideBlkTable")
        self.waysideBlkTable.setColumnCount(2)
        self.waysideBlkTable.setRowCount(3)

        self.waysideBlkTable.verticalHeader().setVisible(False)
        self.waysideBlkTable.setItemDelegate(CenterDelegate(self.waysideBlkTable))

        self.waysideBlkTable.setHorizontalHeaderLabels(['Waysides', 'Blocks'])
        self.waysideBlkTable.horizontalHeader().setFont(font)
        self.waysideBlkTable.setColumnWidth(0, 207)
        self.waysideBlkTable.setColumnWidth(1, 206)
        
        self.add_wayside_blk_table_data(lineIndex)
        self.waysideBlkTable.setFont(font)

        #Block info rec
        self.blockInfoRec = Rectangle(60, 270, 1100, 60, DARK_GREY, self.centralwidget)
        self.blockInfoRec.lower()
        self.backBlockInfoRec = Rectangle(60, 330, 1100, 320, WHITE, self.centralwidget)
        self.backBlockInfoRec.lower()

        #Block info table
        self.blockInfoTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.blockInfoTable.setGeometry(QtCore.QRect(60, 330, 1100, 320))
        self.blockInfoTable.setObjectName("blockInfoTable")
        self.blockInfoTable.setColumnCount(7)
        self.blockInfoTable.setRowCount(len(self.track_controllers[0].track_blocks))
        self.blockInfoTable.setColumnWidth(0, 155)
        self.blockInfoTable.setColumnWidth(1, 155)
        self.blockInfoTable.setColumnWidth(2, 155)
        self.blockInfoTable.setColumnWidth(3, 155)
        self.blockInfoTable.setColumnWidth(4, 155)
        self.blockInfoTable.setColumnWidth(5, 155)
        self.blockInfoTable.setColumnWidth(6, 155)

        self.blockInfoTable.verticalHeader().setVisible(False)
        self.blockInfoTable.setFont(font)
        self.blockInfoTable.setHorizontalHeaderLabels(['Block #', 'Occupancy', 'Authority[ft]', 'Speed[mph]','Switch','Signal','Crossing'])
        self.blockInfoTable.horizontalHeader().setFont(font)
        self.add_block_info_table_data(waysideIndex)

        #Search box for block info table
        self.textEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.textEdit.setPlaceholderText("Search Block #")
        self.textEdit.setGeometry(QtCore.QRect(495, 280, 220, 40))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setFont(font)

        #Go to Test Bench button
        self.testBenchBtn = QPushButton("Test Bench", self.centralwidget)
        self.testBenchBtn.clicked.connect(self.open_test_bench)
        self.testBenchBtn.setGeometry(QtCore.QRect(520, 190, 145, 50))
        self.testBenchBtn.setFont(font)

        #Go to Maintenance button
        self.testBenchBtn = QPushButton("Maintenance", self.centralwidget)
        self.testBenchBtn.clicked.connect(self.open_maintenance)
        self.testBenchBtn.setGeometry(QtCore.QRect(710, 190, 145, 50))
        self.testBenchBtn.setFont(font)

        #Updating comboboxes
        self.comboBox.currentIndexChanged.connect(lambda: self.update_ui())
        self.comboBox_3.currentIndexChanged.connect(lambda: self.update_ui())
        self.textEdit.textChanged.connect(self.filter_table)

        #Setting central widget
        self.setCentralWidget(self.centralwidget)

        #Menubar code
        self.menubar = QtWidgets.QMenuBar(parent=self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 855, 26))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("ProgrammerUI", "ProgrammerUI"))
        self.fileUploadPushButton.setText(_translate("ProgrammerUI", "Upload File"))
        self.label.setText(_translate("ProgrammerUI", "Select PLC Program:"))
        self.plcUploadedLabel.setText(_translate("ProgrammerUI", "PLC program uploaded."))

    #Updates UI values to reflect backend changes
    def update_ui(self):
        lineIndex = self.comboBox_3.currentIndex()
        waysideIndex = self.comboBox.currentIndex()
        #self.track_controller.run_PLC_program()
        self.add_wayside_blk_table_data(lineIndex)
        self.add_block_info_table_data(waysideIndex)
        self.display_plc_uploaded(waysideIndex)

    #Allows User to select PLC Program from directory
    def getFileName(self):    
        waysideIndex = self.comboBox.currentIndex()
        file_filter = 'Data File (*.py)'
        response = QFileDialog.getOpenFileName (
            parent = self,
            caption = 'Select a file',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Data File (*.py)'
        )
        self.track_controllers[waysideIndex].get_PLC_program(response[0])

        if(self.track_controllers[waysideIndex].plc_program_uploaded == True and self.track_controllers[waysideIndex].plc_program != ""):
            self.plcUploadedLabel.setVisible(True)
        else:
            self.plcUploadedLabel.setVisible(False)
    
    #Using search box to filter table data
    def filter_table(self):
        filter_text = self.textEdit.text().strip().lower()
        for row in range(self.blockInfoTable.rowCount()):
            item = self.blockInfoTable.item(row, 0)
            if item is not None and filter_text in item.text().strip().lower():
                self.blockInfoTable.setRowHidden(row, False)
            else:
                self.blockInfoTable.setRowHidden(row, True)

    #Converts track_occupancies into "occupied/in operation"
    def display_occupied_tracks(self, i, waysideIndex):
        if (self.track_controllers[waysideIndex].track_blocks[i]._occupancy == False):
            return "Not Occupied"
        else:
            return "Occupied"

    #displays whether or not the plc has been uploaded
    def display_plc_uploaded(self, waysideIndex):
        self.plcUploadedLabel.setVisible(False)
        if(self.track_controllers[waysideIndex].plc_program_uploaded == True and self.track_controllers[waysideIndex].plc_program != ""):
            self.plcUploadedLabel.setVisible(True)

    #adds block info table data
    def add_block_info_table_data(self, waysideIndex):
        self.blockInfoTable.clearContents()
        self.blockInfoTable.setRowCount(len(self.track_controllers[waysideIndex].track_blocks))

        data = []
        for x in range(self.track_controllers[waysideIndex].numBlocks):
            tempData = [self.track_controllers[waysideIndex].track_blocks[x].number, 
                        self.display_occupied_tracks(x, waysideIndex), 
                        self.track_controllers[waysideIndex].track_blocks[x].authority, 
                        self.track_controllers[waysideIndex].track_blocks[x].suggested_speed, 
                        " ", " "]
            tempData.append(self.display_crossing_signal(x, waysideIndex))
            data.append(tempData)

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QtWidgets.QTableWidgetItem(str(item))
                self.blockInfoTable.setItem(i, j, text)
                text.setFlags(text.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        #Method to print light signal statuses
        for x in range(self.track_controllers[waysideIndex].numBlocks):
            self.display_switch_pos(x, waysideIndex)
            self.display_light_signal(x, waysideIndex)

    #Converts switch_states into values they're connected to 
    def display_switch_pos(self, x, waysideIndex):
        
        #if there is a switch that exists at this block
        if(self.track_controllers[waysideIndex].track_blocks[x]._switch_position != None):
            pos = self.track_controllers[waysideIndex].track_blocks[x]._switch_position
            item = self.track_controllers[waysideIndex].track_blocks[x].switch_options[pos]

            #for other block not connected to switch
            if(pos == 0):
                otherPos = 1
            else:
                otherPos = 0
            otherItem = self.track_controllers[waysideIndex].track_blocks[x].switch_options[otherPos]

            #updating block connected to switch
            for i in range(self.track_controllers[waysideIndex].numBlocks):
                if(self.track_controllers[waysideIndex].track_blocks[i].number == item):
                    block = QTableWidgetItem(str(self.track_controllers[waysideIndex].track_blocks[x].number))
                    block.setFlags(block.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.blockInfoTable.setItem(i, 4, block)
                if(self.track_controllers[waysideIndex].track_blocks[i].number == otherItem):
                    block = QTableWidgetItem("-")
                    block.setFlags(block.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.blockInfoTable.setItem(i, 4, block)
            block = QTableWidgetItem(str(item))
            block.setFlags(block.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.blockInfoTable.setItem(x, 4, block)
        elif(self.track_controllers[waysideIndex].track_blocks[x].switch_options == None):
            block = QTableWidgetItem("-")
            block.setFlags(block.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.blockInfoTable.setItem(x, 4, block)

        self.blockInfoTable.viewport().update()
    
    def display_light_signal(self, x, waysideIndex):
        #If light signal is red or green
        if(self.track_controllers[waysideIndex].track_blocks[x]._light_signal == True):
            self.blockInfoTable.setItem(x, 5, CrossingSignalWidget("", GREEN))
        elif(self.track_controllers[waysideIndex].track_blocks[x]._light_signal == False):
            self.blockInfoTable.setItem(x, 5, CrossingSignalWidget("", RED))
        else:
            self.blockInfoTable.setItem(x, 5, CrossingSignalWidget("", WHITE))

        self.blockInfoTable.viewport().update()

    #Displays crossing signals
    def display_crossing_signal(self, x, waysideIndex):
        if (self.track_controllers[waysideIndex].track_blocks[x].crossing_signal == CrossingSignal.ON):
            return "Up"
        elif(self.track_controllers[waysideIndex].track_blocks[x].crossing_signal == CrossingSignal.OFF):
            return "Down"
        else:
            return "-"

    #Adds info about waysides and the blocks they're responsible for
    def add_wayside_blk_table_data(self, lineIndex):

        if (lineIndex == 0):
            data = [
                ['Wayside 1', '1 - 32, 150'],
                ['Wayside 2', '29 - 85, 101 - 150'],
                ['Wayside 3', '74 - 101']
            ]
        elif (lineIndex == 1):
            data = [
                ['Wayside 4', '1 - 23, 73 - 76'], 
                ['Wayside 5', '24 - 45, 68 - 75'],
                ['Wayside 6', '24 - 68']
            ]

        self.waysideBlkTable.clearContents()
        self.waysideBlkTable.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QTableWidgetItem(item)
                text.setFlags(text.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.waysideBlkTable.setItem(i, j, text)

    #Opens test bench
    def open_test_bench(self):
        self.test_bench = TestBench(self.track_controllers, self)
        self.test_bench.show()
        self.hide()

    #Opens maintenance 
    def open_maintenance(self):
        self.track_controllers[0].plc_program_uploaded = False
        self.track_controllers[0].plc_program = ""
        self.maintenance = Maintenance(self.track_controller[0],self)
        self.maintenance.show()
        self.hide()


"""
Test Bench UI - Can be brought here by selecting test bench from Programmer UI
"""
class TestBench(QtWidgets.QMainWindow):

    #def setupUi(self, MainWindow):
    def __init__(self, track_controllers, programmer_ui):
        super().__init__()

        #Programmer UI name & size
        self.setObjectName("Test Bench")
        self.resize(1222, 702)
        self.programmer_ui = programmer_ui

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        #Used in multiple widgets
        waysides = [track_controllers[0].wayside_name, track_controllers[1].wayside_name, track_controllers[2].wayside_name,track_controllers[3].wayside_name, track_controllers[4].wayside_name]
        lines = ['Green Line', 'Red Line']

        #Creating universal font
        font = QtGui.QFont()
        font.setPointSize(15)

        #FileUpload button
        self.fileUploadPushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.fileUploadPushButton.setGeometry(QtCore.QRect(720, 100, 135, 40))
        self.fileUploadPushButton.setObjectName("pushButton")
        self.fileUploadPushButton.clicked.connect(self.getFileName)
        self.fileUploadPushButton.setFont(font)

        #Select PLC Program label
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(530, 100, 180, 40))
        self.label.setObjectName("label")
        self.label.setFont(font)

        #End Test Bench button
        self.testBenchBtn = QPushButton("Test Bench", self.centralwidget)
        self.testBenchBtn.clicked.connect(self.open_programmer_ui)
        self.testBenchBtn.setGeometry(QtCore.QRect(520, 190, 145, 50))
        self.testBenchBtn.setFont(font)
        self.testBenchBtn.setStyleSheet("""
        QPushButton {
            background-color: #FF0000;
        }
        """)

        #Combobox for wayside selection
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(520, 35, 640, 35))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(waysides)
        self.comboBox.setFont(font)

        #Getting current combo box index
        waysideIndex = self.comboBox.currentIndex()

        #Create Rectangle for wayside selection
        self.waysideRec = Rectangle(520, 30, 640, 50, DARK_GREY, self.centralwidget)
        self.waysideRec.lower()
        self.backWaysideBlkRec = Rectangle(520, 80, 640, 80, WHITE, self.centralwidget)
        self.backWaysideBlkRec.lower()

        #Waysides and responsible blocks combo
        self.comboBox_3 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(60, 35, 415, 35))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItems(lines)
        self.comboBox_3.setFont(font)

        #Getting line index
        lineIndex = self.comboBox_3.currentIndex()

        #Create Rectangle for Waysides and responsible blocks rectangles
        self.waysideRec = Rectangle(60, 30, 415, 50, DARK_GREY, self.centralwidget)
        self.waysideRec.lower()
        self.backWaysideBlkRec = Rectangle(60, 80, 415, 130, WHITE, self.centralwidget)
        self.backWaysideBlkRec.lower()

        #Waysides and Blocks their responsible for table
        self.waysideBlkTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.waysideBlkTable.setGeometry(QtCore.QRect(60, 80, 415, 130))
        self.waysideBlkTable.setObjectName("waysideBlkTable")
        self.waysideBlkTable.setColumnCount(2)
        self.waysideBlkTable.setRowCount(3)

        self.waysideBlkTable.verticalHeader().setVisible(False)
        self.waysideBlkTable.setItemDelegate(CenterDelegate(self.waysideBlkTable))

        self.waysideBlkTable.setHorizontalHeaderLabels(['Waysides', 'Blocks'])
        self.waysideBlkTable.horizontalHeader().setFont(font)
        self.waysideBlkTable.setColumnWidth(0, 207)
        self.waysideBlkTable.setColumnWidth(1, 206)
        
        self.add_wayside_blk_table_data(lineIndex)
        self.waysideBlkTable.setFont(font)

        #Updating comboboxes
        #self.comboBox.currentIndexChanged.connect(lambda: self.update_ui())
        self.comboBox_3.currentIndexChanged.connect(lambda: self.update_ui())

        """
        #Block info rec
        self.blockInfoRec = Rectangle(470, 220, 715, 110, DARK_GREY, self.centralwidget)
        self.blockInfoRec.lower()
        self.backBlockInfoRec = Rectangle(470, 330, 715, 320, WHITE, self.centralwidget)
        self.backBlockInfoRec.lower()

        #Block info table
        self.blockInfoTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.blockInfoTable.setGeometry(QtCore.QRect(470, 330, 715, 320))
        self.blockInfoTable.setObjectName("blockInfoTable")
        self.blockInfoTable.setColumnCount(7)
        self.blockInfoTable.setRowCount(len(self.track_controllerTest.track_occupancies))
        self.blockInfoTable.setColumnWidth(1, 120)
        self.blockInfoTable.setColumnWidth(5, 84)

        self.blockInfoTable.verticalHeader().setVisible(False)
        #self.blockInfoTable.setItemDelegate(CenterDelegate(self.tableView))
        self.blockInfoTable.setFont(font)
        self.blockInfoTable.setHorizontalHeaderLabels(['Block #', 'Occupancy', 'Authority[ft]', 'Speed[mph]','Switch','Signal','Crossing'])
        self.blockInfoTable.horizontalHeader().setFont(font)
        self.add_block_info_table_data()

        #Handling updates to block info table
        self.blockInfoTable.itemChanged.connect(self.item_changed_blockInfo)

        #Combobox for block info table
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(540, 230, 575, 35))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(lines)
        self.comboBox.setFont(font)

        #TextEdit box for block info table
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(735, 270, 200, 40))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setFont(font)
        """
        #Updating comboboxes
        self.comboBox.currentIndexChanged.connect(lambda: self.update_ui())
        self.comboBox_3.currentIndexChanged.connect(lambda: self.update_ui())

        #Setting central widget
        self.setCentralWidget(self.centralwidget)

        #Menubar code
        self.menubar = QtWidgets.QMenuBar(parent=self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 855, 26))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("TestBench", "Testbench"))
        self.fileUploadPushButton.setText(_translate("TestBench", "Upload File"))
        self.label.setText(_translate("TestBench", "Select PLC Program:"))
        #self.plcUploadedLabel.setText(_translate("ProgrammerUI", "PLC program uploaded."))

    #Updates UI values to reflect backend changes
    def update_ui(self):
        lineIndex = self.comboBox_3.currentIndex()
        waysideIndex = self.comboBox.currentIndex()
        #self.track_controller.run_PLC_program()
        self.add_wayside_blk_table_data(lineIndex)
        #self.add_block_info_table_data(waysideIndex)
        #self.display_plc_uploaded(waysideIndex)

    """
    #Updates UI values to reflect backend changes
    def update_ui(self):
        self.blockInfoTable.itemChanged.disconnect(self.item_changed_blockInfo)
        self.tableView.itemChanged.disconnect(self.item_changed_waysideData)
        if(self.track_controllerTest.plc_program != ""):
            self.track_controllerTest.run_PLC_program()
        self.add_wayside_table_data()
        self.add_wayside_blk_table_data()
        self.add_block_info_table_data()
        self.blockInfoTable.itemChanged.connect(self.item_changed_blockInfo)
        self.tableView.itemChanged.connect(self.item_changed_waysideData)
    """

    #Allows User to select PLC Program from directory
    def getFileName(self):    
        file_filter = 'Data File (*.py)'
        response = QFileDialog.getOpenFileName (
            parent = self,
            caption = 'Select a file',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Data File (*.py)'
        )
        self.track_controllerTest.get_PLC_program(response[0])

        if(self.track_controllerTest.plc_program_uploaded == True and self.track_controllerTest.plc_program != ""):
            self.plcUploadedLabel.setVisible(True)
        else:
            self.plcUploadedLabel.setVisible(False)

    
    def add_wayside_blk_table_data(self, lineIndex):

        if (lineIndex == 0):
            data = [
                ['Wayside 1', '1 - 32, 150'],
                ['Wayside 2', '29 - 85, 101 - 150'],
                ['Wayside 3', '74 - 101']
            ]
        elif (lineIndex == 1):
            data = [
                ['Wayside 4', '1 - 23, 73 - 76'], 
                ['Wayside 5', '24 - 45, 68 - 75'],
                ['Wayside 6', '24 - 68']
            ]

        self.waysideBlkTable.clearContents()
        self.waysideBlkTable.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QTableWidgetItem(item)
                text.setFlags(text.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.waysideBlkTable.setItem(i, j, text)


    """
    def item_changed_blockInfo(self, item):
        row = item.row()
        column = item.column()
        new_item = item.text()

        match column:
            #Occupancy
            case 1:
                if (new_item == "Occupied"):
                    self.track_controllerTest.track_occupancies[row] = True
                else:
                    self.track_controllerTest.track_occupancies[row] = False
            #Authority
            case 2:
                self.track_controllerTest.train_authorities[row] = new_item
            #Speed
            case 3:
                self.track_controllerTest.train_speeds[row] = new_item
            #Switch
            case _:
                #Update Switches
                #Signal
                print("")
        self.update_ui()
      
    def item_changed_waysideData(self, item):
        row = item.row()
        column = item.column()
        new_item = item.text()

        match column:
            #Occupancy
            case 1:
                if (new_item == "Occupied"):
                    self.track_controllerTest.track_occupancies[row] = True
                else:
                    self.track_controllerTest.track_occupancies[row] = False
            #Switch
            case 2:
                value = self.track_controllerTest.switch_states
                #if making switch to 11
                if(new_item == "5" and row == 10):
                    self.track_controllerTest.switch_states = True
                    value = self.track_controllerTest.switch_states
                elif(new_item == "5" and row == 5):
                    self.track_controllerTest.switch_states = False
                    value = self.track_controllerTest.switch_states
                elif(new_item == "6" and row == 4):
                    self.track_controllerTest.switch_states = False
                    value = self.track_controllerTest.switch_states
                elif(new_item == "11" and row == 4):
                    self.track_controllerTest.switch_states = True
                    value = self.track_controllerTest.switch_states
                else:
                    print("Not valid switch")
            #Signal
            case 3:
                print("")
        self.update_ui()


    #Converts track_occupancies into "occupied/in operation"
    def display_occupied_tracks(self, i):
        if (self.track_controllerTest.track_occupancies[i] == False):
            return "In Operation"
        else:
            return "Occupied"
    
    #Converts switch_states into values they're connected to 
    def display_switch_pos(self, i):
        if(self.track_controllerTest.switch_states == False and i == 5):
            return "6"
        elif(self.track_controllerTest.switch_states == False and i == 6):
            return "5"
        elif(self.track_controllerTest.switch_states == False and i == 11):
            return "-"
        elif(self.track_controllerTest.switch_states == True and i == 5):
            return "11"
        elif(self.track_controllerTest.switch_states == True and i == 6):
            return "-"
        else:
            return "5"

    #Adds data to wayside table
    def add_wayside_table_data(self):
        data = [
            ['1', self.display_occupied_tracks(0), '-', '-'],
            ['2', self.display_occupied_tracks(1), '-', '-'],
            ['3', self.display_occupied_tracks(2), '-', '-'],
            ['4', self.display_occupied_tracks(3), '-', '-'],
            ['5', self.display_occupied_tracks(4), self.display_switch_pos(5), '-'],
            ['6', self.display_occupied_tracks(5), self.display_switch_pos(6), '-'],
            ['7', self.display_occupied_tracks(6), '-', '-'],
            ['8', self.display_occupied_tracks(7), '-', '-'],
            ['9', self.display_occupied_tracks(8), '-', '-'],
            ['10', self.display_occupied_tracks(9), '-', '-'],
            ['11', self.display_occupied_tracks(10), self.display_switch_pos(11), '-'],
            ['12', self.display_occupied_tracks(11), '-', '-'],
            ['13', self.display_occupied_tracks(12), '-', '-'],
            ['14', self.display_occupied_tracks(13), '-', '-'],
            ['15', self.display_occupied_tracks(14), '-', '-']
        ]
        
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.tableView.setItem(i, j, QtWidgets.QTableWidgetItem(str(item))) 
        
        #If light is red/green
        if(self.track_controllerTest.signal_states == False):
            self.tableView.setItem(4, 3, CrossingSignal('', GREEN))
        else:
            self.tableView.setItem(4, 3, CrossingSignal('', RED))

    def add_block_info_table_data(self):
        data = [
            ['1', self.display_occupied_tracks(0), self.track_controllerTest.train_authorities[0], self.track_controllerTest.train_speeds[0] , '-', '-', '-'],
            ['2', self.display_occupied_tracks(1), self.track_controllerTest.train_authorities[1], self.track_controllerTest.train_speeds[1],'-', '-', '-'],
            ['3', self.display_occupied_tracks(2), self.track_controllerTest.train_authorities[2], self.track_controllerTest.train_speeds[2],'-', '-', '-'],
            ['4', self.display_occupied_tracks(3), self.track_controllerTest.train_authorities[3], self.track_controllerTest.train_speeds[3],'-', '-' ,'-'],
            ['5', self.display_occupied_tracks(4), self.track_controllerTest.train_authorities[4], self.track_controllerTest.train_speeds[4],self.display_switch_pos(5), ' ', '-'],
            ['6', self.display_occupied_tracks(5), self.track_controllerTest.train_authorities[5], self.track_controllerTest.train_speeds[5],self.display_switch_pos(6), '-', '-'],
            ['7', self.display_occupied_tracks(6), self.track_controllerTest.train_authorities[6], self.track_controllerTest.train_speeds[6],'-', '-', '-'],
            ['8', self.display_occupied_tracks(7), self.track_controllerTest.train_authorities[7], self.track_controllerTest.train_speeds[7],'-', '-', self.display_crossing_signal()],
            ['9', self.display_occupied_tracks(8), self.track_controllerTest.train_authorities[8], self.track_controllerTest.train_speeds[8],'-', '-', '-'],
            ['10', self.display_occupied_tracks(9), self.track_controllerTest.train_authorities[9], self.track_controllerTest.train_speeds[9],'-', '-','-'],
            ['11', self.display_occupied_tracks(10), self.track_controllerTest.train_authorities[10], self.track_controllerTest.train_speeds[10],self.display_switch_pos(11), '-','-'],
            ['12', self.display_occupied_tracks(11), self.track_controllerTest.train_authorities[11], self.track_controllerTest.train_speeds[11],'-', '-', '-'],
            ['13', self.display_occupied_tracks(12), self.track_controllerTest.train_authorities[12], self.track_controllerTest.train_speeds[12],'-', '-','-'],
            ['14', self.display_occupied_tracks(13), self.track_controllerTest.train_authorities[13], self.track_controllerTest.train_speeds[13],'-', '-','-'],
            ['15', self.display_occupied_tracks(14), self.track_controllerTest.train_authorities[14], self.track_controllerTest.train_speeds[14],'-', '-', '-']
        ]

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.blockInfoTable.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))

        #If light is red/green
        if(self.track_controllerTest.signal_states == False):
            self.blockInfoTable.setItem(4, 5, CrossingSignal('', GREEN))
        else:
            self.blockInfoTable.setItem(4, 5, CrossingSignal('', RED))

    def display_crossing_signal(self):
        if (self.track_controllerTest.crossing_states == False):
            return "Up"
        else: 
            return "Down"

    """
    def open_programmer_ui(self):
        self.programmer_ui.show()
        self.close()


"""
Maintenance Mode
"""
class Maintenance(QtWidgets.QMainWindow):

    #def setupUi(self, MainWindow):
    def __init__(self, track_controller, programmer_ui):
        super().__init__()

        #Setting track controller
        self.track_controllerMain = TrackController()
        self.track_controllerMain.track_occupancies = track_controller.track_occupancies
        self.track_controllerMain.train_speeds = track_controller.train_speeds
        self.track_controllerMain.train_authorities = track_controller.train_authorities
        self.track_controllerMain.switch_states = track_controller.switch_states
        self.track_controllerMain.signal_states = track_controller.signal_states
        self.track_controllerMain.crossing_states = track_controller.crossing_states
        self.track_controllerMain.plc_program_uploaded = False
        self.track_controllerMain.switch_positions = []
        self.track_controllerMain.plc_program = ""

        #Programmer UI name & size
        self.setObjectName("Maintenance")
        self.resize(1222, 702)
        self.programmer_ui = programmer_ui

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        #Used in multiple widgets
        waysides = ['Wayside 1']
        lines = ['Blue Line']

        #Creating universal font
        font = QtGui.QFont()
        font.setPointSize(13)

        #FileUpload button
        self.fileUploadPushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.fileUploadPushButton.setGeometry(QtCore.QRect(710, 60, 135, 40))
        self.fileUploadPushButton.setObjectName("pushButton")
        self.fileUploadPushButton.clicked.connect(self.getFileName)
        self.fileUploadPushButton.setFont(font)

        #Select PLC Program label
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(520, 60, 170, 40))
        self.label.setObjectName("label")
        self.label.setFont(font)

        #Label for PLC program uploaded
        self.plcUploadedLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.plcUploadedLabel.setGeometry(QtCore.QRect(870, 60, 220, 40))
        self.label.setObjectName("plcUploadedLabel")
        self.plcUploadedLabel.setFont(font)
        self.plcUploadedLabel.setVisible(False)

        #Create Rectangle for Wayside Table
        self.waysideRec = Rectangle(40, 30, 415, 50, DARK_GREY, self.centralwidget)
        self.waysideRec.lower()
        """
        self.backWayRec = Rectangle(40, 250, 415, 400, WHITE, self.centralwidget)
        self.backWayRec.lower()

        #Wayside Data Table
        self.tableView = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(40, 250, 415, 400))
        self.tableView.setObjectName("tableView")
        self.tableView.setColumnCount(4)
        self.tableView.setRowCount(15)
        self.tableView.setColumnWidth(1, 120)
        self.tableView.setColumnWidth(3, 80)

        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setItemDelegate(CenterDelegate(self.tableView))
        self.tableView.setHorizontalHeaderLabels(['Block #', 'Occupied', 'Switch', 'Signal'])
        self.tableView.horizontalHeader().setFont(font)
        self.add_wayside_table_data()
        self.tableView.setFont(font)

        #Handling updates to wayside block table
        self.tableView.itemChanged.connect(self.item_changed_waysideData)
        """

        #Wayside data combo
        self.comboBox_3 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(40, 35, 415, 35))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItems(lines)
        self.comboBox_3.setFont(font)

        #Waysides and Blocks rec
        self.waysideBlkRec = Rectangle(40, 200, 415, 50, DARK_GREY, self.centralwidget)
        self.waysideBlkRec.lower()
        self.backWaysideBlkRec = Rectangle(40, 80, 415, 100, WHITE, self.centralwidget)
        self.backWaysideBlkRec.lower()

        #Waysides and Blocks their responsible for table
        self.waysideBlkTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.waysideBlkTable.setGeometry(QtCore.QRect(40, 80, 415, 100))
        self.waysideBlkTable.setObjectName("waysideBlkTable")
        self.waysideBlkTable.setColumnCount(2)
        self.waysideBlkTable.setRowCount(1)

        self.waysideBlkTable.verticalHeader().setVisible(False)
        self.waysideBlkTable.setItemDelegate(CenterDelegate(self.waysideBlkTable))

        self.waysideBlkTable.setHorizontalHeaderLabels(['Waysides', 'Blocks'])
        self.waysideBlkTable.horizontalHeader().setFont(font)
        self.waysideBlkTable.setColumnWidth(0, 207)
        self.waysideBlkTable.setColumnWidth(1, 206)
        
        self.add_wayside_blk_table_data()
        self.waysideBlkTable.setFont(font)

        #Wayside and blocks combo
        """
        self.comboBox_2 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(40, 205, 415, 35))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItems(waysides)
        self.comboBox_2.setFont(font)
        """

        #Block info rec
        self.blockInfoRec = Rectangle(470, 220, 715, 110, DARK_GREY, self.centralwidget)
        self.blockInfoRec.lower()
        self.backBlockInfoRec = Rectangle(470, 330, 715, 320, WHITE, self.centralwidget)
        self.backBlockInfoRec.lower()

        #Block info table
        self.blockInfoTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.blockInfoTable.setGeometry(QtCore.QRect(470, 330, 715, 320))
        self.blockInfoTable.setObjectName("blockInfoTable")
        self.blockInfoTable.setColumnCount(7)
        self.blockInfoTable.setRowCount(len(self.track_controllerMain.track_occupancies))
        self.blockInfoTable.setColumnWidth(1, 120)
        self.blockInfoTable.setColumnWidth(5, 84)

        self.blockInfoTable.verticalHeader().setVisible(False)
        #self.blockInfoTable.setItemDelegate(CenterDelegate(self.tableView))
        self.blockInfoTable.setFont(font)
        self.blockInfoTable.setHorizontalHeaderLabels(['Block #', 'Occupancy', 'Authority[ft]', 'Speed[mph]','Switch','Signal','Crossing'])
        self.blockInfoTable.horizontalHeader().setFont(font)
        self.add_block_info_table_data()

        #Handling updates to block info table
        self.blockInfoTable.itemChanged.connect(self.item_changed_blockInfo)

        #Combobox for block info table
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(540, 230, 575, 35))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(lines)
        self.comboBox.setFont(font)

        #TextEdit box for block info table
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(735, 270, 200, 40))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setFont(font)

        #End Maintenance button
        self.maintenanceBtn = QPushButton("Maintenance", self.centralwidget)
        self.maintenanceBtn.clicked.connect(self.open_programmer_ui)
        self.maintenanceBtn.setGeometry(QtCore.QRect(710, 150, 135, 40))
        self.maintenanceBtn.setFont(font)
        self.maintenanceBtn.setStyleSheet("""
        QPushButton {
            background-color: #FF0000;
        }
        """)

        #Setting central widget
        self.setCentralWidget(self.centralwidget)

        #Menubar code
        self.menubar = QtWidgets.QMenuBar(parent=self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 855, 26))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Maintenance", "Maintenance"))
        self.fileUploadPushButton.setText(_translate("Maintenance", "Upload File"))
        self.label.setText(_translate("Maintenance", "Select PLC Program:"))
        self.plcUploadedLabel.setText(_translate("Maintenance", "PLC program uploaded."))

    #Updates UI values to reflect backend changes
    def update_ui(self):
        self.blockInfoTable.itemChanged.disconnect(self.item_changed_blockInfo)
        self.tableView.itemChanged.disconnect(self.item_changed_waysideData)
        self.track_controllerMain.run_PLC_program()
        self.add_wayside_table_data()
        self.add_wayside_blk_table_data()
        self.add_block_info_table_data()
        self.blockInfoTable.itemChanged.connect(self.item_changed_blockInfo)
        self.tableView.itemChanged.connect(self.item_changed_waysideData)

    #Allows User to select PLC Program from directory
    def getFileName(self):    
        file_filter = 'Data File (*.py)'
        response = QFileDialog.getOpenFileName (
            parent = self,
            caption = 'Select a file',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Data File (*.py)'
        )
        self.track_controllerMain.get_PLC_program(response[0])

        if(self.track_controllerMain.plc_program_uploaded == True and self.track_controllerMain.plc_program != ""):
            self.track_controllerMain.run_PLC_program
            self.plcUploadedLabel.setVisible(True)
        else:
            self.plcUploadedLabel.setVisible(False)

    def item_changed_blockInfo(self, item):
        row = item.row()
        column = item.column()
        new_item = item.text()

        match column:
            #Occupancy
            case 1:
                if (new_item == "Occupied"):
                    self.track_controllerMain.track_occupancies[row] = True
                else:
                    self.track_controllerMain.track_occupancies[row] = False
            #Authority
            case 2:
                self.track_controllerMain.train_authorities[row] = new_item
            #Speed
            case 3:
                self.track_controllerMain.train_speeds[row] = new_item
            #Switch
            case _:
                #Update Switches
                #Signal
                print("")
        self.update_ui()
      
    def item_changed_waysideData(self, item):
        row = item.row()
        column = item.column()
        new_item = item.text()

        match column:
            #Occupancy
            case 1:
                if (new_item == "Occupied"):
                    self.track_controllerMain.track_occupancies[row] = True
                else:
                    self.track_controllerMain.track_occupancies[row] = False
            #Switch
            case 2:
                value = self.track_controllerMain.switch_states
                #if making switch to 11
                if(new_item == "5" and row == 10):
                    self.track_controllerMain.switch_states = True
                    value = self.track_controllerMain.switch_states
                elif(new_item == "5" and row == 5):
                    self.track_controllerMain.switch_states = False
                    value = self.track_controllerMain.switch_states
                elif(new_item == "6" and row == 4):
                    self.track_controllerMain.switch_states = False
                    value = self.track_controllerMain.switch_states
                elif(new_item == "11" and row == 4):
                    self.track_controllerMain.switch_states = True
                    value = self.track_controllerMain.switch_states
                else:
                    print("Not valid switch")
            #Signal
            case 3:
                print("")
        self.update_ui()


    #Converts track_occupancies into "occupied/in operation"
    def display_occupied_tracks(self, i):
        if (self.track_controllerMain.track_occupancies[i] == False):
            return "In Operation"
        else:
            return "Occupied"
    
    #Converts switch_states into values they're connected to 
    def display_switch_pos(self, i):
        if(self.track_controllerMain.switch_states == False and i == 5):
            return "6"
        elif(self.track_controllerMain.switch_states == False and i == 6):
            return "5"
        elif(self.track_controllerMain.switch_states == False and i == 11):
            return "-"
        elif(self.track_controllerMain.switch_states == True and i == 5):
            return "11"
        elif(self.track_controllerMain.switch_states == True and i == 6):
            return "-"
        else:
            return "5"

    #Adds data to wayside table
    def add_wayside_table_data(self):
        data = [
            ['1', self.display_occupied_tracks(0), '-', '-'],
            ['2', self.display_occupied_tracks(1), '-', '-'],
            ['3', self.display_occupied_tracks(2), '-', '-'],
            ['4', self.display_occupied_tracks(3), '-', '-'],
            ['5', self.display_occupied_tracks(4), self.display_switch_pos(5), '-'],
            ['6', self.display_occupied_tracks(5), self.display_switch_pos(6), '-'],
            ['7', self.display_occupied_tracks(6), '-', '-'],
            ['8', self.display_occupied_tracks(7), '-', '-'],
            ['9', self.display_occupied_tracks(8), '-', '-'],
            ['10', self.display_occupied_tracks(9), '-', '-'],
            ['11', self.display_occupied_tracks(10), self.display_switch_pos(11), '-'],
            ['12', self.display_occupied_tracks(11), '-', '-'],
            ['13', self.display_occupied_tracks(12), '-', '-'],
            ['14', self.display_occupied_tracks(13), '-', '-'],
            ['15', self.display_occupied_tracks(14), '-', '-']
        ]
        
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.tableView.setItem(i, j, QtWidgets.QTableWidgetItem(str(item))) 
        
        #If light is red/green
        if(self.track_controllerMain.signal_states == False):
            self.tableView.setItem(4, 3, CrossingSignal('', GREEN))
        else:
            self.tableView.setItem(4, 3, CrossingSignal('', RED))

    def add_block_info_table_data(self):
        data = [
            ['1', self.display_occupied_tracks(0), self.track_controllerMain.train_authorities[0], self.track_controllerMain.train_speeds[0] , '-', '-', '-'],
            ['2', self.display_occupied_tracks(1), self.track_controllerMain.train_authorities[1], self.track_controllerMain.train_speeds[1],'-', '-', '-'],
            ['3', self.display_occupied_tracks(2), self.track_controllerMain.train_authorities[2], self.track_controllerMain.train_speeds[2],'-', '-', '-'],
            ['4', self.display_occupied_tracks(3), self.track_controllerMain.train_authorities[3], self.track_controllerMain.train_speeds[3],'-', '-' ,'-'],
            ['5', self.display_occupied_tracks(4), self.track_controllerMain.train_authorities[4], self.track_controllerMain.train_speeds[4],self.display_switch_pos(5), ' ', '-'],
            ['6', self.display_occupied_tracks(5), self.track_controllerMain.train_authorities[5], self.track_controllerMain.train_speeds[5],self.display_switch_pos(6), '-', '-'],
            ['7', self.display_occupied_tracks(6), self.track_controllerMain.train_authorities[6], self.track_controllerMain.train_speeds[6],'-', '-', '-'],
            ['8', self.display_occupied_tracks(7), self.track_controllerMain.train_authorities[7], self.track_controllerMain.train_speeds[7],'-', '-', self.display_crossing_signal()],
            ['9', self.display_occupied_tracks(8), self.track_controllerMain.train_authorities[8], self.track_controllerMain.train_speeds[8],'-', '-', '-'],
            ['10', self.display_occupied_tracks(9), self.track_controllerMain.train_authorities[9], self.track_controllerMain.train_speeds[9],'-', '-','-'],
            ['11', self.display_occupied_tracks(10), self.track_controllerMain.train_authorities[10], self.track_controllerMain.train_speeds[10],self.display_switch_pos(11), '-','-'],
            ['12', self.display_occupied_tracks(11), self.track_controllerMain.train_authorities[11], self.track_controllerMain.train_speeds[11],'-', '-', '-'],
            ['13', self.display_occupied_tracks(12), self.track_controllerMain.train_authorities[12], self.track_controllerMain.train_speeds[12],'-', '-','-'],
            ['14', self.display_occupied_tracks(13), self.track_controllerMain.train_authorities[13], self.track_controllerMain.train_speeds[13],'-', '-','-'],
            ['15', self.display_occupied_tracks(14), self.track_controllerMain.train_authorities[14], self.track_controllerMain.train_speeds[14],'-', '-', '-']
        ]

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.blockInfoTable.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))

        #If light is red/green
        if(self.track_controllerMain.signal_states == False):
            self.blockInfoTable.setItem(4, 5, CrossingSignal('', GREEN))
        else:
            self.blockInfoTable.setItem(4, 5, CrossingSignal('', RED))

    def display_crossing_signal(self):
        if (self.track_controllerMain.crossing_states == False):
            return "Up"
        else: 
            return "Down"

    def add_wayside_blk_table_data(self):
        data = [
            ['Wayside 1', '1 - 15']
        ]

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QTableWidgetItem(item)
                self.waysideBlkTable.setItem(i, j, text)

    def open_programmer_ui(self):
        self.track_controllerMain.plc_program_uploaded = False
        self.track_controllerMain.plc_program = ""
        self.programmer_ui.show()
        self.close()