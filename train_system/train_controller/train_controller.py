import time
import paramiko
import json

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from train_system.common.time_keeper import TimeKeeper

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
    setpoint_speed_updated = pyqtSignal(float)
    power_updated = pyqtSignal(float)
    #lights_updated = pyqtSignal(bool) -> in lights class
    #left_door_updated = pyqtSignal(bool) -> in doors class
    #right_door_updated = pyqtSignal(bool) -> in doors class
    #train_temp_updated = pyqtSignal(int) -> in ac class
    #service_brake_updated = pyqtSignal(bool) -> in brakes class
    #emergency_brake_updated = pyqtSignal(bool) -> in brakes class
    
    def __init__(self, time_keeper: TimeKeeper, kp: float=25, ki: float=0.1, train_model=None, ssh=None) -> None:
        self.time_keeper = time_keeper
        super().__init__() ###### THIS LINE IS IMPORTANT #####

        self.hardware = True if ssh else False
        print(f"Hardware: {self.hardware}")
        self.elapsed_time = 0
        self.time_step = 0.05  # 0.05 second time step

        ## Initialize objects
        self.train_model = train_model if train_model else TrainModel()  # Used to store data received from Train Model. No computations done in the object
        self.engineer = self.Engineer(kp, ki) # Engineer holds Kp and Ki and is the only one that can set them
        self.brake = self.Brake()       # Brake holds service and emergency brake status
        self.engine = self.Engine(ssh)     # Engine calculates power command and simulates train response
        self.doors = self.Doors(self.train_model.get_exit_door)       # Doors holds left and right door status
        self.lights = self.Lights(self.train_model.get_underground)     # Lights holds light status
        self.ac = self.AC(self.train_model.get_train_temp())             # AC holds temperature status

        # Driver variables
        self.driver_mode = "manual" # Driver mode can be "automatic" or "manual"
        self.setpoint_speed = 0     # Setpoint speed for manual mode
        self.MAX_SPEED = 21.67

        # Train Controller Calculated Variables
        self.maintenance_mode = False     # Maintenance status of the train
        self.position = 0  # Distance traveled by the train. Calculated in the Train Controller
        
        self.track_block: int = 0
        self.block: int = 0
        self.station: str = "station_name"
        self.speed_limit: float = 19.44  #m/s
        self.length: float = self.train_model.get_length()
        self.polarity = self.train_model.get_length() # Polarity changes polarity < 0
        self.exit_door: str = "L"
        self.underground: bool = False

        # Train Model inputs (purely made for convenience)
        # THESE VALUES WILL RECEIVE NO CALCULATIONS (except for current speed FOR NOW)
        self.current_speed = None    # Current speed of the train
        self.commanded_speed = None  # Commanded speed from the Train Model (CTC or MBO)
        self.authority = None        # Authority from the Train Model (CTC or MBO)
        self.faults = None           # Fault statuses from the Train Model (list of bools)

    # Simulate a time step of the train controller
    # Call this for ever press of the refresh button
    def simulate_timestep(self, train_model=None):
        # Update Mock Train Model
        param = train_model if train_model else self.train_model
        self.train_model.update_mock_train_model(param)
        ## Perform calculations then output them
        self.update_train_controller()    # This function will define all the "None" variables above
        ## Transmit to Train Model 
        self.transmit_to_train_model()  # Transmit via Serial communication (For now, also update current speed)
        
    # Update all variables with the train model input, calculate, then output to train model
    # Take train model outputs, update all variables, and transmit to train model the Train Controller's new values
    def update_train_controller(self):
        # Update variables with train model input
        self.current_speed = self.train_model.get_current_speed()
        self.commanded_speed = self.train_model.get_commanded_speed()
        self.authority = self.train_model.get_authority()
        # Update all status variables
        self.ac.update_current_temp(self.train_model, self.driver_mode)
        self.update_fault_status(self.train_model)
        
        # Update all track block variables
        self.engine.update_speed_limit(self.train_model)
        self.doors.set_exit_door(self.train_model)
        self.lights.update_lights(self.train_model, self.elapsed_time)
        self.station = self.train_model.get_station_name()

        ### CHANGE THESE TO POLARITY AND DISTANCE USING LENGTH
        self.position += self.train_model.get_current_speed()*self.time_step
        self.polarity -= self.train_model.get_current_speed()*self.time_step
        if self.polarity <= 0:
            self.train_model.increment_track_block()
            self.polarity += self.train_model.get_length()
        self.block = self.train_model.get_block()
        

        ## Train Controller Calculations
        # Run 1 more cycle of the simulation to update the current speed
        self.simulate_power_command(self.get_desired_speed())
        

    # Transmit necessary variables to Main Computer (Train Model), then mock Train Model will be updated
    def transmit_to_train_model(self):
        ##### THIS WILL BE TAKEN OUT #####
        self.train_model.set_current_speed(self.current_speed)
        pass

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


    ## Setpoint and Commanded Speed Functions
    def set_setpoint_speed(self, speed: float):
        self.setpoint_speed = min(speed, self.MAX_SPEED)
        self.setpoint_speed = max(self.setpoint_speed, 0)
        self.setpoint_speed_updated.emit(self.setpoint_speed)
    def get_setpoint_speed(self):
        return self.setpoint_speed
    
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
    def simulate_power_command(self, speed: float):
        if(self.engine.ssh is None):
            power_command = self.engine.compute_power_command_software(speed, self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
        else:
            power_command = self.engine.compute_power_command_hardware(speed, self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
        power_command, self.current_speed = self.engine.calculate_current_speed(power_command, self.train_model.current_speed, self.time_step, self.brake)
        self.elapsed_time += self.time_step
        print(f"Power Command: {power_command}, Current Speed: {self.current_speed}")
    
    # Update the fault status of the train
    # Call maintenance if there is a fault
    def update_fault_status(self, train_model):
        self.faults = train_model.get_fault_statuses()
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

    @pyqtSlot(bool)
    def handle_toggle_driver_mode(self, check):
        if check:
            print("Automatic Mode")
            self.set_driver_mode("automatic")
        else:
            print("Manual Mode")
            self.set_driver_mode("manual")

    """
    AMBER ADD CONVERT TO MS FUNCTION SOOON!!!!!!!!
    """
    @pyqtSlot(str)
    def handle_setpoint_edit_changed(self, x: str) -> None:
        if(x != ""):
            self.set_setpoint_speed(float(x))

    @pyqtSlot(bool)
    def handle_service_brake_toggled(self, check: bool) -> None:
        if check:
            self.brake.set_service_brake(True)
        else:
            self.brake.set_service_brake(False)

    @pyqtSlot(bool)
    def handle_emergency_brake_toggled(self, check: bool) -> None:
        if check:
            self.brake.set_emergency_brake(True)
        else:
            self.brake.set_emergency_brake(False)

    @pyqtSlot(str)
    def handle_comm_temp_changed(self, x: str) -> None:
        if(x != ""):
            self.ac.set_commanded_temp(int(x))
        

    ## Engineer class to hold Kp and Ki
    class Engineer(QObject):
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
    class Brake(QObject):
        service_brake_updated = pyqtSignal(bool)
        emergency_brake_updated = pyqtSignal(bool)
        def __init__(self):
            super().__init__()
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
            self.service_brake_updated.emit(status)
        # Input) status: boolean
        def set_emergency_brake(self, status: bool):
            self.emergency_brake = status
            self.emergency_brake_updated.emit(status)
        def set_user_service_brake(self, status: bool):
            self.user_service_brake = status
        def set_user_emergency_brake(self, status: bool):
            self.user_emergency_brake

        ## Toggle Functions
        def toggle_service_brake(self):
            self.service_brake = not self.service_brake
            self.service_brake_updated.emit(self.service_brake)
        def toggle_emergency_brake(self):
            self.emergency_brake = not self.emergency_brake
            self.emergency_brake_updated.emit(self.emergency_brake)
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
    class Engine(QObject):
        def __init__(self, ssh):
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
            
            self.ssh = None
            if(ssh):
                self.ssh = ssh  # SSH client for communication with Raspberry Pi
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
        
        # Check if the train needs to stop because of authority
        def stop_for_authority(self, authority: float, current_speed: float):
            # Use kinematics equation v^2 = v0^2 + 2a(x-x0) to calculate the distance needed to stop
            # If the distance needed to stop is greater than the authority, set the service brake
            distance = (current_speed ** 2) / (2 * 1.2)  # 1.2 m/s^2 is the deceleration rate

            # True = need to brake, False = don't need to brake
            ## MIGHT NEED TO ADD A BIT OF PADDING IDK
            return distance < authority # Return True if the distance needed to stop is less than the authority

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
            # If power command is greater than the maximum power, it's exceeded the physical limit so set it to the maximum power
            if power_command > self.P_MAX:
                power_command = self.P_MAX
            # If power command magnitude is negative, we need to slow down so turn on the service brake
            elif power_command < -self.P_MAX:
                power_command = -self.P_MAX
                
            ##### JUST FOR TESTING #####
            if brake.get_status():
                power_command = -self.P_MAX
            
            self.power_command = power_command

            current_speed += power_command * time_step
            current_speed = min(current_speed, self.speed_limit)
            
            return power_command, current_speed
        
        def update_speed_limit(self, train_model):
            self.speed_limit = train_model.get_speed_limit()
        
    ## Door class to hold door status
    # Door status = bool
    # False = closed, True = open
    class Doors(QObject):
        left_door_updated = pyqtSignal(bool)
        right_door_updated = pyqtSignal(bool)
        def __init__(self, exit_door="L"):
            super().__init__()
            self.left = False
            self.right = False
            self.exit_door = exit_door   # False = "left", True = "right"

        ## Mutator Functions
        # Input) status: boolean
        def set_left(self, status: bool):
            self.left = status
            self.left_door_updated.emit(self.left)
        # Input) status: boolean
        def set_right(self, status: bool):
            self.right = status
            self.right_door_updated.emit(self.right)

        ## Toggle Functions
        def toggle_left(self):
            self.left = not self.left
            self.left_door_updated.emit(self.left)
        def toggle_right(self):
            self.right = not self.right
            self.right_door_updated.emit(self.right)

        ## Accessor Functions
        def get_left(self):
            return self.left
        def get_right(self):
            return self.right
        # Output) tuple: (bool: left door status, bool: right door status)
        def get_status(self):
            return self.get_left(), self.get_right()
        
        # Update the exit door status
        def set_exit_door(self, train_model):
            right_door = train_model.get_exit_door()
            self.exit_door = "right" if right_door else "left"

        def open_door(self):
            if self.exit_door == "left":
                self.set_left(True)
                self.left_door_updated.emit(self.left)
            elif self.exit_door == "right":
                self.set_right(True)
                self.right_door_updated.emit(self.right)
            else: 
                raise ValueError("Exit door not set")
            
        def close_door(self):
            if self.exit_door == "left":
                self.set_left(False)
                self.left_door_updated.emit(self.left)
            elif self.exit_door == "right":
                self.set_right(False)
                self.right_door_updated.emit(self.right)
            else: 
                raise ValueError("Exit door not set")
        
    ## Light class to hold light status
    # Light status = bool
    # False = off, True = on
    class Lights(QObject):
        lights_updated = pyqtSignal(bool)
        def __init__(self, underground=False):

            super().__init__()
            self.lights = False
            self.underground = underground # List of blocks that are underground
            self.night_time = 43200 # 12 hours in seconds

        ## Mutator Functions
        def lights_on(self):
            self.lights = True
            self.lights_updated.emit(self.lights)
        def lights_off(self):
            self.lights = False
            self.lights_updated.emit(self.lights)
        def set_lights(self, status: bool):
            self.lights = status
            self.lights_updated.emit(self.lights)

        ## Toggle Function
        def toggle_lights(self):
            self.lights = not self.lights
            self.lights_updated.emit(self.lights)

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
        def update_lights(self, train_model, elapsed_time: float):
            self.update_underground(train_model.get_underground())    # Update underground blocks
            self.set_lights(self.underground or (elapsed_time % 86400) > 43200)   # Set external lights if current block is undreground

    ## AC class to hold temperature status
    # Commanded temperature from driver (initialized to 69)
    # Current temperature from Train Model
    class AC(QObject):
        train_temp_updated = pyqtSignal(int)
        def __init__(self, temp: int):
            super().__init__() 
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

        ## Accessor Function
        def get_commanded_temp(self):
            return self.commanded_temp
        def get_current_temp(self):
            return self.current_temp
        
        ## Update Function
        # Input) TrainModel object, string: "automatic" or "manual"
        def update_current_temp(self, train_model, driver_mode: str):
            self.current_temp = train_model.get_train_temp()
            self.train_temp_updated.emit(self.current_temp)
            # If in automatic mode, set the commanded temperature to the automatic temperature
            if(driver_mode == "automatic"):
                self.set_commanded_temp(self.auto_temp)


# Does beacon need to be encrypted
# All information from MBO needs to be encrypted
class TrainModel(QObject):
    def __init__(self):
        # Train Model variables
        self.current_speed: float = 0
        self.commanded_speed: float = 0
        self.authority: float = 1000
        self.train_temp: int = 69
        self.faults: int[3] = [0, 0, 0]

        # Track block variables
        self.track_block: int = 0
        self.block: int = 0
        self.station: str = "station_name"
        self.speed_limit: float = 19.44  #m/s
        self.length: float = 0
        self.exit_door: str = "L"
        self.underground: bool = False

    # Float
    def get_current_speed(self):
        # Logic to get current speed of the train
        return self.current_speed
    def set_current_speed(self, speed: float):
        self.current_speed = round(speed, 2)
    
    # Float
    def get_speed_limit(self):
        # Logic to get the speed limit of the train
        return self.speed_limit
    def set_speed_limit(self, speed: float):
        self.speed_limit = speed

    # 1 floats
    # Length of the current block
    def get_length(self):
        # Logic to get current length of the train
        return self.length
    def set_length(self, length: float):
        self.length = length

    # Iterative (float representing meters)? Absolute (position representing when to stop by)?
    def get_authority(self):
        # Logic to get the authority from the train model
        return self.authority
    def set_authority(self, authority: float):
        self.authority = round(authority, 2)

    # Float
    def get_commanded_speed(self):
        # Logic to get commanded speed from the train model
        return self.commanded_speed
    def set_commanded_speed(self, speed: float):
        self.commanded_speed = round(speed)

    # float
    def get_train_temp(self):
        # Logic to get the temperature inside the train
        return self.train_temp
    def set_train_temp(self, temp: int):
        self.train_temp = temp

    def get_track_block(self):
        return self.track_block
    def increment_track_block(self):
        self.track_block += 1
    
    # String or station ID?
    # Need to decrypt the information and figure it out from that
    # Is the full name even needed
    def get_station_name(self):
        # Logic to get the name of the current station
        return self.station
    def set_station_name(self, station: str):
        self.station = station
    
    # Char
    # Used for underground logic
    def get_block(self):
        # Logic to get the block number
        return self.block
    def set_block(self, block: int):
        if block < 0:
            raise ValueError("Block number must be positive.")
        self.block = block

    # List of chars (list of blocks)
    def get_underground(self):
        # Logic to get the underground status of the train
        return self.underground
    def set_underground(self, underground: bool):
        self.underground = underground

    # Bool (left, right)
    def get_exit_door(self):
        # Logic to get the status of the exit door
        return self.exit_door
    def set_exit_door(self, door: str):
        if door not in ["L", "R"]:
            raise ValueError("Invalid door. Door must be 'L' or 'R'.")
        self.exit_door = door

    # List of bools? Individual bools?
    # [engine, brake, signal]
    # No fault = [0, 0, 0]
    def get_fault_statuses(self):
        # Logic to get the fault status of the train
        return self.faults
    def set_fault_statuses(self, faults: list[bool]):
        self.faults = faults[0:3]   # Only take the first 3 elements
    
    
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
        self.train_model = TrainModel()
        self.ssh_client = None
        if(host and port and username and password):
            self.ssh_client = self.create_ssh_connection(HOST, PORT, USERNAME, PASSWORD)
        # Hardware
        #self.controller = TrainController(25, 0.1, self.train_model, self.ssh_client)
        # Software
        self.controller = TrainController(25, 0.1, self.train_model)

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