import sys
from train_system.train_controller.train_controller import TrainController, TrainModel, TrainSystem
from train_system.train_controller.tc_ui import *
from train_system.common.time_keeper import TimeKeeper
from PyQt6.QtWidgets import QApplication

HOST= '192.168.0.114'
PORT = 22
USERNAME = 'danim'
PASSWORD = 'danim'

app = QApplication(sys.argv)
   
# Create the time keeper object
time_keeper = TimeKeeper()
time_keeper.start_timer()   

# Hardware
# ts = TrainSystem(HOST, PORT, USERNAME, PASSWORD)
# Software
ts = TrainSystem()

tm = ts.train_model
        
tc = ts.controller

driver = DriverWindow(time_keeper)
test = TestBenchWindow()
engineer = EngineerWindow()

print("Test: " + str(test.ki_val))
print("Engineer UI: " + str(engineer.data[0][2]))
print("TC: " + str(tc.engineer.get_ki()))

# tc.train_model.authority_received.connect(tc.handle_tick) #### USE INSTEAD THIS INSTEAD AFTER INTEGRATION
time_keeper.tick.connect(tc.handle_tick)

#TRAIN CONTROLLER TO EXTERNAL


#TEST BENCH TO TRAIN CONTROLLER
test.setpoint_updated.connect(tc.handle_setpoint_edit_changed) 
test.service_brake_updated.connect(tc.handle_service_brake_toggled) ###checked
test.emergency_brake_updated.connect(tc.handle_emergency_brake_toggled) ###checked
#test.comm_temp_updated.connect(tc.handle_comm_temp_changed) 
test.engine_fault_updated.connect(tc.handle_engine_fault_changed)###checked
test.brake_fault_updated.connect(tc.handle_brake_fault_changed)###checked
test.signal_fault_updated.connect(tc.handle_signal_fault_changed)###checked
test.curr_speed_updated.connect(tc.handle_curr_speed_changed)###checked
test.comm_speed_updated.connect(tc.handle_comm_speed_changed)###checked
test.authority_updated.connect(tc.handle_authority_changed)###checked
test.light_status_updated.connect(tc.handle_light_status_changed)###checked
test.right_door_updated.connect(tc.handle_right_door_changed)###checked
test.left_door_updated.connect(tc.handle_left_door_changed)###checked
#test.kp_updated.connect(tc.handle_kp_changed) ###checked but needs to update table
#test.ki_updated.connect(tc.handle_ki_changed) ###checked but needs to update table
test.position_updated.connect(tc.handle_position_changed) ###checked
test.destination_updated.connect(tc.handle_destination_changed) ###checked

#DRIVER TO TRAIN CONTROLLER
driver.mode_button.toggled.connect(tc.handle_toggle_driver_mode) ###checked
driver.em_brake_button.toggled.connect(tc.handle_emergency_brake_toggled) ###checked
driver.service_brake_button.toggled.connect(tc.handle_service_brake_toggled) ###checked
driver.speed_input.textChanged.connect(tc.handle_setpoint_edit_changed) ###checked but conversions need fixed
driver.comm_temp_input.textChanged.connect(tc.handle_commanded_temp_changed) ###checked
driver.setpoint_updated.connect(tc.handle_setpoint_edit_changed)

#TRAIN CONTROLLER TO DRIVER
tc.setpoint_speed_updated.connect(driver.handle_setpoint_speed_update) ###checked
tc.power_updated.connect(driver.handle_power_update)
tc.lights.lights_updated.connect(driver.handle_light_status_update) ###checked but does not change ui
tc.doors.left_door_updated.connect(driver.handle_left_door_update)
tc.doors.right_door_updated.connect(driver.handle_right_door_update)
tc.ac.train_temp_updated.connect(driver.handle_train_temp_update)
tc.brake.user_service_brake_updated.connect(driver.handle_user_service_brake_update)
tc.brake.user_emergency_brake_updated.connect(driver.handle_user_emerg_brake_update) ###checked but does not change ui
tc.brake.service_brake_updated.connect(driver.handle_service_brake_update)
tc.brake.emergency_brake_updated.connect(driver.handle_emerg_brake_update)
tc.train_model.engine_fault_updated.connect(driver.handle_engine_fault_update)
tc.train_model.brake_fault_updated.connect(driver.handle_brake_fault_update)
tc.train_model.signal_fault_updated.connect(driver.handle_signal_fault_update)
tc.curr_speed_updated.connect(driver.handle_curr_speed_update)
tc.train_model.comm_speed_received.connect(driver.handle_comm_speed_update)
tc.authority_updated.connect(driver.handle_authority_update)
tc.position_updated.connect(driver.handle_position_update)
tc.destination_updated.connect(driver.handle_destination_update)

#TRAIN CONTROLLER TO ENGINEER
#tc.kp_updated_for_eng.connect(engineer.handle_kp_update)
#tc.engineer.ki_updated.connect(engineer.handle_ki_update)

#str to int between engineer/train controller/test bench

#ENGINEER TO TRAIN CONTROLLER
engineer.kp_updated.connect(tc.handle_kp_changed)
engineer.ki_updated.connect(tc.handle_ki_changed)

driver_window = driver
driver_window.show()

test_window = test
test_window.show()

engineer_window = engineer
engineer_window.show()

app.exec()


print("Driver UI: " + str(driver.user_serv_brake_status))
print("TC: " + str(tc.brake.user_service_brake))



