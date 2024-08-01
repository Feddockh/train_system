import math

from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject
from cryptography.fernet import Fernet

from train_system.common.time_keeper import TimeKeeper
from train_system.common.authority import Authority

class TrainModel(QObject) :

    # establish pyqt signal connections to other modules
    satellite_received = pyqtSignal(int, str, float) # ID, authority, commanded speed
    satellite_sent = pyqtSignal(int, str, str, str) # ID, track_block, position, Velocity
    authority_received = pyqtSignal(str)
    position_updated = pyqtSignal(int, float)

    engine_fault_updated = pyqtSignal(bool)
    brake_fault_updated = pyqtSignal(bool)
    signal_fault_updated = pyqtSignal(bool)

    train_temp_updated = pyqtSignal(float)
    override_tc_update = pyqtSignal()
    emergency_mode = pyqtSignal()

################################
#### vvvv Constructors vvvv ####
################################

    # this function constructs and sets default values for a new train model instance
    # parameters : self
    def __init__(self, time_keeper : TimeKeeper, train_id : int, line : str) :

        # connect to TimeKeeper
        super().__init__()
        self.time_keeper = time_keeper
        self.time_keeper.tick.connect(self.handle_pickup_failure)
        self.time_keeper.tick.connect(self.physics_update)
        self.time_keeper.tick.connect(self.update_current_temp)

        # mbo satellite variables
        self.encrypted_speed : str = "S"
        self.encrypted_authority : str = "A"

        # physics variables
        self.current_speed : float = 0
        self.current_acceleration : float = 0
        self.power_command : float = 0
        self.service_brake : bool = False
        self.emergency_brake : bool = False
        self.passengers : int = 0
        self.current_grade : float = 0

        self.last_velocity : float = 0
        self.last_acceleration : float = 0
        self.last_second : int = 0

        # physics constants
        self.FRICTION_COEFF = 0.05
        self.EMPTY_TRAIN_MASS = 40.9 * 907.185 # tons to kilograms
        self.PASSENGER_MASS = 62 # mass for one passenger in kilograms
        self.CREW_COUNT = 2
        self.passengers += self.CREW_COUNT
        self.MAX_TRAIN_ACCEL = 0.75 # m/s/s
        self.MAX_TRAIN_VELOCITY = 70 / 3.6 # k/h to m/s
        self.TRAIN_LENGTH = 32.2 # m
        self.TRAIN_HEIGHT = 3.41 # m
        self.TRAIN_WIDTH = 2.65 # m
        self.SERVICE_BRAKE_ACCEL = -1.2 # m/s/s
        self.EMERGENCY_BRAKE_ACCEL = -2.73 # m/s/s
        self.G_ACCEL = -9.81 # m/s/s

        # fault variables
        self.faults : list[bool] = [False, False, False] # [engine, brake, signal]
        self.engine_fault : bool = False
        self.brake_fault : bool = False
        self.signal_fault : bool = False

        # train status variables
        self.line = line
#        self.authority = Authority(0, 0) # "authority , block destination number"
        self.authority : float = 0
        self.key : bytes = 0
        self.cipher_suite = 0 
        self.commanded_speed : float = 0
        self.position : float = 0 # distance from yard
        self.block_number : int = 0
        self.train_id = train_id # 0 - 19 green line, 20 - 39 red line
        self.left_doors : bool = False
        self.right_doors : bool = False
        self.interior_lights : bool = False
        self.exterior_lights : bool = False
        self.ac : bool = False
        self.heater : bool = False
        self.commanded_temp : float = 70
        self.train_temp : float = 70
        self.outdoor_temp : int = 70

################################
#### ^^^^ Constructors ^^^^ ####
################################

################################
#### vvvv   Setters    vvvv ####
################################

    # vvvv physics variables vvvv

    # this function will set the power_command variable value
    # parameters : float power_command
    def set_power_command(self, power_command : float) :
        self.power_command = power_command

    # this function will set the service_brake variable status
    # parameters : bool service_brake
    def set_service_brake(self, service_brake : bool) :
        if self.get_brake_fault() == False :
            self.service_brake = service_brake
            self.set_power_command(0)

    # this function will set the emergency_brake variable status
    # parameters : bool emergency_brake
    def set_emergency_brake(self, emergency_brake : bool) :
        self.emergency_brake = emergency_brake
        self.set_power_command(0)

    # this function will set the number of passengers on the train
    # parameters : int passengers
    def set_passengers(self, passengers : int) :
        self.passengers = passengers + self.CREW_COUNT

    # this function will set the value for the current_grade variable
    # parameters : float current_grade
    def set_current_grade(self, current_grade : float) :
        self.current_grade = current_grade

    # this function will set the value of the last_velocity variable
    # parameters : float last_velocity
    def set_last_velocity(self, last_velocity : float) :
        self.last_velocity = last_velocity

    # this function will set the value of the last_acceleration variable
    # parameters : float last_acceleration
    def set_last_acceleration(self, last_acceleration : float) :
        self.last_acceleration = last_acceleration

    # this function will set the value of the last_second variable
    # parameters : int last_second
    def set_last_second(self, last_second : int) :
        self.last_second = last_second

    # ^^^^ physics variables ^^^^

    # vvvv fault variables vvvv

    # this function will set the fault status for all faults ; [engine, brake, signal]
    # parameters : list[bool] faults
    def set_fault_statuses(self, faults : list[bool]) :
        self.set_engine_fault(faults[0])
        self.set_brake_fault(faults[1])
        self.set_signal_fault(faults[2])

    # this function will set the fault status for engine_fault (faults[0])
    # parameters : bool engine_fault
    def set_engine_fault(self, engine_fault : bool) :
        self.faults[0] = engine_fault
        self.engine_fault_updated.emit(engine_fault)

    # this function will set the fault status for brake_fault (faults[1])
    # parameters : bool brake_fault
    def set_brake_fault(self, brake_fault : bool) :
        self.faults[1] = brake_fault
        self.brake_fault_updated.emit(brake_fault)

    # this function will set the fault status for signal_fault (faults[2])
    # parameters : bool signal_fault
    def set_signal_fault(self, signal_fault : bool) :
        self.faults[2] = signal_fault
        self.signal_fault_updated.emit(signal_fault)

    # ^^^^ fault variables ^^^^

    # vvvv train status variables vvvv

    # this function will set the authority variable
    # parameters : Authority authority
#    def set_authority(self, authority : Authority) :
#        self.authority = authority
#        self.authority_received.emit(self.authority)   
    # parameters : float authority
    def set_authority(self, authority : float) :
        self.authority = authority

    # this function will set the commanded_speed variable
    # parameters : float commanded_speed
    def set_commanded_speed(self, commanded_speed : float) :
        self.commanded_speed = commanded_speed

    # this function will set the position variable ; distance from yard
    # parameters : float position
    def set_position(self, position : float) :
        self.position = position

    # this function will set the train_id variable ; 0 - 19 green, 20 - 39 red
    # parameters : int train_id
    def set_train_id(self, train_id : int) :
        self.train_id = train_id

    # this function will set the left doors status ; true = open
    # parameters : bool left_doors
    def set_left_doors(self, left_doors : bool) :
        self.left_doors = left_doors

    # this function will set the right doors status ; true = open
    # parameters : bool right_doors
    def set_right_doors(self, right_doors : bool) :
        self.right_doors = right_doors

    # this function will set the light variable status ; true = on
    # paramters : bool lights
    def set_lights(self, lights : bool) :
        self.set_interior_lights(lights)
        self.set_exterior_lights(lights)

    # this function will set the interior light variable status ; true = on
    # parameter : bool interior_lights
    def set_interior_lights(self, interior_lights : bool) :
        self.interior_lights = interior_lights

    # this function will set the exterior light variable status ; true = on
    # parameter : bool exterior_lights
    def set_exterior_lights(self, exterior_lights : bool) :
        self.exterior_lights = exterior_lights

    # this function will set the ac variable status ; true = on
    # parameters : bool ac
    def set_ac(self, ac : bool) :
        self.ac = ac

    # this function will set the heater variable status ; true = on
    # parameters : bool heater
    def set_heater(self, heater : bool) :
        self.heater = heater

    # this function will set the commanded_temp variable ; Fahrenheit
    # parameters : float commanded_temp
    def set_commanded_temp(self, commanded_temp : float) :
        self.commanded_temp = commanded_temp

    # ^^^^ train status variables ^^^^

################################
#### ^^^^   Setters    ^^^^ ####
################################

################################
#### vvvv   Getters    vvvv ####
################################

    # vvvv physics variables vvvv

    # this function will return the value of the power_command variable
    # return : float power_command
    def get_power_command(self) :
        return self.power_command

    # this function will return the value of the current_speed variable ; meters per second
    # return : float current_speed
    def get_current_speed(self) :
        return self.current_speed
    
    # this function will return the value of the current_acceleration variable
    # return : float current_acceleration
    def get_current_acceleration(self) :
        return self.current_acceleration

    # this function will return the service_brake variable status
    # return : bool service_brake
    def get_service_brake(self) :
        return self.service_brake

    # this function will return the emergency_brake variable status
    # return : bool emergency_brake
    def get_emergency_brake(self) :
        return self.emergency_brake

    # this function will return the number of passengers on the train
    # return : int passengers
    def get_passengers(self) :
        return self.passengers
    
    # this function will return the value for the current_grade variable
    # parameters : float current_grade
    def get_current_grade(self) :
        return self.current_grade

    # this function will return the value of the last_velocity variable
    # return : float last_velocity
    def get_last_velocity(self) :
        return self.last_velocity

    # this function will return the value of the last_acceleration variable
    # return : float last_acceleration
    def get_last_acceleration(self) :
        return self.last_acceleration

    # this function will return the value of the last_second variable
    # return : int last_second
    def get_last_second(self) :
       return self.last_second

    # ^^^^ physics variables ^^^^ 

    # vvvv fault variables vvvv

    # this function will return the fault status for all faults ; [engine, brake, signal]
    # return : list[bool] faults
    def get_fault_statuses(self) :
        return self.faults

    # this function will return the fault status for engine_fault (faults[0])
    # return : bool engine_fault
    def get_engine_fault(self) :
        return self.faults[0]

    # this function will return the fault status for brake_fault (faults[1])
    # return : bool brake_fault
    def get_brake_fault(self) :
        return self.faults[1]

    # this function will return the fault status for signal_fault (faults[2])
    # return : bool signal_fault
    def get_signal_fault(self) :
        return self.faults[2]

    # ^^^^ fault variables ^^^^

    # vvvv train status variables vvvv

    # this function will return the authority variable ; "authority : block destination number"
#    # return : Authority authority
    # return : float authority
    def get_authority(self) :
        return self.authority
    
    # this function will return the commanded_speed variable
    # reutrn : float commanded_speed
    def get_commanded_speed(self) :
        return self.commanded_speed

    # this function will return the position variable ; distance from yard
    # return : float position
    def get_position(self) :
        return self.position

    # this function will return the block number the train instance is currently in
    # return : int block_number
    def get_block_number(self) :
        return self.block_number

    # this function will return the train_id variable ; 0 - 19 green, 20 - 39 red
    # return : int train_id
    def get_train_id(self) :
        return self.train_id

    # this function will return the left doors status ; true = open
    # return : bool left_doors
    def get_left_doors(self) :
        return self.left_doors

    # this function will return the right doors status ; true = open
    # return : bool right_doors
    def get_right_doors(self) :
        return self.right_doors

    # this function will return the light variable status ; true = on
    # return : bool all lights on
    def get_lights(self) :
        if self.interior_lights == True and self.exterior_lights == True :
            return True
        else :
            return False
        
    # this function will return the interior_lights variable status ; true = on
    # return : bool interior_lights
    def get_interior_lights(self) :
        return self.interior_lights

    # this function will return the exterior_lights variable status ; true = on
    # return : bool exterior_lights
    def get_exterior_lights(self) :
        return self.exterior_lights
    
    # this function will return the ac variable status ; true = on
    # return : bool ac
    def get_ac(self) :
        return self.ac

    # this function will return the heater variable status ; true = on
    # return : bool heater
    def get_heater(self) :
        return self.heater

    # this function will return the current_temp variable ; Fahrenheit
    # return : float current_temp
    def get_current_temp(self) :
        return self.train_temp

    # this function will return the number of crew on board the train
    # return : int 2
    def get_crew(self) :
        return self.CREW_COUNT

    # this function will return a random advertisement for every 100 seconds
    # return : str advertisement
    def get_advertisement(self) :
        if round(self.time_keeper.current_second / 100) % 2 == 0 :
            return "Drink Coca-Cola!"
        else :
            return "Drink Pepsi!"

    # ^^^^ train status variables ^^^^

################################
#### ^^^^   Getters    ^^^^ ####
################################

################################
#### vvvv   Toggles    vvvv ####
################################

    # this function toggles the service brake boolean variable
    def toggle_service_brake(self) :
        if self.get_service_brake() == True :
            self.set_service_brake(False)
        else :
            self.set_service_brake(True)

    # this function toggles the emergency brake boolean variable
    def toggle_emergency_brake(self) :
        if self.get_emergency_brake() == True :
            self.set_emergency_brake(False)
        else :
            self.set_emergency_brake(True)

    # this function toggles the right side doors boolean variable
    def toggle_right_doors(self) :
        if self.get_right_doors() :
            self.set_right_doors(False)
        else :
            self.set_right_doors(True)

    # this function toggles the left side doors boolean variable
    def toggle_left_doors(self) :
        if self.get_left_doors() :
            self.set_left_doors(False)
        else :
            self.set_left_doors(True)

    # this function toggles the interior lights boolean variable
    def toggle_interior_lights(self) :
        if self.get_interior_lights() == True :
            self.set_interior_lights(False)
        else :
            self.set_interior_lights(True)

    # this function toggles the exterior lights boolean variable
    def toggle_exterior_lights(self) :
        if self.get_exterior_lights() == True :
            self.set_exterior_lights(False)
        else :
            self.set_exterior_lights(True)

    # this function toggles the ac boolean variable
    def toggle_ac(self) :
        if self.get_ac() == True :
            self.set_ac(False)
        else :
            self.set_ac(True)

    # this function toggles the heater boolean variable
    def toggle_heater(self) :
        if self.get_heater() == True :
            self.set_heater(False)
        else :
            self.set_heater(True)

    # this function toggles the engine failure boolean variable
    def toggle_engine_fault(self) :
        if self.get_engine_fault() == True :
            self.set_engine_fault(False)
        else :
            self.set_engine_fault(True)

    # this function toggles the brake failure boolean variable
    def toggle_brake_fault(self) :
        if self.get_brake_fault() == True :
            self.set_brake_fault(False)
        else :
            self.set_brake_fault(True)

    # this function toggles the signal failure boolean variable
    def toggle_signal_fault(self) :
        if self.get_signal_fault() == True :
            self.set_signal_fault(False)
        else :
            self.set_signal_fault(True)

################################
#### ^^^^   Toggles    ^^^^ ####
################################

################################
#### vvvv   Handlers   vvvv ####
################################

    # this function will handle a pyqt signal change to service_brake status
    # parameters : bool status
    @pyqtSlot(bool)
    def handle_service_brake_update(self, status: bool) -> None :
        self.set_service_brake(status)

    # this function will handle a pyqt signal change to emergency_brake status
    # parameters : bool status
    @pyqtSlot(bool)
    def handle_emergency_brake_update(self, status: bool) -> None :
        self.set_emergency_brake(status)

    # this function will stop all communication with the train model if signal pickup failure
    @pyqtSlot()
    def handle_pickup_failure(self):
        if self.faults[2] :
            self.override_tc_update.emit()

    # this function will handle a pyqt signal change when faults are fixed
    @pyqtSlot()
    def handle_faults_fixed(self) -> None :
        self.set_engine_fault(False)
        self.set_brake_fault(False)
        self.set_signal_fault(False)

    # this function will handle a pyqt signal indicating the end of emergency mode
    @pyqtSlot()
    def handle_emergency_stop(self):
        self.emergency_mode.emit()

    # this function will handle a pyqt signal change to left_door status
    # parameters : bool status
    @pyqtSlot(bool)
    def handle_left_door_update(self, status: bool) -> None :
        self.set_left_doors(status)

    # this function will handle a pyqt signal change to right_door status
    # parameters : bool status
    @pyqtSlot(bool)
    def handle_right_door_update(self, status: bool) -> None :
        self.set_right_door(status)

    # this function will handle a pyqt signal change to lights status
    # parameters : bool status
    @pyqtSlot(bool)
    def handle_lights_update(self, status: bool) -> None :
        self.set_lights(status)

    # this function will handle a pyqt signal change to commanded_temp
    # parameter : int temperature
    @pyqtSlot(int)
    def handle_commanded_temp_update(self, temp: int) :
        self.commanded_temp = temp

    # this function will handle the temperature of the train
    @pyqtSlot(int)
    def update_current_temp(self) :
        if self.ac == True :
            self.train_temp -= 0.25
        elif self.heater == True :
            self.train_temp += 0.25
        else :
            if self.outdoor_temp < self.train_temp :
                self.train_temp -= 0.01
            else :
                self.train_temp += 0.01
        self.train_temp_updated.emit(self.train_temp)

################################
#### ^^^^   Handlers   ^^^^ ####
################################

################################
#### vvvv    Others    vvvv ####
################################

    # this function will recieve the encoded information from the mbo, decrypt it, and update variables
    # parameters : str mbo_data
    def receive_mbo(self, mbo_data : str) :
        print("receive_mbo to be implemented")
        ## code to decrypt
        ## code to update variables

    # this function will decrypt the commanded speed received from the mbo
    # parameter: str encrypted_speed
    def decrypt_commanded_speed(self, encrypted_speed : str) :
        decrypted_speed = self.decrypt(encrypted_speed)
        self.set_commanded_speed(float(decrypted_speed))

    # this function will decrupt the authority received from the mbo
    # parameter: str encrypted_authority
    def decrypt_authority(self, encrypted_authority : str) :
        decrypted_authority = self.decrypt(encrypted_authority)
        new_authority = Authority()
        new_authority.authority = decrypted_authority 
        self.set_authority(new_authority)

    # this functio will set the cipher key value for the encryption
    # parameter: key value
    def set_cipher_suite(self, key_value : bytes) :
        self.key = key_value 
        self.cipher_suite = Fernet(self.key)

    # this function will encrypt message text for transmission to mbo
    # parameters : str plain_text
    # return : str cipher_text 
    def encrypt(self, plain_text : str) :    # need to pass in or create slot to get cipher_suite with key from main
        cipher_text = self.cipher_suite.encrypt(plain_text.encode())
        return (cipher_text)

    # this fucntion will decrypt message text for transmission from mbo
    # parameters : str cipher_text
    # return : str plain_text
    def decrypt(self, cipher_text : str) :
        plain_text = self.cipher_suite.decrypt(cipher_text.encode())
        return (plain_text)

    # this function will send all necessary data to mbo
    def send_all_outputs(self) :
        self.position_updated.emit(self.train_id, self.position)
        self.satellite_sent.emit(self.train_id, self.encrypt(self.block_number), 
                                 self.encrypt(self.position), self.encrypt(self.current_speed))

    # this function will put passengers on the train
    # parameters : int passengers boarding
    # return : int passengers on board
    def add_passengers(self, passengers : int) :
        self.passengers += passengers
        return self.passengers

    # this function will remove passengers from the train
    # parameters : int passengers leaving
    # return : int passengers on board
    def remove_passengers(self, passengers : int) :
        self.passengers -= passengers
        if self.passengers < 0 :
            self.passengers = 0
        return self.passengers

    # this function update the physics status and properties for the train based on commanded_power
    def physics_update(self) :

        # let one tick run if current = last
        if self.get_last_second() == self.time_keeper.current_second :
            self.set_last_second(self.time_keeper.current_second)
        else :

            # calculate engine forces
            if self.power_command <= 0.0001 :
                engine_force = 0
            elif self.power_command > 0.0001 and self.current_speed < 0.0001 :
                engine_force = self.power_command / 0.1
            else :
                engine_force = (self.power_command / self.get_last_velocity())

            # engine force = 0 if either brake engaged
            if self.service_brake or self.emergency_brake :
                engine_force = 0

            # determine current mass
            current_mass = self.EMPTY_TRAIN_MASS + (self.passengers * self.PASSENGER_MASS)

            # calculate force due to gravity
            # m*g*sin(angle)
            if self.current_grade > 0 : # if up hill
                grav_force = (-1 * current_mass * self.G_ACCEL * math.sin(self.current_grade))
            elif self.current_grade < 0 : # if down hill
                grav_force = (current_mass * self.G_ACCEL * math.sin(-1 * self.current_grade))
            else : # if flat
                grav_force = 0

            # calculate force due to friction (only if power is 0 & brake if off)
            # Ff = Fn*u
            # Fn = m*g*cos(angle)
            if self.power_command == 0 and (not self.last_velocity == 0) and self.service_brake == False and self.emergency_brake == False :
                normal_force = (-1 * current_mass * self.G_ACCEL * math.cos(self.current_grade))
                friction_force = (-1 * normal_force * self.FRICTION_COEFF)
            else :
                friction_force = 0

            # sum forces
            net_force = engine_force + grav_force + friction_force

            # calcualte forward acceleration
            current_acceleration = net_force / current_mass

            # limit to max forward acceleration
            if current_acceleration > self.MAX_TRAIN_ACCEL :
                current_acceleration = self.MAX_TRAIN_ACCEL

            # add brake acceleration if brake applied
            if self.emergency_brake :
                current_acceleration += self.EMERGENCY_BRAKE_ACCEL
            elif self.service_brake :
                current_acceleration += self.SERVICE_BRAKE_ACCEL

            # calculate velocity
            delta_t = self.time_keeper.current_second - self.get_last_second()
            total_acceleration = current_acceleration + self.get_last_acceleration()
            total_velocity = self.get_last_velocity() + (delta_t / 2) * total_acceleration

            # limit velocity to max characteristics
            if total_velocity > self.MAX_TRAIN_VELOCITY :
                total_velocity = self.MAX_TRAIN_VELOCITY
            elif total_velocity < 0 :
                total_velocity = 0

            # reset acceleration if stopped
            if self.last_velocity >= 0 and total_velocity == 0 :
                total_acceleration = 0

            # set last tick varaibles
            self.current_speed = total_velocity
            self.current_acceleration = total_acceleration
            self.set_last_acceleration(total_acceleration)
            self.set_last_velocity(total_velocity)
            self.set_last_second(self.time_keeper.current_second)

    # this function will print the current status of all the variables within this instance
    def print_all_variables(self) :

        print("\nPhysics Variables:\n")

        print("Current Speed: ", end = "")
        print(self.current_speed)
        print("Power Command: ", end = "")
        print(self.current_speed)
        print("Service Brake: ", end = "")
        print(self.service_brake)
        print("Emergency Brake: ", end = "")
        print(self.emergency_brake)
        print("Passengers: ", end = "")
        print(self.passengers)
        print("Last Velocity: ", end = "")
        print(self.last_velocity)
        print("Last Acceleration: ", end = "")
        print(self.last_acceleration)
        print("Last Second: ", end = "")
        print(self.last_second)

        print("\nFault Variables:\n")
        
        print("All Faults: ", end  ="")
        print(self.faults)
        print("Engine Fault: ", end = "")
        print(self.engine_fault)
        print("Brake Fault: ", end = "")
        print(self.brake_fault)
        print("Signal Fault: ", end = "")
        print(self.signal_fault)

        print("\nTrain Status Variables:\n")

        print("Line : ", end = "")
        print(self.line)
        print("Authority: ", end = "")
        print(self.authority)
        print("Commanded Speed: ", end = "")
        print(self.commanded_speed)
        print("Position: ", end = "")
        print(self.position)
        print("Train ID: ", end = "")
        print(self.train_id)
        print("Left Doors: ", end = "")
        print(self.left_doors)
        print("Right Doors: ", end = "")
        print(self.right_doors)
        print("Interior Lights: ", end = "")
        print(self.interior_lights)
        print("Exterior Lights: ", end = "")
        print(self.right_doors)
        print("Interior Lights: ", end = "")
        print(self.interior_lights)
        print("Exterior Lights: ", end = "")
        print(self.exterior_lights)
        print("AC: ", end = "")
        print(self.ac)
        print("Heater: ", end = "")
        print(self.heater)
        print("Commanded Temperature: ", end = "")
        print(self.commanded_temp)
        print("Train Temperature: ", end = "")
        print(self.train_temp)

    # this fucntion will print the returns from all functions with returns given the variables of the current instance
    def print_all_functions(self) :

        print("\nGetters:\n")

        print(".get_current_speed() : ", end = "")
        print(self.get_current_speed())
        print(".get_service_brake() : ", end = "")
        print(self.get_service_brake())
        print(".get_emergency_brake() : ", end = "")
        print(self.get_emergency_brake())
        print(".get_passengers() : ", end = "")
        print(self.get_passengers())

        print("\n.get_fault_statuses() : ", end = "")
        print(self.get_fault_statuses())
        print(".get_engine_fault() : ", end = "")
        print(self.get_engine_fault())
        print(".get_brake_fault() : ", end = "")
        print(self.get_brake_fault())
        print(".get_signal_fault() : ", end = "")
        print(self.get_signal_fault())

        print("\n.get_authority() : ", end = "")
        print(self.get_authority())
        print(".get_position() : ", end = "")
        print(self.get_position())
        print(".get_train_id() : ", end = "")
        print(self.get_train_id())
        print(".get_left_doors() : ", end = "")
        print(self.get_left_doors())
        print(".get_right_doors() : ", end = "")
        print(self.get_right_doors())
        print(".get_lights() : ", end = "")
        print(self.get_lights())
        print(".get_exterior_light() : ", end = "")
        print(self.get_exterior_light())
        print(".get_interior_lights() : ", end = "")
        print(self.get_interior_lights())
        print(".get_ac() : ", end = "")
        print(self.get_ac())
        print(".get_heater() : ", end = "")
        print(self.get_heater())
        print(".get_current_temp() : ", end = "")
        print(self.get_current_temp())

################################
#### ^^^^    Others    ^^^^ ####
################################

#timer = TimeKeeper()
#train = TrainModel(1, timer)
#train.print_all_variables()
#train.print_all_functions()