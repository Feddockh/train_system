import sys
from typing import List
from PyQt6.QtWidgets import QApplication

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

from train_system.mbo_manager.mbo_manager import MBOOffice
from train_system.mbo_manager.mbo_ui import MBOWindow

#Create the application 
app = QApplication(sys.argv)

#Create time keeper object 
time_keeper = TimeKeeper()
time_keeper.start_timer()

#instantiate MBOController
mbo_office = MBOOffice()
schedules = MBOOffice.Schedules()

#instantiate the MBO UI
mbo_main_ui = MBOWindow()

#connect time keeper signal to MBO Manager 
    #what needs connected to time? Commanded Speed and Authority?? Not completely time dependent could just recalculate when new train positions are emitted? 


#connect vital signals 
commanded_speed = 0.0
mbo_office.update_commanded_speed.connect(commanded_speed)

#Connect GUI signals
#for planner create schedule

#is this connected right?? 
mbo_main_ui.schedule_created.connect(schedules.create_schedules)


mbo_main_ui.show()
sys.exit(app.exec())