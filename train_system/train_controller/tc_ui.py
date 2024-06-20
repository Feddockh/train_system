import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from tc_widgets import CircleWidget, TinyCircleWidget
from train_controller import TrainController

GREEN = "#29C84C"
RED = "#FF4444"
DARK_GREY = "#C8C8C8"
YELLOW = "FFB800"

KP_MIN = 0
KP_MAX = 50

KI_MIN = 0
KI_MAX = 5

SPEED_MIN = 0
SPEED_MAX = 43


class TestBenchWindow(QMainWindow):
    def __init__(self, train_controller):
        super().__init__()

        self.setWindowTitle("Test Bench")
        #speed and authority inputs
        #power output
        #fault toggles
        #current train temp input
        #open/close door
        #turn lights on/off
        #kp and ki instead of location???

class AutoDriverWindow(QMainWindow):
    def __init__(self, train_controller):
        super().__init__()

        self.setWindowTitle("Driver-Automatic")



class DriverWindow(QMainWindow):
    def __init__(self, train_controller):
        super().__init__()
        
        self.train = train_controller

        self.test_window = None
        self.auto_window = None

        self.faults_list = self.train.faults
        self.curr_speed = self.convert_to_mph(self.train.current_speed)
        self.comm_speed = self.convert_to_mph(self.train.commanded_speed)
        self.authority = self.convert_to_ft(self.train.authority)
        self.setpoint_speed = self.convert_to_mph(self.train.setpoint_speed)
        self.power = self.train.get_power_command() ###units???
        self.light_status = self.train.lights.get_status()
        self.left_door = self.train.doors.get_left()
        self.right_door = self.train.doors.get_right()
        self.temp = self.train.train_temp #units???
        self.comm_temp = self.train.ac.get_commanded_temp() #units???
        self.position = self.train.position #units???

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

        #the brake button and its label will be vertically aligned
        brake_layout = QVBoxLayout()

        #the power layout and brake layout will be horizontally aligned
        power_and_brake_layout = QHBoxLayout()

        #the layout for the status symbols will be a grid
        status_layout = QGridLayout()

        #the layout for the center of the page is vertically aligned
        center_layout = QVBoxLayout()

        #the layout for the commanded temp input and labels will be a grid
        comm_temp_layout = QGridLayout()

        #the layout for the location, destination, and brake will be vertically aligned
        loc_and_brake_layout = QVBoxLayout()
        
        #the layout for the right of the page is vertically aligned
        right_layout = QVBoxLayout()

        #the whole page layout
        main_layout = QHBoxLayout()

        #create the engine fault signal
        """
        ###THESE CIRCLES WILL NEED TO BE CONNECTED TO FAULT VARIABLES TO DETERMINE IF THEY ARE RED OR GREEN
        ---DONE---
        """
        if(self.faults_list[0] == False):
            engine_circle = CircleWidget(10, 300, GREEN)
        else:
            engine_circle = CircleWidget(10, 300, RED)
        engine_label = QLabel("Train Engine")
        engine_label.setFixedSize(100, 50)

        #create the brake fault signal
        if(self.faults_list[1] == False):
            brake_circle = CircleWidget(20, 300, GREEN)
        else:
            brake_circle = CircleWidget(20, 300, RED)
        brake_label = QLabel("Brake Function")
        brake_label.setFixedSize(100, 50)

        #create the signal fault signal
        if(self.faults_list[2] == False):
            signal_circle = CircleWidget(30, 300, GREEN)
        else:
            signal_circle = CircleWidget(30, 300, RED)
        signal_label = QLabel("Signal Pickup")
        signal_label.setFixedSize(100, 50)

        #add fault circles and labels to their layout
        fault_layout.addWidget(engine_circle, 0, 0)
        fault_layout.addWidget(engine_label, 1, 0)
        fault_layout.addWidget(brake_circle, 0, 1)
        fault_layout.addWidget(brake_label, 1, 1)
        fault_layout.addWidget(signal_circle, 0, 2)
        fault_layout.addWidget(signal_label, 1, 2)

        #create label and stat line for current speed
        curr_speed_label = QLabel("Current Speed")
        curr_speed_label.setFixedSize(150, 25)

        #create a font that will be used for all headers
        header_font = curr_speed_label.font()
        header_font.setBold(True)
        header_font.setPointSize(12)
        curr_speed_label.setFont(header_font)
        
        """
        ###ALL OF THESE STATS WITH 00... WILL NEED TO BE CONNECTED TO THE RIGHT VARIABLE
        THE LABELS WILL THEN CHANGE TO EITHER QLABEL(STR(STAT) + "MPH") OR SELF.LABEL.SETTEXT(STR(STAT) + "MPH")
        ---DONE---
        """
        curr_speed_stat = QLabel(str(self.curr_speed) + " mph") 
        curr_speed_stat.setFixedSize(50, 25)
        curr_speed_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

        #create a font that will be used for
        data_font = curr_speed_stat.font()
        data_font.setPointSize(11)
        curr_speed_stat.setFont(data_font)

        #create label and stat line for commanded speed
        comm_speed_label = QLabel("Commanded Speed")
        comm_speed_label.setFixedSize(150, 25)
        comm_speed_label.setFont(header_font)

        comm_speed_stat = QLabel(str(self.comm_speed) + " mph")
        comm_speed_stat.setFixedSize(50, 25)
        comm_speed_stat.setFont(data_font)
        comm_speed_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

        #create label and stat line for commanded speed
        curr_authority_label = QLabel("Current Authority")
        curr_authority_label.setFixedSize(150, 25)
        curr_authority_label.setFont(header_font)

        curr_authority_stat = QLabel(str(self.authority) + " ft")
        curr_authority_stat.setFixedSize(50, 25)
        curr_authority_stat.setFont(data_font)
        curr_authority_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

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

        """
        ADD FUNCTION TO NAVIGATE TO DRIVER-AUTOMATIC PAGE
        ---DONE---
        """
        #create control mode button and label
        mode_label = QLabel("Change Control Mode")
        mode_label.setFixedSize(175, 50)
        mode_label.setFont(header_font)
        mode_button = QPushButton("")
        mode_button.setFixedSize(75, 75)
        mode_button.clicked.connect(self.navigate_automatic_mode)

        #add button and label to the mode layout
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(mode_button)


        """
        ###CONNECT THIS VALUE TO MEMBER VARIABLE AND LINE EDIT
        CONVERT FROM INPUTTED M/S TO MPH
        ---DONE---
        """
        #create the adjustable arrow box for setpoint speed and its label
        speed_adjust = QSpinBox() #adjust by 5
        speed_adjust.setMinimum(SPEED_MIN)
        speed_adjust.setMaximum(SPEED_MAX) 
        speed_adjust.setFixedSize(50, 50)
        speed_adjust.valueChanged.connect(self.setpoint_spinbox_changed)

        setpoint_label = QLabel("Setpoint Speed")
        setpoint_label.setFixedSize(125, 50)
        setpoint_label.setFont(header_font)

        """
        ###CONNECT THIS VALUE TO MEMBER VARIABLE AND SPINBOX
        SAME AS ABOVE
        ---DONE---
        """
        #create the type input box for setpoint speed
        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter Speed")
        self.speed_input.setFixedSize(75, 50)
        self.speed_input.textChanged.connect(self.setpoint_edit_changed)

        #create the service brake button and its label
        """
        ###CONNECT TO SPEED AND BRAKE STATUS
        WRITE FUNCTION FOR WHEN CLICKED

        """
        service_brake_button = QPushButton("X")
        service_brake_button.setFixedSize(75, 75)
        service_brake_button.setStyleSheet("background-color: #FFB800; color: black;")
        #service_brake_button.setCheckable(True)
        service_brake_button.clicked.connect(self.service_brake_toggled)

        service_brake_label = QLabel("Service Brake")
        service_brake_label.setFixedSize(125, 50)
        service_brake_label.setFont(header_font)

        #create the unit label for setpoint speed
        setpoint_mph_label = QLabel("mph")
        setpoint_mph_label.setFixedSize(25, 50)

        #add widgets to the setpoint layout
        setpoint_layout.addWidget(speed_adjust, 1, 0)
        setpoint_layout.addWidget(setpoint_label, 0, 0)
        setpoint_layout.addWidget(self.speed_input, 1, 1)
        setpoint_layout.addWidget(setpoint_mph_label, 1, 2)

        #create the label and output for power
        power_label = QLabel("Power")
        power_label.setFixedSize(50,50)
        power_label.setFont(header_font)

        """
        ###CONNECT TO MEMBER VARIABLE (SIMILAR TO OTHER STATS)
        ---DONE---
        """
        power_stat = QLabel(str(self.power) + " kW")
        power_stat.setFixedSize(75, 50)
        power_stat.setFont(data_font)
        power_stat.setStyleSheet("background-color: #C8C8C8; color: black;")


        #add labels to power layout
        power_layout.addWidget(power_label)
        power_layout.addWidget(power_stat)

        #create brake layout
        brake_layout.addWidget(service_brake_label)
        brake_layout.addWidget(service_brake_button)

        #combine brake and power layouts
        power_and_brake_layout.addLayout(power_layout)
        power_and_brake_layout.addLayout(brake_layout)

        
        #create status labels at bottom-center
        """
        ###CONNECT ALL STATUSES TO MEMBER VARIABLE
        WILL DETERMINE BACKGROUND COLOR FOR BRAKE AND LIGHT
        WILL DETERMINE TEXT AS SAID ABOVE FOR DOORS
        """
        brake_status_label = QLabel("Brake Status")
        brake_status_label.setFixedSize(75, 50)
        brake_status_label.setStyleSheet("background-color: #29C84C; color: white;")

        """---DONE---"""
        light_staus_label = QLabel("Light Status")
        light_staus_label.setFixedSize(75, 50)
        if(self.light_status == True): ###might change colors
            light_staus_label.setStyleSheet("background-color: #29C84C; color: white;")
        else:
            light_staus_label.setStyleSheet("background-color: #FF4444; color: white;")

        """---DONE---"""
        if(self.right_door == True):
            right_door_label = QLabel("Right Door Status: Open")
        else:
            right_door_label = QLabel("Right Door Status: Closed")
        right_door_label.setFixedSize(150, 50)

        """---DONE---"""
        if(self.left_door == True):
            left_door_label = QLabel("Left Door Status: Open")
        else:
            left_door_label = QLabel("Left Door Status: Closed")
        left_door_label.setFixedSize(150, 50)   

        #add statuses to layout
        status_layout.addWidget(brake_status_label, 0, 0) 
        status_layout.addWidget(light_staus_label, 1, 0)
        status_layout.addWidget(right_door_label, 0, 2)
        status_layout.addWidget(left_door_label, 1, 2)

        #add the control mode, setpoint speed, power, brake, and statuses to the center layout
        center_layout.addLayout(mode_layout)
        center_layout.addLayout(setpoint_layout)
        center_layout.addLayout(power_and_brake_layout)
        center_layout.addLayout(status_layout)

        #create a button to navigate to test bench
        """
        CREATE A FUNCTION TO NAVIGATE TO TEST BENCH
        ---DONE---
        """
        test_button = QPushButton("Test Bench")
        test_button.setFixedSize(75, 75)
        test_button.clicked.connect(self.navigate_test_page)

        #display current temp
        """
        ###CONNECT CURRENT AND COMMANDED TRAIN TEMP VARIABLES
        CURR TEMP WILL BE DISPLAYED AND EDITED LIKE PREVIOUS STATS
        COMM TEMP WILL BE CHANGED LIKE OTHER INPUTS
        ---DONE---
        """
        curr_temp = QLabel("Train Temperature: " + str(self.temp) + " F")
        curr_temp.setFixedSize(150, 50)
        curr_temp_font = curr_temp.font()
        curr_temp_font.setBold(True)
        curr_temp.setFont(curr_temp_font)

        #display and changed commanded temp
        comm_temp_label = QLabel("Commanded Train Temp")
        comm_temp_label.setFixedSize(150, 50)

        self.comm_temp_input = QLineEdit()
        self.comm_temp_input.setPlaceholderText("Enter Temp")
        self.comm_temp_input.setFixedSize(100, 50)
        self.comm_temp_input.textChanged.connect(self.comm_temp_changed)

        temp_unit_label = QLabel("F")
        temp_unit_label.setFixedSize(50, 50)

        comm_temp_layout.addWidget(comm_temp_label, 0, 0)
        comm_temp_layout.addWidget(self.comm_temp_input, 1, 0)
        comm_temp_layout.addWidget(temp_unit_label, 1, 1)

        #create labels for location and destination
        loc_and_des_label = QLabel("Train Location and Destination")
        loc_and_des_label.setFixedSize(250, 50)
        loc_and_des_label.setFont(header_font)

        """###CONNECT TO MEMBER VARIABLES FOR LOCATION AND DESTINATION
        WILL BE CHANGED LIKE OTHER LABEL STATS
        """
        """---DONE---"""
        loc_label = QLabel("Block: " + str(self.position)) 
        loc_label.setFixedSize(100, 50)

        des_label = QLabel("South Hills Village") ###will update with tc function
        des_label.setFixedSize(100, 50)

        #create emergency brake
        em_brake_label = QLabel("Emergency Brake")
        em_brake_label.setFixedSize(150, 50)
        em_brake_label.setFont(header_font)

        """
        ###CONNECT TO EMERGENCY BRAKE, BRAKE STATUS, AND SPEED
        CREATE FUNCTION FOR WHEN CLICKED
        """
        em_brake_button = QPushButton("!")
        em_brake_button.setFixedSize(100, 100)
        em_brake_button.setStyleSheet("background-color: #FF4444; color: white;")

        #add location, destination, and emergency brake to layout
        loc_and_brake_layout.addWidget(loc_and_des_label)
        loc_and_brake_layout.addWidget(loc_label)
        loc_and_brake_layout.addWidget(des_label)
        loc_and_brake_layout.addWidget(em_brake_label)
        loc_and_brake_layout.addWidget(em_brake_button)

        #add all right side components to the same layout
        right_layout.addWidget(test_button)
        right_layout.addWidget(curr_temp)
        right_layout.addLayout(comm_temp_layout)
        right_layout.addLayout(loc_and_brake_layout)

        #add to the final main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(right_layout)

        #display the layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def navigate_automatic_mode(self, checked):
        #check that window is not already opened before opening
        if self.auto_window is None:
            self.auto_window = AutoDriverWindow(self.train)
            self.auto_window.show()
        else:
            self.auto_window.close()
            self.auto_window = None

    def navigate_test_page(self, checked):
        #check that window is not already opened before opening
        if self.test_window is None:
            self.test_window = TestBenchWindow(self.train)
            self.test_window.show()
        else:
            self.test_window.close()
            self.test_window = None

    def convert_to_mph(self, ms_speed):
        mph = ms_speed * 2.23694
        return mph
    
    def convert_to_ms(self, mph_speed):
        ms = mph_speed / 2.23694
        return ms
    
    def convert_to_ft(self, m):
        ft = m * 3.28084
        return ft
    
    def convert_to_m(self, ft):
        m = ft / 3.28084
        return m

    def setpoint_spinbox_changed(self, x):
        self.setpoint_speed = x
        self.train.setpoint_speed = self.convert_to_ms(x)


    """
    NEEDS ERROR CHECKING
    """
    def setpoint_edit_changed(self, x):
        if(x != ""):
            self.setpoint_speed = float(x)
            self.train.setpoint_speed = self.convert_to_ms(float(x))

    """
    DOESNT WORK
    """
    def service_brake_toggled(self, check):
        self.comm_speed = 0
        self.setpoint_speed = 0
        self.train.setpoint_speed = 0
        self.train.commanded_speed = 0

    """
    NEEDS ERROR CHECKING
    """
    def comm_temp_changed(self, x):
        if(x != ""):
            self.comm_temp = int(x)
            self.train.ac.set_commanded_temp(int(x))




class EngineerWindow(QMainWindow):
    def __init__(self, train_controller):
        super().__init__()

        self.test_window = None
        self.driver_window = None
        self.train = train_controller

        """
        ###I THINK USING SOMETHING LIKE THIS WILL BE A GOOD WAY TO CONNECT VARIABLES
        I HAVE MEMBER VARIABLES WHICH ARE CONNECTED TO YOURS???
        """
        self.ki_val = self.train.engineer.get_kp()
        self.kp_val = self.train.engineer.get_ki()

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


        """
        ###EVENTUALLY CONNECT LINE AND TRAIN OPTIONS TO BE INCLUDED AS A LIST
        """
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

        """
        ###CONNECT KP AND KI VARIABLES - DONE
        FIX MIN AND MAX
        SEE SELF.KP(OR KI)_SLIDER_POSITION FUNCTION FOR HOW VARIABLES ARE CHANGING ON SCREEN
        """
        #create the Kp slider
        kp_slider = QSlider() #make horizontal
        kp_slider.setMinimum(KP_MIN) #eventually use constants
        kp_slider.setMaximum(KP_MAX) #check for kp and ki member variable/ default
        kp_slider.setFixedSize(50, 100)
        kp_slider.sliderMoved.connect(self.kp_slider_position)
        slider_layout.addWidget(kp_slider, 0, 1)

        self.kp_label = QLabel("Kp: 0") #font increase
        self.kp_label.setFixedSize(50,15)
        slider_layout.addWidget(self.kp_label, 0, 0)

        #create the Ki slider
        ki_slider = QSlider()
        ki_slider.setMinimum(KI_MIN) #eventually use constants
        ki_slider.setMaximum(KI_MAX)
        ki_slider.setFixedSize(50, 100)
        ki_slider.sliderMoved.connect(self.ki_slider_position)
        slider_layout.addWidget(ki_slider, 1, 1)

        self.ki_label = QLabel("Ki: 0")
        self.ki_label.setFixedSize(50,10)
        slider_layout.addWidget(self.ki_label, 1, 0)

        #create the start button
        start_button = QPushButton("Start")
        start_button.setFixedSize(800,100) #figure out how to make button smaller but still spaced this way
        start_button.setStyleSheet("background-color: #29C84C; color: white;")
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
            self.test_window = TestBenchWindow(self.train)
            self.test_window.show()
        else:
            self.test_window.close()
            self.test_window = None
    
    def navigate_driver_page(self, checked):
        #check that window is not already opened before opening
        if self.driver_window is None:
            self.driver_window = DriverWindow(self.train)
            self.driver_window.show()
        else:
            self.driver_window.close()
            self.driver_window = None

    def kp_slider_position(self, p):
        self.kp_val = p
        self.kp_label.setText("Kp: " + str(p))
        self.train.engineer.set_kp(self.kp_val)
    
    def ki_slider_position(self, p):
        self.ki_val = p
        self.ki_label.setText("Ki: " + str(p))
        self.train.engineer.set_ki(self.ki_val)
    
    def get_ki_val(self):
        return self.ki_val
    
    def get_kp_val(self):
        return self.kp_val

