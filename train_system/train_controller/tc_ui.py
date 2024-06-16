import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class EngineerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Train Controller UI")

        #the whole window will use a grid layout
        main_layout = QGridLayout()

        #the second level layout will use a vertical box layout
        level2_layout = QVBoxLayout()

        #the two header labels will use a vertical box layout
        header_layout = QVBoxLayout()

        #the dropdowns and their labels will use a grid layout
        dropdown_layout = QGridLayout()

        #the sliders and their labels will use a grid layout
        slider_layout = QGridLayout()

        #the test bench button and its label will use a vertical layout
        test_layout = QVBoxLayout()

        #create the Train Engineer label
        engineer_label = QLabel("Train Engineer")
        engineer_font = engineer_label.font()
        engineer_font.setPointSize(50)
        engineer_label.setFont(engineer_font)
        engineer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header_layout.addWidget(engineer_label)

        #create the prompt to input gain
        prompt_label = QLabel("Enter Proportional and Integral Gain for the selected train")
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header_layout.addWidget(prompt_label)

        #create the Line dropdown
        line_select = QComboBox()
        line_select.addItems(["1", "2", "3"])
        line_select.setFixedSize(400,50)
        dropdown_layout.addWidget(line_select, 3, 1)

        line_label = QLabel("Line")
        line_label.setFixedHeight(10)
        dropdown_layout.addWidget(line_label, 2, 1)

        #create the Train dropdown
        train_select = QComboBox()
        train_select.addItems(["1", "2", "3"])
        train_select.setFixedSize(400,50)
        dropdown_layout.addWidget(train_select, 3, 2)
        
        train_label = QLabel("Train")
        train_label.setFixedHeight(10)
        dropdown_layout.addWidget(train_label, 2, 2)

        #create the Kp slider
        kp_slider = QSlider()
        kp_slider.setMinimum(-10) #eventually use constants
        kp_slider.setMaximum(10)
        kp_slider.setFixedSize(50, 100)
        slider_layout.addWidget(kp_slider, 0, 1)

        kp_label = QLabel("Kp")
        kp_label.setFixedSize(15,15)
        slider_layout.addWidget(kp_label, 0, 0)

        #create the Ki slider
        ki_slider = QSlider()
        ki_slider.setMinimum(-10) #eventually use constants
        ki_slider.setMaximum(10)
        ki_slider.setFixedSize(50, 100)
        slider_layout.addWidget(ki_slider, 1, 1)

        ki_label = QLabel("Ki")
        ki_label.setFixedSize(10,10)
        slider_layout.addWidget(ki_label, 1, 0)

        #create the start button
        start_button = QPushButton("Start")
        start_button.setFixedSize(800,100) #figure out how to make button smaller but still spaced this way

        #create the test bench button
        test_button = QPushButton("")
        test_button.setFixedSize(50, 50)
        test_layout.addWidget(test_button)

        test_label = QLabel("Test Bench")
        test_label.setFixedSize(100, 50)
        test_layout.addWidget(test_label)

        #arrange the smaller layouts vertically
        level2_layout.addLayout(header_layout)
        level2_layout.addLayout(dropdown_layout)
        level2_layout.addLayout(slider_layout)
        level2_layout.addWidget(start_button)

        #combine all
        main_layout.addLayout(level2_layout, 0, 2)
        main_layout.addLayout(test_layout, 3, 0)

        #display the layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)



app = QApplication(sys.argv)
window = EngineerWindow()
window.show()

app.exec()