from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
import paramiko
import json
from collections import deque as dq

# from train_system.common.conversions import time_to_seconds
# from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

HOST= '192.168.0.114'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'

"""
setStation
-uses beacon data to know and update upcoming station
-do we keep this station displayed after leaving?
"""

'''
Storing previous beacon data: How are we going to do that and what will it look like
'''

'''
# Functions with the word "update" in the name are updated from the Train Model and takes the Train Model as an argument
# Train Controller only talks with Train Model
# Train Model needed for initialization
'''

class TrainController(QObject):
    # Signals
    power_changed = pyqtSignal(float)
    position_changed = pyqtSignal(float)
    lights_changed = pyqtSignal(bool)
    doors_changed = pyqtSignal(bool[2])
    commanded_temp_changed = pyqtSignal(int)
    service_brake_changed = pyqtSignal(bool)
    emergency_brake_changed = pyqtSignal(bool)
    faults_fixed = pyqtSignal(bool)
    

    def __init__(self, ssh=None, line_name: str = "green", id: int = 0, kp: float = 25, ki: float = 0.1):
        super().__init__()
        self.hardware = True if ssh else False
        print(f"Hardware: {self.hardware}")
        self.time_step = 1
        self.train_length = 32.2  # 32.2 meters

        ## Initialize objects
        self.train_model = TrainModel()  # Used to store data received from Train Model. No computations done in the object
        self.engineer = self.Engineer(kp, ki) # Engineer holds Kp and Ki and is the only one that can set them
        self.brake = self.Brake()       # Brake holds service and emergency brake status
        self.engine = self.Engine(ssh)     # Engine calculates power command and simulates train response
        self.doors = self.Doors()       # Doors holds left and right door status
        self.lights = self.Lights()     # Lights holds light status
        self.ac = self.AC(self.train_model.train_temp)             # AC holds temperature status
        self.line = Line(line_name)
        
        self.line.load_track_blocks()
        self.line.load_routes()
        self.reset_route()  # Initialize track block, position, and polarity

        # Driver variables
        self.driver_mode = "manual" # Driver mode can be "automatic" or "manual"
        self.setpoint_speed = 0     # Setpoint speed for manual mode
        self.MAX_SPEED = 21.67

        # Train Controller Calculated Variables
        self.maintenance_mode = False     # Maintenance status of the train

        # Train Model inputs (purely made for convenience)
        # THESE VALUES WILL RECEIVE NO CALCULATIONS (except for current speed FOR NOW)
        self.current_speed = self.train_model.current_speed    # Current speed of the train
        self.commanded_speed = self.train_model.commanded_speed  # Commanded speed from the Train Model (CTC or MBO)
        self.authority = self.train_model.authority        # Authority from the Train Model (CTC or MBO)
        self.faults = self.train_model.faults           # Fault statuses from the Train Model (list of bools)

        ## Connections
        self.call_power_command = 0

        self.train_model.train_temp_changed.connect(self.ac.set_current_temp)
        self.train_model.faults_changed.connect(self.update_fault_status)
        self.train_model.authority_changed.connect(self.update_authority)
        self.train_model.commanded_speed_changed.connect(self.update_commanded_speed)
        self.train_model.current_speed_changed.connect(self.update_current_speed)
        
        
    # ## THIS IS NO LONGER USED ##
    # def update_train_controller(self, train_model=None):
    #     if train_model:
    #         self.train_model = train_model
            
    #     # Update variables with train model input
    #     self.current_speed = self.train_model.get_current_speed()
    #     self.commanded_speed = self.train_model.get_commanded_speed()
    #     self.authority = self.train_model.get_authority()
    #     self.ac.current_temp = self.train_model # Update AC temperature

    #     self.update_fault_status(self.train_model)  # Update fault status and call maintenance if necessary
        
    #     self.lights.update_lights(self.time)  # Update lights based on time

    #     self.calculate_position(self.time_step) # Update Position and polarity
        
    #     self.calculate_power_command(self.get_desired_speed())  # Calculate power command based on desired speed

    ## Track Block Functions
    # Reset the route queue, exit door dictionary, and update the track block
    def reset_route(self):
        self.route = dq(self.line.from_yard + self.line.default_route)
        self.block = self.route[0]
        self.track_block: TrackBlock = self.line.get_track_block(self.block)
        self.exit_door_dict = {}

        self.position = 0
        self.polarity = 0
        self.update_track_block()

    # Update all Track Block variables
    def update_track_block(self):
        # Update all Track Block variables
        self.engine.speed_limit = self.track_block.speed_limit
        self.polarity += self.track_block.length
        self.doors.update_exit_door(self.track_block.station_side in self.exit_door_dict)
        self.lights.update_underground(self.track_block.underground)

    # Dequeue current block from queue and update track block
    # Decide whether to go to yard or loop around depending on authority
    def increment_track_block(self):
        # Pop to get next track block
        self.route.popleft()

        # If not next to finish, continue
        if len(self.route) == 0:
            ## If authority is positive, go back around
            if self.authority >= 0:
                self.route.append(self.line.past_yard, self.line.default_route) # Append past_yard and append default route again
            else:
                self.route.append(self.line.to_yard)    ## If authority is negative, go back to yard
            
            ## Clear dictionary if loop is finished
            self.exit_door_dict = {}
            
        # Increment track block
        self.block = self.route[0]
        self.track_block = self.line.get_track_block(self.block)

        # If station is already in dictionary, toggle exit door
        if self.track_block.station not in self.exit_door_dict:
            self.exit_door_dict[self.track_block.station] = True   # Add station to dictionary
            
        # Update all Track Block variables
        self.update_track_block()
        
    def calculate_distance_traveled(self):
        self.distance_traveled = self.current_speed * self.time_step

    ## Position Functions
    def set_position(self, position: float):
        if(position > self.position):
            self.polarity -= self.position - position
        else:
            # Reset Route and position
            self.reset_route()
            # Increment track blocks until polarity is positive and we're on the correct block
            self.polarity = self.track_block.length - position
        
        # Increment track block until position is reached
        if(self.polarity <= 0):
            self.increment_track_block()
        # Update position
        self.position = position
            
    def calculate_position(self):
        distance = self.current_speed * self.time_step
        self.position += distance
        self.polarity -= distance
        self.authority -= distance
        if self.polarity <= 0:
            self.increment_track_block()
        self.position_changed.emit(self.position)


    ## Driver Mode Funtions
    # Output) string: "automatic" or "manual"
    def get_driver_mode(self):
        return self.driver_mode
    # Input) string: "automatic" or "manual"
    def set_driver_mode(self, mode: str):
        if mode not in ["automatic", "manual"]:
            raise ValueError("Invalid mode. Mode must be 'automatic' or 'manual'.")
        self.driver_mode = mode
    def toggle_driver_mode(self):
        self.driver_mode = "automatic" if self.driver_mode == "manual" else "manual"

    @pyqtSlot(float)
    def update_current_speed(self, speed: float):
        self.current_speed = speed
        if self.call_power_command == 3:
            self.calculate_position(self.time_step) # Update Position and polarity
            self.calculate_power_command(self.get_desired_speed(), self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
            self.call_power_command = 0
        else:
            self.call_power_command += 1
    def set_current_speed(self, speed: float):
        self.current_speed = speed
    def get_current_speed(self):
        return self.current_speed

    ## Setpoint and Commanded Speed Functions
    @pyqtSlot(float)
    def set_setpoint_speed(self, speed: float):
        self.setpoint_speed = min(speed, self.MAX_SPEED)
        self.setpoint_speed = max(self.setpoint_speed, 0)
    def get_setpoint_speed(self):
        return self.setpoint_speed
    
    @pyqtSlot(float)
    def update_commanded_speed(self, speed: float):
        self.commanded_speed = speed
        if self.call_power_command == 3:
            self.calculate_position(self.time_step) # Update Position and polarity
            self.calculate_power_command(self.get_desired_speed(), self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
            self.call_power_command = 0
        else:
            self.call_power_command += 1
    def set_commanded_speed(self, speed: float):
        self.commanded_speed = speed
    def get_commanded_speed(self):
        return self.commanded_speed
    
    ## Power Functions (assumes commanded speed has already been updated)
    # Input) TrainModel object
    # Output) float: desired speed (Commanded speed if mode=automatic, Setpoint speed if mode=manual)
    def get_desired_speed(self):
        return self.setpoint_speed if self.driver_mode == "manual" else self.commanded_speed
    
    # Will give different power command based on driver mode
    # Output) float: power command
    def get_power_command(self):
        return self.engine.power_command

    # Simulate the train's response to desired speeds
    ## Purely for debugging purposes
    def calculate_power_command(self, speed: float):
        if(self.engine.ssh is None):
            power_command = self.engine.compute_power_command_software(speed, self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
        else:
            power_command = self.engine.compute_power_command_hardware(speed, self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
        
        ''' ## TESTING ONLY ##
        self.engine.power_command, self.train_model.current_speed = self.engine.calculate_current_speed(power_command, self.train_model.current_speed, self.time_step, self.brake)
        self.position += self.train_model.current_speed * self.time_step
        # print(f"Power Command: {power_command}, Current Speed: {self.current_speed}")
        '''
        self.power_changed.emit(self.engine.power_command)
    
    # Check if the train needs to stop because of authority
    @pyqtSlot(float)
    def update_authority(self, authority: float):
        self.authority = authority
        ### Authority shows it's a station
        if self.authority == 1_000_000:
            self.at_station()
            distance = 0
            self.authority = 0
        else:
            if self.station:
                self.leaving_station()
        
        if self.call_power_command == 3:
            self.calculate_position(self.time_step) # Update Position and polarity
            self.calculate_power_command(self.get_desired_speed(), self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
            self.call_power_command = 0
        else:
            self.call_power_command += 1

        # Use kinematics equation v^2 = v0^2 + 2a(x-x0) to calculate the distance needed to stop
        # If the distance needed to stop is greater than the authority, set the service brake
        distance = (self.current_speed ** 2) / (2 * 1.2)  # 1.2 m/s^2 is the deceleration rate

        # True = need to brake, False = don't need to brake
        # If the distance and a train's length needed to stop is less than the authority
        ### ADD PADDING LATER ###
        if distance < self.authority:
            self.brake.set_service_brake(True)
            self.engine.power_command = 0

        
    # Update the fault status of the train
    # Call maintenance if there is a fault
    @pyqtSlot(bool[3])
    def update_fault_status(self, faults: bool[3]):
        self.faults = faults
        if(self.faults != [0, 0, 0]):
            self.maintenance()

    ## Maintenance Mode Functions
    # Maintenance mode = set emergency brake and make full stop to fix faults
    def get_maintenance_mode(self):
        return self.maintenance_mode
    def set_maintenance_mode(self, status: bool):
        self.maintenance_mode = status
    def maintenance(self):
        # If the train hasn't made a full stop yet, set the maintenance mode to True and keep emergency brake on
        # Once the train has made a full stop, set the maintenance mode to False and turn off the emergency brake
        done = (self.current_speed != 0)
        self.brake.set_emergency_brake(done)
        self.set_maintenance_mode(done)
        
    def at_station(self):
        self.doors.open_door()
        self.station = self.track_block.station

    def leaving_station(self):
        self.doors.close_door()
        self.station = None

    ## Engineer class to hold Kp and Ki
    class Engineer:
        def __init__(self, kp=25, ki=0.5):
            self.kp = kp
            self.ki = ki

        ## Mutator functions
        def set_kp(self, kp: float):
            if kp > 0:
                self.kp = kp
            else: raise ValueError("kp must be positive")
        def set_ki(self, ki: float):
            if ki > 0:
                self.ki = ki
            else: raise ValueError("ki must be positive")
        def set_engineer(self, kp: float, ki: float):
            self.set_kp(kp)
            self.set_ki(ki)

        ## Accessor functions
        def get_kp(self):
            return self.kp
        def get_ki(self):
            return self.ki
        def get_engineer(self):
            return self.get_kp(), self.get_ki()

    ## Brake class to hold brake status
    class Brake:
        def __init__(self):
            # These are for outputting to the Train Model and for UI status
            self.service_brake = False
            self.emergency_brake = False
            # This is for user inputs
            self.user_service_brake = False
            self.user_emergency_brake = False

        ## Mutator functions
        # Input) status: boolean
        def set_service_brake(self, status: bool):
            self.service_brake = status
        # Input) status: boolean
        def set_emergency_brake(self, status: bool):
            self.emergency_brake = status
        def set_user_service_brake(self, status: bool):
            self.user_service_brake = status
        def set_user_emergency_brake(self, status: bool):
            self.user_emergency_brake

        ## Toggle Functions
        def toggle_service_brake(self):
            self.service_brake = not self.service_brake
        def toggle_emergency_brake(self):
            self.emergency_brake = not self.emergency_brake
        def toggle_user_service_brake(self):
            self.user_service_brake = not self.user_service_brake
        def toggle_user_emergency_brake(self):
            self.user_emergency_brake = not self.user_emergency_brake

        ## Accessor functions
        def get_service_brake(self):
            return self.service_brake
        def get_emergency_brake(self):
            return self.emergency_brake
        def get_user_service_brake(self):
            return self.user_service_brake
        def get_user_emergency_brake(self):
            return self.user_emergency_brake
        def get_status(self):
            return self.service_brake or self.emergency_brake or self.user_service_brake or self.user_emergency_brake
        def get_user_status(self):
            return self.user_service_brake or self.user_emergency_brake
       
    ## Engine class calculates power command and can simulate train response
    class Engine:
        def __init__(self, ssh=None):
            self.speed_limit = None  # Speed limit of the train
            self.P_MAX = 120  # Maximum power (kW)
            self.power_command = 0 # Power command

            self.u_k = 0 # Power command
            self.u_k_integral = 0 # Error integral
            self.e_k_integral = 0 # Power integral
            
            '''
            ## Factors/considerations
            # - Speed limit: Train Controller
            # - Power limit: Train Controller
            # - Brake status: Service and Emergency brake
            # - Brake Deceleration Rates: Service and Emergency
            '''
            
            self.ssh = ssh  # SSH client for communication with Raspberry Pi
            if(self.ssh):
                self.channel = self.create_channel()  # Persistent channel

        def create_channel(self):
            try:
                transport = self.ssh.get_transport()
                channel = transport.open_session()
                channel.get_pty()
                channel.invoke_shell()
                return channel
            except Exception as e:
                print(f"An error occurred while creating the channel: {e}")
                return None

        def send_data_to_raspberry_pi(self, data):
            try:
                # Execute the calculate_power_command.py script and send data to it
                stdin, stdout, stderr = self.ssh.exec_command('python3 calculate_power_command.py')
                stdin.write(json.dumps(data) + '\n')
                stdin.flush()

                # Read the response
                response = stdout.read().decode('utf-8').strip()
                p_cmd, new_u_k = map(float, response.split(','))
                return p_cmd, new_u_k
            except Exception as e:
                print(f"An error occurred during communication: {e}")
                return 0, self.u_k

        # PID controller to compute the power command
        # Input) desired_speed: float, current_speed: float, engineer: Engineer object
        # Return) the power command to be applied to the train
        ### If fault exists, return 0
        ### HOW DO WE HANDLE INTEGRAL OR U_K WHEN BRAKE IS ON
        def compute_power_command_software(self, desired_speed: float, current_speed: float, time_step: float, engineer, brake, maintenance_mode: bool = False):
            print("Software")
            
            if(maintenance_mode):
                # Reset values
                self.u_k = 0 # Power command
                self.e_k_integral = 0 # Error integral
                self.u_k_integral = 0 # Power integral
                return 0
            
            brake.set_service_brake(False)

            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()

            # Calculate the error
            # Authority distance = 
            desired_speed = min(desired_speed, self.speed_limit)
            e_k = desired_speed - current_speed
            # Power command = Kp * error + Ki * integral of error
            self.power_command = kp * e_k + ki * self.u_k

            # Check if the power command exceeds the maximum power
            if self.power_command < self.P_MAX:
                self.u_k = self.u_k_integral + (time_step / 2) * (e_k + self.e_k_integral)
            else:
                # If the power command exceeds the maximum power, use the previous power command
                self.u_k = self.u_k_integral

            # Update the error and power integral for the next iteration
            self.e_k_integral = e_k
            self.u_k_integral = self.u_k
            self.power_command = min(self.power_command, self.P_MAX)

            #### This will be used after integration
            if self.power_command < 0:
                brake.set_service_brake(True)
                #### THIS LINE IS FOR TESTING PURPOSES ONLY ####
                self.power_command = max(self.power_command , -self.P_MAX)    # self.power_command = 0

            return self.power_command 
        
        def compute_power_command_hardware(self, desired_speed: float, current_speed: float, time_step: float, engineer, brake, maintenance_mode: bool = False):
            print("Hardware")
            
            if(maintenance_mode):
                # Reset values
                self.u_k = 0 # Power command
                self.e_k_integral = 0 # Error integral
                self.u_k_integral = 0 # Power integral
                return 0
            
            brake.set_service_brake(False)

            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()

            # Calculate the error
            # Authority distance = 
            desired_speed = min(desired_speed, self.speed_limit)
            e_k = desired_speed - current_speed
            
            # Send the data to the Raspberry Pi for power command calculation
            data = {
                'kp': kp,
                'ki': ki,
                'ek': e_k,
                'uk': self.u_k,
                'eki': self.e_k_integral,
                'uki': self.u_k_integral,
                'ts': time_step
            }

            self.power_command, self.u_k = self.send_data_to_raspberry_pi(data)

            # Update the error and power integral for the next iteration
            self.e_k_integral = e_k
            self.u_k_integral = self.u_k
            self.power_command = min(self.power_command, self.P_MAX)

            #### This will be used after integration
            if self.power_command < 0:
                brake.set_service_brake(True)
                #### THIS LINE IS FOR TESTING PURPOSES ONLY ####
                self.power_command = max(self.power_command, -self.P_MAX)    # self.power_command = 0

            return self.power_command
        
        def calculate_current_speed(self, power_command, current_speed, time_step: float, brake):
                
            ##### JUST FOR TESTING #####
            if brake.get_status():
                power_command = -self.P_MAX
            
            self.power_command = power_command

            current_speed += power_command * time_step
            current_speed = min(current_speed, self.speed_limit)
            
            return power_command, current_speed
        
    ## Door class to hold door status
    # Door status = bool
    # False = closed, True = open
    class Doors:
        def __init__(self):
            self.left: bool = False
            self.right: bool = False
            self.exit_door: str = None   # False = "L", True = "R"

        ## Mutator Functions
        # Input) status: boolean
        def set_left(self, status: bool):
            self.left = status
        # Input) status: boolean
        def set_right(self, status: bool):
            self.right = status

        ## Toggle Functions
        def toggle_left(self):
            self.left = not self.left
        def toggle_right(self):
            self.right = not self.right

        ## Accessor Functions
        def get_left(self):
            return self.left
        def get_right(self):
            return self.right
        # Output) tuple: (bool: left door status, bool: right door status)
        def get_status(self):
            return self.get_left(), self.get_right()
        
        # Update the exit door status
        # Input) bool: False = first value, Trye = second value
        def update_exit_door(self, bool=False):
            if bool:
                if self.exit_door == "Right/Left":
                    self.exit_door = "left"
                elif self.exit_door == "Left/Right":
                    self.exit_door = "right"
                else:
                    raise ValueError("Exit door not set")
            else:
                self.exit_door = "right" if self.exit_door[0] == "R" else "left"

        def open_door(self):
            if self.exit_door == "left":
                self.set_left(True)
            elif self.exit_door == "right":
                self.set_right(True)
            else: 
                raise ValueError("Exit door not set")
            
        def close_door(self):
            if self.exit_door == "left":
                self.set_left(False)
            elif self.exit_door == "right":
                self.set_right(False)
            else: 
                raise ValueError("Exit door not set")
        
    ## Light class to hold light status
    # Light status = bool
    # False = off, True = on
    class Lights:
        def __init__(self):
            self.lights: bool = False
            self.underground: bool = None # Boolean
            self.night_time: int = 43200 # 12 hours in seconds

        ## Mutator Functions
        def lights_on(self):
            self.lights = True
        def lights_off(self):
            self.lights = False
        def set_lights(self, status: bool):
            self.lights = status

        ## Toggle Function
        def toggle_lights(self):
            self.lights = not self.lights

        ## Accessor Function
        def get_lights(self):
            return self.lights
        def get_status(self):
            return self.lights
        def get_underground(self):
            return self.underground
        
        ## Update Functions
        def update_underground(self, underground: bool):
            self.underground = underground
        
        def update_lights(self, elapsed_time: float):
            prev_lights = self.lights
            self.set_lights(self.underground or (elapsed_time % 86400) > 43200)   # Set external lights if current block is undreground
            if prev_lights != self.lights:
                print(f"Lights are now {'on' if self.lights else 'off'}")

    ## AC class to hold temperature status
    # Commanded temperature from driver (initialized to 69)
    # Current temperature from Train Model
    class AC:
        def __init__(self, temp: int):
            # Automatic temperature when in Automatic mode (69 degrees Fahrenheit)
            self.auto_temp = 69
            self.MAX_TEMP = 80
            self.MIN_TEMP = 60
            # Commanded temperature from driver (initialized to auto_temp)
            self.commanded_temp = self.auto_temp
            # Current temperature inside the train
            self.current_temp = temp

        ## Mutator Function
        def set_commanded_temp(self, temp: int):
            self.commanded_temp = min(round(temp), self.MAX_TEMP)
            self.commanded_temp = max(self.commanded_temp, self.MIN_TEMP)
        @pyqtSlot(int)
        def set_current_temp(self, temp: int):
            self.current_temp = temp

        ## Accessor Function
        def get_commanded_temp(self):
            return self.commanded_temp
        def get_current_temp(self):
            return self.current_temp
        


# Does beacon need to be encrypted
# All information from MBO needs to be encrypted
class TrainModel(QObject):
    current_speed_changed = pyqtSignal(float)
    commanded_speed_changed = pyqtSignal(float)
    authority_changed = pyqtSignal(float)
    train_temp_changed = pyqtSignal(int)
    faults_changed = pyqtSignal(bool[3])
    
    def __init__(self):
        super().__init__()

        # Train Model -> Train Controller
        self.current_speed: float = 0
        self.commanded_speed: float = 0
        self.authority: float = 1000
        self.train_temp: int = 69
        self.faults: bool[3] = [0, 0, 0]

        self.power = None
        self.position = None
        self.lights = None
        self.doors = None
        self.commanded_temp = None
        self.service_brake = None
        self.emergency_brake = None

    @property
    def current_speed(self):
        return self.current_speed

    @current_speed.setter
    def set_current_speed(self, value):
        self.current_speed = value
        self.current_speed_changed.emit(value)

    @property
    def commanded_speed(self):
        return self._commanded_speed

    @commanded_speed.setter
    def set_commanded_speed(self, value):
        self._commanded_speed = value
        self.commanded_speed_changed.emit(value)

    @property
    def authority(self):
        return self.authority

    @authority.setter
    def set_authority(self, value):
        self.authority = value
        self.authority_changed.emit(value)

    @property
    def train_temp(self):
        return self.train_temp

    @train_temp.setter
    def set_train_temp(self, value):
        self.train_temp = value
        self.train_temp_changed.emit(value)

    @property
    def faults(self):
        return self.faults

    @faults.setter
    def set_faults(self, value):
        self.faults = value
        self.faults_changed.emit(value)
    
    
    # This is used to update all train model variables with the real Train Model
    # In hardware, this is done through parsing. In software, this is done through the object
    def update_mock_train_model(self, train_model):
        self.current_speed = train_model.get_current_speed()
        self.speed_limit = train_model.get_speed_limit()
        self.length = train_model.get_length()
        self.authority = train_model.get_authority()
        self.commanded_speed = train_model.get_commanded_speed()
        self.train_temp = train_model.get_train_temp()

        # self.exit_door = train_model.get_exit_door()
        # self.station = train_model.get_station_name()
        # self.distance_from_station = train_model.get_distance_from_station()
        # self.exit_door = train_model.get_exit_door()
        # self.block = train_model.get_block()
        # self.underground_blocks = train_model.get_underground_blocks()
        # self.faults = train_model.get_fault_statuses()
        return True
        


class TrainSystem:
    def __init__(self, host=None, port=None, username=None, password=None):
        self.ssh_client = None
        if(host and port and username and password):
            self.ssh_client = self.create_ssh_connection(HOST, PORT, USERNAME, PASSWORD)
        # Hardware
        #self.controller = TrainController(self.ssh_client)
        # Software
        self.controller = TrainController()

    # Example usage
    def create_ssh_connection(self, host, port=22, username='danim', password='danim'):
        """Establish an SSH connection to the Raspberry Pi and return the SSH client."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect to the Raspberry Pi
            ssh.connect(host, port, username, password)
            print("Connection established")
            return ssh
        except Exception as e:
            print(f"An error occurred while connecting: {e}")
            return None


    def run(self):
        self.controller.set_setpoint_speed(30)
        for _ in range(5):
            self.controller.simulate_timestep()

        self.controller.set_setpoint_speed(40)
        for _ in range(5):
            self.controller.simulate_timestep()
        
        self.controller.set_setpoint_speed(500)
        for _ in range(50):
            self.controller.simulate_timestep()
        
        self.controller.set_setpoint_speed(10)
        for _ in range(5):
            self.controller.simulate_timestep()
            

if __name__ == "__main__":
    train_system = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
    train_system.run()
