# train_system/ctc_manager/main.py

import os
import sys
from PyQt6.QtWidgets import QApplication

from train_system.common.line import Line
from train_system.common.track_block import TrackBlock
from train_system.ctc_manager.ctc_manager import CTCOffice
from train_system.ctc_manager.dispatcher_ui import DispatcherUI

# Create the application
app = QApplication(sys.argv)

# Create the line object
line = Line("Blue")
file_path = os.path.abspath(os.path.join("tests", "blue_line.xlsx"))
line.load_track_blocks(file_path)

# Instatiating the CTCOffice object
ctc_manager = CTCOffice()

# Instantiate the DispatcherUI object
dispatcher_ui = DispatcherUI(line)

# Connect the signals and slots
dispatcher_ui.test_bench_toggle_switch.toggled.connect(ctc_manager.handle_test_bench_toggle)
dispatcher_ui.maintenance_toggle_switch.toggled.connect(ctc_manager.handle_maintenance_toggle)
dispatcher_ui.mbo_toggle_switch.toggled.connect(ctc_manager.handle_mbo_toggle)
dispatcher_ui.automatic_toggle_switch.toggled.connect(ctc_manager.handle_automatic_toggle)

# Show the dispatcher UI
dispatcher_ui.show()
sys.exit(app.exec())

# TODO:
# - Implement functionality of signals and slots
# - Implement throughput metric widget
# - Implement improved train visual widget
# - Implement time (including authority and speed computations)