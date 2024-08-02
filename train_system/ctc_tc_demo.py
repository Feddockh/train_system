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
from train_system.track_model.track_model import TrackModel


# from train_system.mbo_manager.mbo_manager import MBOOffice
# from train_system.mbo_manager.mbo_ui import MBOWindow
from train_system.train_controller.tc_manager import TrainManager
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

    # Connect the CTC's line signals to the Track Controller Manager's green line handler
    ctc_manager.green_line.authority_queue_signal.connect(track_controller_manager.green_line.handle_authority_queue)
    ctc_manager.green_line.suggested_speed_queue_signal.connect(track_controller_manager.green_line.handle_suggested_speed_queue)
    ctc_manager.green_line.under_maintenance_queue_signal.connect(track_controller_manager.green_line.handle_under_maintenance_queue)
    ctc_manager.green_line.switch_position_queue_signal.connect(track_controller_manager.green_line.handle_switch_position_queue)

    # This was added for testing purposes
    ctc_manager.green_line.occupancy_queue_signal.connect(track_controller_manager.green_line.handle_occupancy_queue)
    ctc_manager.red_line.occupancy_queue_signal.connect(track_controller_manager.red_line.handle_occupancy_queue)

    # Connect the CTC's line signals to the Track Controller Manager's red line handler
    ctc_manager.red_line.authority_queue_signal.connect(track_controller_manager.red_line.handle_authority_queue)
    ctc_manager.red_line.suggested_speed_queue_signal.connect(track_controller_manager.red_line.handle_suggested_speed_queue)
    ctc_manager.red_line.under_maintenance_queue_signal.connect(track_controller_manager.red_line.handle_under_maintenance_queue)
    ctc_manager.red_line.switch_position_queue_signal.connect(track_controller_manager.red_line.handle_switch_position_queue)

    # Connect the green line Track Controller Manager's signals to the CTC's green line handler
    # track_controller_manager.green_line.track_block_occupancy_updated.connect(ctc_manager.green_line.handle_occupancy_update)
    track_controller_manager.green_line.switch_position_updated.connect(ctc_manager.green_line.handle_switch_position_update)

    # Connect the red line Track Controller Manager's signals to the CTC's red line handler
    # track_controller_manager.red_line.track_block_occupancy_updated.connect(ctc_manager.red_line.handle_occupancy_update)
    track_controller_manager.red_line.switch_position_updated.connect(ctc_manager.red_line.handle_switch_position_update)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
