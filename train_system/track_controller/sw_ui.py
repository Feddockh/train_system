import os
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic, QtWidgets
from sw_widgets import RectangleWidget
from sw_track_controller import TrackController

#Colors
DARK_GREY = "#C8C8C8"

class CenterDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignCenter


class ProgrammerUI(QtWidgets.QMainWindow):

    #def setupUi(self, MainWindow):
    def __init__(self, track_controller):
        super().__init__()

        #Setting track controller
        self.track_controller = track_controller

        #Programmer UI name & size
        self.setObjectName("Programmer UI")
        self.resize(1222, 702)

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        #Used in multiple widgets
        waysides = ['Wayside 1']
        lines = ['Blue Line']

        #Creating universal font
        font = QtGui.QFont()
        font.setPointSize(13)

        #FileUpload button
        self.fileUploadPushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.fileUploadPushButton.setGeometry(QtCore.QRect(700, 60, 131, 31))
        self.fileUploadPushButton.setObjectName("pushButton")
        self.fileUploadPushButton.clicked.connect(self.getFileName)
        self.fileUploadPushButton.setFont(font)

        #Select PLC Program label
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(550, 60, 120, 20))
        self.label.setObjectName("label")
        self.label.setFont(font)

        """
        #Create Rectange for Wayside Table
        waysideRec = RectangleWidget(200, 100, 100, 100, DARK_GREY)
        test_layout.addWidget(waysideRec, 0, 0)
        """

        #Wayside Data Table
        self.tableView = QtWidgets.QTableView(parent=self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(60, 250, 415, 400))
        self.tableView.setObjectName("tableView")

        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setItemDelegate(CenterDelegate(self.tableView))

        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Block #', 'Occupied', 'Switch', 'Signal'])
        self.tableView.setModel(self.model)
        self.add_wayside_table_data()
        self.tableView.setFont(font)

        #Wayside Data Table ComboBox
        self.comboBox_2 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(60, 215, 415, 35))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItems(waysides)
        self.comboBox_2.setFont(font)

        #Waysides and Blocks their responsible for table
        self.waysideBlkTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.waysideBlkTable.setGeometry(QtCore.QRect(60, 80, 415, 100))
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
        #self.waysideBlkTable.resizeColumnsToContents()
        self.waysideBlkTable.setFont(font)

        #Combo box for waysideBlockTable
        self.comboBox_3 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(60, 45, 415, 35))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItems(lines)
        self.comboBox_3.setFont(font)

        #Block info table
        self.blockInfoTable = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.blockInfoTable.setGeometry(QtCore.QRect(550, 330, 615, 320))
        self.blockInfoTable.setObjectName("blockInfoTable")
        self.blockInfoTable.setColumnCount(6)
        self.blockInfoTable.setRowCount(len(self.track_controller.track_occupancies))

        self.blockInfoTable.verticalHeader().setVisible(False)
        self.blockInfoTable.setItemDelegate(CenterDelegate(self.tableView))
        self.blockInfoTable.setFont(font)
        self.blockInfoTable.setHorizontalHeaderLabels(['Block #', 'Occupancy', 'Authority[ft]', 'Speed[mph]','Switch','Signal'])
        self.blockInfoTable.horizontalHeader().setFont(font)
        self.add_block_info_table_data()

        #Combobox for block info table
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(570, 220, 575, 35))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(lines)
        self.comboBox.setFont(font)

        #TextEdit box for block info table
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(750, 270, 200, 40))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setFont(font)

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
        self.track_controller.get_PLC_program(response[0])

    #Converts track_occupancies into "occupied/in operation"
    def display_occupied_tracks(self, i):
        if (self.track_controller.track_occupancies[i] == False):
            return "In Operation"
        else:
            return "Occupied"
    
    #Converts switch_states into values they're connected to 
    def display_switch_pos(self, i):
        if(self.track_controller.switch_states == False and i == 5):
            return "6"
        elif(self.track_controller.switch_states == False and i == 6):
            return "5"
        elif(self.track_controller.switch_states == False and i == 11):
            return "-"
        elif(self.track_controller.switch_states == True and i == 5):
            return "11"
        elif(self.track_controller.switch_states == True and i == 6):
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

        for row in data:
            items = [QtGui.QStandardItem(item) for item in row]
            self.model.appendRow(items)

    def add_block_info_table_data(self):
        data = [
            ['1', self.display_occupied_tracks(0), self.track_controller.train_authorities[0], self.track_controller.train_authorities[0] , '-', '-'],
            ['2', self.display_occupied_tracks(1), self.track_controller.train_authorities[1], self.track_controller.train_authorities[1],'-', '-'],
            ['3', self.display_occupied_tracks(2), self.track_controller.train_authorities[2], self.track_controller.train_authorities[2],'-', '-'],
            ['4', self.display_occupied_tracks(3), self.track_controller.train_authorities[3], self.track_controller.train_authorities[3],'-', '-'],
            ['5', self.display_occupied_tracks(4), self.track_controller.train_authorities[4], self.track_controller.train_authorities[4],self.display_switch_pos(5), '-'],
            ['6', self.display_occupied_tracks(5), self.track_controller.train_authorities[5], self.track_controller.train_authorities[5],self.display_switch_pos(6), '-'],
            ['7', self.display_occupied_tracks(6), self.track_controller.train_authorities[6], self.track_controller.train_authorities[6],'-', '-'],
            ['8', self.display_occupied_tracks(7), self.track_controller.train_authorities[7], self.track_controller.train_authorities[7],'-', '-'],
            ['9', self.display_occupied_tracks(8), self.track_controller.train_authorities[8], self.track_controller.train_authorities[8],'-', '-'],
            ['10', self.display_occupied_tracks(9), self.track_controller.train_authorities[9], self.track_controller.train_authorities[9],'-', '-'],
            ['11', self.display_occupied_tracks(10), self.track_controller.train_authorities[10], self.track_controller.train_authorities[10],self.display_switch_pos(11), '-'],
            ['12', self.display_occupied_tracks(11), self.track_controller.train_authorities[11], self.track_controller.train_authorities[11],'-', '-'],
            ['13', self.display_occupied_tracks(12), self.track_controller.train_authorities[12], self.track_controller.train_authorities[12],'-', '-'],
            ['14', self.display_occupied_tracks(13), self.track_controller.train_authorities[13], self.track_controller.train_authorities[13],'-', '-'],
            ['15', self.display_occupied_tracks(14), self.track_controller.train_authorities[14], self.track_controller.train_authorities[14],'-', '-']
        ]

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.blockInfoTable.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))

    def add_wayside_blk_table_data(self):
        data = [
            ['Wayside 1', '1 - 15']
        ]

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.waysideBlkTable.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
