# train_system/ctc_manager/main.py

import sys
from typing import List
from PyQt6.QtWidgets import QApplication

from train_system.common.time_keeper import TimeKeeper
from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.common.train_dispatch import TrainDispatch
from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.dispatcher_ui import DispatcherUI

# Create the application
app = QApplication(sys.argv)

# Create the time keeper object
time_keeper = TimeKeeper()
time_keeper.start_timer()

# Instatiate the CTCOffice object
ctc_manager = CTCOffice(time_keeper, "Green")

# Instantiate the DispatcherUI object
dispatcher_ui = DispatcherUI(time_keeper, ctc_manager.line, ctc_manager.trains)

# Connect the time keeper signal to the CTC Manager slot
time_keeper.tick.connect(ctc_manager.handle_time_update)

# Connect the GUI switch signals to the CTC Manager slots
dispatcher_ui.test_bench_toggle_switch.toggled.connect(ctc_manager.handle_test_bench_toggle)
dispatcher_ui.maintenance_toggle_switch.toggled.connect(ctc_manager.handle_maintenance_toggle)
dispatcher_ui.mbo_toggle_switch.toggled.connect(ctc_manager.handle_mbo_toggle)
dispatcher_ui.automatic_toggle_switch.toggled.connect(ctc_manager.handle_automatic_toggle)

# Connect the GUI dispatch signals to the CTC Manager slots
dispatcher_ui.dispatch_command_widget.dispatched_train.connect(ctc_manager.handle_dispatcher_command)
dispatcher_ui.schedule_selection_widget.dispatched_train.connect(ctc_manager.handle_dispatcher_command)

# Connect the Line signals to the DispatcherUI slots
ctc_manager.line.track_block_occupancy_updated.connect(dispatcher_ui.handle_occupancy_update)
ctc_manager.line.track_block_crossing_signal_updated.connect(dispatcher_ui.handle_crossing_signal_update)
ctc_manager.line.track_block_under_maintenance_updated.connect(dispatcher_ui.handle_maintenance_update)

# Connect the CTC Manager signals to the DispatcherUI slots


# Show the dispatcher UI
dispatcher_ui.show()
sys.exit(app.exec())

# TODO:
# - Compute dispatch times
# - Implement dispatch logic
# - Implement conversions between back end and gui
# - Testbench mode
# - Create top level system main