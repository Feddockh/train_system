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
def handle_sent_data(train_id, authority, commanded_speed)-> None:
    #should be signal for train model 
    print(f"sent data {train_id}, {authority}, {commanded_speed}")

#Create the application 
app = QApplication(sys.argv)

#Create time keeper object 
time_keeper = TimeKeeper()
time_keeper.start_timer()

#instantiate MBOController
mbo_office = MBOOffice(time_keeper)
schedules = MBOOffice.Schedules()
satellite = MBOOffice.Satellite()
satellite.mbo_mode = True

#connect vital signals 
#recieving updated train positions
#train.position_signal.connect(satellite.satellite_recieve)
#sending update speed and authority
satellite.send_data_signal.connect(handle_sent_data)


#Connect GUI signals
#for planner create schedule
mbo_main_ui = MBOWindow()
mbo_main_ui.schedule_created.connect(schedules.create_schedules)

mbo_main_ui.show()
sys.exit(app.exec())

"""if __name__ == "__main__":
    
    #train leaving yard
    train.update_position('Train1', 0, "from_yard")
    
    #train in 1st block on way to Glenbury
    train.update_position('Train1', 73.0, 63)
    
    #train in 2nd block on way to Glenbury
    train.update_position('Train1', 200.00, 64)
    
    #train at station 
    #@313m in middle of block """




