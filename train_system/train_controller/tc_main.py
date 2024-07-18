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

driver = DriverWindow()

print("TC: " + str(tc.ac.get_commanded_temp()))
print("UI: " + str(driver.tm.get_train_temp()))

time_keeper.tick.connect(tc.handle_time_update)
time_keeper.current_second.connect(tc.lights.update_lights)

driver.mode_button.toggled.connect(tc.handle_toggle_driver_mode) ###checked
driver.em_brake_button.toggled.connect(tc.handle_emergency_brake_toggled) ###checked
driver.service_brake_button.toggled.connect(tc.handle_service_brake_toggled) ###checked
driver.speed_input.textChanged.connect(tc.handle_setpoint_edit_changed) ###checked but conversions need fixed
driver.comm_temp_input.textChanged.connect(tc.handle_comm_temp_changed) ###checked

tc.setpoint_speed_updated.connect(driver.handle_setpoint_speed_update)
tc.power_updated.connect(driver.handle_power_update)
tc.lights.lights_updated.connect(driver.handle_light_status_update)
tc.doors.left_door_updated.connect(driver.handle_left_door_update)
tc.doors.right_door_updated.connect(driver.handle_right_door_update)
tc.ac.train_temp_updated.connect(driver.handle_train_temp_update)
tc.brake.service_brake_updated.connect(driver.handle_service_brake_update)
tc.brake.emergency_brake_updated.connect(driver.handle_emerg_brake_update)

window = driver
window.show()

app.exec()

print("TC: " + str(tc.ac.get_commanded_temp()))
print("UI: " + str(driver.tm.get_train_temp()))

