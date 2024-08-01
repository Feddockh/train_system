# train_system/main.py

import sys
from PyQt6.QtWidgets import QApplication

from train_system.common.time_keeper import TimeKeeper
from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.dispatcher_ui import DispatcherUI
from train_system.train_controller.tc_manager import TrainManager
from train_system.track_model.track_model import TrackModel

from train_system.train_controller.train_controller import TrainSystem

def main():

    # Create the application
    app = QApplication(sys.argv)

    # Create the time keeper object
    time_keeper = TimeKeeper()
    time_keeper.start_timer()

    ### Instantiate the CTCOffice object and the dispatcher's UI ###
    ctc_manager = CTCOffice(time_keeper)
    dispatcher_ui = DispatcherUI(time_keeper, ctc_manager.lines, ctc_manager.trains)
    ctc_manager.connect_dispatcher_ui(dispatcher_ui)
    dispatcher_ui.show()

    ### Instantiate the TrackController object and the programmer's UI ###
    

    ### Instantiate the TrackModel object and the track's UI ###
    track_model = TrackModel(time_keeper)

    ### Instantiate the TrainController object and the driver's UI ###
    train_manager = TrainManager(time_keeper)
    # track_model.track_to_train.connect(train_manager.handle_CTC_update)
    # train_manager.passengers_to_train.connect(train_manager.handle_passenger_update)
    
    '''
    # train_manager.train_dispatched.connect(mbo.handle_dispatch)   # Signal to make more connections for the Train Model speaks to MBO
    # mbo.send_satellite.connect(train_manager.handle_MBO_update)   # MBO speaks to Train Model

    # def handle_dispatch(train_system: TrainSystem):
    #     train_system.satellite_sent.connect(mbo.satellite_receive)

    # Connect Track model's outputs to manager
    # Connect MBO's outputs to manager
    '''


    # Connect the CTC's dispatch signal to the Train Manager's dispatch handler
    


    ### Instantiate the TrainModel object and the train's UI ###
    # Connect Train Model to Track Model
    # Connect Track Model to Train Model

    ### Instantiate the MBOController object and the operator's UI ###
    # Connect MBO to Train Model
    # Connect Train Model to MBO


    





    sys.exit(app.exec())

if __name__ == "__main__":
    main()
