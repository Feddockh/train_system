# train_system/main.py

import sys
from PyQt6.QtWidgets import QApplication
from cryptography.fernet import Fernet

from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper
from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.dispatcher_ui import DispatcherUI
from train_system.track_controller.track_controller_manager import TrackControllerManager
from train_system.track_controller.sw_ui import ProgrammerUI
# from train_system.mbo_manager.mbo_manager import MBOOffice
# from train_system.mbo_manager.mbo_ui import MBOWindow
# from train_system.train_controller.tc_manager import TrainManager
# from train_system.track_model.track_model import TrackModel

# from train_system.train_controller.train_controller import TrainSystem

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
    track_controller_manager = TrackControllerManager(time_keeper)
    programmer_ui = ProgrammerUI(track_controller_manager.waysides)
    programmer_ui.show()

    # Connect the CTC's line signals to the Track Controller Manager's line handler
    ctc_manager.green_line.authority_queue_signal.connect(track_controller_manager.green_line.handle_authority_queue)

    ### Instantiate the TrackModel object and the track's UI ###
    # track_model = TrackModel(time_keeper)

    ### Instantiate the TrainController object and the driver's UI ###
    # train_manager = TrainManager(time_keeper)
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
    # Function to generate and store a key
    # def write_key():
    #     key = Fernet.generate_key()
    #     with open("key.key", "wb") as key_file:
    #         key_file.write(key)
            
    # def load_key():
    #     return open("key.key", "rb").read()
    # write_key()
    # key = load_key()
    
    # mbo_manager = MBOOffice(time_keeper)
    # mbo_satellite = mbo_manager.Satellite()
    # mbo_ui = MBOWindow()
    # mbo_ui.show()
    
    # mbo_satellite.key_recieved.emit(key)
    #emit key to train_manager?
    # train_manager.key_recieved.emit(key)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
