
import serial
import time

"""
closeDoor
-have function for left, right and both
-set corresponding door status variables
"""

"""
setStation
-uses beacon data to know and update upcoming station
-do we keep this station displayed after leaving?
"""

'''
Storing previous beacon data: How are we going to do that and what will it look like
'''

'''
Authority: If authority == prev_authority, count down
            If authority != prev_authority, reset count down and begin counting down
'''

'''
# Functions with the word "update" in the name are updated from the Train Model and takes the Train Model as an argument
# Train Controller only talks with Train Model
# Train Model needed for initialization
#### = PySerial Integration for Hardware Train Controller
#### Train Controller (Raspberry Pi) will start the conversation by reaching out to the Train Model (Windows Computer) asking if the Train Controller can send its outputs
#### Train Model (Windows Computer) will respond with a message saying it is ready to receive the outputs and the Train Controller (Raspberry Pi) will send the outputs
#### Train Model (Raspberry Pi) will then receive the message from the Train Model (Windows Computer) with the Train Model's  outputs (Windows Computer)
#### Train Controller (Raspberry Pi) will then send a received message and update all of its variables with the Train Model's outputs\
'''

class TrainController:
    def __init__(self, train_model=None):
        self.hardware = False
        self.elapsed_time = 0
        self.time_step = 0.05  # 0.05 second time step

        ## Initialize objects
        self.train_model = train_model if train_model else TrainModel()  # Used to store data received from Train Model. No computations done in the object
        self.engineer = self.Engineer() # Engineer holds Kp and Ki and is the only one that can set them
        self.brake = self.Brake()       # Brake holds service and emergency brake status
        self.engine = self.Engine()     # Engine calculates power command and simulates train response
        self.doors = self.Doors()       # Doors holds left and right door status
        self.lights = self.Lights()     # Lights holds light status
        self.ac = self.AC()             # AC holds temperature status

        # Driver variables
        self.driver_mode = "manual" # Driver mode can be "automatic" or "manual"
        self.setpoint_speed = 0     # Setpoint speed for manual mode

        # Train Controller Calculated Variables
        self.maintenance_mode = False     # Maintenance status of the train
        self.distance_traveled = 0  # Distance traveled by the train. Calculated in the Train Controller

        # Train Model inputs (purely made for convenience)
        # THESE VALUES WILL RECEIVE NO CALCULATIONS (except for current speed FOR NOW)
        self.current_speed = None    # Current speed of the train
        self.commanded_speed = None  # Commanded speed from the Train Model (CTC or MBO)
        self.authority = None        # Authority from the Train Model (CTC or MBO)
        self.position = None         # Position of the train
        self.block = None            # Block the train is currently in
        self.station = None          # Station of the beacon the train is connected to
        self.faults = None           # Fault statuses from the Train Model (list of bools)

    # Simulate a time step of the train controller
    # Call this for ever press of the refresh button
    def simulate_timestep(self, train_model=None):
        # Update Mock Train Model
        hw_param = None if self.hardware else (train_model if train_model else self.train_model)
        self.train_model.update_mock_train_model(hw_param)
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
        self.position = self.train_model.get_position()
        self.block = self.train_model.get_block()
        self.station = self.train_model.get_station_name()
        # -- Distance from station -- #

        # Update all status variables
        self.engine.update_speed_limit(self.train_model)
        self.doors.set_exit_door(self.train_model)
        self.ac.update_current_temp(self.train_model, self.driver_mode)
        self.update_fault_status(self.train_model)
        self.lights.update_lights(self.train_model, self.elapsed_time, self.block)

        ## Train Controller Calculations
        # Run 1 more cycle of the simulation to update the current speed
        self.simulate_power_command(self.get_desired_speed())
        

    # Transmit necessary variables to Main Computer (Train Model), then mock Train Model will be updated
    def transmit_to_train_model(self):
        ##### THIS WILL BE TAKEN OUT #####
        self.train_model.set_current_speed(self.current_speed)

        if(self.hardware):
            '''
            #### Pyserial write all of the necessary outputs of the Train Controller to the Train Model
            #### Transmission starts with a ! and separation between variables is a space. Separation between elements in a list is a comma
            #### "!Power, Commanded train temp (2 digit int), Doors and lights commands (3 bools), Emergency brake (bool), Service brake (bool), Maintenance mode (bool)!"
            ##### This is how the function will work: The Train Controller will start the conversation by reaching out to the Train Model asking if the Train Controller can send its outputs
            #### The Train Model will respond with a message saying it is ready to receive the outputs and the Train Controller will send the outputs
            #### The Train Controller will then wait until it reads a message from the Train Model with the Train Model's outputs
            '''
            message = f"!{self.get_power_command()},{self.ac.get_commanded_temp()},{self.doors.get_left()},{self.doors.get_right()},{self.lights.get_status()},{self.brake.get_emergency_brake()},{self.brake.get_service_brake()},{self.maintenance_mode}!"
            
            with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
                ser.write(message.encode())
                time.sleep(1)  # Wait for the Train Model to be ready to receive

        else:
            '''
            # Transmit outputs to train model (Jeremy)
            # Train model (Jeremy) performs calculations and updates the train model
            ## Because there are no updates on train model, we are skipping this part and going straight to the update
            ## Test bench is changing train model directly so self.train_model will be automatically updated with new values
            # Take new train model (Jeremy) values and update the mock train model
            '''
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
        self.setpoint_speed = speed
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
        power_command = self.engine.compute_power_command(speed, self.current_speed, self.time_step, self.engineer, self.brake, self.maintenance_mode)
        self.current_speed, distance_traveled = self.engine.calculate_current_speed(power_command, self.train_model.current_speed, self.time_step, self.brake)
        self.distance_traveled += distance_traveled
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
            self.service_brake = False
            self.emergency_brake = False
        ## Mutator functions
        # Input) status: boolean
        def set_service_brake(self, status: bool):
            self.service_brake = status
        # Input) status: boolean
        def set_emergency_brake(self, status: bool):
            self.emergency_brake = status

        ## Toggle Functions
        def toggle_service_brake(self):
            self.service_brake = not self.service_brake
        def toggle_emergency_brake(self):
            self.emergency_brake = not self.emergency_brake

        ## Accessor functions
        def get_service_brake(self):
            return self.service_brake
        def get_emergency_brake(self):
            return self.emergency_brake
        def get_status(self):
            return self.service_brake or self.emergency_brake
       
    ## Engine class calculates power command and can simulate train response
    class Engine:
        def __init__(self):
            self.speed_limit = None  # Speed limit of the train
            self.P_MAX = 120  # Maximum power (kW)
            self.power_command = 0 # Power command

            self.u_k = 0 # Power command
            self.e_k_integral = 0 # Error integral
            self.u_k_integral = 0 # Power integral
            
        '''
        ## Factors/considerations
        # - Speed limit: Train Controller
        # - Power limit: Train Controller
        # - Brake status: Service and Emergency brake
        # - Brake Deceleration Rates: Service and Emergency
        '''

        def computer_authority(self, authority: float, current_speed: float, brake):
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
        def compute_power_command(self, desired_speed: float, current_speed: float, time_step: float, engineer, brake, maintenance_mode: bool = False):
            if(maintenance_mode):
                # Reset values
                self.u_k = 0 # Power command
                self.e_k_integral = 0 # Error integral
                self.u_k_integral = 0 # Power integral
                return 0
            
            

            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()

            # Calculate the error
            # Authority distance = 
            best_speed = min(desired_speed, self.speed_limit)
            e_k = best_speed - current_speed
            # Power command = Kp * error + Ki * integral of error
            p_cmd = kp * e_k + ki * self.u_k

            # Check if the power command exceeds the maximum power
            if p_cmd < self.P_MAX:
                self.u_k = self.u_k_integral + (time_step / 2) * (e_k + self.e_k_integral)
            else:
                # If the power command exceeds the maximum power, use the previous power command
                self.u_k = self.u_k_integral

            # Update the error and power integral for the next iteration
            self.e_k_integral = e_k
            self.u_k_integral = self.u_k

            ##### This will be used after integration
            # if p_cmd < 0:
            #     brake.set_service_brake(True)
            #     p_cmd = 0

            self.power_command = p_cmd
            return p_cmd
        
        def calculate_current_speed(self, power_command, current_speed, time_step: float, brake):
            # If power command is greater than the maximum power, it's exceeded the physical limit so set it to the maximum power
            if power_command > self.P_MAX:
                power_command = self.P_MAX
            # If power command magnitude is negative, we need to slow down so turn on the service brake
            elif power_command < -self.P_MAX:
                power_command = -self.P_MAX
            
            # If negative power command, set the power command to 0 and turn on brake
            if power_command < 0:
                brake.set_service_brake(True)
                
            ##### JUST FOR TESTING #####
            if(brake.get_service_brake() or brake.get_emergency_brake()):
                power_command = -self.P_MAX

            current_speed += power_command * time_step
            distance_traveled = current_speed * time_step
            
            return current_speed, distance_traveled
        def update_speed_limit(self, train_model):
            self.speed_limit = train_model.get_speed_limit()
        
    ## Door class to hold door status
    # Door status = bool
    # False = closed, True = open
    class Doors:
        def __init__(self):
            self.left = False
            self.right = False
            self.exit_door = None   # False = "left", True = "right"

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
        def set_exit_door(self, train_model):
            right_door = train_model.get_exit_door()
            self.exit_door = "right" if right_door else "left"

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
            self.ext_lights = False
            self.int_lights = False
            self.underground_blocks = [] # List of blocks that are underground
            self.night_time = 43200 # 12 hours in seconds

        ## Mutator Function
        def set_ext_lights(self, status: bool):
            self.lights = status
        def set_int_lights(self, status: bool):
            self.lights = status
        def lights_on(self):
            self.lights = True
        def lights_on(self):
            self.lights = False

        ## Toggle Function
        def toggle_lights(self):
            self.lights = not self.lights

        ## Accessor Function
        def get_int_lights(self):
            return self.int_lights
        def get_ext_lights(self):
            return self.ext_lights
        def get_status(self):
            return self.ext_lights, self.int_lights
        def get_underground_blocks(self):
            return self.underground_blocks
        
        ## Update Functions
        def update_underground_blocks(self, underground_blocks):
            self.underground_blocks = underground_blocks
        def update_lights(self, train_model, elapsed_time: float, block: int):
            self.update_underground_blocks(train_model.get_underground_blocks())    # Update underground blocks
            self.set_ext_lights(block in self.underground_blocks or (elapsed_time % 86400) > 43200)   # Set external lights if current block is undreground
            self.set_int_lights((elapsed_time % 86400) > 43200)   # Set internal lights if it's night time. Assumes train starts at dawn

    ## AC class to hold temperature status
    # Commanded temperature from driver (initialized to 69)
    # Current temperature from Train Model
    class AC:
        def __init__(self):
            # Automatic temperature when in Automatic mode (69 degrees Fahrenheit)
            self.auto_temp = 69
            self.max_temp = 80
            # Commanded temperature from driver (initialized to auto_temp)
            self.commanded_temp = self.auto_temp
            # Current temperature inside the train
            self.current_temp = None

        ## Mutator Function
        def set_commanded_temp(self, temp: int):
            self.commanded_temp = min(round(temp), self.max_temp)

        ## Accessor Function
        def get_commanded_temp(self):
            return self.commanded_temp
        def get_current_temp(self):
            return self.current_temp
        
        ## Update Function
        # Input) TrainModel object, string: "automatic" or "manual"
        def update_current_temp(self, train_model, driver_mode: str):
            self.current_temp = train_model.get_train_temp()
            # If in automatic mode, set the commanded temperature to the automatic temperature
            if(driver_mode == "automatic"):
                self.set_commanded_temp(self.auto_temp)


# Does beacon need to be encrypted
# All information from MBO needs to be encrypted
class TrainModel:
    def __init__(self):
        self.current_speed = 0
        self.speed_limit = 19.44  #m/s
        self.position = 0
        self.authority = 0
        self.commanded_speed = 0
        self.train_temp = 0
        self.station = 0
        self.distance_from_station = 0
        self.exit_door = 0
        self.block = 0
        self.underground_blocks = [0, 1, 2]
        self.faults = [0, 0, 0]

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
    def set_speed_limit(self, speed: int):
        self.speed_limit = speed

    def get_distance_from_station(self):
        # Logic to get the distance from the station
        return self.distance_from_station
    def set_distance_from_station(self, distance: float):
        self.distance_from_station = round(distance, 2)

    # 1 floats
    # Distance from starting point (or relative point 0)
    # Distance from previous beacon
    # Still need to figure out how to do this
    def get_position(self):
        # Logic to get current position of the train
        return self.position
    def set_position(self, position: float):
        self.position = round(position, 2)

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
    def set_train_temp(self, temp: float):
        self.train_temp = round(temp)

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
        self.block = block

    # List of chars (list of blocks)
    def get_underground_blocks(self):
        # Logic to get the underground status of the train
        return self.underground_blocks
    def set_underground_blocks(self, blocks: list[int]):
        self.underground_blocks = blocks

    # Bool (left, right)
    def get_exit_door(self):
        # Logic to get the status of the exit door
        return self.exit_door
    def set_exit_door(self, door: bool):
        self.exit_door = door

    # List of bools? Individual bools?
    # [engine, brake, signal]
    # No fault = [0, 0, 0]
    def get_fault_statuses(self):
        # Logic to get the fault status of the train
        return self.faults
    def set_fault_statuses(self, faults: list[bool]):
        self.faults = faults[0:3]   # Only take the first 3 elements




    # #### MAIN COMPUTER USES THIS FUNCTION ####
    # #### THIS IS JEREMY ####
    def transmit_to_hw_train_model(self):
        '''
        #### Pyserial write all of the necessary outputs of the Train Model to the Train Controller
        #### Transmission starts with a ! and separation between variables is a space. Separation between elements in a list is a comma
        #### "!Current speed, Position, Authority, Commanded speed, Train temp, Station, Block, Underground blocks, Exit door, Faults, Speed limit!"
        ##### This is how the function will work: The Train Model will start the conversation by reaching out to the Train Controller asking if the Train Model can send its outputs
        #### The Train Controller will respond with a message saying it is ready to receive the outputs and the Train Model will send the outputs
        #### The Train model will wait until the message is received
        #### The Train Model will then update all of its variables with the Train Controller's outputs
        #### The Train Model will then send the newly updated variables to the Train Controller
        '''
        message = f"!{self.get_current_speed()},{self.get_position()},{self.get_authority()},{self.get_commanded_speed()},{self.get_train_temp()},{self.get_station_name()},{self.get_block()},{','.join(self.get_underground_blocks())},{','.join(map(str, self.get_exit_door()))},{','.join(map(str, self.get_fault_statuses()))},{self.get_speed_limit()}!"

        with serial.Serial('COM1', 9600, timeout=1) as ser:  # Adjust COM port as necessary
            ser.write(message.encode())
            time.sleep(1)  # Wait for the Train Controller to be ready to receive

        return True
    
    
    # This is used to update all train model variables with the real Train Model
    # In hardware, this is done through parsing. In software, this is done through the object
    def update_mock_train_model(self, train_model=None):
        # Update through serial encoding
        if(train_model is None):
            '''
            #### Pyserial read all of the variables for the Train Model from another Train Model
            #### Update its own variables with the variables from the pyserial message
            #### Will take the message from the Windows Computer and keep it in this object on the Raspberry Pi
            #### Message to decode: "!Current speed, Position, Authority, Commanded speed, Train temp, Station, Block, Underground blocks, Exit door, Faults, Speed limit!"
            '''
            with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
                message = ser.readline().decode().strip()

            if message.startswith("!"):
                data = message[1:-1].split(',')
                self.current_speed = float(data[0])
                self.position = float(data[1])
                self.authority = float(data[2])
                self.commanded_speed = float(data[3])
                self.train_temp = float(data[4])
                self.station = data[5]
                self.block = data[6]
                self.underground_blocks = data[7].split(',')
                self.exit_door = [bool(int(data[8])), bool(int(data[9]))]
                self.faults = [bool(int(fault)) for fault in data[10].split(',')]
                self.speed_limit = float(data[11])
            return False
        else:
            self.current_speed = train_model.get_current_speed()
            self.speed_limit = train_model.get_speed_limit()
            self.position = train_model.get_position()
            self.authority = train_model.get_authority()
            self.commanded_speed = train_model.get_commanded_speed()
            self.train_temp = train_model.get_train_temp()

            self.exit_door = train_model.get_exit_door()
            self.station = train_model.get_station_name()
            self.distance_from_station = train_model.get_distance_from_station()
            self.exit_door = train_model.get_exit_door()
            self.block = train_model.get_block()
            self.underground_blocks = train_model.get_underground_blocks()
            self.faults = train_model.get_fault_statuses()
            return True
        


class TrainSystem:
    def __init__(self):
        self.train_model = TrainModel()
        self.controller = TrainController()


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
    train_system = TrainSystem()
    train_system.run()
