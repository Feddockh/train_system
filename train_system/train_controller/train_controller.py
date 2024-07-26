import paramiko
import json
from collections import deque as dq

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.station import Station

from train_system.train_model.train_model import TrainModel

HOST= '192.168.0.114'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'


'''
# Functions with the word "update" in the name are updated from the Train Model and takes the Train Model as an argument
# Train Controller only talks with Train Model
# Train Model needed for initialization
'''

class TrainController(QObject):
    setpoint_speed_updated = pyqtSignal(float)
    position_updated = pyqtSignal(float)
    power_updated = pyqtSignal(float)
    faults_fixed = pyqtSignal()

    #lights_updated = pyqtSignal(bool) -> in lights class
    #left_door_updated = pyqtSignal(bool) -> in doors class
    #right_door_updated = pyqtSignal(bool) -> in doors class
    #train_temp_updated = pyqtSignal(int) -> in ac class
    #service_brake_updated = pyqtSignal(bool) -> in brakes class
    #emergency_brake_updated = pyqtSignal(bool) -> in brakes class
    
    
    def __init__(self, kp: float=25, ki: float=0.5, train_model=None, line_name: str = "green", id: int = 0, ssh=None) -> None:
        super().__init__() ###### THIS LINE IS IMPORTANT #####

        self.hardware = True if ssh else False
        print(f"Hardware: {self.hardware}")
        self.time_step = 1  # 1 second time step
        self.train_length = 32.2  # 32.2 meters

        ## Initialize objects
        self.train_model = MockTrainModel()  # Used to store data received from Train Model. No computations done in the object
        self.train_model.engine_fault_updated.connect(self.handle_fault_update)
        self.train_model.brake_fault_updated.connect(self.handle_fault_update)
        self.train_model.signal_fault_updated.connect(self.handle_fault_update)
        self.train_model.comm_speed_updated.connect(self.handle_commanded_speed)
        self.train_model.authority_updated.connect(self.update_authority)

        self.engineer = self.Engineer(kp, ki) # Engineer holds Kp and Ki and is the only one that can set them

        self.brake = self.Brake()       # Brake holds service and emergency brake status
        self.brake.service_brake_updated.connect(self.train_model.handle_service_brake_update)
        self.brake.emergency_brake_updated.connect(self.train_model.handle_emergency_brake_update)

        self.engine = self.Engine(ssh)     # Engine calculates power command and simulates train response
        self.doors = self.Doors()       # Doors holds left and right door status
        self.doors.left_door_updated.connect(self.train_model.handle_left_door_update)
        self.doors.right_door_updated.connect(self.train_model.handle_right_door_update)
        self.lights = self.Lights()     # Lights holds light status
        self.lights.lights_updated.connect(self.train_model.handle_lights_update)
        self.ac = self.AC(self.train_model.get_train_temp())    # AC holds temperature status
        self.ac.commanded_temp_updated.connect(self.train_model.handle_commanded_temp_update)
        self.line = Line(line_name)

        # Driver variables
        self.driver_mode = "manual" # Driver mode can be "automatic" or "manual"
        self.setpoint_speed = 0     # Setpoint speed for manual mode
        self.MAX_SPEED = 21.67

        # Train Controller Calculated Variables
        self.maintenance_mode = False     # Maintenance status of the train
        self.position = 0  # Distance traveled by the train. Calculated in the Train Controller
        
        # Train Block Inputs
        self.line.load_defaults()
        self.route = dq(self.line.route.from_yard)  # Route queue
        self.reset_route()  # Initialize track block, position, and polarity

        # Train Model inputs
        self.current_speed = self.train_model.current_speed    # Current speed of the train
        self.commanded_speed = self.train_model.commanded_speed  # Commanded speed from the Train Model (CTC or MBO)
        self.update_authority(self.train_model.authority)        # Authority from the Train Model (CTC or MBO)
        self.engine_fault = self.train_model.engine_fault           # Fault status from the Train Model
        self.brake_fault = self.train_model.brake_fault           # Fault status from the Train Model
        self.signal_fault = self.train_model.signal_fault           # Fault status from the Train Model
        
    # Update all variables with the train model input, calculate, then output to train model
    # Take train model outputs, update all variables, and transmit to train model the Train Controller's new values
    def update_train_controller(self):
        self.brake.set_service_brake(False)
        self.set_current_speed(self.train_model.get_current_speed())

        # Update variables with train model input
        # self.commanded_speed = self.train_model.get_commanded_speed()
        # self.update_authority(self.train_model.get_authority())
        
        # Update all status variables
        # self.ac.update_current_temp(self.train_model.get_train_temp())
        # self.update_fault_status(self.train_model.get_fault_statuses())

        ## Train Controller Calculations
        self.calculate_position()
        self.calculate_power_command(self.get_desired_speed())
        

    ## Track Block Functions
    # Reset the route queue, exit door dictionary, and update the track block
    def reset_route(self):
        self.route.extend(self.line.route.default_route)
        self.block = self.route[0]
        self.track_block: TrackBlock = self.line.get_track_block(self.block)
        print("Track block: ", self.track_block.number)

        self.position = 0
        self.polarity = 0
        self.station = None
        self.destination = None
        self.finish = False
        self.update_track_block()

    # Update all Track Block variables
    def update_track_block(self):
        # Update all Track Block variables
        self.engine.set_speed_limit(self.track_block.speed_limit / 3.6)
        self.polarity += self.track_block.length
        
        self.station = self.track_block.station.name if self.track_block.station else None

        if self.station:
            exit_door = self.track_block.station.get_side(self.block, self.track_block.number)
            self.doors.update_exit_door(exit_door)

        self.block = self.track_block.number
        self.lights.update_underground(self.track_block.underground)

    def increment_track_block(self):
        # Pop to get next track block
        self.route.popleft()
        print(f"Route Length: {len(self.route)}")

        # If not next to finish, continue
        if len(self.route) == 0 and not self.finish:
            ## Look at authority to see whether to circle or to end route
            if self.to_yard:
                self.route.extend(self.line.route.to_yard)    ## If authority is negative, go back to yard
                self.finish = True
            else:
                self.route.extend(self.line.route.past_yard, self.line.route.default_route) # Append past_yard and append default route again
        elif self.finish:
            pass
            
        # Increment track block
        self.block = self.route[0]
        self.track_block = self.line.get_track_block(self.block)
        print("--------------------- Track block: ", self.track_block.number, "---------------------")
        
        # Update all Track Block variables
        self.update_track_block()

    ## Position Functions
    # Input) float: position from the yard
    def set_position(self, position: float):
        print("------------- Setting Position ---------------")
        if(position > self.position):
            self.polarity -= position - self.position
        else:
            # Reset Route and position
            self.route = dq(self.line.route.from_yard)
            self.reset_route()
            self.polarity -= position
            print(f"Track Block: {self.track_block.number}")
        
        # Increment track block until position is reached
        while(self.polarity <= 0):
            self.increment_track_block()
        # Update position
        self.position = position
        self.position_updated.emit(self.position)


        print(f"----------- Position: {self.position}, Polarity: {self.polarity} -----------")
            
    def calculate_position(self):
        distance = self.current_speed * self.time_step
        self.position += distance
        self.polarity -= distance

        self.stop_for_authority()

        if self.polarity <= 0:
            self.increment_track_block()
        print(f"Position: {self.position}, Polarity: {self.polarity}")
        self.train_model.set_position(self.position)
        self.position_updated.emit(self.position)

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

    def get_current_speed(self):
        return self.current_speed
    def set_current_speed(self, speed: float):
        self.current_speed = speed
        if(self.current_speed == 0):
            # Emit that faults are fixed
            self.faults_fixed.emit()
            self.brake.set_emergency_brake(False)
        
        
    ## Setpoint and Commanded Speed Functions
    def set_setpoint_speed(self, speed: float):
        self.setpoint_speed = min(speed, self.MAX_SPEED)
        self.setpoint_speed = max(self.setpoint_speed, 0)
        self.setpoint_speed_updated.emit(self.setpoint_speed)
        print("new setpoint speed " + str(self.setpoint_speed))
    def get_setpoint_speed(self):
        return self.setpoint_speed
    
    def get_commanded_speed(self):
        return self.commanded_speed
    def handle_commanded_speed(self, speed: float):
        self.commanded_speed = speed
    
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
        print(f"Current Speed from Train Model: {self.current_speed}")
        if(self.engine.ssh is None):
            self.engine.calculate_power_command_software(speed, self.current_speed, self.time_step, self.engineer, self.brake)
        else:
            self.engine.calculate_power_command_hardware(speed, self.current_speed, self.time_step, self.engineer, self.brake)
        self.train_model.set_power_command(self.engine.power_command)
        self.power_updated.emit(self.engine.power_command)

    # Update the fault status of the train
    # Call maintenance if there is a fault
    @pyqtSlot(bool)
    def handle_fault_update(self, fault: bool):
        if(fault):
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

    def update_authority(self, authority: float):
        self.to_yard = authority < 0

        # self.padding = self.train_length / 2
        self.authority = self.position + abs(authority)
        
        ### Authority shows it's a station
        if self.authority >= 1_000_000:
            self.at_station()
            self.authority = self.position
        else:
            if self.destination:
                self.leaving_station()

    # Check if the train needs to stop because of authority
    def stop_for_authority(self):
        # Use kinematics equation v^2 = v0^2 + 2a(x-x0) to calculate the distance needed to stop
        # If the distance needed to stop is greater than the authority, set the service brake
        distance = (self.current_speed ** 2) / (2 * 1.2)  # 1.2 m/s^2 is the deceleration rate
        print(f"Distance: {distance}, Authority: {self.authority}")

        # Position you will be stopped by >= position you need to be stopped by
        ## MIGHT NEED TO ADD PADDING
        if self.position + distance >= self.authority: # Return True if the distance needed to stop is less than the authority
            self.brake.set_service_brake(True)
            print("Stopping for authority")

    ## Functions for arriving and departing from stations
    def set_station(self, station: str):
        self.station = station
    def get_station(self):
        return self.station
    def set_destination(self, destination: str):
        self.destination = destination
    def get_destination(self):
        return self.destination
    def at_station(self):
        self.doors.open_door()
        self.set_destination(self.station)
    def leaving_station(self):
        self.doors.close_door()
        self.set_destination(None)

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
    def handle_commanded_temp_changed(self, x: str) -> None:
        if(x != ""):
            self.ac.set_commanded_temp(float(x))

    @pyqtSlot(bool)
    def handle_engine_fault_changed(self, fault: bool) -> None:
        self.train_model.set_engine_fault(fault)

    @pyqtSlot(bool)
    def handle_brake_fault_changed(self, fault: bool) -> None:
        self.train_model.set_brake_fault(fault)
        
    @pyqtSlot(bool)
    def handle_signal_fault_changed(self, fault: bool) -> None:
        self.train_model.set_signal_fault(fault)

    @pyqtSlot(float)
    def handle_curr_speed_changed(self, speed: float) -> None:
        self.current_speed = speed
    
    @pyqtSlot(float)
    def handle_comm_speed_changed(self, speed: float) -> None:
        self.commanded_speed = speed

    @pyqtSlot(float)
    def handle_authority_changed(self, authority: float) -> None:
        self.update_authority(authority)

    @pyqtSlot(bool)
    def handle_light_status_changed(self, light: bool) -> None:
        self.lights.set_lights(light)

    @pyqtSlot(bool)
    def handle_left_door_changed(self, door: bool) -> None:
        self.doors.set_left(door)
    @pyqtSlot(bool)
    def handle_right_door_changed(self, door: bool) -> None:
        self.doors.set_right(door)

    @pyqtSlot(int)
    def handle_kp_changed(self, kp: int) -> None:
        #do this to keep from being recursive
        self.kp = kp

    @pyqtSlot(int)
    def handle_ki_changed(self, ki: int) -> None:
        #do this to keep from being recursive
        self.ki = ki

    @pyqtSlot(int)
    def handle_position_changed(self, loc: int) -> None:
        self.set_position(loc)

    @pyqtSlot(str)
    def handle_destination_changed(self, des: str) -> None:
        self.set_station(des)

    @pyqtSlot()
    def handle_tick(self) -> None:
        self.update_train_controller()

    ## Engineer class to hold Kp and Ki
    class Engineer(QObject):
        kp_updated = pyqtSignal(int)
        ki_updated = pyqtSignal(int)
        
        def __init__(self, kp=25, ki=0.5):
            super().__init__()
            self.kp = kp
            self.ki = ki

        ## Mutator functions
        def set_kp(self, kp: float):
            if kp >= 0:
                self.kp = kp
                self.kp_updated.emit(self.kp)
            else: raise ValueError("kp must be non-negative")
        def set_ki(self, ki: float):
            if ki >= 0:
                self.ki = ki
                self.ki_updated.emit(self.ki)
            else: raise ValueError("ki must be non-negative")
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
            self.user_emergency_brake = status

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
            return self.service_brake or self.user_service_brake
        def get_emergency_brake(self):
            return self.emergency_brake or self.user_emergency_brake
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
            super().__init__()
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

        # PID controller to compute the power command
        # Input) desired_speed: float, current_speed: float, engineer: Engineer object
        # Return) the power command to be applied to the train
        ### If fault exists, return 0
        ### HOW DO WE HANDLE INTEGRAL OR U_K WHEN BRAKE IS ON
        def calculate_power_command_software(self, desired_speed: float, current_speed: float, time_step: float, engineer, brake):
            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()
            print(f"Kp: {kp}, Ki: {ki}")

            # Calculate the error
            desired_speed = min(desired_speed, self.speed_limit)
            print("Current Speed: ", current_speed, "Desired Speed: ", desired_speed)
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

            if self.power_command < 0:
                brake.set_service_brake(True)
            
            if brake.get_status():
                #### THIS LINE IS FOR TESTING PURPOSES ONLY ####
                # self.power_command = max(self.power_command , -self.P_MAX)    # self.power_command = 0

            print(f"Power Command from Train Controller: {self.power_command}")

        
        def calculate_power_command_hardware(self, desired_speed: float, current_speed: float, time_step: float, engineer, brake):
            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()
            print(f"Kp: {kp}, Ki: {ki}")

            # Calculate the error
            # Authority distance = 
            desired_speed = min(desired_speed, self.speed_limit)
            print("Current Speed: ", current_speed, "Desired Speed: ", desired_speed)
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
                
            if self.brake.get_status():
                self.power_command = 0
                    
        # def calculate_current_speed(self, current_speed, time_step: float, brake):
        #     # If power command is greater than the maximum power, it's exceeded the physical limit so set it to the maximum power
            
        #     # if brake.get_status():
        #     #     self.power_command = -5
            
        #     # Calculate current speed based on power command            
        #     current_speed += self.power_command * time_step
        #     current_speed = min(current_speed, self.speed_limit)
        #     current_speed = max(current_speed, 0)

        #     return current_speed
        
        def set_speed_limit(self, speed_limit: float):
            self.speed_limit = speed_limit
            print(f"Speed Limit: {self.speed_limit}")
        
    ## Door class to hold door status
    # Door status = bool
    # False = closed, True = open
    class Doors(QObject):
        left_door_updated = pyqtSignal(bool)
        right_door_updated = pyqtSignal(bool)
        def __init__(self):
            super().__init__()
            self.left: bool = False
            self.right: bool = False
            self.exit_door: str = None   # left = "left", True = "right"

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
        # Input) bool: False = first value, Trye = second value
        def update_exit_door(self, exit_door: str):
            self.exit_door = "right" if self.exit_door == "Right" else "left"

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
        def __init__(self):

            super().__init__()
            self.lights: bool = False
            self.underground: bool = None # Boolean
            self.night_time: int = 43200 # 12 hours in seconds

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
        def update_lights(self, elapsed_time: float):
            prev_lights = self.lights
            self.set_lights(self.underground or (elapsed_time % 86400) > 43200)   # Set external lights if current block is underground
            if prev_lights != self.lights:
                print(f"Lights are now {'on' if self.lights else 'off'}")

    ## AC class to hold temperature status
    # Commanded temperature from driver (initialized to 69)
    # Current temperature from Train Model
    class AC(QObject):
        commanded_temp_updated = pyqtSignal(int)    # --> Train Model
        train_temp_updated = pyqtSignal(int)    # --> UI

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
            self.commanded_temp_updated.emit(self.commanded_temp)

        ## Accessor Function
        def get_commanded_temp(self):
            return self.commanded_temp
        def get_current_temp(self):
            return self.current_temp
        
        ## Update Function
        # Input) TrainModel object, string: "automatic" or "manual"
        def update_current_temp(self, temp: int):
            self.current_temp = temp
            self.train_temp_updated.emit(self.current_temp)


# Does beacon need to be encrypted
# All information from MBO needs to be encrypted
class MockTrainModel(QObject):
    engine_fault_updated = pyqtSignal(bool)
    brake_fault_updated = pyqtSignal(bool)
    signal_fault_updated = pyqtSignal(bool)
    comm_speed_updated = pyqtSignal(float)
    authority_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__() 
        # Train Model variables
        self.current_speed: float = 0
        self.commanded_speed: float = 0
        self.authority: float = 0

        self.power_command = 0
        self.position = 0
        self.block = 0

        self.commanded_temp = 69
        self.train_temp: int = 69

        self.engine_fault: bool = False
        self.brake_fault: bool = False
        self.signal_fault: bool = False
        
        self.service_brake: bool = False
        self.emergency_brake: bool = False

        self.left_door: bool = False
        self.right_door: bool = False
        self.lights: bool = False

    def set_power_command(self, power: float):
        self.power_command = power
        self.calculate_current_speed(1)

    # Float
    def get_current_speed(self):
        # Logic to get current speed of the train
        return self.current_speed
    def set_current_speed(self, speed: float):
        self.current_speed = round(speed, 2)
    def calculate_current_speed(self, time_step: float):
        # If power command is greater than the maximum power, it's exceeded the physical limit so set it to the maximum power
        
        # if brake.get_status():
        #     self.power_command = -5
        
        # Calculate current speed based on power command            
        self.current_speed += self.power_command * time_step
        self.set_current_speed(max(self.current_speed, 0))
        print("Current Speed: ", self.current_speed, "\n")

    # Iterative (float representing meters)? Absolute (position representing when to stop by)?
    def get_authority(self):
        # Logic to get the authority from the train model
        return self.authority
    def set_authority(self, authority: float):
        self.authority = round(authority, 2)
        self.authority_updated.emit(self.authority)

    # Float
    def get_commanded_speed(self):
        # Logic to get commanded speed from the train model
        return self.commanded_speed
    def set_commanded_speed(self, speed: float):
        self.commanded_speed = round(speed)
        self.comm_speed_updated.emit(self.commanded_speed)


    def set_position(self, position: float):
        self.position = position
    @pyqtSlot(int)
    def handle_block_update(self, block: int) -> None:
        self.block = block


    # Float
    def get_commanded_temp(self):
        # Logic to get commanded speed from the train model
        return self.commanded_temp
    def handle_commanded_temp_update(self, temp: int):
        self.commanded_temp = temp

    # float
    def get_train_temp(self):
        # Logic to get the temperature inside the train
        return self.train_temp
    def set_train_temp(self, temp: int):
        self.train_temp = temp
    

    # List of bools? Individual bools?
    # [engine, brake, signal]
    # No fault = [0, 0, 0]
    def get_fault_statuses(self):
        # Logic to get the fault status of the train
        return self.faults
    def set_fault_statuses(self, faults: list[bool]):
        self.faults = faults[0:3]   # Only take the first 3 elements

    def set_engine_fault(self, status: bool):
        self.faults[0] = status
        self.engine_fault_updated.emit(status)

    def set_brake_fault(self, status: bool):
        self.faults[1] = status
        self.brake_fault_updated.emit(status)
    
    def set_signal_fault(self, status: bool):
        self.faults[2] = status
        self.signal_fault_updated.emit(status)


    @pyqtSlot(bool)
    def handle_service_brake_update(self, status: bool) -> None:
        self.service_brake = status
    @pyqtSlot(bool)
    def handle_emergency_brake_update(self, status: bool) -> None:
        self.service_brake = status


    @pyqtSlot(bool)
    def handle_left_door_update(self, status: bool) -> None:
        self.left_door = status

    @pyqtSlot(bool)
    def handle_right_door_update(self, status: bool) -> None:
        self.right_door = status
    @pyqtSlot(bool)
    def handle_lights_update(self, status: bool) -> None:
        self.lights = status
        


class TrainSystem:
    def __init__(self, host=None, port=None, username=None, password=None):
        self.train_model = MockTrainModel()
        self.ssh_client = None
        if(host and port and username and password):
            self.ssh_client = self.create_ssh_connection(HOST, PORT, USERNAME, PASSWORD)
        # Hardware
        # self.controller = TrainController(25, 0.1, self.train_model, self.ssh_client)
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
        for _ in range(50):
            self.controller.update_train_controller()

        # self.controller.set_position(65)

        self.controller.set_setpoint_speed(30)
        for _ in range(50):
            self.controller.update_train_controller()
        
        # self.controller.set_setpoint_speed(30)
        # for _ in range(50):
        #     self.controller.update_train_controller()
        
        # self.controller.set_setpoint_speed(10)
        # for _ in range(50):
        #     self.controller.update_train_controller()
            

if __name__ == "__main__":
    # train_system = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
    train_system = TrainSystem()
    train_system.run()