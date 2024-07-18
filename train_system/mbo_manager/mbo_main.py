import sys
from typing import List
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.mbo_manager.mbo_manager import MBOOffice
from train_system.mbo_manager.mbo_ui import MBOWindow
from train_system.common.train_dispatch import TrainDispatchUpdate
from train_system.common.train_dispatch import TrainDispatch
from train_system.ctc_manager.ctc_manager import CTCOffice

#for testing
from train_system.mbo_manager.train_model import Train

@pyqtSlot()
def handle_sent_data(train_id, authority, commanded_speed)-> None:
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

#pass time_keeper.tick.connect(mbo_office.handle_time_update)

#train example for testing? 
train = Train()

#instantiate the MBO UI
mbo_main_ui = MBOWindow()

#connect time keeper signal to MBO Manager 
    #what needs connected to time? Commanded Speed and Authority?? Not completely time dependent could just recalculate when new train positions are emitted? 


#need signal from CTC office for satellite sending

#need signal from train model for satellite recieving 

#connect vital signals 
#recieving updated train positions
train.position_signal.connect(satellite.satellite_recieve)
#sending update speed and authority
satellite.send_data_signal.connect(handle_sent_data)

#generate key for encryption on top top level? signal here to get it? and send to satellite 


#Connect GUI signals
#for planner create schedule

#is this connected right?? 
mbo_main_ui.schedule_created.connect(schedules.create_schedules)


if __name__ == "__main__":
    
    t_time_keeper = TimeKeeper()
    t_time_keeper.start_timer()
    
    satellite = MBOOffice(t_time_keeper).Satellite()
    ctc_office = CTCOffice(t_time_keeper, 'Green')
    dispatched_trains = TrainDispatch('Train1', 'Green', time_keeper)
    
    ctc_office.add_train('Train1', 'Green')
    dispatched_trains.add_stop(50, 65)
    
    #train leaving yard
    train.update_position('Train1', 0, "from_yard")
    
    #train in 1st block on way to Glenbury
    train.update_position('Train1', 73.0, 63)
    
    #train in 2nd block on way to Glenbury
    train.update_position('Train1', 200.00, 64)
    
    #train at station 
    #@313m in middle of block 
    train.update_position('Train1', 329.1, 65 )

    #pass mbo_main_ui.show()
    #pass sys.exit(app.exec())




