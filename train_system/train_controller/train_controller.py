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

# Functions with the word "update" in the name are updated from the Train Model and takes the Train Model as an argument
# Train Controller only talks with Train Model
# Train Model needed for initialization
#### = PySerial Integration for Hardware Train Controller
#### Train Controller will start the conversation by reaching out to the Train Model asking if the Train Controller can send its outputs
#### Train Model will respond with a message saying it is ready to receive the outputs and the Train Controller will send the outputs
#### Train Controller will then wait until it reads a message from the Train Model with the Train Model's outputs
#### Train Controller will then send a received message and update all of its variables with the Train Model's outputs
class TrainController:
    def __init__(self, train_model):
        ## Initialize objects
        self.engineer = self.Engineer()         # Engineer holds Kp and Ki and is the only one that can set them
        self.brake = self.Brake()               # Brake holds service and emergency brake status
        self.engine = self.Engine()             # Engine calculates power command and simulates train response
        self.doors = self.Doors()    # Doors holds left and right door status
        self.lights = self.Lights()  # Lights holds light status
        self.ac = self.AC(train_model)          # AC holds temperature status

        # Driver variables
        self.driver_mode = "manual" # Driver mode can be "automatic" or "manual"
        self.setpoint_speed = 0     # Setpoint speed for manual mode
        self.maintenance_mode = False     # Maintenance status of the train

        # Train Model inputs
        self.current_speed = None    # Current speed of the train
        self.commanded_speed = None  # Commanded speed from the Train Model (CTC or MBO)
        self.authority = None        # Authority from the Train Model (CTC or MBO)
        self.position = None         # Position of the train
        self.block = None            # Block the train is currently in
        self.station = None          # Station of the beacon the train is connected to
        self.train_temp = None       # Current temperature inside the train
        self.faults = None           # Fault statuses from the Train Model (list of bools)

        # Update functions
        self.update_train_model(train_model)    # This functoin will define all the "None" variables above
        
    # Update all variables with the train model input
    # Input) TrainModel object
    #### This function will no longer need the TrainModel object as an argument
    def update_train_model(self, train_model):
        #### PySerial write to Train Model "Update"
        #### PySerial read from Train Model "!All the inputs separated by spaces!"
        #### Parse through the message and assign each value to the corresponding variable
        # Update variables with train model input
        self.current_speed = train_model.get_current_speed()
        self.commanded_speed = train_model.get_commanded_speed()
        self.authority = train_model.get_authority()
        self.position = train_model.get_position()
        self.block = train_model.get_block()
        self.train_temp = train_model.get_train_temp()

        # Update all status variables
        self.update_fault_status(train_model)
        self.lights.update_lights(train_model, self.block)
        self.ac.update_current_temp(train_model)

        # Run 1 more cycle of the simulation to update the current speed
        self.simulate_speed(self.get_desired_speed())

    # Transmit necessary variables to the Train Model
    def transmit_to_train_model(self):
        #### Pyserial write all of the necessary outputs of the Train Controller to the Train Model
        #### "!Power, Commanded train temp (2 digit int), Doors and lights commands (3 bools), Emergency brake (bool), Service brake (bool), Fixed faults (bool)"
        pass

    ## Driver Mode Funtions
    # Input) string: "automatic" or "manual"
    def set_driver_mode(self, mode: str):
        if mode not in ["automatic", "manual"]:
            raise ValueError("Invalid mode. Mode must be 'automatic' or 'manual'.")
        self.driver_mode = mode
    
    # Output) string: "automatic" or "manual"
    def get_driver_mode(self):
        return self.driver_mode
    def toggle_driver_mode(self):
        self.driver_mode = "automatic" if self.driver_mode == "manual" else "manual"


    ## Setpoint and Commanded Speed Functions
    def set_setpoint_speed(self, speed: float):
        self.setpoint_speed = speed
    def get_setpoint_speed(self):
        return self.setpoint_speed
    def get_commanded_speed(self):
        return self.commanded_speed
    def update_commanded_speed(self, train_model):
        self.commanded_speed = train_model.get_commanded_speed()
    
    ## Power Functions (assumes commanded speed has already been updated)
    # Input) TrainModel object
    # Output) float: desired speed (Commanded speed if mode=automatic, Setpoint speed if mode=manual)
    def get_desired_speed(self):
        return self.setpoint_speed if self.driver_mode == "manual" else self.commanded_speed
    # Will give different power command based on driver mode
    # Output) float: power command
    def get_power_command(self):
        return self.engine.compute_power_command(self.get_desired_speed(), self.current_speed, self.engineer)

    # Simulate the train's response to desired speeds
    ## Purely for debugging purposes
    def simulate_speed(self, speed: float):
        power_command = self.engine.compute_power_command(speed, self.current_speed, self.engineer, self.maintenance_mode)
        self.current_speed = self.engine.calculate_current_speed(power_command, self.current_speed, self.brake)
        print(f"Power Command: {power_command}, Current Speed: {self.current_speed}")
    
    def update_fault_status(self, train_model):
        self.faults = train_model.get_fault_statuses()
        if(self.faults != [0, 0, 0]):
            self.maintenance()

    def maintenance(self):
        # If the train hasn't made a full stop yet, set the maintenance mode to True and keep emergency brake on
        # Once the train has made a full stop, set the maintenance mode to False and turn off the emergency brake
        done = (self.current_speed == 0)
        self.maintenance_mode = done
        self.brake.set_emergency_brake(done)
        

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
            if ki < 0:
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
       
        # Update Status???? Confirmation???? #
    
    ## Engine class calculates power command and can simulate train response
    class Engine:
        def __init__(self):
            self.T = 0.05  # Sample period
            self.P_MAX = 120  # Maximum power (kW)
            # brake_force = mass * brake_deceleration
            self.u_k = 0 # Power command
            self.e_k_integral = 0 # Error integral
            self.u_k_integral = 0 # Power integral
            

        # This is called by the Train System in order to speed up or slow down the simulation
        def update_T(self, T: float):
            self.T = T

        ## Factors/considerations
        # - Speed limit: Train Controller
        # - Power limit: Train Controller
        # - Brake status: Service and Emergency brake
        # - Brake Deceleration Rates: Service and Emergency


        # PID controller to compute the power command
        # Input) desired_speed: float, current_speed: float, engineer: Engineer object
        # Return) the power command to be applied to the train
        ### If fault exists, return 0
        def compute_power_command(self, desired_speed: float, current_speed: float, engineer, maintenance_mode: bool = False):
            if(maintenance_mode):
                # Reset values
                self.u_k = 0 # Power command
                self.e_k_integral = 0 # Error integral
                self.u_k_integral = 0 # Power integral
                return 0
            
            # Get kp and ki from engineer
            kp, ki = engineer.get_engineer()

            # Calculate the error
            e_k = desired_speed - current_speed
            # Power command = Kp * error + Ki * integral of error
            p_cmd = kp * e_k + ki * self.u_k

            # Check if the power command exceeds the maximum power
            if p_cmd < self.P_MAX:
                self.u_k = self.u_k_integral + (self.T / 2) * (e_k + self.e_k_integral)
            else:
                # If the power command exceeds the maximum power, use the previous power command
                self.u_k = self.u_k_integral

            # Update the error and power integral for the next iteration
            self.e_k_integral = e_k
            self.u_k_integral = self.u_k

            return p_cmd
        
        def calculate_current_speed(self, power_command, current_speed, brake):
            # If power command is greater than the maximum power, it's exceeded the physical limit so set it to the maximum power
            if power_command > self.P_MAX:
                power_command = self.P_MAX
            # If power command magnitude is negative, we need to slow down so turn on the service brake
            elif power_command < 0:
                brake.set_service_brake(True)

            '''
            # This will be used once integrated with Train Model
            if power_command < 0:
                power_command = 0
            '''
                
            
            current_speed += power_command * self.T
            
            print(f"Power Command: {round(power_command, 2)}, Current Speed: {round(current_speed, 2)}")

            return current_speed, brake
        
    ## Door class to hold door status
    # Door status = bool
    # False = closed, True = open
    class Doors:
        def __init__(self):
            self.left = False
            self.right = False

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
        
    ## Light class to hold light status
    # Light status = bool
    # False = off, True = on
    class Lights:
        def __init__(self):
            self.lights = False

        ## Mutator Function
        def set_lights(self, status: bool):
            self.lights = status
        def turn_on(self):
            self.lights = True
        def turn_off(self):
            self.lights = False

        ## Toggle Function
        def toggle_lights(self):
            self.lights = not self.lights

        ## Accessor Function
        def get_status(self):
            return self.lights
        def update_lights(self, train_model, block):
            underground_blocks = train_model.get_underground_status()
            self.lights = block in underground_blocks

    ## AC class to hold temperature status
    # Commanded temperature from driver (initialized to 69)
    # Current temperature from Train Model
    class AC:
        def __init__(self, train_model):
            # Commanded temperature from driver (initialized to 69)
            self.commanded_temp = 69
            # Current temperature inside the train
            self.current_temp = None
            # Initialize current temperature from Train Model
            self.update_current_temp(train_model)

        ## Mutator Function
        # Input) temp: int
        def set_commanded_temp(self, temp: int):
            self.commanded_temp = temp
        # Input) TrainModel object
        def update_current_temp(self, train_model):
            self.current_temp = train_model.get_train_temp()

        ## Accessor Function
        def get_commanded_temp(self):
            return self.commanded_temp
        def get_current_temp(self):
            return self.current_temp


# Does beacon need to be encrypted
# All information from MBO needs to be encrypted
class TrainModel:
    def __init__(self):
        self.current_speed = 0
        self.position = 0
        self.authority = 0
        self.commanded_speed = 0
        self.train_temp = 0
        self.station = 0
        self.block = 'A'
        self.underground_status = ['A', 'B', 'C']
        self.exit_door = [0, 0]
        self.faults = [0, 0, 0]
        self.speed_limit = 100

    # Float
    def get_current_speed(self):
        # Logic to get current speed of the train
        return self.current_speed

    # 1 floats
    # Distance from starting point (or relative point 0)
    # Distance from previous beacon
    # Still need to figure out how to do this
    def get_position(self):
        # Logic to get current position of the train (GPS)
        return self.position

    # Iterative (float representing meters)? Absolute (position representing when to stop by)?
    def get_authority(self):
        # Logic to get the authority from the train model
        return self.authority

    # Float
    def get_commanded_speed(self):
        # Logic to get commanded speed from the train model
        return self.commanded_speed

    # float
    def get_train_temp(self):
        # Logic to get the temperature inside the train
        return self.train_temp

    # String or station ID?
    # Need to decrypt the information and figure it out from that
    # Is the full name even needed
    def get_station_name(self):
        # Logic to get the name of the current station
        return self.station
    
    # Char
    # Used for underground logic
    def get_block(self):
        # Logic to get the block number
        return 'A'

    # List of chars (list of blocks)
    def get_underground_status(self):
        # Logic to get the underground status of the train
        return 0

    # String? Bool[2]? Int?
    # [left door, right door]
    def get_exit_door(self):
        # Logic to get the status of the exit door
        return 0

    # List of bools? Individual bools?
    # [engine, brake, signal]
    # No fault = [0, 0, 0]
    def get_fault_statuses(self):
        # Logic to get the fault status of the train
        return 0

    # Float
    def get_speed_limit(self):
        # Logic to get the speed limit of the train
        return 100


    ## Potentially needed functions ##

    # Get distance traveled (Could be calculated based on current speed * time step)
    def get_distance_traveled(self):
        # Logic to get the distance traveled by the train
        return 0

    # Other methods to get various inputs from the train model

    def transmit_to_train_controller(self):
        #### Pyserial write all of the necessary outputs of the Train Model to the Train Controller
        return 0



class TrainSystem:
    def __init__(self):
        self.train_model = TrainModel()
        self.controller = TrainController(self.train_model)


    def run(self):
        self.controller.simulate_speed(30)
        self.controller.simulate_speed(50)
        self.controller.simulate_speed(70)
        self.controller.simulate_speed(10)

if __name__ == "__main__":
    train_system = TrainSystem()
    train_system.run()
