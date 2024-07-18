import sys
from train_system.train_controller.train_controller import TrainController, TrainModel
from train_system.train_controller.tc_ui import *
from train_system.common.time_keeper import TimeKeeper
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
   
# Create the time keeper object
time_keeper = TimeKeeper()
time_keeper.start_timer()   

tm = TrainModel()
    
tc = TrainController(time_keeper, train_model=tm)

driver = DriverWindow(time_keeper)
test = TestBenchWindow()

print("TC: speed " + str(tc.get_setpoint_speed()))
print("UI: speed " + str(driver.setpoint_speed))
print("TC: serv " + str(tc.brake.get_service_brake()))
print("UI driver: serv " + str(driver.serv_brake_status))
print("UI test: serv " + str(test.serv_brake_status))


"""
with two separate windows, connections can be made
-brake is the only one reliably tested
-brake status changes but checked is not reliable
"""

test.setpoint_updated.connect(tc.handle_setpoint_edit_changed) 
test.service_brake_updated.connect(tc.handle_service_brake_toggled)

driver.mode_button.toggled.connect(tc.handle_toggle_driver_mode) ###checked
driver.em_brake_button.toggled.connect(tc.handle_emergency_brake_toggled) ###checked
driver.service_brake_button.toggled.connect(tc.handle_service_brake_toggled) ###checked
driver.speed_input.textChanged.connect(tc.handle_setpoint_edit_changed) ###checked but conversions need fixed
driver.comm_temp_input.textChanged.connect(tc.handle_comm_temp_changed) ###checked

tc.setpoint_speed_updated.connect(driver.handle_setpoint_speed_update) ###checked
tc.power_updated.connect(driver.handle_power_update)
tc.lights.lights_updated.connect(driver.handle_light_status_update) ###checked but does not change ui
tc.doors.left_door_updated.connect(driver.handle_left_door_update)
tc.doors.right_door_updated.connect(driver.handle_right_door_update)
tc.ac.train_temp_updated.connect(driver.handle_train_temp_update)
tc.brake.service_brake_updated.connect(driver.handle_service_brake_update)
tc.brake.emergency_brake_updated.connect(driver.handle_emerg_brake_update) ###checked but does not change ui

driver_window = driver
driver_window.show()

test_window = test
test_window.show()

app.exec()

#tc.set_setpoint_speed(20)
#tc.lights.set_lights(True)

print("TC: speed " + str(tc.get_setpoint_speed()))
print("UI: speed " + str(driver.setpoint_speed))
print("TC: serv " + str(tc.brake.get_service_brake()))
print("UI driver: serv " + str(driver.serv_brake_status))
print("UI test: serv " + str(test.serv_brake_status))

