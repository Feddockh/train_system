import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from train_system.train_controller.tc_widgets import CircleWidget, EngineerTable
#from train_system.train_controller import TrainController
from train_system.common.gui_features import CustomTable
from train_system.train_controller.train_controller import TrainModel

GREEN = "#29C84C"
RED = "#FF4444"
DARK_GREY = "#C8C8C8"
YELLOW = "FFB800"

KP_MIN = 1
KP_MAX = 50

KI_MIN = 1
KI_MAX = 5

SPEED_MIN = 0
SPEED_MAX = 43



class TestBenchWindow(QMainWindow):
    def __init__(self, train_controller):
        super().__init__()

        self.setWindowTitle("Test Bench")

        """
        INTIALIZE DYNAMIC VARIABLES
        """
        self.train = train_controller

        #some train controlller variables will equal None if not updated
        #self.train.update_train_controller()

        #variables from the train controller
        #self.faults_list = self.train.faults
        #self.curr_speed = self.convert_to_mph(self.train.current_speed)
        #self.comm_speed = self.convert_to_mph(self.train.commanded_speed)
        #self.authority = self.convert_to_ft(self.train.authority)
        self.setpoint_speed = self.convert_to_mph(self.train.setpoint_speed)
        self.power = self.train.get_power_command() 
        self.light_status = self.train.lights.get_status()
        self.left_door = self.train.doors.get_left()
        self.right_door = self.train.doors.get_right()
        #self.temp = self.train.ac.get_current_temp()
        self.comm_temp = self.train.ac.get_commanded_temp()
        #self.position = self.train.position
        #self.destination = self.train.station
        self.serv_brake_status = self.train.brake.get_service_brake()
        self.emerg_brake_status = self.train.brake.get_emergency_brake()
        self.brake_on = self.train.brake.get_service_brake() or self.train.brake.get_emergency_brake()
        self.ki_val = self.train.engineer.get_kp()
        self.kp_val = self.train.engineer.get_ki()

        """
        UPDATE LIGHTS WITH NEW FUNCTION
        """
        self.train.lights.update_lights(self.train.train_model, self.train.elapsed_time, self.train.block)

        #the left outputs will use a vertical layout
        left_out_layout = QVBoxLayout()

        #fault signals and labels will use a grid layout
        fault_layout = QGridLayout()

        #the sliders and their labels will use a grid layout
        slider_layout = QGridLayout()

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
        self.engine_toggle_button = QPushButton("Off")
        self.engine_toggle_button.setFixedSize(75, 75)
        self.engine_toggle_button.setStyleSheet("background-color: #29C84C; color: black;")
        self.engine_toggle_button.setCheckable(True)
        self.engine_toggle_button.toggled.connect(self.engine_fault_toggled)

        engine_label = QLabel("Train Engine")
        engine_label.setFixedSize(100, 50)


        #create the brake fault signal
        self.brake_toggle_button = QPushButton("Off")
        self.brake_toggle_button.setFixedSize(75, 75)
        self.brake_toggle_button.setStyleSheet("background-color: #29C84C; color: black;")
        self.brake_toggle_button.setCheckable(True)
        self.brake_toggle_button.toggled.connect(self.brake_fault_toggled)
        
        brake_label = QLabel("Brake Function")
        brake_label.setFixedSize(100, 50)

        #create the signal fault signal
        self.signal_toggle_button = QPushButton("Off")
        self.signal_toggle_button.setFixedSize(75, 75)
        self.signal_toggle_button.setStyleSheet("background-color: #29C84C; color: black;")
        self.signal_toggle_button.setCheckable(True)
        self.signal_toggle_button.toggled.connect(self.signal_fault_toggled)
        signal_label = QLabel("Signal Pickup")
        signal_label.setFixedSize(100, 50)

        #add fault circles and labels to their layout
        fault_layout.addWidget(self.engine_toggle_button, 0, 0)
        fault_layout.addWidget(engine_label, 1, 0)
        fault_layout.addWidget(self.brake_toggle_button, 0, 1)
        fault_layout.addWidget(brake_label, 1, 1)
        fault_layout.addWidget(self.signal_toggle_button, 0, 2)
        fault_layout.addWidget(signal_label, 1, 2)

        #create label and stat line for current speed
        curr_speed_label = QLabel("Current Speed")
        curr_speed_label.setFixedSize(150, 25)

        #create a font that will be used for all headers
        header_font = curr_speed_label.font()
        header_font.setBold(True)
        header_font.setPointSize(12)
        curr_speed_label.setFont(header_font)
        
        #enter current speed
        self.curr_speed_stat = QLineEdit()
        self.curr_speed_stat.setFixedSize(75, 25)
        self.curr_speed_stat.setPlaceholderText("Enter Current Speed")
        self.curr_speed_stat.textChanged.connect(self.curr_speed_changed)


        #create label and stat line for commanded speed
        comm_speed_label = QLabel("Commanded Speed")
        comm_speed_label.setFixedSize(150, 25)
        comm_speed_label.setFont(header_font)

        #enter commanded speed
        self.comm_speed_stat = QLineEdit()
        self.comm_speed_stat.setFixedSize(75, 25)
        self.comm_speed_stat.setPlaceholderText("Enter Commanded Speed")
        self.comm_speed_stat.textChanged.connect(self.comm_speed_changed)

        #create label and stat line for commanded speed
        curr_authority_label = QLabel("Current Authority")
        curr_authority_label.setFixedSize(150, 25)
        curr_authority_label.setFont(header_font)

        #enter authority
        self.curr_authority_stat = QLineEdit()
        self.curr_authority_stat.setFixedSize(75, 25)
        self.curr_authority_stat.setPlaceholderText("Enter Authority")
        self.curr_authority_stat.textChanged.connect(self.authority_changed)

        #add stat lines and labels to left_out layout
        left_out_layout.addWidget(curr_speed_label)
        left_out_layout.addWidget(self.curr_speed_stat)
        left_out_layout.addWidget(comm_speed_label)
        left_out_layout.addWidget(self.comm_speed_stat)
        left_out_layout.addWidget(curr_authority_label)
        left_out_layout.addWidget(self.curr_authority_stat)

        #create the Kp slider
        kp_slider = QSlider() #make horizontal
        kp_slider.setMinimum(KP_MIN)
        kp_slider.setMaximum(KP_MAX) #check for kp and ki member variable/ default
        kp_slider.setFixedSize(50, 100)
        kp_slider.sliderMoved.connect(self.kp_slider_position)
        slider_layout.addWidget(kp_slider, 0, 1)

        self.kp_label = QLabel("Kp: 1")
        self.kp_label.setFixedSize(50,15)
        slider_layout.addWidget(self.kp_label, 0, 0)

        #create the Ki slider
        ki_slider = QSlider()
        ki_slider.setMinimum(KI_MIN)
        ki_slider.setMaximum(KI_MAX)
        ki_slider.setFixedSize(50, 100)
        ki_slider.sliderMoved.connect(self.ki_slider_position)
        slider_layout.addWidget(ki_slider, 1, 1)

        self.ki_label = QLabel("Ki: 1")
        self.ki_label.setFixedSize(50,10)
        slider_layout.addWidget(self.ki_label, 1, 0)

        #add faults and left outputs to entire left layout
        left_layout.addLayout(left_out_layout)
        left_layout.addLayout(slider_layout)
        left_layout.addLayout(fault_layout)


        #create the label for setpoint speed
        setpoint_label = QLabel("Setpoint Speed")
        setpoint_label.setFixedSize(125, 50)
        setpoint_label.setFont(header_font)

        #create the type input box for setpoint speed
        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter Speed")
        self.speed_input.setFixedSize(75, 50)
        self.speed_input.textChanged.connect(self.handle_setpoint_edit_changed)

        #create the service brake button and its label
        self.service_brake_button = QPushButton("X")
        self.service_brake_button.setFixedSize(75, 75)
        self.service_brake_button.setStyleSheet("background-color: #FFB800; color: black;")
        self.service_brake_button.setCheckable(True)
        if self.serv_brake_status == True: #checks if brake on other pages is on
            self.service_brake_button.setChecked(True)
        self.service_brake_button.toggled.connect(self.service_brake_toggled)

        service_brake_label = QLabel("Service Brake")
        service_brake_label.setFixedSize(125, 50)
        service_brake_label.setFont(header_font)

        #create the unit label for setpoint speed
        setpoint_mph_label = QLabel("mph")
        setpoint_mph_label.setFixedSize(25, 50)

        #add widgets to the setpoint layout
        setpoint_layout.addWidget(setpoint_label, 0, 0)
        setpoint_layout.addWidget(self.speed_input, 1, 1)
        setpoint_layout.addWidget(setpoint_mph_label, 1, 2)

        #create the label and output for power
        power_label = QLabel("Power")
        power_label.setFixedSize(50,50)
        power_label.setFont(header_font)

        power_stat = QLabel(str(self.power) + " kW")
        power_stat.setFixedSize(100, 50)

        #create a font for data
        data_font = power_stat.font()
        data_font.setPointSize(11)
        power_stat.setFont(data_font)
        power_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

        
        #add labels to power layout
        power_layout.addWidget(power_label)
        power_layout.addWidget(power_stat)

        #create brake layout
        brake_layout.addWidget(service_brake_label)
        brake_layout.addWidget(self.service_brake_button)

        #combine brake and power layouts
        power_and_brake_layout.addLayout(power_layout)
        power_and_brake_layout.addLayout(brake_layout)

        
        #create status buttons at bottom-center
        self.light_status_button = QPushButton("Lights On")
        self.light_status_button.setFixedSize(75, 75)
        self.light_status_button.setStyleSheet("background-color: #29C84C; color: black;")
        if(self.light_status == False):
            self.light_status_button.setChecked(True)
        self.light_status_button.setCheckable(True)
        self.light_status_button.toggled.connect(self.light_status_toggled)

        self.right_door_button = QPushButton("Right Door Closed")
        self.right_door_button.setFixedSize(75, 75)
        self.right_door_button.setStyleSheet("background-color: #29C84C; color: black;")
        if(self.right_door == True):
            self.right_door_button.setChecked(True)
        self.right_door_button.setCheckable(True)
        self.right_door_button.toggled.connect(self.right_door_toggled)

        self.left_door_button = QPushButton("Left Door Closed")
        self.left_door_button.setFixedSize(75, 75)
        self.left_door_button.setStyleSheet("background-color: #29C84C; color: black;")
        if(self.left_door == True):
            self.left_door_button.setChecked(True)
        self.left_door_button.setCheckable(True)
        self.left_door_button.toggled.connect(self.left_door_toggled)

        #add statuses to layout
        status_layout.addWidget(self.light_status_button, 1, 0)
        status_layout.addWidget(self.right_door_button, 0, 2)
        status_layout.addWidget(self.left_door_button, 1, 2)

        #add the control mode, setpoint speed, power, brake, and statuses to the center layout
        center_layout.addLayout(mode_layout)
        center_layout.addLayout(setpoint_layout)
        center_layout.addLayout(power_and_brake_layout)
        center_layout.addLayout(status_layout)


        #display current temp
        self.curr_temp = QLineEdit()
        self.curr_temp.setFixedSize(150, 50)
        self.curr_temp.setPlaceholderText("Enter Temp")
        self.curr_temp.textChanged.connect(self.curr_temp_changed)

        #display and change commanded temp
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

        #create line edits for location and destination
        loc_and_des_label = QLabel("Train Location and Destination")
        loc_and_des_label.setFixedSize(250, 50)
        loc_and_des_label.setFont(header_font)

        self.loc_edit = QLineEdit()
        self.loc_edit.setPlaceholderText("Enter Location")
        self.loc_edit.setFixedSize(100, 50)
        self.loc_edit.textChanged.connect(self.location_changed)

        self.des_edit = QLineEdit() 
        self.des_edit.setFixedSize(100, 50)
        self.des_edit.setPlaceholderText("Enter Destination")
        self.des_edit.textChanged.connect(self.destination_changed)

        #create emergency brake
        em_brake_label = QLabel("Emergency Brake")
        em_brake_label.setFixedSize(150, 50)
        em_brake_label.setFont(header_font)

        self.em_brake_button = QPushButton("!")
        self.em_brake_button.setFixedSize(100, 100)
        self.em_brake_button.setStyleSheet("background-color: #FF4444; color: white;")
        self.em_brake_button.setCheckable(True)
        if self.emerg_brake_status == True:
            self.em_brake_button.setChecked(True)
        self.em_brake_button.toggled.connect(self.emergency_brake_toggled)

        #add location, destination, and emergency brake to layout
        loc_and_brake_layout.addWidget(loc_and_des_label)
        loc_and_brake_layout.addWidget(self.loc_edit)
        loc_and_brake_layout.addWidget(self.des_edit)
        loc_and_brake_layout.addWidget(em_brake_label)
        loc_and_brake_layout.addWidget(self.em_brake_button)

        #add all right side components to the same layout
        right_layout.addWidget(self.curr_temp)
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
            self.auto_window = DriverWindow(self.train)
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
        if check:
            self.serv_brake_status = True
            self.train.brake.set_service_brake(True)
        else:
            self.serv_brake_status = False
            self.train.brake.set_service_brake(False)
    def emergency_brake_toggled(self, check):
        if check:
            self.emerg_brake_status = True
            self.train.brake.set_emergency_brake(True)
        else:
            self.emerg_brake_status = False
            self.train.brake.set_emergency_brake(False)
    """
    NEEDS ERROR CHECKING
    """
    def comm_temp_changed(self, x):
        if(x != ""):
            self.comm_temp = int(x)
            self.train.ac.set_commanded_temp(int(x))

    def engine_fault_toggled(self, check):
        if check:
            self.engine_toggle_button.setText("On")
            self.train.faults[0] = True
            self.train.train_model.faults[0] = True
            self.engine_toggle_button.setStyleSheet("background-color: #FF4444; color: black;")
        else:
            self.engine_toggle_button.setText("Off")
            self.train.faults[0] = False
            self.train.train_model.faults[0] = False
            self.engine_toggle_button.setStyleSheet("background-color: #29C84C; color: black;")

    def brake_fault_toggled(self, check):
        if check:
            self.brake_toggle_button.setText("On")
            self.train.faults[1] = True
            self.train.train_model.faults[1] = True
            self.brake_toggle_button.setStyleSheet("background-color: #FF4444; color: black;")
        else:
            self.brake_toggle_button.setText("Off")
            self.train.faults[1] = False
            self.train.train_model.faults[1] = False
            self.brake_toggle_button.setStyleSheet("background-color: #29C84C; color: black;")
    
    def signal_fault_toggled(self, check):
        if check:
            self.signal_toggle_button.setText("On")
            self.train.faults[2] = True
            self.train.train_model.faults[2] = True
            self.signal_toggle_button.setStyleSheet("background-color: #FF4444; color: black;")
        else:
            self.signal_toggle_button.setText("Off")
            self.train.faults[2] = False
            self.train.train_model.faults[2] = False
            self.signal_toggle_button.setStyleSheet("background-color: #29C84C; color: black;")

    def curr_speed_changed(self, x):
        if(x != ""):
            #self.curr_speed = int(x)
            self.train.train_model.set_current_speed(self.convert_to_ms(int(x)))
            self.train.current_speed = self.convert_to_ms(int(x))
            #self.train.simulate_timestep()

    def comm_speed_changed(self, x):
        if(x != ""):
            #self.comm_speed = int(x)
            self.train.train_model.set_commanded_speed(self.convert_to_ms(int(x)))
            self.train.commanded_speed = self.convert_to_ms(int(x))
    
    def authority_changed(self, x):
        if(x != ""):
            #self.authority = int(x)
            self.train.train_model.set_authority(self.convert_to_m(int(x)))
            self.train.authority = self.convert_to_m(int(x))
    
    def curr_temp_changed(self, x):
        if(x != ""):
            self.train.train_model.set_train_temp(int(x))
            self.train.ac.update_current_temp(self.train.train_model, "manual") #change mode later

    def light_status_toggled(self, check):
        if check:
            self.light_status_button.setText("Lights Off")
            self.light_status = False
            self.train.lights.set_lights(False)
            self.light_status_button.setStyleSheet("background-color: #FF4444; color: black;") 
        else:
            self.light_status_button.setText("Lights On")
            self.light_status = True
            self.train.lights.set_lights(True)
            self.light_status_button.setStyleSheet("background-color: #29C84C; color: black;")

    def right_door_toggled(self, check):
        if check:
            self.right_door_button.setText("Right Door Open")
            self.right_door = True
            self.train.doors.set_right(True)
            self.right_door_button.setStyleSheet("background-color: #FF4444; color: black;") 
        else:
            self.right_door_button.setText("Right Door Closed")
            self.right_door = False
            self.train.doors.set_right(False)
            self.right_door_button.setStyleSheet("background-color: #29C84C; color: black;")

    def left_door_toggled(self, check):
        if check:
            self.left_door_button.setText("Left Door Open")
            self.left_door = True
            self.train.doors.set_left(True)
            self.left_door_button.setStyleSheet("background-color: #FF4444; color: black;")

        else:
            self.left_door_button.setText("Left Door Closed")
            self.left_door = False
            self.train.doors.set_left(False)
            self.left_door_button.setStyleSheet("background-color: #29C84C; color: black;")

    def kp_slider_position(self, p):
        self.kp_val = p
        self.kp_label.setText("Kp: " + str(p))
        self.train.engineer.set_kp(self.kp_val)
    
    def ki_slider_position(self, p):
        self.ki_val = p
        self.ki_label.setText("Ki: " + str(p))
        self.train.engineer.set_ki(self.ki_val)
    
    """
    location is currently using the train model's position variable
    this would be the gps coordinates
    can change to block later
    """
    def location_changed(self, x):
        if(x != ""):
            self.train.train_model.set_position(float(x))
            self.train.position = float(x)

    def destination_changed(self, x):
        if(x != ""):
            self.train.train_model.set_station_name(x)
            self.train.station = x



class DriverWindow(QMainWindow): ###DriverWindow
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Driver") #Driver

        self.tm = TrainModel()

        self.test_window = None
        self.manual_window = None

        self.driver_mode = "manual"
        self.serv_brake_status = False
        self.emerg_brake_status = False
        self.power = 0
        self.brake_on = False
        self.light_status = False
        self.right_door = False
        self.left_door = False
        self.temp = 0

        self.setpoint_speed = 0
        


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
        self.engine_circle = CircleWidget(10, 200)
        if(self.tm.faults[0] == False):
            self.engine_circle.setColor(GREEN)
        else:
            self.engine_circle.setColor(RED)
        engine_label = QLabel("Train Engine")
        engine_label.setFixedSize(100, 50)

        #create the brake fault signal
        self.brake_circle = CircleWidget(20, 200)
        if(self.tm.faults[1] == False):
            self.brake_circle.setColor(GREEN)
        else:
            self.brake_circle.setColor(RED)
        brake_label = QLabel("Brake Function")
        brake_label.setFixedSize(100, 50)

        #create the signal fault signal
        self.signal_circle = CircleWidget(30, 200)
        if(self.tm.faults[2] == False):
            self.signal_circle.setColor(GREEN)
        else:
            self.signal_circle.setColor(RED)
        signal_label = QLabel("Signal Pickup")
        signal_label.setFixedSize(100, 50)

        #add fault circles and labels to their layout
        fault_layout.addWidget(self.engine_circle, 0, 0)
        fault_layout.addWidget(engine_label, 1, 0)
        fault_layout.addWidget(self.brake_circle, 0, 1)
        fault_layout.addWidget(brake_label, 1, 1)
        fault_layout.addWidget(self.signal_circle, 0, 2)
        fault_layout.addWidget(signal_label, 1, 2)

        #create label and stat line for current speed
        curr_speed_label = QLabel("Current Speed")
        curr_speed_label.setFixedSize(150, 25)

        #create a font that will be used for all headers
        header_font = curr_speed_label.font()
        header_font.setBold(True)
        header_font.setPointSize(12)
        curr_speed_label.setFont(header_font)
        
        self.curr_speed_stat = QLabel(str(self.convert_to_mph(self.tm.get_current_speed())) + " mph") 
        self.curr_speed_stat.setFixedSize(50, 25)
        self.curr_speed_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

        #create a font that will be used for
        data_font = self.curr_speed_stat.font()
        data_font.setPointSize(11)
        self.curr_speed_stat.setFont(data_font)

        #create label and stat line for commanded speed
        comm_speed_label = QLabel("Commanded Speed")
        comm_speed_label.setFixedSize(150, 25)
        comm_speed_label.setFont(header_font)

        self.comm_speed_stat = QLabel(str(self.convert_to_mph(self.tm.get_commanded_speed())) + " mph")
        self.comm_speed_stat.setFixedSize(50, 25)
        self.comm_speed_stat.setFont(data_font)
        self.comm_speed_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

        #create label and stat line for commanded speed
        curr_authority_label = QLabel("Current Authority")
        curr_authority_label.setFixedSize(150, 25)
        curr_authority_label.setFont(header_font)

        self.curr_authority_stat = QLabel(str(self.convert_to_ft(self.tm.authority)) + " ft")
        self.curr_authority_stat.setFixedSize(50, 25)
        self.curr_authority_stat.setFont(data_font)
        self.curr_authority_stat.setStyleSheet("background-color: #C8C8C8; color: black;")

        #button to refresh data from train controller/test bench
        refresh_button = QPushButton("Refresh")
        refresh_button.setFixedSize(50, 50)
        #refresh_button.clicked.connect(self.refresh)

        #add stat lines and labels to left_out layout
        left_out_layout.addWidget(curr_speed_label)
        left_out_layout.addWidget(self.curr_speed_stat)
        left_out_layout.addWidget(comm_speed_label)
        left_out_layout.addWidget(self.comm_speed_stat)
        left_out_layout.addWidget(curr_authority_label)
        left_out_layout.addWidget(self.curr_authority_stat)

        #add faults and left outputs to entire left layout
        left_layout.addLayout(left_out_layout)
        left_layout.addLayout(fault_layout)
        left_layout.addWidget(refresh_button)
    
        #create the type input box for setpoint speed
        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter Speed")
        self.speed_input.setFixedSize(75, 50)
        ###move to mode toggle function

        #create control mode button and label
        mode_label = QLabel("Change Control Mode")
        mode_label.setFixedSize(175, 50)
        mode_label.setFont(header_font)
        self.mode_button = QPushButton("")
        self.mode_button.setFixedSize(75, 75)
        self.mode_button.setCheckable(True)
        if self.driver_mode == "automatic":
            self.mode_button.setChecked(True)
            self.mode_button.setText("Auto")
            self.speed_input.setEnabled(False)
        else:
            self.mode_button.setChecked(False)
            self.mode_button.setText("Manual")
            self.speed_input.setEnabled(True)
        self.mode_button.toggled.connect(self.handle_toggle_driver_mode)###change to toggle instead of page naviagte


        #add button and label to the mode layout
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_button)


        #create the label for setpoint speed
        setpoint_label = QLabel("Setpoint Speed")
        setpoint_label.setFixedSize(125, 50)
        setpoint_label.setFont(header_font)

        #setpoint input moved before mode toggle

        #create the service brake button and its label
        self.service_brake_button = QPushButton("X")
        self.service_brake_button.setFixedSize(75, 75)
        self.service_brake_button.setStyleSheet("background-color: #FFB800; color: black;")
        self.service_brake_button.setCheckable(True)
        if self.serv_brake_status == True:
            self.service_brake_button.setChecked(True)
        self.service_brake_button.toggled.connect(self.handle_service_brake_toggled)

        service_brake_label = QLabel("Service Brake")
        service_brake_label.setFixedSize(125, 50)
        service_brake_label.setFont(header_font)

        #create the unit label for setpoint speed
        setpoint_mph_label = QLabel("mph")
        setpoint_mph_label.setFixedSize(25, 50)

        #add widgets to the setpoint layout
        setpoint_layout.addWidget(setpoint_label, 0, 0)
        setpoint_layout.addWidget(self.speed_input, 1, 1)
        setpoint_layout.addWidget(setpoint_mph_label, 1, 2)

        #create the label and output for power
        power_label = QLabel("Power")
        power_label.setFixedSize(50,50)
        power_label.setFont(header_font)

        self.power_stat = QLabel(str(self.power) + " kW")
        self.power_stat.setFixedSize(75, 50)
        self.power_stat.setFont(data_font)
        self.power_stat.setStyleSheet("background-color: #C8C8C8; color: black;")


        #add labels to power layout
        power_layout.addWidget(power_label)
        power_layout.addWidget(self.power_stat)

        #create brake layout
        brake_layout.addWidget(service_brake_label)
        brake_layout.addWidget(self.service_brake_button)

        #combine brake and power layouts
        power_and_brake_layout.addLayout(power_layout)
        power_and_brake_layout.addLayout(brake_layout)

        
        #create status labels at bottom-center
        if self.brake_on == True:
            self.brake_status_label = QLabel("Brake Status: On")
            self.brake_status_label.setFixedSize(75, 50)
            self.brake_status_label.setStyleSheet("background-color: #FF4444; color: white;")
        else:
            self.brake_status_label = QLabel("Brake Status: Off")
            self.brake_status_label.setFixedSize(75, 50)
            self.brake_status_label.setStyleSheet("background-color: #29C84C; color: white;")

        """FIX LIGHTS!!!!!!"""
        self.light_staus_label = QLabel("Lights On")
        self.light_staus_label.setFixedSize(75, 50)
        if(self.light_status == True): ###might change colors
            self.light_staus_label.setStyleSheet("background-color: #29C84C; color: white;")
        else:
            self.light_staus_label.setStyleSheet("background-color: #FF4444; color: white;")

        if(self.right_door == True):
            self.right_door_label = QLabel("Right Door Status: Open")
        else:
            self.right_door_label = QLabel("Right Door Status: Closed")
        self.right_door_label.setFixedSize(150, 50)

        if(self.left_door == True):
            self.left_door_label = QLabel("Left Door Status: Open")
        else:
            self.left_door_label = QLabel("Left Door Status: Closed")
        self.left_door_label.setFixedSize(150, 50)   

        #add statuses to layout
        status_layout.addWidget(self.brake_status_label, 0, 0) 
        status_layout.addWidget(self.light_staus_label, 1, 0)
        status_layout.addWidget(self.right_door_label, 0, 2)
        status_layout.addWidget(self.left_door_label, 1, 2)

        #add the control mode, setpoint speed, power, brake, and statuses to the center layout
        center_layout.addLayout(mode_layout)
        center_layout.addLayout(setpoint_layout)
        center_layout.addLayout(power_and_brake_layout)
        center_layout.addLayout(status_layout)

        #create a button to navigate to test bench
        test_button = QPushButton("Test Bench")
        test_button.setFixedSize(75, 75)
        test_button.clicked.connect(self.navigate_test_page)

        #display current temp
        self.curr_temp = QLabel("Train Temperature: " + str(self.temp) + " F")
        self.curr_temp.setFixedSize(150, 50)
        curr_temp_font = self.curr_temp.font()
        curr_temp_font.setBold(True)
        self.curr_temp.setFont(curr_temp_font)

        #display and changed commanded temp
        comm_temp_label = QLabel("Commanded Train Temp")
        comm_temp_label.setFixedSize(150, 50)

        self.comm_temp_input = QLineEdit() 
        self.comm_temp_input.setPlaceholderText("Enter Temp")
        self.comm_temp_input.setFixedSize(100, 50)
        self.comm_temp_input.textChanged.connect(self.handle_comm_temp_changed)###enabled/disabled depends on mode

        temp_unit_label = QLabel("F")
        temp_unit_label.setFixedSize(50, 50)

        comm_temp_layout.addWidget(comm_temp_label, 0, 0)
        comm_temp_layout.addWidget(self.comm_temp_input, 1, 0)
        comm_temp_layout.addWidget(temp_unit_label, 1, 1)

        #create labels for location and destination
        loc_and_des_label = QLabel("Train Location and Destination")
        loc_and_des_label.setFixedSize(250, 50)
        loc_and_des_label.setFont(header_font)

        self.loc_label = QLabel("Location: " + str(self.tm.get_track_block())) 
        self.loc_label.setFixedSize(100, 50)

        self.des_label = QLabel(str(self.tm.get_station_name()))
        self.des_label.setFixedSize(100, 50)

        #create emergency brake
        em_brake_label = QLabel("Emergency Brake")
        em_brake_label.setFixedSize(150, 50)
        em_brake_label.setFont(header_font)

        self.em_brake_button = QPushButton("!")
        self.em_brake_button.setFixedSize(100, 100)
        self.em_brake_button.setStyleSheet("background-color: #FF4444; color: white;")
        self.em_brake_button.setCheckable(True)
        if self.emerg_brake_status == True:
            self.em_brake_button.setChecked(True)
        self.em_brake_button.toggled.connect(self.handle_emergency_brake_toggled)

        #add location, destination, and emergency brake to layout
        loc_and_brake_layout.addWidget(loc_and_des_label)
        loc_and_brake_layout.addWidget(self.loc_label)
        loc_and_brake_layout.addWidget(self.des_label)
        loc_and_brake_layout.addWidget(em_brake_label)
        loc_and_brake_layout.addWidget(self.em_brake_button)

        #add all right side components to the same layout
        right_layout.addWidget(test_button)
        right_layout.addWidget(self.curr_temp)
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

    @pyqtSlot (bool)
    def handle_toggle_driver_mode(self, check: bool) -> None:
        if check:
            print("Automatic Mode")
            self.driver_mode = "automatic"
            #self.train.set_driver_mode("automatic")
            self.mode_button.setText("Automatic")
            self.speed_input.setEnabled(False)
        else:
            print("Manual Mode")
            self.driver_mode = "manual"
            #self.train.set_driver_mode("manual")
            self.mode_button.setText("Manual")
            self.speed_input.setEnabled(True)

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
    @pyqtSlot(str)
    def handle_setpoint_edit_changed(self, x: str) -> None:
        if(x != ""):
            self.setpoint_speed = float(x)
            #self.train.setpoint_speed = self.convert_to_ms(float(x))

    @pyqtSlot(bool)
    def handle_service_brake_toggled(self, check: bool) -> None:
        if check:
            self.serv_brake_status = True
            #self.train.brake.set_service_brake(True)
        else:
            self.serv_brake_status = False
            #self.train.brake.set_service_brake(False)

    @pyqtSlot(bool)
    def handle_emergency_brake_toggled(self, check: bool) -> None:
        if check:
            self.emerg_brake_status = True
            #self.train.brake.set_emergency_brake(True)
        else:
            self.emerg_brake_status = False
            #self.train.brake.set_emergency_brake(False)


    """
    NEEDS ERROR CHECKING
    """
    @pyqtSlot(str)
    def handle_comm_temp_changed(self, x: str) -> None:
        if(x != ""):
            self.tm.set_train_temp(int(x))
            #self.train.ac.set_commanded_temp(int(x))

    @pyqtSlot(TrainModel)
    def handle_mock_train_update(self, train_model: TrainModel) -> None:
        self.tm = train_model

        self.curr_speed_stat.setText(str(self.convert_to_mph(self.tm.get_current_speed())) + " mph")
        self.comm_speed_stat.setText(str(self.convert_to_mph(self.tm.get_commanded_speed())) + " mph")
        self.curr_authority_stat.setText(str(self.convert_to_ft(self.tm.authority)) + " ft")
        self.loc_label.setText("Location: " + str(self.tm.get_position()))
        self.des_label.setText(str(self.tm.get_station_name()))

        if(self.tm.faults[0] == False):
            self.engine_circle.setColor(GREEN)
        else:
            self.engine_circle.setColor(RED)

        if(self.tm.faults[1] == False):
            self.brake_circle.setColor(GREEN)
        else:
            self.brake_circle.setColor(RED)

        if(self.tm.faults[2] == False):
            self.signal_circle.setColor(GREEN)
        else:
            self.signal_circle.setColor(RED)

    ###??? and commanded temp
    @pyqtSlot(float)
    def handle_setpoint_speed_update(self, speed: float) -> None:
        self.setpoint_speed = self.convert_to_mph(speed)


    @pyqtSlot(float) 
    def handle_power_update(self, power: float) -> None:
        self.power = power
        self.power_stat.setText(str(self.power) + " kW")

    @pyqtSlot(bool)
    def handle_light_status_update(self, lights: bool) -> None:
        self.light_status = lights

        if(self.light_status == True): ###might change colors
            self.light_staus_label.setText("Lights On")
            self.light_staus_label.setStyleSheet("background-color: #29C84C; color: white;")
        else:
            self.light_staus_label.setText("Lights Off")
            self.light_staus_label.setStyleSheet("background-color: #FF4444; color: white;")

    @pyqtSlot(bool)
    def handle_left_door_update(self, door: bool) -> None:
        self.left_door = door

        if(self.left_door == True):
            self.left_door_label.setText("Left Door Status: Open")
        else:
            self.left_door_label.setText("Left Door Status: Closed")
            
    @pyqtSlot(bool)
    def handle_right_door_update(self, door: bool) -> None:
        self.right_door = door

        if(self.right_door == True):
            self.right_door_label.setText("Right Door Status: Open")
        else:
            self.right_door_label.setText("Right Door Status: Closed")

    @pyqtSlot(int)
    def handle_train_temp_update(self, temp: int) -> None:
        self.temp = temp

        self.curr_temp.setText("Train Temperature: " + str(self.temp) + " F")

    @pyqtSlot(bool)
    def handle_service_brake_update(self, brake: bool) -> None:
        self.serv_brake_status = brake

        self.brake_on = self.serv_brake_status or self.emerg_brake_status

        if self.serv_brake_status == True:
            self.service_brake_button.setChecked(True)

        if self.brake_on == True:
            self.brake_status_label.setText("Brake Status: On")
            self.brake_status_label.setFixedSize(75, 50)
            self.brake_status_label.setStyleSheet("background-color: #FF4444; color: white;")
        else:
            self.brake_status_label.setText("Brake Status: Off")
            self.brake_status_label.setFixedSize(75, 50)
            self.brake_status_label.setStyleSheet("background-color: #29C84C; color: white;")

    @pyqtSlot(bool)
    def handle_emerg_brake_update(self, brake: bool) -> None:
        self.emerg_brake_status = brake

        self.brake_on = self.serv_brake_status or self.emerg_brake_status

        if self.emerg_brake_status == True:
            self.em_brake_button.setChecked(True)

        if self.brake_on == True:
            self.brake_status_label.setText("Brake Status: On")
            self.brake_status_label.setFixedSize(75, 50)
            self.brake_status_label.setStyleSheet("background-color: #FF4444; color: white;")
        else:
            self.brake_status_label.setText("Brake Status: Off")
            self.brake_status_label.setFixedSize(75, 50)
            self.brake_status_label.setStyleSheet("background-color: #29C84C; color: white;")
    """
    @pyqtSlot(str)
    def handle_driver_mode_update(self, mode: str) -> None:
        self.driver_mode = mode

        if self.driver_mode == "automatic":
            self.mode_button.setChecked(True)
            self.mode_button.setText("Auto")
            self.speed_input.setEnabled(False)
        else:
            self.mode_button.setChecked(False)
            self.mode_button.setText("Manual")
            self.speed_input.setEnabled(True)"""
    






        

"""




        
        
        
        

        
"""
        


class EngineerWindow(QMainWindow):
    def __init__(self, train_controller):
        super().__init__()

        self.train = train_controller

        headers = ["Train", "Kp", "Ki"]
        self.data = []

        for i in range(1, 21):
            self.data.append([str(i), "-", "-"])

        self.table = EngineerTable("Set Kp and Ki", 21, 3, headers, self.data)

        self.table.table.itemChanged.connect(self.item_changed)

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.table)

        #display the layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)


    def item_changed(self, item):
        row = item.row()
        col = item.column()
        new_item = item.text()
        
        if(col == 1):
            self.data[row][col] = new_item
            self.train.engineer.set_kp(int(new_item))
        if(col == 2):
            self.data[row][col] = new_item
            self.train.engineer.set_kp(int(new_item))
            
        print(self.data)

