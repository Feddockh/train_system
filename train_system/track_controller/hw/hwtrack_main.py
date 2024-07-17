# train_system/track_controller/hwtrack_main.py
import sys
from hw_trackcontroller import HWTrackController
#import sys
#from PyQt6.QtWidgets import *
#from PyQt6.QtGui import QPainter, QColor
#from PyQt6.QtCore import Qt
#from PyQt6 import QtCore, QtGui, QtWidgets, uic
#from hwtrack_ui import TrackControllerWindow

# Test main function
def main():
    """
    Test Bench
    """
    
    print(f"Red Line Example 1: Wayside Controller #4\n")
      #                  yard   1      2      3     4       5      6      7      8      9     10      11     12     13     14     15
    #track_occupancies = [False, False, False, True, False, False, False, False, True, False, False, False, False, False, False, False ]
    track_occupancies = 150*[False]

    #Testing occupancies section
    
    #block 2 should be occupied, so trains cannot leave the yard, and block 15 to 16 must connect
    #track_occupancies[2] = True

    track_occupancies[75] = True

    instance1 = HWTrackController(track_occupancies)
    #instance1.get_switch_position()

if __name__ == "__main__":
    main()