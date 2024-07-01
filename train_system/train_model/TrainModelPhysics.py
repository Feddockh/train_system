import sys
import math
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer

class TrainModel() :	

	def __init__(self) :
		self.current_speed = 0
		self.position = 0
		self.authority = 0
		self.commanded_speed = 0
		self.train_temp = 0
		self.station = 0
		self.block = 'A'
		self.underground_blocks = ['A', 'B', 'C']
		self.exit_door = [False, False]
		self.failures = [False, False, False] # [engine, brake, signal]
		self.speed_limit = 100
		self.service_brake = False
		self.emergency_brake = False
		
	
        
        # constants
		self.TIME_STEP = 1
		self.TIME_DELTA = 0.0001
		self.FRICTION_COEF = 0 # typically 0.35 to 0.5 for railways
		self.EMPTY_TRAIN_WEIGHT = 40.9 * 907.185 # tons convert to kilograms
		self.PASSENGER_MASS = 62 # mass in kilograms for one passenger
		self.MAX_TRAIN_ACCEL = 0.75 # m/s/s
		self.SERVICE_BRAKE_ACCEL = -1.2 # m/s/s
		self.EMERGENCY_BRAKE_ACCEL = -2.73 # m/s/s
		self.G_ACCEL = -9.81 # m/s/s
		
		# physics variables
		self.current_power = 0
		self.last_velocity = 0
		self.last_acceleration = 0
		self.last_position = 0
		self.engine_force = 0
		self.passengers = 0
        
		#self.last_time = time.time()
		self.last_time = 0

        # non-physics variables
        
	
	# this function sets the enginer power as commanded by the train
	#	train controller, unless there is an engine failure.
	#	commanded_power given as a float
	def giveCommandedPower(self, commanded_power) :
		
		self.commanded_power = commanded_power #* 1000
		
		# set engine power
		if self.failures[1] : # if engine failure
			self.current_power = 0
		else :
			self.current_power = self.commanded_power

		# calculate engine forces with new power input

		if self.last_velocity != 0 :
			self.engine_force = (self.current_power / 
								 self.last_velocity)
		
		# determine current mass
		self.current_mass = (self.EMPTY_TRAIN_WEIGHT + 
							 (self.passengers * self.PASSENGER_MASS))
		
		# calculate force due to gravity & normal force
		# m*g*sin(angle)
		self.current_grade = TrainModel.getGrade()
		if self.current_grade > 0 : #if up hill
			self.grav_force = (-1 * self.current_mass * self.G_ACCEL *
							   math.sin(self.current_grade))
		elif self.current_grade < 0 : # if down hill
			self.grav_force = (self.current_mass * self.G_ACCEL *
							   math.sin(-1 * self.current_grade))
		else : # if flat
			self.grav_force = 0
		
		# calcualate force due to friction
		# Ff = Fn*u
		# Fn = m*g*cos(angle)
		self.normal_force = (-1 * self.current_mass * self.G_ACCEL *
							 math.cos(self.current_grade))
		self.friction_force = (-1 * self.normal_force * 
							   self.FRICTION_COEF)

		# sum forces into net force
		self.net_force = (self.engine_force + self.grav_force + 
						  self.friction_force)
		
		# if friction force > net force -> no friction force
		if self.engine_force < -1 * self.friction_force :
			print("Frictuion")
			print(self.friction_force)
			print("engine")
			print(self.engine_force)
			self.net_force -= self.friction_force

		# limit the force of the train to max characteristics
		# if above max enginer force or no previous velocity set to max
		if (self.net_force > self.current_mass * 
			self.MAX_TRAIN_ACCEL or self.last_velocity == 0) :
			self.net_force = self.current_mass * self.MAX_TRAIN_ACCEL
		# if emergency brake or no movement
		elif ((self.current_power == 0 and self.last_velocity == 0) or
			  self.emergency_brake) :
			self.current_force = 0
			 
		
		# calculate acceleration
		self.current_acceleration = self.net_force / self.current_mass
		
		# limit acceleration of train to max characteristics
		# if brake failure gravity and friction only
		if self.failures[1] or self.current_power == 0 :
			self.current_acceleration = (self.grav_force + 
										 self.friction_force)
		#if brake applied
		elif self.service_brake and not self.emergency_brake :
			self.current_acceleration += self.SERVICE_BRAKE_ACCEL
		elif self.emergency_brake :
			self.current_acceleration += self.EMERGENCY_BRAKE_ACCEL
		# standard acceleration limit
		else : # current_power != 0 and no brake or failure
			if self.current_acceleration > self.MAX_TRAIN_ACCEL :
				self.current_acceleration = self.MAX_TRAIN_ACCEL


		# get current time
		#self.new_time = time.time()
		#self.time_delta = (self.new_time - self.last_time) * self.TIME_STEP
		#self.last_time = self.new_time
		self.new_time = self.last_time + self.TIME_DELTA


		# calculate velocity
		self.total_acceleration = (self.last_acceleration + 
								   self.current_acceleration) #/ self.TIME_STEP
		self.current_velocity = (self.last_velocity + 
								 ((self.TIME_DELTA / 2) * 
								  self.total_acceleration))
						   
		# limit velocity of train to max characteristics
		if self.current_velocity < 0 :
			self.current_velocity = 0
		if (self.last_velocity <= 0 and 
		    (self.service_brake or self.emergency_brake)) :
			self.current_velocity = 0
			
		# determine new position
		self.current_position = (self.last_position + 
								 ((self.TIME_DELTA / 2) * 
								  self.current_velocity))
						   
		# reset variagles back for next loop
		self.last_position = self.current_position
		self.last_velocity = self.current_velocity
		self.last_acceleration = self.total_acceleration
							
		#return velocity
		return self.current_velocity
	
	# this function returns the grade of the block the train is 
	#	currently in units of radians
	def getGrade() :
		grade_in_radians = 0 
		return grade_in_radians

	def setServiceBrake(self, engage) :
		self.service_brake = engage

	def setEmergencyBrake(self, engage) :
		self.emergency_brake = engage


#class DisplayCurrentVelocity(QWidget) :
#	def __init__(self,train):
#		super().__init__()
#
#		self.velocity = 0
#		self.train = train
#		self.current_time = 0
#		self.service_brake = False
#		self.emergency_brake = False
#		self.setFixedSize(500, 500)
#
#		self.createUI()
#
#	def createUI(self) :
#		self.setWindowTitle("Velocity over Time")
#
#		self.layout = QVBoxLayout()
#		
#		#display velocity
#		self.velocity_label = QLabel(f'Current Velocity: {self.velocity} m/s', self)
#		self.velocity_label.setStyleSheet("font-size: 24px;")
#		self.layout.addWidget(self.velocity_label)	
#
#		#display brake control
#		self.brake_button = QPushButton('Service Brake', self)
#		self.brake_button.setStyleSheet("font-size: 24px;")
#		self.layout.addWidget(self.brake_button)
#
#		#connect button to variable
#		self.brake_button.pressed.connect(self.serviceBrakePressed)
#		self.brake_button.released.connect(self.serviceBrakeReleased)
#
#
#		#display emergency brake control
#		self.emergency_brake_button = QPushButton('Emergency Brake', self)
#		self.emergency_brake_button.setStyleSheet("font-size: 24px;")
#		self.layout.addWidget(self.emergency_brake_button)
#		
#		#connect to emergency brake variable
#		self.emergency_brake_button.clicked.connect(self.emergencyToggle)
#		train.setEmergencyBrake(self.emergency_brake)
#
#	def serviceBrakePressed(self) :
#		self.service_brake = True
#		train.setServiceBrake(self.service_brake)
#
#	def serviceBrakeReleased(self) :
#		self.service_brake = False
#		train.setServiceBrake(self.service_brake)
#
#	def emergencyToggle(self) :
#		emergency_brake = not emergency_brake
#		train.setEmergencyBrake(emergency_brake)
#
#	def update_velocity(self,velocity) :
#		self.velocity = velocity



# Create an instance of TrainModel
#app = QApplication(sys.argv)
train = TrainModel()
#output = DisplayCurrentVelocity(train)
#output.show()



print("\nInput Commanded Power (0 - 120 kW): ",end="")
commanded_power = (int)(input())
print("Goal Velocity (0 to 40 miles/hour): ",end="")
end_velocity = (int)(input())
velocity = train.giveCommandedPower(commanded_power)
while velocity < end_velocity :
	time.sleep(0.001)
	#velocity = train.giveCommandedPower(commanded_power) * 3.6 #kph
	velocity = train.giveCommandedPower(commanded_power) * 2.23694 #mph
	print(f'\rCurrent Velocity: {velocity:.5f} miles/hour',end='',flush=True)
print(f'\rCurrent Velocity: {velocity:.5f} miles/hour - ',
	  'Speed Met, power set to 0',end='',flush=True)

time.sleep(2)
print(f'\rCurrent Velocity: {velocity:.5f} miles/hour - ',
	  'Service Brake Engaged.      ',end='',flush=True)

while velocity > 0 :
	train.setServiceBrake(True)
	time.sleep(0.001)
	#velocity = train.giveCommandedPower(commanded_power) * 3.6 #kph
	velocity = train.giveCommandedPower(commanded_power) * 2.23694 #mph
	print(f'\rCurrent Velocity: {velocity:.5f} miles/hour - ',
		   'Service Brake Engaged.      ',end='',flush=True)

print("\n")
