import os
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from sw_track_controller import TrackController

#Colors
DARK_GREY = "#C8C8C8"

class QMainWindow(QWidget):
    def setupUi(self, MainWindow):

        #Programmer UI name & size
        MainWindow.setObjectName("Programmer UI")
        MainWindow.resize(860, 520)

        #Central widget layout
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        #FileUpload button
        self.fileUploadPushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.fileUploadPushButton.setGeometry(QtCore.QRect(460, 55, 131, 31))
        self.fileUploadPushButton.setObjectName("pushButton")
        self.fileUploadPushButton.clicked.connect(self.getFileName)

        #Select PLC Program label
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(330, 60, 120, 20))
        self.label.setObjectName("label")

        #Table
        self.tableView = QtWidgets.QTableView(parent=self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(30, 200, 261, 231))
        self.tableView.setObjectName("tableView")

        #Scroll & Contents
        self.scrollArea = QtWidgets.QScrollArea(parent=self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(30, 50, 261, 87))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 259, 85))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)


        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(420, 170, 311, 31))
        self.comboBox.setObjectName("comboBox")

        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(330, 240, 481, 192))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(510, 210, 131, 21))
        self.textEdit.setObjectName("textEdit")

        self.comboBox_2 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(30, 170, 261, 31))
        self.comboBox_2.setObjectName("comboBox_2")

        self.comboBox_3 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(30, 20, 261, 31))
        self.comboBox_3.setObjectName("comboBox_3")

        MainWindow.setCentralWidget(self.centralwidget)

        #Menubar code
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 855, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.fileUploadPushButton.setText(_translate("MainWindow", "Upload File"))
        self.label.setText(_translate("MainWindow", "Select PLC Program:"))

    #Allows User to select PLC Program
    def getFileName(self):    
        file_filter = 'Data File (*.py)'
        response = QFileDialog.getOpenFileName (
            parent = self,
            caption = 'Select a file',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter = 'Data File (*.py)'
        )


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = QMainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
