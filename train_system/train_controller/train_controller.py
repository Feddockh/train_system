
import paramiko
import json
from collections import deque as dq

from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QObject

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.station import Station
from train_system.common.authority import Authority
from train_system.common.authority import Authority

from train_system.train_model.train_model import TrainModel
from train_system.train_controller.engineer import Engineer



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
    authority_updated = pyqtSignal(float)
    destination_updated = pyqtSignal(int)
    delete_train = pyqtSignal(int)

    #lights_updated = pyqtSignal(bool) -> in lights class
    #left_door_updated = pyqtSignal(bool) -> in doors class
    #right_door_updated = pyqtSignal(bool) -> in doors class
    #train_temp_updated = pyqtSignal(int) -> in ac class
    #service_brake_updated = pyqtSignal(bool) -> in brakes class
    #emergency_brake_updated = pyqtSignal(bool) -> in brakes class

    curr_speed_updated = pyqtSignal(float)
    station_name_updated = pyqtSignal(str)

    def __init__(self, engineer: Engineer = None, train_model=None, line_name: str = "green", id: int = 0, ssh=None) -> None:
        super().__init__()
        self.line = line_name
        self.id = id

        self.hardware = True if ssh else False
        print(f"Hardware: {self.hardware}")
        self.time_step = 1  # 1 second time step
        self.train_length = 32.2  # 32.2 meters

        ## Initialize objects
        self.train_model = MockTrainModel()  # Used to store data received from Train Model. No computations done in the object
        self.train_model.engine_fault_updated.connect(self.handle_fault_update)
        self.train_model.brake_fault_updated.connect(self.handle_fault_update)
        self.train_model.signal_fault_updated.connect(self.handle_fault_update)
        self.faults_fixed.connect(self.train_model.handle_faults_fixed)
        # self.train_model.comm_speed_received.connect(self.handle_comm_speed_changed)
        self.train_model.authority_received.connect(self.update_authority)
        self.train_model.satellite_received.connect(self.handle_satellite_received)
        self.train_model.emergency_mode.connect(self.handle_emergency_mode)

        self.engineer = engineer if engineer else Engineer() # Engineer holds Kp and Ki and is the only one that can set them

        self.brake = self.Brake()       # Brake holds service and emergency brake status
        self.brake.service_brake_updated.connect(self.train_model.handle_service_brake_update)
        self.brake.emergency_brake_updated.connect(self.train_model.handle_emergency_brake_update)


        self.engine = self.Engine(ssh)     # Engine calculates power command and simulates train response
        self.doors = self.Doors()       # Doors holds left and right door status
        self.doors.left_door_updated.connect(self.train_model.handle_left_door_update)
        self.doors.right_door_updated.connect(self.train_model.handle_right_door_update)
        self.lights = self.Lights()     # Lights holds light status
        self.lights.lights_updated.connect(self.train_model.handle_lights_update)
        ##### self.time_keeper.tick.connect(self.lights.update_lights)
        self.ac = self.AC(self.train_model.get_train_temp())    # AC holds temperature status
        self.ac.commanded_temp_updated.connect(self.train_model.handle_commanded_temp_update)
        self.train_model.train_temp_updated.connect(self.ac.update_current_temp)
        self.line = Line(line_name)

        # Driver variables
        self.driver_mode = "manual" # Driver mode can be "automatic" or "manual"
        self.setpoint_speed = 0     # Setpoint speed for manual mode
        self.MAX_SPEED = 21.67

        # Train Controller Calculated Variables
        self.maintenance_mode = False     # Maintenance status of the train
        self.emergency_mode = False     # Track Controller emergency signal
        
        # Train Block Inputs
        self.line.load_defaults()
        self.route = dq(self.line.route.from_yard)  # Route queue
        self.reset_route()  # Initialize track block, position, and polarity

        # Train Model inputs
        self.current_speed = self.train_model.current_speed    # Current speed of the train
        self.commanded_speed = self.train_model.commanded_speed  # Commanded speed from the Train Model (CTC or MBO)
        self.authority, self.destination = None, None
        self.AUTHORITY_PADDING = 0 #0.25 * self.train_length  # Padding for authority
        self.authority = 0        # Authority and destination from the Train Model (CTC or MBO)
        self.destination = None     # Track block that the train should open its doors at
        self.dropped_off = True     # Initialized to true so destination can receive a new value
        self.engine_fault = self.train_model.engine_fault           # Fault status from the Train Model
        self.brake_fault = self.train_model.brake_fault           # Fault status from the Train Model
        self.signal_fault = self.train_model.signal_fault           # Fault status from the Train Model
        
        self.station_name = ""

    # Update all variables with the train model input, calculate, then output to train model
    # Take train model outputs, update all variables, and transmit to train model the Train Controller's new values
    # Triggered by receiving authority
    def update_train_controller(self):
        self.brake.service_brake = False
        # If last timestep TM received emergency from Track Controller, set service brake
        if self.emergency_mode:
            self.brake.set_service_brake(True)
        if self.destination_counter > 0:
            print("Destination Counter: ", self.destination_counter)
            self.brake.set_service_brake(True)
            self.destination_counter -= 1
        self.emergency_mode = False # Reset emergency mode. Will be set back to True if emergency mode is triggered again
        self.update_current_speed(self.train_model.get_current_speed())
        self.update_commanded_speed(self.train_model.get_commanded_speed())
        self.train_model.update_current_temp()

        self.lights.update_lights()


        # Update variables with train model input
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
        self.loop_length = self.line.get_path_length(self.line.route.default_route + self.line.route.past_yard)
        print("========= Route Loop Length: ", self.loop_length, "===========")
        self.block = self.route[0]
        self.track_block: TrackBlock = self.line.get_track_block(self.block)
        print("Track block: ", self.track_block.number)

        self.position = 0
        self.polarity = 0
        self.block_number = None
        self.station = None
        self.destination_counter = 0
        self.yard_block = 152
        self.finished = False
        self.update_track_block()

    # Update all Track Block variables
    def update_track_block(self):
        # Update all Track Block variables
        self.engine.set_speed_limit(self.track_block.speed_limit / 3.6)
        self.polarity += self.track_block.length
        
        self.station = self.track_block.station.name if self.track_block.station else None
        print(f"Station: {self.station}")

        if self.station:
            exit_door = self.track_block.station.get_side(self.block_number, self.track_block.number)
            self.doors.update_exit_door(exit_door)
            print(f"------------ Track Block: {self.track_block.number}, Exit Door: {exit_door} ------------")

        self.block_number = self.track_block.number
        self.lights.update_underground(self.track_block.underground)

    def increment_track_block(self):
        # Pop to get next track block
        self.route.popleft()
        print(f"Route Length: {len(self.route)}")

        # If not next to finish, continue
        if len(self.route) == 0 and not self.finished:
            ## Look at authority to see whether to circle or to end route
            if self.destination == self.yard_block:
                self.route.extend(self.line.route.to_yard)    ## If authority is negative, go back to yard
                self.finished = True
            else:
                print("------------------------------ Finished Route --------------------------------")
                # Append past_yard and append default route again
                self.route.extend(self.line.route.past_yard)
                self.route.extend(self.line.route.default_route)
                self.position -= self.loop_length
                self.set_position(self.position)
        elif self.finished:
            #### DELETE TRAIN CONTROLLER ####
            self.delete_train.emit(self.id)
            return
            
        # Increment track block
        self.block = self.route[0]
        self.track_block = self.line.get_track_block(self.block)
        print("--------------------- Track block: ", self.track_block.number, "---------------------")
        
        # Update all Track Block variables
        self.update_track_block()

    ## Position Functions
    # Input) float: position from the yard
    def set_position(self, position: float):
        # print("------------- Setting Position ---------------")
        if position > self.position:
            self.polarity -= position - self.position
            self.destination_counter = 0
        elif position < self.position:
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


        # print(f"----------- Position: {self.position}, Polarity: {self.polarity} -----------")
            
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
    def update_current_speed(self, speed: float):
        self.current_speed = speed
        self.curr_speed_updated.emit(speed)
        if(self.current_speed == 0):
            # Emit that faults are fixed
            if self.maintenance_mode:
                self.set_maintenance_mode(False)

            # If the destination is the current block number
            if self.destination == self.block_number:
                # If we're in the center of the block, open doors
                if abs(self.track_block.length / 2 - self.polarity) <= 0.25*self.track_block.length:
                    self.at_station()
        elif self.doors.get_status():
            self.doors.close_door()
        
    def at_station(self):
        self.doors.open_door()
        if self.dropped_off == False:
            self.dropped_off = True
            self.destination_counter = 30
        
    ## Setpoint and Commanded Speed Functions
    def set_setpoint_speed(self, speed: float):
        self.setpoint_speed = min(speed, self.MAX_SPEED)
        self.setpoint_speed = max(self.setpoint_speed, 0)
        self.setpoint_speed_updated.emit(self.setpoint_speed)
        print(f"Setpoint Speed: {self.setpoint_speed}")
    def get_setpoint_speed(self):
        return self.setpoint_speed
    
    def get_commanded_speed(self):
        return self.commanded_speed       
    def update_commanded_speed(self, speed: float):
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
        # print(f"Current Speed from Train Model: {self.current_speed}")
        if(self.engine.ssh is None):
            self.engine.calculate_power_command_software(speed, self.current_speed, self.time_step, self.engineer, self.brake)
        else:
            self.engine.calculate_power_command_hardware(speed, self.current_speed, self.time_step, self.engineer, self.brake)
        
        # Set brakes to trigger signals for Train Model and UI
        self.brake.set_service_brake(self.brake.get_service_brake())
        self.brake.set_emergency_brake(self.brake.get_emergency_brake())
        print(f"Train Model Brakes: Service: {self.train_model.service_brake}, Emergency: {self.train_model.emergency_brake}")

        # Update the power command in the Train Model 
        ##### WILL GET RID OF SPEED LIMIT LATER
        self.train_model.set_power_command(self.engine.power_command, self.engine.speed_limit)  #self.train_model.set_power_command(self.engine.power_command)

        self.power_updated.emit(self.engine.power_command) # Emit power command to UI
        
    # Update the fault status of the train
    # Call maintenance if there is a fault
    @pyqtSlot(bool)
    def handle_fault_update(self, fault: bool):
        if(fault):
            print("!!!! Fault detected !!!!")
            self.faults = self.train_model.get_fault_statuses()
            self.set_maintenance_mode(True)

    ## Maintenance Mode Functions
    # Maintenance mode = set emergency brake and make full stop to fix faults
    def get_maintenance_mode(self):
        return self.maintenance_mode
    def set_maintenance_mode(self, status: bool):
        self.maintenance_mode = status
        self.brake.set_emergency_brake(status)
        if status == False:
            self.faults = [False, False, False]
            self.faults_fixed.emit()


    def get_authority(self):
        return self.authority
    @pyqtSlot(float)
    def set_authority(self, authority: float):
        self.authority = authority

        # Go to destination station if at destination block
        # Only go to destination station if this is the destination block and train hasn't dropped off yet
        if self.destination == self.block_number and self.dropped_off == False:
            # Calculate position of the station
            station_pos = self.position + self.polarity - 0.5*self.track_block.length
            print(f"Station Position: {station_pos}")
            
            self.authority = min(self.authority, station_pos)
        print(f"New authority: {self.authority}")
        self.authority_updated.emit(authority)
    def parse_authority(self, authority: Authority):
        self.authority = abs(authority.get_distance() + self.AUTHORITY_PADDING)
        self.set_destination(authority.get_stop_block())

        #parse the station name from authority
        # block_str = str(self.line.get_track_block(int(self.destination)))
        # find_station = block_str.splitlines()
        # full_station = find_station[10]
        # m_loc = full_station.find("m")
        # b_loc = full_station.find("b")
        # self.station_name = ""
        # for i in range(m_loc + 3, b_loc -2):
        #     self.station_name = self.station_name + full_station[i]

        # self.station_name_updated.emit(self.station_name)
    @pyqtSlot(Authority)
    def update_authority(self, authority: Authority):
        self.parse_authority(authority)
        self.set_authority(self.authority + self.position)
        self.update_train_controller()

    # Check if the train needs to stop because of authority
    def stop_for_authority(self):
        # Use kinematics equation v^2 = v0^2 + 2a(x-x0) to calculate the distance needed to stop
        # If the distance needed to stop is greater than the authority, set the service brake
        distance = (self.current_speed ** 2) / (2 * 1.2)  # 1.2 m/s^2 is the deceleration rate
        # print(f"Position + Distance: {self.position + distance}, Authority: {self.authority}")

        # Position you will be stopped by >= position you need to be stopped by
        ## MIGHT NEED TO ADD PADDING
        if self.position + distance >= self.authority - self.AUTHORITY_PADDING: # Return True if the distance needed to stop is less than the authority
            print("Stopping for authority")
            self.brake.set_service_brake(True)
        
    @pyqtSlot(str, float)
    def handle_satellite_received(self, authority: str, commanded_speed: float):
        self.update_authority(authority)
        self.update_commanded_speed(commanded_speed)
        self.update_train_controller()

    
    @pyqtSlot()
    def handle_emergency_mode(self):
        self.emergency_mode = True


    ## Functions for arriving and departing from stations
    def set_station(self, station: str):
        self.station = station
    def get_station(self):
        return self.station
    @pyqtSlot(int)
    def set_destination(self, destination: int):
        # If new destination is received, reset dropped off variable
        if self.destination != destination and self.dropped_off:
            self.destination = destination
            self.dropped_off = False
            self.destination_updated.emit(destination)
    def get_destination(self):
        return self.destination

    @pyqtSlot(bool)
    def handle_toggle_driver_mode(self, check):
        if check:
            print("Automatic Mode")
            self.set_driver_mode("automatic")
        else:
            print("Manual Mode")
            self.set_driver_mode("manual")

    @pyqtSlot(str)
    def handle_setpoint_edit_changed(self, x: str) -> None:
        x_num = float(x)
        if(x_num <= 43 and x_num >= 0):
            self.set_setpoint_speed(x_num / 2.23694)
        else:
            self.set_setpoint_speed(0)

    @pyqtSlot(bool)
    def handle_service_brake_toggled(self, check: bool) -> None:
        if check:
            self.brake.set_user_service_brake(True)
        else:
            self.brake.set_user_service_brake(False)

    @pyqtSlot(bool)
    def handle_emergency_brake_toggled(self, check: bool) -> None:
        if check:
            self.brake.set_user_emergency_brake(True)
        else:
            self.brake.set_user_emergency_brake(False)

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

    @pyqtSlot(str)
    def handle_authority_changed(self, authority: str) -> None:
        new_authority = Authority()
        new_authority.authority = authority
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
        #self.engineer.kp = kp
        self.engineer.kp = kp
        self.kp_updated_for_eng.emit(kp)

    @pyqtSlot(int)
    def handle_ki_changed(self, ki: int) -> None:
        #do this to keep from being recursive
        self.engineer.ki = ki

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
    # class Engineer(QObject):
    #     kp_updated = pyqtSignal(int)
    #     ki_updated = pyqtSignal(int)
        
    #     def __init__(self, kp=400, ki=20):
    #         super().__init__()
    #         self.kp = kp
    #         self.ki = ki

    #     ## Mutator functions
    #     def set_kp(self, kp: float):
    #         if kp >= 0:
    #             self.kp = kp
    #             self.kp_updated.emit(self.kp)
    #         else: raise ValueError("kp must be non-negative")
    #     def set_ki(self, ki: float):
    #         if ki >= 0:
    #             self.ki = ki
    #             self.ki_updated.emit(self.ki)
    #         else: raise ValueError("ki must be non-negative")
    #     def set_engineer(self, kp: float, ki: float):
    #         self.set_kp(kp)
    #         self.set_ki(ki)

    #     ## Accessor functions
    #     def get_kp(self):
    #         return self.kp
    #     def get_ki(self):
    #         return self.ki
    #     def get_engineer(self):
    #         return self.get_kp(), self.get_ki()

    ## Brake class to hold brake status
    class Brake(QObject):
        user_service_brake_updated = pyqtSignal(bool)
        user_emergency_brake_updated = pyqtSignal(bool)
        emergency_brake_updated = pyqtSignal(bool)
        service_brake_updated = pyqtSignal(bool)
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
            self.service_brake = status or self.user_service_brake
            self.service_brake_updated.emit(status) # For Train Model
        # Input) status: boolean
        def set_emergency_brake(self, status: bool):
            self.emergency_brake = status or self.user_emergency_brake
            self.emergency_brake_updated.emit(status) # For Train Model
        def set_user_service_brake(self, status: bool):
            print("set brake")
            self.user_service_brake = status
            self.user_service_brake_updated.emit(status)
        def set_user_emergency_brake(self, status: bool):
            self.user_emergency_brake = status
            self.user_emergency_brake_updated.emit(status)

        ## Toggle Functions
        def toggle_service_brake(self):
            self.set_service_brake(not self.service_brake)
        def toggle_emergency_brake(self):
            self.set_emergency_brake(not self.emergency_brake)
        def toggle_user_service_brake(self):
            self.user_service_brake = not self.user_service_brake
            self.user_service_brake_updated.emit(self.user_service_brake)
        def toggle_user_emergency_brake(self):
            self.user_emergency_brake = not self.user_emergency_brake
            self.user_emergency_brake_updated.emit(self.user_emergency_brake)


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
            self.SL_PADDING = 0 #4.4704    # Padding of 10 mph
            self.P_MAX = 120  # Maximum power (kW) = 120
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
            #print(f"Kp: {kp}, Ki: {ki}")

            # Calculate the error
            desired_speed = min(desired_speed, self.speed_limit)
            print("Current Speed: ", current_speed, "Desired Speed: ", desired_speed)
            e_k = desired_speed - current_speed
            # Power command = Kp * error + Ki * integral of error
            self.power_command = kp * e_k + ki * self.u_k

            # Check if the power command exceeds the maximum power
            if self.power_command <= self.P_MAX:
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
            
            # print(f"Power Command from Train Controller: {self.power_command}")

            if brake.get_status():
                #### THIS LINE IS FOR TESTING PURPOSES ONLY
                self.power_command = -self.P_MAX    # self.power_command = 0

        
        def calculate_power_command_hardware(self, desired_speed: float, current_speed: float, time_step: float, engineer, brake):
            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()
            #print(f"Kp: {kp}, Ki: {ki}")

            # Calculate the error
            # Authority distance = 
            desired_speed = min(desired_speed, self.speed_limit)
            #print("Current Speed: ", current_speed, "Desired Speed: ", desired_speed)
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
        
        def set_speed_limit(self, speed_limit: float):
            self.speed_limit = speed_limit - self.SL_PADDING
            #print(f"Speed Limit: {self.speed_limit}")
        
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
            print(f"Left Door: {self.left}")
            self.left_door_updated.emit(self.left)
        # Input) status: boolean
        def set_right(self, status: bool):
            self.right = status
            print(f"Right Door: {self.right}")
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
            return self.get_left() or self.get_right()
        
        # Update the exit door status
        # Input) bool: False = first value, Trye = second value
        def update_exit_door(self, exit_door: str):
            self.exit_door = "right" if exit_door == "Right" else "left"

        def open_door(self):
            print("Opening door: ", self.exit_door)
            if self.exit_door == "left":
                self.set_left(True)
                self.left_door_updated.emit(self.left)
            elif self.exit_door == "right":
                self.set_right(True)
                self.right_door_updated.emit(self.right)
            else: 
                raise ValueError("Exit door not set")
            
        def close_door(self):
            print("Closing doors")
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
            self.elapsed_time: int = 0

        ## Mutator Functions
        def lights_on(self):
            self.lights = True
            self.lights_updated.emit(self.lights)
        def lights_off(self):
            self.lights = False
            self.lights_updated.emit(self.lights)
        def set_lights(self, status: bool):
            self.lights = status
            if self.lights:
                print(f"Lights are on. Underground: {self.underground}")
            else:
                print(f"Lights are off. Underground: {self.underground}")
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
            self.set_lights(underground)
            
        def update_lights(self):
            self.set_lights(self.underground or (self.elapsed_time % 86400) > 43200)   # Set external lights if current block is underground
            self.elapsed_time += 1

    ## AC class to hold temperature status
    # Commanded temperature from driver (initialized to 69)
    # Current temperature from Train Model
    class AC(QObject):
        commanded_temp_updated = pyqtSignal(int)    # --> Train Model
        train_temp_updated = pyqtSignal(float)    # --> UI

        def __init__(self, temp: int):
            super().__init__() 
            # Commanded temperature from driver (initialized to auto_temp)
            self.commanded_temp = temp
            # Current temperature inside the train
            self.current_temp = temp
            
            self.MAX_TEMP = 80
            self.MIN_TEMP = 60
            

        ## Mutator Function
        def set_commanded_temp(self, temp: int):
            self.commanded_temp = min(round(temp), self.MAX_TEMP)
            self.commanded_temp = max(self.commanded_temp, self.MIN_TEMP)
            print(f"Commanded Temp Set: {self.commanded_temp}")
            self.commanded_temp_updated.emit(self.commanded_temp)

        ## Accessor Function
        def get_commanded_temp(self):
            return self.commanded_temp
        def get_current_temp(self):
            return self.current_temp
        
        ## Update Function
        # Input) TrainModel object, string: "automatic" or "manual"
        def update_current_temp(self, temp: float):
            self.current_temp = round(temp)
            print(f"Current Temp: {self.current_temp}")
            self.train_temp_updated.emit(self.current_temp) # For UI


# Does beacon need to be encrypted
# All information from MBO needs to be encrypted
class MockTrainModel(QObject):
    engine_fault_updated = pyqtSignal(bool)
    brake_fault_updated = pyqtSignal(bool)
    signal_fault_updated = pyqtSignal(bool)
    # comm_speed_received = pyqtSignal(float)
    authority_received = pyqtSignal(Authority)
    satellite_received = pyqtSignal(str, float) # Authority, commanded speed
    train_temp_updated = pyqtSignal(float)
    emergency_mode = pyqtSignal()

    def __init__(self):
        super().__init__() 
        # Train Model variables
        self.current_speed: float = 0
        self.commanded_speed: float = 10
        self.authority: Authority = Authority(10000000,65) # Authority and desination block number

        self.power_command = 0
        self.position = 0
        self.block_number = 0

        self.commanded_temp = 69
        self.train_temp: float = 69

        self.faults: list[bool] = [False, False, False]
        self.engine_fault: bool = False
        self.brake_fault: bool = False
        self.signal_fault: bool = False
        
        self.service_brake: bool = False
        self.emergency_brake: bool = False

        self.left_door: bool = False
        self.right_door: bool = False
        self.lights: bool = False

    def set_power_command(self, power: float, speed_limit: float):
        self.power_command = power
        self.calculate_current_speed(1, speed_limit)

    # Float
    def get_current_speed(self):
        # Logic to get current speed of the train
        return self.current_speed
    def update_current_speed(self, speed: float):
        self.current_speed = round(speed, 2)

    def calculate_current_speed(self, time_step: float, speed_limit: float):        
        if self.service_brake or self.emergency_brake:
            self.power_command = -5
            # print(f"BRAKES ACTIVATED === Service Brake: {self.service_brake}, Emergency Brake: {self.emergency_brake}")
    
        # Calculate current speed based on power command            
        self.current_speed += self.power_command * time_step
        self.current_speed = min(self.current_speed, speed_limit)
        self.update_current_speed(max(self.current_speed, 0))
        print("Power Command:", self.power_command, "Current Speed: ", self.current_speed, "\n")

    # Iterative (float representing meters)? Absolute (position representing when to stop by)?
    def get_authority(self):
        # Logic to get the authority from the train model
        return self.authority
    def set_authority(self, authority: Authority):
        self.authority = authority
        self.authority_received.emit(self.authority)
    def decode_authority(self, authority: str):
        ### Decode the authority string ###
        new_authority = Authority()
        new_authority.authority = authority
        self.set_authority(authority)

    # Float
    def get_commanded_speed(self):
        # Logic to get commanded speed from the train model
        return self.commanded_speed
    def set_commanded_speed(self, speed: float):
        self.commanded_speed = speed
        self.comm_speed_received.emit(self.commanded_speed)
        print("Train Model -- Commanded Speed: ", self.commanded_speed)
        # self.comm_speed_received.emit(self.commanded_speed)
    def decode_commanded_speed(self, speed: str):
        # String to float
        self.set_commanded_speed(float(speed))

    def set_position(self, position: float):
        self.position = position
    @pyqtSlot(int)
    def handle_block_update(self, block: int) -> None:
        self.block_number = block


    # Float
    def get_commanded_temp(self):
        # Logic to get commanded speed from the train model
        return self.commanded_temp
    def handle_commanded_temp_update(self, temp: int):
        self.commanded_temp = temp
    @pyqtSlot(int)
    def update_current_temp(self):
        if self.train_temp < self.commanded_temp:
            self.train_temp += 0.25
        elif self.train_temp > self.commanded_temp:
            self.train_temp -= 0.25
        else:
            return
        self.train_temp_updated.emit(self.train_temp)

    # float
    def get_train_temp(self):
        # Logic to get the temperature inside the train
        return self.train_temp
    def set_train_temp(self, temp: float):
        self.train_temp = round(temp, 1)
    

    # List of bools? Individual bools?
    # [engine, brake, signal]
    # No fault = [0, 0, 0]
    def get_fault_statuses(self):
        # Logic to get the fault status of the train
        return self.faults
    def set_fault_statuses(self, faults: list[bool]):
        self.set_engine_fault(faults[0])
        self.set_brake_fault(faults[1])
        self.set_signal_fault(faults[2])
    @pyqtSlot()
    def handle_faults_fixed(self) -> None:
        self.set_engine_fault(False)
        self.set_brake_fault(False)
        self.set_signal_fault(False)

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
        # print("Train Model -- Service Brake: ", self.service_brake)
    @pyqtSlot(bool)
    def handle_emergency_brake_update(self, status: bool) -> None:
        self.emergency_brake = status
        # print("Train Model -- Emergency Brake: ", self.emergency_brake)

    @pyqtSlot()
    def handle_emergency_stop(self):
        self.emergency_mode.emit()


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
    def __init__(self, engineer: Engineer = None, line_name: str = "green", id: int = 0, ssh=None):
        self.line = line_name
        self.id = id
        self.train_model = MockTrainModel()
        self.engineer = engineer if engineer else Engineer()
        print(f"Engineer: {self.engineer.kp}, {self.engineer.ki}")
        self.ssh = ssh
        # Software if ssh, hardware if ssh=None
        self.controller = TrainController(self.engineer, self.train_model, line_name, id, self.ssh)


    # Move train forward
    def small_run(self):
        self.controller.set_setpoint_speed(10)
        for _ in range(5):
            self.controller.update_authority(Authority(1000000000,65))
            print(f"Power Command: {self.controller.engine.power_command}, Current Speed: {self.controller.current_speed}, Position: {self.controller.position}")

    # Multiple laps around
    def long_run(self):
        self.controller.set_setpoint_speed(20)
        for _ in range(80):
            self.controller.update_authority(Authority(1000000000,65))
            print(f"Position: {self.controller.position}, Authority: {self.controller.authority}")

    def full_loop_run(self):
        self.controller.set_setpoint_speed(20)
        self.controller.set_position(19900)
        for _ in range(20):
            self.controller.update_authority(Authority(1000000000,65))
            print(f"Position: {self.controller.position}, Loop Length: {self.controller.loop_length}")

    def to_yard_run(self):
        self.controller.set_setpoint_speed(20)
        self.controller.set_position(19900)
        for _ in range(20):
            self.controller.update_authority(Authority(1000000000,152))
            print(f"Position: {self.controller.position}")
            print(f"Track Block Start: {self.controller.position + self.controller.polarity - self.controller.track_block.length}, Track Block End: {self.controller.position + self.controller.polarity}")

    def destination_run(self):
        self.controller.set_position(200)
        self.controller.set_setpoint_speed(20)
        for _ in range(30):
            self.controller.update_authority(Authority(1000000000,65))
            print("Current Track Block: ", self.controller.track_block.number, ", Destination: ", self.controller.destination)
            print(f"Position: {self.controller.position}, Authority: {self.controller.authority}")
            
            if self.controller.doors.get_left() or self.controller.doors.get_right():
                print("!!!!!!!!!!!!! Destination Counter: ", self.controller.destination_counter, "!!!!!!!!!!!!!!!!")
                print(f"Position: {self.controller.position}, Authority: {self.controller.authority}, Destination: {self.controller.destination}")
                print("Doors are open. Exit Door: ", self.controller.doors.exit_door, "Left: ", self.controller.doors.get_left(), ", Right: ", self.controller.doors.get_right())
                print("Current Track Block: ", self.controller.track_block.number, ", Destination: ", self.controller.destination)
                print(f"Track Block Start: {self.controller.position + self.controller.polarity - self.controller.track_block.length}, Track Block End: {self.controller.position + self.controller.polarity}")
         
    # Can't move with emergency brake on
    def service_run(self):
        self.controller.brake.set_user_service_brake(True)
        self.controller.train_model.current_speed = 10
        self.controller.set_setpoint_speed(10)
        for _ in range(5):
            print(f"Train Model Brake: Service: {self.controller.train_model.service_brake}, Emergency: {self.controller.train_model.emergency_brake}")
            print(f"Train Model Current Speed: {self.controller.train_model.current_speed}")
            self.controller.update_authority(Authority(1000000000,65))

    # Can't move with emergency brake on
    def emergency_run(self):
        self.controller.brake.set_user_emergency_brake(True)
        self.controller.train_model.current_speed = 10
        self.controller.set_setpoint_speed(10)
        for _ in range(5):
            print(f"Train Model Brake: Service: {self.controller.train_model.service_brake}, Emergency: {self.controller.train_model.emergency_brake}")
            print(f"Train Model Current Speed: {self.controller.train_model.current_speed}")
            self.controller.update_authority(Authority(1000000000,65))

    # Desired speed follows the commanded speed and commanded speed updates
    def commanded_speed_run(self):
        self.controller.driver_mode = "automatic"
        for i in range(10):
            self.controller.train_model.set_commanded_speed(i)
            self.controller.update_authority(Authority(1000000000,65))
            print(f"Commanded Speed: {self.controller.train_model.commanded_speed}, Setpoint Speed: {self.controller.setpoint_speed}, Desired Speed: {self.controller.get_desired_speed()}")
            print(f"Train Model Current Speed: {self.controller.train_model.current_speed}")

    def switch_modes_run(self):
        self.controller.set_setpoint_speed(7)
        self.controller.train_model.set_commanded_speed(5)

        for i in range(10):
            self.controller.driver_mode = "automatic" if i%2 == 0 else "manual"
            print(f"Driver Mode: {self.controller.driver_mode}, Desired Speed: {self.controller.get_desired_speed()}")
            self.controller.update_authority(Authority(1000000000,65))
            print(f"Train Model Current Speed: {self.controller.train_model.current_speed}")

    # Train should slow to 0 then continue after full stop
    def fault_run(self):
        self.controller.train_model.set_fault_statuses([True, True, True])
        self.controller.train_model.current_speed = 10
        self.controller.set_setpoint_speed(10)
        print()
        for _ in range(5):
            self.controller.update_authority(Authority(1000000000,65))
            print(f"Maintenance mode: {self.controller.maintenance_mode}, Emergency brake: {self.controller.brake.get_emergency_brake()}")
            print(f"Current Speed: {self.controller.current_speed}")
            print(f"Train Model Faults: Engine: {self.controller.train_model.faults[0]}, Brake: {self.controller.train_model.faults[1]}, Signal: {self.controller.train_model.faults[2]}")
            

    def ac_run(self):
        self.controller.ac.set_commanded_temp(82)
        print("Commanded Temp: ", self.controller.ac.get_commanded_temp(), "\n")
        for _ in range(50):
            print(f"Current Temp: {self.controller.ac.get_current_temp()}")
            self.controller.update_authority(Authority(1000000000,65))
            

    

            

if __name__ == "__main__":
    # train_system = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
    train_system = TrainSystem()
    # train_system.small_run()
    # train_system.long_run()
    # train_system.full_loop_run()
    train_system.destination_run()
    # train_system.service_run()
    # train_system.emergency_run()
    # train_system.commanded_speed_run()
    # train_system.switch_modes_run()
    # train_system.fault_run()
    # train_system.ac_run()
