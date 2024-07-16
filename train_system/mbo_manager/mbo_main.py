import sys
from typing import List
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock

from train_system.mbo_manager.mbo_manager import MBOOffice
from train_system.mbo_manager.mbo_ui import MBOWindow

@pyqtSlot()
def handle_recieved_data(data)-> None:
    print("recieved data ", data)

#Create the application 
app = QApplication(sys.argv)

#Create time keeper object 
time_keeper = TimeKeeper()
time_keeper.start_timer()

#instantiate MBOController
mbo_office = MBOOffice()
schedules = MBOOffice.Schedules()
satellite = MBOOffice.Satellite()
satellite.mbo_mode = True

#instantiate the MBO UI
mbo_main_ui = MBOWindow()

#connect time keeper signal to MBO Manager 
    #what needs connected to time? Commanded Speed and Authority?? Not completely time dependent could just recalculate when new train positions are emitted? 


#need signal from CTC office for satellite sending

#need signal from train model for satellite recieving 

#connect vital signals 
satellite.send_data_signal.connect(handle_recieved_data)

#generate key for encryption on top top level? signal here to get it? and send to satellite 


#Connect GUI signals
#for planner create schedule

#is this connected right?? 
mbo_main_ui.schedule_created.connect(schedules.create_schedules)


if __name__ == "__main__":
    
    satellite.satellite_send()
    
    #pass mbo_main_ui.show()
    #pass sys.exit(app.exec())




