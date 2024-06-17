import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from tc_widgets import CircleWidget

GREEN = "#29C84C"
RED = "#FF4444"

class TestBenchWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test Bench")

class DriverWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Driver-Manual")

        #the left outputs will use a vertical layout
        left_out_layout = QVBoxLayout()

        #fault signals and labels will use a grid layout
        fault_layout = QGridLayout()

        #the faults and left outputs will use a vertical layout
        left_layout = QVBoxLayout()

        #the manual/automatic mode button and labels
        mode_layout = QVBoxLayout()

        #the setpoint speed box will use a grid layout
        setpoint_layout = QGridLayout()

        #the layout for the power box and labels will vertically aligned
        power_layout = QVBoxLayout()

        #the layout for the center of the page is vertically aligned
        center_layout = QVBoxLayout()

        #the whole page layout
        main_layout = QHBoxLayout()

        #create the engine fault signal
        engine_circle = CircleWidget(10, 300, GREEN)
        engine_label = QLabel("Train Engine")
        engine_label.setFixedSize(100, 50)

        #create the brake fault signal
        brake_circle = CircleWidget(20, 300, GREEN)
        brake_label = QLabel("Brake Function")
        engine_label.setFixedSize(100, 50)

        #create the signal fault signal
        signal_circle = CircleWidget(30, 300, RED)
        signal_label = QLabel("Signal Pickup")
        engine_label.setFixedSize(100, 50)

        #add fault circles and labels to their layout
        fault_layout.addWidget(engine_circle, 0, 0)
        fault_layout.addWidget(engine_label, 1, 0)
        fault_layout.addWidget(brake_circle, 0, 1)
        fault_layout.addWidget(brake_label, 1, 1)
        fault_layout.addWidget(signal_circle, 0, 2)
        fault_layout.addWidget(signal_label, 1, 2)

        #create label and stat line for current speed
        curr_speed_label = QLabel("Current Speed")
        curr_speed_label.setFixedSize(100, 25)
        curr_speed_stat = QLabel("00 mph") #maybe make a member variable that current speed can be set equal to in main file
        curr_speed_stat.setFixedSize(50, 25)

        #create label and stat line for commanded speed
        comm_speed_label = QLabel("Commanded Speed")
        comm_speed_label.setFixedSize(125, 25)
        comm_speed_stat = QLabel("00 mph")
        comm_speed_stat.setFixedSize(50, 25)

        #create label and stat line for commanded speed
        curr_authority_label = QLabel("Current Authority")
        curr_authority_label.setFixedSize(100, 25)
        curr_authority_stat = QLabel("00 ft")
        curr_authority_stat.setFixedSize(50, 25)

        #add stat lines and labels to left_out layout
        left_out_layout.addWidget(curr_speed_label)
        left_out_layout.addWidget(curr_speed_stat)
        left_out_layout.addWidget(comm_speed_label)
        left_out_layout.addWidget(comm_speed_stat)
        left_out_layout.addWidget(curr_authority_label)
        left_out_layout.addWidget(curr_authority_stat)

        #add faults and left outputs to entire left layout
        left_layout.addLayout(left_out_layout)
        left_layout.addLayout(fault_layout)

        #create control mode button and label
        mode_label = QLabel("Change Control Mode")
        mode_label.setFixedSize(150, 50)
        mode_button = QPushButton("")
        mode_button.setFixedSize(100, 100)

        #add button and label to the mode layout
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(mode_button)

        #create the adjustable arrow box for setpoint speed and its label
        speed_adjust = QSpinBox()
        speed_adjust.setMinimum(-10)
        speed_adjust.setMaximum(10)
        speed_adjust.setFixedSize(50, 50)

        setpoint_label = QLabel("Setpoint Speed")
        setpoint_label.setFixedSize(100, 50)

        #create the type input box for setpoint speed
        speed_input = QLineEdit()
        speed_input.setPlaceholderText("Enter Speed")
        speed_input.setFixedSize(75, 50)

        #create the service brake button and its label
        service_brake_button = QPushButton("X")
        service_brake_button.setFixedSize(75, 75)

        service_brake_label = QLabel("Service Brake")
        service_brake_label.setFixedSize(75, 50)

        #create the unit label for setpoint speed
        setpoint_mph_label = QLabel("mph")
        setpoint_mph_label.setFixedSize(25, 50)

        #add widgets to the setpoint layout
        setpoint_layout.addWidget(speed_adjust, 1, 0)
        setpoint_layout.addWidget(setpoint_label, 0, 0)
        setpoint_layout.addWidget(speed_input, 1, 1)
        setpoint_layout.addWidget(setpoint_mph_label, 1, 2)
        setpoint_layout.addWidget(service_brake_button, 3, 2)
        setpoint_layout.addWidget(service_brake_label, 2, 2)

        #create the label and output for power
        power_label = QLabel("Power")
        power_label.setFixedSize(50,50)

        power_stat = QLabel("00 kW")
        power_stat.setFixedSize(75, 50)

        #add labels to power layout
        power_layout.addWidget(power_label)
        power_layout.addWidget(power_stat)

        #add the control mode, setpoint speed, and power to the center layout
        center_layout.addLayout(mode_layout)
        center_layout.addLayout(setpoint_layout)
        center_layout.addLayout(power_layout)

        #add to the final main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(center_layout)

        #display the layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)


class EngineerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.test_window = None
        self.driver_window = None

        self.ki_val = 0
        self.kp_val = 0

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
        kp_slider.sliderMoved.connect(self.kp_slider_position)
        slider_layout.addWidget(kp_slider, 0, 1)

        self.kp_label = QLabel("Kp: 0")
        self.kp_label.setFixedSize(50,15)
        slider_layout.addWidget(self.kp_label, 0, 0)

        #create the Ki slider
        ki_slider = QSlider()
        ki_slider.setMinimum(-10) #eventually use constants
        ki_slider.setMaximum(10)
        ki_slider.setFixedSize(50, 100)
        ki_slider.sliderMoved.connect(self.ki_slider_position)
        slider_layout.addWidget(ki_slider, 1, 1)

        self.ki_label = QLabel("Ki: 0")
        self.ki_label.setFixedSize(50,10)
        slider_layout.addWidget(self.ki_label, 1, 0)

        #create the start button
        start_button = QPushButton("Start")
        start_button.setFixedSize(800,100) #figure out how to make button smaller but still spaced this way
        start_button.clicked.connect(self.navigate_driver_page)

        #create the test bench button
        test_button = QPushButton("")
        test_button.setFixedSize(50, 50)
        test_layout.addWidget(test_button)
        test_button.clicked.connect(self.navigate_test_bench)

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

    def navigate_test_bench(self, checked):
        #check that window is not already opened before opening
        if self.test_window is None:
            self.test_window = TestBenchWindow()
            self.test_window.show()
        else:
            self.test_window.close()
            self.test_window = None
    
    def navigate_driver_page(self, checked):
        #check that window is not already opened before opening
        if self.driver_window is None:
            self.driver_window = DriverWindow()
            self.driver_window.show()
        else:
            self.driver_window.close()
            self.driver_window = None

    def kp_slider_position(self, p):
        self.kp_val = p
        self.kp_label.setText("Kp: " + str(p))
    
    def ki_slider_position(self, p):
        self.ki_val = p
        self.ki_label.setText("Ki: " + str(p))

app = QApplication(sys.argv)
window = EngineerWindow()
window.show()

app.exec()