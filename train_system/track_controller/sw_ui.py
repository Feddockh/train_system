import os
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6 import QtCore, QtGui, QtWidgets, uic, QtWidgets
from train_system.common.palette import Colors
from train_system.track_controller.sw_track_controller import TrackController

#Colors
DARK_GREY = "#C8C8C8"
WHITE = "#FFFFFF"
RED = "#FF0000"
GREEN = "#00FF00"
LIGHT_GREY = "#D5DBE3"


class CenterDelegate(QtWidgets.QStyledItemDelegate):
    """
        Used to hold objects on UI. 
    """
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignCenter

class CrossingSignalWidget(QTableWidgetItem):
    """
        Used to display current color of each signal. 
    """
    def __init__(self, text='', background_color=None):
        super().__init__(text)
        if background_color:
            self.setBackground(QtGui.QColor(background_color))
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)

class Rectangle(QWidget):
    """
        Used to create rectangles for UI. 
    """

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
        """
        Sets up the Programmer UI.
        
        Args:
            track_controllers(TrackController): List of waysides
        """
        super().__init__()

        #Setting track controller
        self.track_controllers = track_controllers

        #Adding handler for each track controller
        for track_controller in self.track_controllers:
            track_controller.plc_ran.connect(self.update_ui)

        #Programmer UI name & size
        self.setObjectName("Programmer UI")
        self.resize(1222, 702)

        #Creating universal font
        font = QtGui.QFont()
        font.setPointSize(15)

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WHITE};
            }}
            QHeaderView::section {{
                background-color: #EFEFEF;
                font-family: 'Arial';
                font-size: 15px;
                font-weight: bold;
            }}
        """)
        self.setCentralWidget(self.centralwidget)

        #Used in multiple widgets
        waysides = [track_controllers[0].wayside_name, track_controllers[1].wayside_name, track_controllers[2].wayside_name,track_controllers[3].wayside_name, track_controllers[4].wayside_name, track_controllers[5].wayside_name]
        lines = ['Green Line', 'Red Line']

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
        self.waysideRec = Rectangle(520, 30, 640, 50, Colors.GREY, self.centralwidget)
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
        self.waysideRec = Rectangle(60, 30, 415, 50, Colors.GREY, self.centralwidget)
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
        self.blockInfoRec = Rectangle(60, 270, 1100, 60, Colors.GREY, self.centralwidget)
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
        """
        Retranslates the UI's widgets. 
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("ProgrammerUI", "ProgrammerUI"))
        self.fileUploadPushButton.setText(_translate("ProgrammerUI", "Upload File"))
        self.label.setText(_translate("ProgrammerUI", "Select PLC Program:"))
        self.plcUploadedLabel.setText(_translate("ProgrammerUI", "PLC program uploaded."))

    #Updates UI values to reflect backend changes
    def update_ui(self):
        """
        Refreshes and updates the tables on the UI every time its called. 
        """
        lineIndex = self.comboBox_3.currentIndex()
        waysideIndex = self.comboBox.currentIndex()
        self.add_wayside_blk_table_data(lineIndex)
        self.add_block_info_table_data(waysideIndex)
        self.display_plc_uploaded(waysideIndex)

    #Allows User to select PLC Program from directory
    def getFileName(self):    
        """
        Gets filename once inputted by user. 
        """
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
            self.track_controllers[waysideIndex].run_PLC_program()
            self.update_ui()
        else:
            self.plcUploadedLabel.setVisible(False)
    
    #Using search box to filter table data
    def filter_table(self):
        """
        Performs a search on the wayside data table for matching block numbers. 
        """
        filter_text = self.textEdit.text().strip().lower()
        for row in range(self.blockInfoTable.rowCount()):
            item = self.blockInfoTable.item(row, 0)
            if item is not None and filter_text in item.text().strip().lower():
                self.blockInfoTable.setRowHidden(row, False)
            else:
                self.blockInfoTable.setRowHidden(row, True)

    #Converts track_occupancies into "occupied/in operation"
    def display_occupied_tracks(self, i, waysideIndex):
        """
        Converts track occupancy to "Occupied" or "Not Occupied". 
        """
        if (self.track_controllers[waysideIndex].track_blocks[i]._occupancy == False):
            return "Not Occupied"
        else:
            return "Occupied"

    #displays whether or not the plc has been uploaded
    def display_plc_uploaded(self, waysideIndex):
        """
        Displays a label once a PLC program has been uploaded. 

        Args:
            waysideIndex(int): index of wayside that needs to be updated. 
        """
        self.plcUploadedLabel.setVisible(False)
        if(self.track_controllers[waysideIndex].plc_program_uploaded == True and self.track_controllers[waysideIndex].plc_program != ""):
            self.plcUploadedLabel.setVisible(True)

    #adds block info table data
    def add_block_info_table_data(self, waysideIndex):
        """
        Updates information in block info table. 
        
        Args:
            waysideIndex(int): index of wayside that needs to be updated. 
        """
        self.blockInfoTable.clearContents()
        self.blockInfoTable.setRowCount(len(self.track_controllers[waysideIndex].track_blocks))

        data = []
        for x in range(len(self.track_controllers[waysideIndex].track_blocks)):
            tempData = [self.track_controllers[waysideIndex].track_blocks[x].number, 
                        self.display_occupied_tracks(x, waysideIndex), 
                        self.track_controllers[waysideIndex].track_blocks[x]._authority.get_distance(), 
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
        """
        Displays switch position on UI.  
        
        Args:
            x(int): Block number of switch is located
            waysideIndex(int):index of wayside that needs to be updated
        """
        
        #if there is a switch that exists at this block
        if((self.track_controllers[waysideIndex].track_blocks[x].switch != None) and (self.track_controllers[waysideIndex].track_blocks[x].switch.parent_block == self.track_controllers[waysideIndex].track_blocks[x].number)):
            pos = self.track_controllers[waysideIndex].track_blocks[x].switch.get_child_index()
            item = self.track_controllers[waysideIndex].track_blocks[x].switch.position

            #for other block not connected to switch
            if(pos == False):
                otherPos = 1
            else:
                otherPos = 0
            otherItem = self.track_controllers[waysideIndex].track_blocks[x].switch.child_blocks[otherPos]
            
            #updating block connected to switch
            for i in range(len(self.track_controllers[waysideIndex].track_blocks)):
                if(self.track_controllers[waysideIndex].track_blocks[i].number == item):
                    Itemblock = QTableWidgetItem(str(self.track_controllers[waysideIndex].track_blocks[x].number))
                    Itemblock.setFlags(Itemblock.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.blockInfoTable.setItem(i, 4, Itemblock)
                elif(self.track_controllers[waysideIndex].track_blocks[i].number == otherItem):
                    Otherblock = QTableWidgetItem("-")
                    Otherblock.setFlags(Otherblock.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.blockInfoTable.setItem(i, 4, Otherblock)
            block = QTableWidgetItem(str(item))
            block.setBackground(QtGui.QColor(LIGHT_GREY))
            block.setFlags(block.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.blockInfoTable.setItem(x, 4, block)

        self.blockInfoTable.viewport().update()
    
    def display_light_signal(self, x, waysideIndex):
        """
        Displays light signal on UI.  
        
        Args:
            x(int): Block number of light signal is located
            waysideIndex(int):index of wayside that needs to be updated
        """

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
        """
        Displays crossing signal on UI.  
        
        Args:
            x(int): Block number of crossing signal is located.
            waysideIndex(int):index of wayside that needs to be updated
        """
        if (self.track_controllers[waysideIndex].track_blocks[x]._crossing_signal == False):
            return "Up"
        elif(self.track_controllers[waysideIndex].track_blocks[x]._crossing_signal == True):
            return "Down"
        else:
            return "-"

    #Adds info about waysides and the blocks they're responsible for
    def add_wayside_blk_table_data(self, lineIndex):
        """
        Updates wayside block table with respective line information 
        
        Args:
            x(int): Block number of crossing signal is located.
            lineIndex(int):index of line that needs to be updated
        """

        if (lineIndex == 0):
            data = [
                ['Wayside 1', '1 - 32, 150'],
                ['Wayside 2', '29 - 85, 101 - 153'],
                ['Wayside 3', '74 - 101']
            ]
        elif (lineIndex == 1):
            data = [
                ['Wayside 4', '1 - 23, 73 - 76'], 
                ['Wayside 5', '24 - 45, 68 - 75'],
                ['Wayside 6', '40 - 68']
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
        """
        Opens test bench  
        """
        self.test_bench = TestBench(self.track_controllers, self)
        self.test_bench.show()
        self.hide()

    #Opens maintenance 
    def open_maintenance(self):
        """
        Opens maintenance
        """
        self.maintenance = Maintenance(self.track_controllers,self)
        self.maintenance.show()
        self.hide()


"""
Test Bench UI - Can be brought here by selecting test bench from Programmer UI
"""
class TestBench(QtWidgets.QMainWindow):

    
    def __init__(self, track_controllers, programmer_ui):
        super().__init__()
        """
        Initialization for TestBench

        Args:
            track_controllers(TrackControllers): List of TrackControllers
            programmer_ui(QMainWindow): Programmer UI so that it can go back 
        """

        self.track_controllers = track_controllers

        #Programmer UI name & size
        self.setObjectName("Test Bench")
        self.resize(1222, 702)
        self.programmer_ui = programmer_ui

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WHITE};
            }}
            QHeaderView::section {{
                background-color: #EFEFEF;
                font-family: 'Arial';
                font-size: 15px;
                font-weight: bold;
            }}
        """)
        self.setCentralWidget(self.centralwidget)

        #Used in multiple widgets
        waysides = [track_controllers[0].wayside_name, track_controllers[1].wayside_name, track_controllers[2].wayside_name,track_controllers[3].wayside_name, track_controllers[4].wayside_name, track_controllers[5].wayside_name]
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
        self.waysideRec = Rectangle(520, 30, 640, 50, Colors.GREY, self.centralwidget)
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
        self.waysideRec = Rectangle(60, 30, 415, 50, Colors.GREY, self.centralwidget)
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
        self.comboBox.currentIndexChanged.connect(lambda: self.update_ui())
        self.comboBox_3.currentIndexChanged.connect(lambda: self.update_ui())

        #Block info rec
        self.blockInfoRec = Rectangle(60, 270, 1100, 60, Colors.GREY, self.centralwidget)
        self.blockInfoRec.lower()
        self.backBlockInfoRec = Rectangle(60, 330, 1100, 320, WHITE, self.centralwidget)
        self.backBlockInfoRec.lower()

        #Block info table
        self.blockInfoTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.blockInfoTable.setGeometry(QtCore.QRect(60, 330, 1100, 320))
        self.blockInfoTable.setObjectName("blockInfoTable")
        self.blockInfoTable.setColumnCount(4)
        self.blockInfoTable.setRowCount(len(self.track_controllers[0]. track_blocks))
        self.blockInfoTable.setColumnWidth(0, 275)
        self.blockInfoTable.setColumnWidth(1, 275)
        self.blockInfoTable.setColumnWidth(2, 275)
        self.blockInfoTable.setColumnWidth(3, 270)
        self.blockInfoTable.setColumnWidth(5, 84)

        self.blockInfoTable.verticalHeader().setVisible(False)
        self.blockInfoTable.setFont(font)
        self.blockInfoTable.setHorizontalHeaderLabels(['Block #', 'Occupancy', 'Authority[ft]', 'Speed[mph]'])
        self.blockInfoTable.horizontalHeader().setFont(font)
        self.add_block_info_table_data(waysideIndex)

        #Search box for block info table
        self.textEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.textEdit.setPlaceholderText("Search Block #")
        self.textEdit.setGeometry(QtCore.QRect(495, 280, 220, 40))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setFont(font)

        #Handling updates to block info table
        self.blockInfoTable.itemChanged.connect(lambda item: self.item_changed_blockInfo(item))
        self.textEdit.textChanged.connect(self.filter_table)

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
        """
        Retranslate the UI for its widgets. 
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("TestBench", "Testbench"))
        self.fileUploadPushButton.setText(_translate("TestBench", "Upload File"))
        self.label.setText(_translate("TestBench", "Select PLC Program:"))
        #self.plcUploadedLabel.setText(_translate("ProgrammerUI", "PLC program uploaded."))

    #Updates UI values to reflect backend changes
    def update_ui(self):
        self.blockInfoTable.blockSignals(True)
        lineIndex = self.comboBox_3.currentIndex()
        waysideIndex = self.comboBox.currentIndex()
        #self.track_controller.run_PLC_program()
        self.add_wayside_blk_table_data(lineIndex)
        self.add_block_info_table_data(waysideIndex)
        self.blockInfoTable.blockSignals(False)

    #Allows User to select PLC Program from directory
    def getFileName(self):    
        """
        Get filename from user. 
        """
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

    #Using search box to filter table data
    def filter_table(self):
        """
        Filters table and shows matching search critera.  
        """
        filter_text = self.textEdit.text().strip().lower()
        for row in range(self.blockInfoTable.rowCount()):
            item = self.blockInfoTable.item(row, 0)
            if item is not None and filter_text in item.text().strip().lower():
                self.blockInfoTable.setRowHidden(row, False)
            else:
                self.blockInfoTable.setRowHidden(row, True)
    
    def add_wayside_blk_table_data(self, lineIndex):
        """
        Updates wayside block table. 

        Args:
            lineIndex(int): index of line to be updated
        """
        if (lineIndex == 0):
            data = [
                ['Wayside 1', '1 - 32, 150'],
                ['Wayside 2', '29 - 85, 101 - 153'],
                ['Wayside 3', '74 - 101']
            ]
        elif (lineIndex == 1):
            data = [
                ['Wayside 4', '1 - 23, 73 - 76'], 
                ['Wayside 5', '24 - 45, 68 - 75'],
                ['Wayside 6', '40 - 68']
            ]

        self.waysideBlkTable.clearContents()
        self.waysideBlkTable.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QTableWidgetItem(item)
                text.setFlags(text.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.waysideBlkTable.setItem(i, j, text)


    def item_changed_blockInfo(self, item):
        """
        Called if item is changed within block info table. 

        Args:
            item(Object): item that was changed within the table.
        """
        waysideIndex = self.comboBox.currentIndex()
        row = item.row()
        column = item.column()
        new_item = item.text()
        
        match column:
            #Occupancy
            case 1:
                if (new_item == "Occupied"):
                    self.track_controllers[waysideIndex].track_blocks[row].occupancy = True
                else:
                    self.track_controllers[waysideIndex].track_blocks[row].occupancy = False
            #Authority
            case 2:
                new_authority = float(new_item)
                self.track_controllers[waysideIndex].track_blocks[row]._authority.set_distance(new_authority)
            #Speed
            case 3:
                new_speed = int(new_item)
                self.track_controllers[waysideIndex].track_blocks[row].suggested_speed = new_speed
            case _:
                print("")
        self.blockInfoTable.blockSignals(True)
        self.update_ui()
        self.blockInfoTable.blockSignals(False)


    #Converts track_occupancies into "occupied/in operation"
    def display_occupied_tracks(self, i, waysideIndex):
        """
        Takes block occupancy and displays as "Occupied" or "Not Occupied"

        Args:
            i(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """
        if (self.track_controllers[waysideIndex].track_blocks[i]._occupancy == False):
            return "Not Occupied"
        else:
            return "Occupied"

    #adds block info table data
    def add_block_info_table_data(self, waysideIndex):
        """
        Updates block info table

        Args:
            waysideIndex(int): index of wayside that needs to be changed 
        """
        self.blockInfoTable.clearContents()
        self.blockInfoTable.setRowCount(len(self.track_controllers[waysideIndex].track_blocks))

        data = []
        for x in range(len(self.track_controllers[waysideIndex].track_blocks)):
            tempData = [self.track_controllers[waysideIndex].track_blocks[x].number, 
                        self.display_occupied_tracks(x, waysideIndex), 
                        self.track_controllers[waysideIndex].track_blocks[x]._authority.get_distance(), 
                        self.track_controllers[waysideIndex].track_blocks[x].suggested_speed]
            data.append(tempData)

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QtWidgets.QTableWidgetItem(str(item))
                self.blockInfoTable.setItem(i, j, text)
                if j == 0:
                    text.setFlags(text.flags() & Qt.ItemFlag.ItemIsEditable)
        

    #open programmer ui - close testbench
    """
        Open programmer UI and close Testbench
    """
    def open_programmer_ui(self):
        self.programmer_ui.show()
        self.programmer_ui.update_ui()
        self.close()


"""
Maintenance Mode
"""
class Maintenance(QtWidgets.QMainWindow):

    #def setupUi(self, MainWindow):
    def __init__(self, track_controllers, programmer_ui):
        """
        Initializes Maintenance window

        Args:
            track_controllers(TrackController): List of waysides
            programmer_ui(QMainWindow): programmer ui
        """

        super().__init__()

        self.track_controllers = track_controllers

        #Programmer UI name & size
        self.setObjectName("Maintenance")
        self.resize(1222, 702)
        self.programmer_ui = programmer_ui

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.WHITE};
            }}
            QHeaderView::section {{
                background-color: #EFEFEF;
                font-family: 'Arial';
                font-size: 15px;
                font-weight: bold;
            }}
        """)
        self.setCentralWidget(self.centralwidget)

        #Used in multiple widgets
        waysides = [track_controllers[0].wayside_name, track_controllers[1].wayside_name, track_controllers[2].wayside_name,track_controllers[3].wayside_name, track_controllers[4].wayside_name, track_controllers[5].wayside_name]
        #waysides = [self.track_controllers[0].wayside_name, self.track_controllers[1].wayside_name, self.track_controllers[2].wayside_name]
        lines = ['Green Line', 'Red Line']

        #Creating universal font
        font = QtGui.QFont()
        font.setPointSize(15)

        #Combobox for wayside selection
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(520, 35, 640, 35))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(waysides)
        self.comboBox.setFont(font)

        #Getting current combo box index
        waysideIndex = self.comboBox.currentIndex()

        #Create Rectangle for wayside selection
        self.waysideRec = Rectangle(520, 30, 640, 50, Colors.GREY, self.centralwidget)
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
        self.waysideRec = Rectangle(60, 30, 415, 50, Colors.GREY, self.centralwidget)
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
        self.comboBox.currentIndexChanged.connect(lambda: self.update_ui())
        self.comboBox_3.currentIndexChanged.connect(lambda: self.update_ui())

        #Block info rec
        self.blockInfoRec = Rectangle(60, 270, 1100, 60, Colors.GREY, self.centralwidget)
        self.blockInfoRec.lower()
        self.backBlockInfoRec = Rectangle(60, 330, 1100, 320, WHITE, self.centralwidget)
        self.backBlockInfoRec.lower()

        #Block info table
        self.blockInfoTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.blockInfoTable.setGeometry(QtCore.QRect(60, 330, 1100, 320))
        self.blockInfoTable.setObjectName("blockInfoTable")
        self.blockInfoTable.setColumnCount(4)
        self.blockInfoTable.setRowCount(len(self.track_controllers[0]. track_blocks))
        self.blockInfoTable.setColumnWidth(0, 275)
        self.blockInfoTable.setColumnWidth(1, 275)
        self.blockInfoTable.setColumnWidth(2, 275)
        self.blockInfoTable.setColumnWidth(3, 270)
   
        self.blockInfoTable.verticalHeader().setVisible(False)
        self.blockInfoTable.setFont(font)
        self.blockInfoTable.setHorizontalHeaderLabels(['Block #', 'Switch', 'Signal', 'Crossing'])
        self.blockInfoTable.horizontalHeader().setFont(font)
        self.add_block_info_table_data(waysideIndex)

        #Handling updates to block info table
        #self.blockInfoTable.itemChanged.connect(lambda item: self.item_changed_blockInfo(item))
        self.blockInfoTable.itemClicked.connect(lambda item: self.item_changed_blockInfo_Signal(item))

        #Updating comboboxes
        self.comboBox.currentIndexChanged.connect(lambda: self.update_ui())
        self.comboBox_3.currentIndexChanged.connect(lambda: self.update_ui())

        #Search box for block info table
        self.textEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.textEdit.setPlaceholderText("Search Block #")
        self.textEdit.setGeometry(QtCore.QRect(495, 280, 220, 40))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setFont(font)

        self.textEdit.textChanged.connect(self.filter_table)

        #End Maintenance button
        self.maintenanceBtn = QPushButton("Maintenance", self.centralwidget)
        self.maintenanceBtn.clicked.connect(self.open_programmer_ui)
        self.maintenanceBtn.setGeometry(QtCore.QRect(710, 190, 145, 50))
        self.maintenanceBtn.setFont(font)
        self.maintenanceBtn.setStyleSheet("""
        QPushButton {
            background-color: #FF0000;
        }
        """)

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
        """
        Retranslates the widgets of the UI
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Maintenance", "Maintenance"))
        #self.fileUploadPushButton.setText(_translate("Maintenance", "Upload File"))
        #self.label.setText(_translate("Maintenance", "Select PLC Program:"))
        #self.plcUploadedLabel.setText(_translate("Maintenance", "PLC program uploaded."))

    #Updates UI values to reflect backend changes
    def update_ui(self):
        """
        Updates the UI & Refreshes its tables
        """
        self.blockInfoTable.blockSignals(True)
        lineIndex = self.comboBox_3.currentIndex()
        waysideIndex = self.comboBox.currentIndex()
        #self.track_controllers[waysideIndex].run_PLC_program()
        self.add_wayside_blk_table_data(lineIndex)
        self.add_block_info_table_data(waysideIndex)
        self.blockInfoTable.blockSignals(False)
    
    #Allows User to select PLC Program from directory
    def getFileName(self):    
        """
        Gets filename for PLC from the user. 
        """
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

    #Using search box to filter table data
    def filter_table(self):
        """
        Searches block info table based on search criteria 
        """
        filter_text = self.textEdit.text().strip().lower()
        for row in range(self.blockInfoTable.rowCount()):
            item = self.blockInfoTable.item(row, 0)
            if item is not None and filter_text in item.text().strip().lower():
                self.blockInfoTable.setRowHidden(row, False)
            else:
                self.blockInfoTable.setRowHidden(row, True)

    def add_wayside_blk_table_data(self, lineIndex):
        """
        Updates wayside block table

        Args:
            lineIndex(int): index of line that needs to be changed 
        """

        if (lineIndex == 0):
            data = [
                ['Wayside 1', '1 - 32, 150'],
                ['Wayside 2', '29 - 85, 101 - 153'],
                ['Wayside 3', '74 - 101']
            ]
        elif (lineIndex == 1):
            data = [
                ['Wayside 4', '1 - 23, 73 - 76'], 
                ['Wayside 5', '24 - 45, 68 - 75'],
                ['Wayside 6', '40 - 68']
            ]

        self.waysideBlkTable.clearContents()
        self.waysideBlkTable.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QTableWidgetItem(item)
                text.setFlags(text.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.waysideBlkTable.setItem(i, j, text)

    def item_changed_blockInfo_Signal(self, item):
        """
        Called when there was an update to any of the items in block info table.

        Args:
            item(object): item that was changed in table
        """
        waysideIndex = self.comboBox.currentIndex()
        #if switch
        if(item.column() == 1):
            row = item.row()
            self.check_switch(row, waysideIndex)
        #If light signal column
        elif(item.column() == 2):
            #getting block 
            row = item.row()
            self.check_signal(row, waysideIndex)
        #If crossing signal column
        elif(item.column() == 3):
            row = item.row()
            self.check_crossing(row, waysideIndex)
            print("here")

    def check_crossing(self, x, waysideIndex):
        """
        Checks if potenial new crossing signal is safe by PLC standards. 

        Args:
            x(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """
        #checking to see if there is a crossing at this block
        if(self.track_controllers[waysideIndex].track_blocks[x]._crossing_signal != None):
            #Getting current signal
            curr_crossing = self.track_controllers[waysideIndex].track_blocks[x]._crossing_signal
            print("Curr")
            print(curr_crossing)

            #Getting possible new signal
            if (curr_crossing == True):
                new_crossing_bool = False
            else:
                new_crossing_bool = True

            #Checking PLC Program
            self.track_controllers[waysideIndex].check_PLC_program_crossing(x, curr_crossing, new_crossing_bool)

            self.blockInfoTable.blockSignals(True)
            self.update_ui()
            self.blockInfoTable.blockSignals(False)

    def check_signal(self, x, waysideIndex):
        """
        Checks if potenial new light signal is safe by PLC standards. 

        Args:
            x(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """

        #checking to see if there is a light signal at this block
        if(self.track_controllers[waysideIndex].track_blocks[x]._light_signal != None):
            #Getting current signal
            curr_signal = self.track_controllers[waysideIndex].track_blocks[x]._light_signal

            #Getting possible new signal
            if (curr_signal == True):
                new_signal = False
            else: 
                new_signal = True

            #Checking PLC Program
            self.track_controllers[waysideIndex].check_PLC_program_signal(x, curr_signal, new_signal)

            self.blockInfoTable.blockSignals(True)
            self.update_ui()
            self.blockInfoTable.blockSignals(False)
            


    def check_switch(self, x, waysideIndex):
        """
        Checks if potenial new switch position is safe by PLC standards. 

        Args:
            x(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """
        #if this block has a switch
        if(self.track_controllers[waysideIndex].track_blocks[x].switch != None):
            #Getting current position & block switch is connected to
            pos = self.track_controllers[waysideIndex].track_blocks[x].switch.get_child_index()
            #item = self.track_controllers[waysideIndex].track_blocks[x].switch_options[pos]
            print(pos)

            if(pos == False):
                otherPos = 1
            else:
                otherPos = 0
            
            int_pos = int(pos)

            self.track_controllers[waysideIndex].check_PLC_program_switch(x, pos, otherPos)
        #this block has nothing to do with switches
        elif(self.track_controllers[waysideIndex].track_blocks[x].switch == None):
            block = QTableWidgetItem("-")
            block.setFlags(block.flags() & Qt.ItemFlag.ItemIsEditable)
            self.blockInfoTable.setItem(x, 1, block)

        self.blockInfoTable.blockSignals(True)
        self.update_ui()
        self.blockInfoTable.blockSignals(False)


    #Converts switch_states into values they're connected to 
    def display_switch_pos(self, x, waysideIndex):
        """
        Displays position of switch on UI in block info table

        Args:
            x(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """
        #if there is a switch that exists at this block
        if((self.track_controllers[waysideIndex].track_blocks[x].switch != None) and (self.track_controllers[waysideIndex].track_blocks[x].switch.parent_block == self.track_controllers[waysideIndex].track_blocks[x].number)):
            pos = self.track_controllers[waysideIndex].track_blocks[x].switch.get_child_index()
            item = self.track_controllers[waysideIndex].track_blocks[x].switch.position

            #for other block not connected to switch
            if(pos == False):
                otherPos = 1
            else:
                otherPos = 0
            otherItem = self.track_controllers[waysideIndex].track_blocks[x].switch.child_blocks[otherPos]

            #updating block connected to switch
            for i in range(self.track_controllers[waysideIndex].numBlocks):
                if(self.track_controllers[waysideIndex].track_blocks[i].number == item):
                    block = QTableWidgetItem(str(self.track_controllers[waysideIndex].track_blocks[x].number))
                    block.setFlags(block.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.blockInfoTable.setItem(i, 1, block)
                elif(self.track_controllers[waysideIndex].track_blocks[i].number == otherItem):
                    block = QTableWidgetItem("-")
                    block.setFlags(block.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.blockInfoTable.setItem(i, 1, block)
            block = QTableWidgetItem(str(item))
            block.setBackground(QtGui.QColor(LIGHT_GREY))
            block.setFlags(block.flags() | Qt.ItemFlag.ItemIsEditable)
            self.blockInfoTable.setItem(x, 1, block)

        self.blockInfoTable.viewport().update()
    
    def display_light_signal(self, x, waysideIndex):
        """
        Displays light signals in block info table

        Args:
            x(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """
        #If light signal is red or green
        if(self.track_controllers[waysideIndex].track_blocks[x]._light_signal == True):
            self.blockInfoTable.setItem(x, 2, CrossingSignalWidget("", GREEN))
        elif(self.track_controllers[waysideIndex].track_blocks[x]._light_signal == False):
            self.blockInfoTable.setItem(x, 2, CrossingSignalWidget("", RED))
        else:
            self.blockInfoTable.setItem(x, 2, CrossingSignalWidget("", WHITE))

        self.blockInfoTable.viewport().update()

    #Displays crossing signals
    def display_crossing_signal(self, x, waysideIndex):
        """
        Displays crossing signals in block info table

        Args:
            x(int): index of block
            waysideIndex(int): index of wayside that needs to be changed 
        """
        if (self.track_controllers[waysideIndex].track_blocks[x]._crossing_signal == False):
            return "Up"
        elif(self.track_controllers[waysideIndex].track_blocks[x]._crossing_signal == True):
            return "Down"
        else:
            return "-"

    #adds block info table data
    def add_block_info_table_data(self, waysideIndex):
        """
        Updates block info table data

        Args:
            waysideIndex(int): index of wayside that needs to be changed 
        """
        self.blockInfoTable.clearContents()
        self.blockInfoTable.setRowCount(len(self.track_controllers[waysideIndex].track_blocks))

        data = []
        for x in range(len(self.track_controllers[waysideIndex].track_blocks)):
            tempData = [self.track_controllers[waysideIndex].track_blocks[x].number, " ", " "]
            tempData.append(self.display_crossing_signal(x, waysideIndex))
            data.append(tempData)

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                text = QtWidgets.QTableWidgetItem(str(item))
                self.blockInfoTable.setItem(i, j, text)
                if j == 0:
                    text.setFlags(text.flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    text.setFlags(text.flags() | Qt.ItemFlag.ItemIsEditable)
        
        #Method to print light signal statuses
        for x in range(self.track_controllers[waysideIndex].numBlocks):
            self.display_switch_pos(x, waysideIndex)
            self.display_light_signal(x, waysideIndex)
        
    
    def open_programmer_ui(self):
        """
        Open programmer UI and close Maintenance mode
        """
        self.programmer_ui.show()
        self.programmer_ui.update_ui()
        self.close()