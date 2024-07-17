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
    
tc = TrainController(tm)

driver = DriverWindow()

driver.mode_button.toggled.connect(tc.handle_toggle_driver_mode)
driver.em_brake_button.toggled.connect(tc.handle_emergency_brake_toggled)
driver.service_brake_button.toggled.connect(tc.handle_service_brake_toggled)
driver.speed_input.textChanged.connect(tc.handle_setpoint_edit_changed)



window = DriverWindow()
window.show()

app.exec()

#test ui outputs
print("train model temp " + str(tc.train_model.get_train_temp()))
print("controller temp " + str(tc.ac.get_commanded_temp()))
    

