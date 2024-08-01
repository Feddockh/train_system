import sys
from typing import List
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.mbo_manager.mbo_manager import MBOOffice
from train_system.mbo_manager.mbo_ui import MBOWindow
from train_system.mbo_manager.mbo_schedule import Schedules


@pyqtSlot()
def handle_sent_data(train_id, authority, commanded_speed)-> None:
    #should be signal for train model 
    print(f"sent data {train_id}, {authority}, {commanded_speed}")

app = QApplication(sys.argv)

#Create time keeper object 
time_keeper = TimeKeeper()
time_keeper.start_timer()

#instantiate MBOController
mbo_office = MBOOffice(time_keeper)
schedules = Schedules()
satellite = MBOOffice.Satellite()

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

#if __name__ == "__main__":
