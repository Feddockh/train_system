import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
							 QHBoxLayout, QVBoxLayout, QLabel, 
							 QLineEdit, QPushButton, QTableWidget, 
							 QTableWidgetItem)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRect


# This class is used in conjunction with the TopNavigationBar class in
#	order to create the navigation bar at the top of each page in the
#	UX interface. It accepts the text to put in the rectangle, the font
#	size for the rectangle, as well as a boolean variable used to
#	signify if that is the tab selected or not in the menu. If it is,
#	there is a variance in the formatting of the rectangle and the text
#	within.
class TNB_RectangleWidget(QWidget) :
	
	# This method is the constructor for the RectangleWidget class.
	def __init__(self, text = "", font_size = 1, selected_bool = False):
		
		super().__init__()
		self.setFixedSize(153, 42)
		self.text = text
		self.font_size = font_size
		self.selected_bool = selected_bool
		
	# This method creates the formatting and look of the rectangle
	#	based off the paramter inputs.
	def paintEvent(self, event) :
		
		painter = QPainter(self)
		rect = event.rect()
		
		# set formatting characteristics based on selected_bool value
		if self.selected_bool :
			painter.setBrush(QColor("#FFFFFF"))
			font_weight = QFont.Weight.Bold
		else :
			painter.setBrush(QColor("#D9D9D9"))
			painter.setPen(QPen(QColor("#000000"), 1))
			painter.drawRect(rect)
			font_weight = QFont.Weight.Normal
			
		# draw text within rectangle
		painter.setPen(QColor("#000000"))
		font = QFont()
		font.setPointSize(self.font_size)
		font.setWeight(font_weight) # font_weight set in above if/else
		painter.setFont(font)
		painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text)

# This class is used to create the top navigation menu bar in each page
#	of the UX interface. It accepts an integer as a parameter, which
#	signifies the tab on the navigation bar that is selected. The tab
#	that is selected is formatted differently in the menu.
class TopNavigationBar(QWidget) :
	
	# This method is the constructor for the TopNavigationBar class.
	def __init__(self,selected_tab_id=0):
		
		super().__init__()
		self.selected_tab_id = selected_tab_id
		self.init_ui()
		
	# This method creates the formatting and look of the top naviation
	#	menu bar.
	def init_ui(self) :
		
		# build row of rectangles with hard default values
		top_row_layout = QHBoxLayout()
		top_row_layout.setSpacing(0)
		top_row_layout.setContentsMargins(0, 0, 0, 0)
		font_sizes = [18,18,18,18,12,12,12,12]
		texts = ["MBO", "CTC Office", "Track Model", "Train Model",
				 "SW Track\nController", "HW Track\nController",
				 "SW Train\nController", "HW Train\nController"]
		for i in range(8) :
			if self.selected_tab_id == i :
				rectangle = TNB_RectangleWidget(texts[i],font_sizes[i],
												True)
			else :
				rectangle = TNB_RectangleWidget(texts[i],font_sizes[i],
												False)
			top_row_layout.addWidget(rectangle)
			
		# add rectangles to layout
		self.setLayout(top_row_layout)

class CodeInputTable(QWidget):
	def __init__(self):
		super().__init__()
		
		# Initialize the table widget with 8 rows and 2 columns
		self.table_widget = QTableWidget()
		self.table_widget.setRowCount(8)
		self.table_widget.setColumnCount(2)
		
		# Set headers for the table
		self.table_widget.setHorizontalHeaderLabels(["Coded Text", "Variable Input"])
		
		# Populate the table with labels and line edits
		for row in range(8):
			coded_text_label = QLabel(f"Coded Text {row + 1}:")
			variable_input_edit = QLineEdit()
			self.table_widget.setCellWidget(row, 0, coded_text_label)
			self.table_widget.setCellWidget(row, 1, variable_input_edit)
			
		# Layout for the table widget
		table_layout = QVBoxLayout()
		table_layout.addWidget(self.table_widget)
		self.setLayout(table_layout)
		
	def get_table_data(self):
		data = []
		for row in range(self.table_widget.rowCount()):
			coded_text = self.table_widget.cellWidget(row, 0).text()
			variable_input = self.table_widget.cellWidget(row, 1).text()
			data.append((coded_text, variable_input))
		return data

# This class creates the main UX window display containing all elements
#	for the UX interface.
class MainWindow(QMainWindow):
	
	# This method is the constructor for the MainWindow class.
	def __init__(self):
		
		super().__init__()
		self.setWindowTitle('Train Model')
		self.setGeometry(100,100,1224,702)
		self.setFixedSize(1224, 702)

		# main widget and layout
		main_widget = QWidget()
		self.setCentralWidget(main_widget)
		main_layout = QVBoxLayout(main_widget)
		main_layout.setContentsMargins(0, 0, 0, 0)
		
		# change background color
		self.setStyleSheet("background-color: #FFFFFF;")
		
		# add top navigation bar
		main_layout.addWidget(TopNavigationBar(3)) # 3 = Train Model
		main_layout.addStretch()
		
		# add input table
		main_layout.addWidget(CodeInputTable())




# Create an instance of QApplication
app = QApplication(sys.argv)

# Create an instance of MainWindow
window = MainWindow()
window.show()

# Start the application event loop
sys.exit(app.exec())
