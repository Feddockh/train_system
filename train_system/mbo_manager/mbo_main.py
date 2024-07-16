import sys
from typing import List
from PyQt6.QtWidgets import QApplication

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.mbo_manager.mbo_manager import MBOController
from train_system.mbo_manager.mbo_ui import MBOWindow

#Create the application 
app = QApplication(sys.argv)

#Create time keeper object 
time_keeper = TimeKeeper()
time_keeper.start_timer()

#instantiate MBOController
mbo_controller = MBOController()

#instantiate the MBO UI
mbo_main_ui = MBOWindow()

#connect time keeper signal to MBO Manager 

#Connect GUI signals
#for planner create schedule
mbo_main_ui.schedule_created.connect(mbo_controller.create_schedules)


#connect create schedules button 

#connect MBO mode view window 

#connect test bench 

#connect to read train position from satellite? 

#show the MBO UI


mbo_main_ui.show()
sys.exit(app.exec())