import math

from PyQt6.QtWidgets import QWidget
from train_system.common.time_keeper import TimeKeeper


#from train_system.train_controller.train_controller import TrainController
#from train_system.track_model.track_model import TrackModel 

class TrainModel(QWidget) :

    # this function constructs and set default values for a new train model instance
    #   parameters: self, train id number, and global time_keeper for time connection
    def __init__(self, train_id, time_keeper: TimeKeeper) :

        # connect to TimeKeeper
        super().__init__()
        self.time_keeper = time_keeper
        self.time_keeper.start_timer()
        self.time_keeper.tick.connect(self.physics_update)
        self.time_keeper.tick.connect(self.temperature_control)

        # testing
        self.testing = False

        # physics variables  
        self.current_speed = 0 # m/s
        self.commanded_power = 0 # vital
        self.service_brake = False # vital
        self.emergency_brake = False # vital
        self.passengers = 0
    
        self.last_velocity = 0
        self.last_acceleration = 0
        self.last_second = time_keeper.current_second - 1

        # physics constants
        self.FRICTION_COEFF = 0.1 # typically 0.35 to 0.5 for steel
        self.EMPTY_TRAIN_MASS = 40.9 * 907.185 # tons to kilograms
        self.PASSENGER_MASS = 62 # mass for one passenger in kilograms
        self.CREW_COUNT = 2
        self.passengers += self.CREW_COUNT

        self.MAX_TRAIN_ACCEL = 0.75 # m/s/s
        self.MAX_TRAIN_VELOCITY = 70 / 3.6 # k/h to m/s
        self.SERVICE_BRAKE_ACCEL = -1.2 # m/s/s
        self.EMERGENCY_BRAKE_ACCEL = -2.73 # m/s/s
        self.G_ACCEL = -9.81 # m/s/s

        # failures [engine, brake, signal]
        self.failures = [False, False, False]

        # train status variables
        self.train_id = train_id
        self.right_side_doors = False
        self.left_side_doors = False
        self.interior_lights = False
        self.exterior_lights = False
        self.ac = False
        self.heater = False
        self.train_temp = 72

        # intermediate variables
        self.satellite_data = ""
        self.mbo_status = False # mbo infomation trumps all
        self.commanded_speed = 0
        self.authority = 0
        self.track_polarity = False
        # beacon intermediate variables
        self.beacon_data = ""
        self.station_name = ""
        self.block = ""
        self.under_ground = ""
        self.speed_limit = ""

###########################
#### vvvv Setters vvvv ####
###########################
        
    # this function sets the commanded speed
    def set_commanded_speed(self, commanded_speed) :
        self.commanded_speed = commanded_speed

    # this function sets the authority
    def set_authority(self, authority) :
        self.authority = authority

    # this function sets the engine power as commanded by the train controller, unless
    #   there is an engine failure. also limits to max engine characteristics
    #   parameters: self, commanded power
    def set_power(self, commanded_power) :
        
        # check if failure or max engine characteristics
        if self.failures [0] or commanded_power < 0 :
            self.commanded_power = 0
        elif commanded_power > 120 :
            self.commanded_power = 120
        else :
            self.commanded_power = commanded_power

        self.physics_update()

    # this function sets the train id number variable
    def set_train_id(self, train_id) :
        self.train_id = train_id

    # this function sets the number of train passengers
    def set_passengers(self, passengers) :
        self.passengers = passengers + self.CREW_COUNT

###########################
#### ^^^^ Setters ^^^^ ####
###########################

###########################
#### vvvv Toggles vvvv ####
###########################

    # this function toggles the testing boolean variable
    def toggle_testing(self) :
        if self.testing :
            self.testing = False
        else :
            self.testing = True

    # this function toggles the service brake boolean variable
    def toggle_service_brake(self) :
        if self.service_brake :
            self.service_brake = False
        else :
            self.service_brake = True
        self.set_power(0)

    # this function toggles the emergency brake boolean variable
    def toggle_emergency_brake(self) :
        if self.emergency_brake :
            self.emergency_brake = False
        else :
            self.emergency_brake = True
        self.set_power(0)
        print("emergency brake toggled:")
        print(self.emergency_brake)

    # this function toggles the right side doors boolean variable
    def toggle_right_side_doors(self) :
        if self.right_side_doors :
            self.right_side_doors = False
        else :
            self.right_side_doors = True
        print("right side doors toggled:")
        print(self.right_side_doors)

    # this function toggles the left side doors boolean variable
    def toggle_left_side_doors(self) :
        if self.left_side_doors :
            self.left_side_doors = False
        else :
            self.left_side_doors = True
        print("left side doors toggled:")
        print(self.left_side_doors)

    # this function toggles the interior lights boolean variable
    def toggle_interior_lights(self) :
        if self.interior_lights :
            self.interior_lights = False
        else :
            self.interior_lights = True
        print("interior lights toggled:")
        print(self.interior_lights)

    # this function toggles the exterior lights boolean variable
    def toggle_exterior_lights(self) :
        if self.exterior_lights :
            self.exterior_lights = False
        else :
            self.exterior_lights = True
        print("exterior lights toggled:")
        print(self.exterior_lights)

    # this function toggles the ac boolean variable
    def toggle_ac(self) :
        if self.ac :
            self.ac = False
        else :
            self.ac = True
        print("ac toggled:")
        print(self.ac)

    # this function toggles the heater boolean variable
    def toggle_heater(self) :
        if self.heater :
            self.heater = False
        else :
            self.heater = True
        print("heater toggled:")
        print(self.heater)

    # this function toggles the engine failure boolean variable
    def toggle_engine_failure(self) :
        if self.failures[0] :
            self.failures[0] = False
        else :
            self.failures[0] = True
        print("engine failure toggled:")
        print(self.failures[0])

    # this function toggles the brake failure boolean variable
    def toggle_brake_failure(self) :
        if self.failures[1] :
            self.failures[1] = False
        else :
            self.failures[1] = True
        print("brake failure toggled:")
        print(self.failures[1])

    # this function toggles the signal failure boolean variable
    def toggle_signal_failure(self) :
        if self.failures[2] :
            self.failures[2] = False
        else :
            self.failures[2] = True
        print("signal failure toggled:")
        print(self.failures[2])

###########################
#### ^^^^ Toggles ^^^^ ####
###########################

###########################
#### vvvv Getters vvvv ####
###########################

    # this function returns the current speed of the train
    def get_current_speed(self) :
        return self.current_speed
    
    # this function returns the curreny authority of the train
    def get_authority(self) :
        return self.authority
    
    #this function returns the commanded spee of the train
    def get_commanded_speed(self) :
        return self.commanded_speed
    
    # this function returns the status of the service brake
    def get_service_brake(self) :
        return self.service_brake
    
    # this function returns the status of the emergency brake
    def get_emergency_brake(self) :
        return self.emergency_brake
    
    # this function returns the number of on board passengers
    def get_passengers(self) :
        return self.passengers
        
    # this function returns all failures status
    def get_failures(self) :
        return self.failures
    
    # this function returns engine failure status
    def get_engine_failure(self) :
        return self.failures[0]
    
    # this function returns brake failure status
    def get_brake_failure(self) :
        return self.failures[1]

    # this function returns signal failure status
    def get_signal_failure(self) :
        return self.failures[2]

    # this function returns the trian id number
    def get_train_id(self) :
        return self.train_id
    
    # this function returns the right side doors status
    def get_right_side_doors(self) :
        return self.right_side_doors

    # this function returns the left side doors status
    def get_left_side_doors(self) :
        return self.left_side_doors
    
    # this function returns the interior lights status
    def get_interior_lights(self) :
        return self.interior_lights
    
    # this function returns the exterior lights status
    def get_exterior_lights(self) :
        return self.exterior_lights

    # this function returns the ac status
    def get_ac(self) :
        return self.ac
    
    # this function returns the heater status
    def get_heater(self) :
        return self.heater
    
    # this function returns the temperature of the train
    def get_train_temp(self) :
        return self.train_temp

###########################
#### ^^^^ Getters ^^^^ ####
###########################

###########################
#### vvvv Others  vvvv ####
###########################

    # this function updates the trian temperature each time step
    #   if the ac or heater or on, train temp decreased or increases by 0.1 respectively
    #   if the track temperature is lower or higher than train temp, train temp decreases
    #       or increase by 0.0001 resepctively
    #   this function updates every time step
    def temperature_control(self) :
        if self.ac :
            self.train_temp -= 0.1
        if self.heater :
            self.train_temp += 0.1
        #if TrackModel.get_temperature() < self.train_temp :
        #    self.train_temp -= 0.0001
        #if TrackModel.get_temperature() > self.train_temp :
        #    self.train_temp += 0.0001

    # this function updates all physics values each time step
    #   parameters: self
    def physics_update(self) :
        # calculate engine forces
        if self.commanded_power > 0 :
            if self.current_speed < 0.0001 :
                engine_force = self.commanded_power / 0.1
            else :
                engine_force = (self.commanded_power / self.last_velocity)
        else :
            engine_force = 0

        # engine force = 0 if either brake engaged
        if self.service_brake or self.emergency_brake :
            engine_force = 0

        # determine current mass
        current_mass = self.EMPTY_TRAIN_MASS + (self.passengers * self.PASSENGER_MASS)

        # calculate force due to gravity
        # m*g*sin(angle)
        #grade = TrackModel.get_grade(TrainController.get_position())
        #if grade > 0 : # if up hill
        #    grav_force = (-1 * current_mass * self.G_ACCEL * math.sin(grade))
        #elif grade < 0 : # if down hill
        #    grav_force = (current_mass * self.G_ACCEL * math.sin(-1 * grade))
        #else : # if flat
        #    grav_force = 0
        grav_force = 0 # remove when grade implemented
        grade = 0 # remove when grade implemented

        # calculate force due to friction (only if power is 0)
        # Ff = Fn*u
        # Fn = m*g*cos(angle)
        if self.commanded_power == 0 :
            normal_force = (-1 * current_mass * self.G_ACCEL * math.cos(grade))
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

        # make sure no roll back
        if self.last_velocity <= 0 and current_acceleration < 0 :
            current_acceleration = 0

        # calculate velocity
        delta_t = self.time_keeper.current_second - self.last_second
        total_acceleration = current_acceleration + self.last_acceleration
        total_velocity = self.last_velocity + (delta_t / 2 ) * total_acceleration
        
        # make sure no roll back
        if total_velocity < 0 :
            total_velocity = 0

        # limit velocity to max characteristics
        if total_velocity < 0 :
            total_velocity = 0
        elif total_velocity > self.MAX_TRAIN_VELOCITY :
            total_velocity = self.MAX_TRAIN_VELOCITY

        # set last tick varaibles
        if self.last_acceleration < 0 and total_velocity == 0 :
            self.last_acceleration = 0
        else :
            self.last_acceleration = total_acceleration
        self.last_velocity = total_velocity
        self.last_second = self.time_keeper.current_second
        self.current_speed = self.last_velocity

###########################
#### ^^^^ Others  ^^^^ ####
###########################