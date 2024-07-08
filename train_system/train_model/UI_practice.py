import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QLabel
from PyQt6.QtGui import QPalette, QColor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the main window properties
        self.setWindowTitle('Train Model')
        self.setGeometry(100, 100, 1222, 702)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a main layout
        main_layout = QVBoxLayout()

        # Create a horizontal layout for buttons and text inputs
        input_layout = QHBoxLayout()

        # Create and add text box inputs
        self.text_input1 = QLineEdit(self)
        self.text_input1.setPlaceholderText('Enter text here...')
        self.text_input1.returnPressed.connect(self.output_text)
        self.text_input2 = QLineEdit(self)
        self.text_input2.setPlaceholderText('Enter more text here...')
        self.text_input2.returnPressed.connect(self.output_text)
        input_layout.addWidget(self.text_input1)
        input_layout.addWidget(self.text_input2)

        # Create and add buttons
        button1 = QPushButton('Button 1', self)
        button1.clicked.connect(lambda: self.button_pressed('Button 1'))
        button2 = QPushButton('Button 2', self)
        button2.clicked.connect(lambda: self.button_pressed('Button 2'))
        input_layout.addWidget(button1)
        input_layout.addWidget(button2)

        # Create and add drop-down menus (combo boxes)
        dropdown = QComboBox(self)
        dropdown.addItems(['Red', 'Black', 'Blue'])
        dropdown.currentIndexChanged.connect(self.change_background_color)
        input_layout.addWidget(dropdown)

        # Add input layout to the main layout
        main_layout.addLayout(input_layout)

        # Create and add a label to display status or information
        self.label = QLabel('Just Testing out some PyQt Stuff', self)
        main_layout.addWidget(self.label)

        # Set the layout for the central widget
        central_widget.setLayout(main_layout)

    def output_text(self):
        text1 = self.text_input1.text()
        text2 = self.text_input2.text()
        print(f'Text Input 1: {text1}')
        print(f'Text Input 2: {text2}')

    def button_pressed(self, button_name):
        print(f'{button_name} pressed')

    def change_background_color(self, index):
        color = ['red', 'black', 'blue'][index]
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

# Create an instance of QApplication
app = QApplication(sys.argv)

# Create an instance of MainWindow
window = MainWindow()
window.show()

# Start the application event loop
sys.exit(app.exec())
