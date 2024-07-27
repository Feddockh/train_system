# train_system/main.py

import sys
from PyQt6.QtWidgets import QApplication

from train_system.common.time_keeper import TimeKeeper
from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.dispatcher_ui import DispatcherUI

def main():

    # Create the application
    app = QApplication(sys.argv)

    # Create the time keeper object
    time_keeper = TimeKeeper()
    time_keeper.start_timer()

    ### Instantiate the CTCOffice object and the dispatcher's UI ###
    line_names = ["green", "red"]
    ctc_manager = CTCOffice(time_keeper, line_names)
    dispatcher_ui = DispatcherUI(time_keeper, ctc_manager.lines, ctc_manager.trains)
    ctc_manager.connect_dispatcher_ui(dispatcher_ui)
    dispatcher_ui.show()

    ### Instantiate the TrackController object and the programmer's UI ###


    ### Instantiate the TrainModel object and the track's UI ###


    ### Instantiate the TrainModel object and the train's UI ###


    ### Instantiate the TrainController object and the driver's UI ###


    ### Instantiate the MBOController object and the operator's UI ###







    sys.exit(app.exec())

if __name__ == "__main__":
    main()