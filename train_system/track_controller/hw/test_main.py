import sys
from PyQt6.QtWidgets import QApplication
from train_system.track_controller.hw.hw_track_controller import TrackController
from train_system.common.track_block import TrackBlock
from train_system.common.crossing_signal import CrossingSignal
from train_system.track_controller.hw.hwtrack_ui import ProgrammerUI

def create_track_blocks(num_blocks):
    blocks = []
    for i in range(1, num_blocks + 1):
        block = TrackBlock("", "", i, 1, 1, 1, 1, 1, 1, "")
        block.authority = 45
        if i == 13:  # Example of setting some specific properties for the first block
            #block.crossing_signal = CrossingSignal.OFF
            #block._light_signal = False
            block.switch_options = [1, 12]
            block.switch_position = 1
        elif i == 1:  # Setting properties for the second block
            block.switch_options = [13]
        elif i == 12:  # Setting properties for the third block
            block.switch_options = [13]
        elif i == 58:  # Setting properties for block 58
            block.switch_options = ["go to yard",59]
        elif i == 63:  # Setting properties for block 76
            block.switch_options = ["stay in yard",63]
        elif i == 29:
            block.switch_options = [30, 150]
        elif i == 76:
            block.switch_options = [77, 101]
        
        #simulating an emergency stop
        #elif i == 9:
            #block._occupancy = True
        elif i == 57: #simulate block 78 being occupied to make the switch go to 101
            block._occupancy = False
        elif i == 60:#simulate block 125 being occupied.
            block._occupancy = True
        elif i == 125:
            block._occupancy = True

        blocks.append(block)
    return blocks

def main():
    num_blocks = 150

    track_blocks1 = create_track_blocks(num_blocks)
    Wayside_1 = TrackController(track_blocks1)
    Wayside_1.numBlocks = len(Wayside_1.track_blocks)
    Wayside_1.wayside_name = "Wayside 1"

    track_blocks2 = create_track_blocks(num_blocks)
    Wayside_2 = TrackController(track_blocks2)
    Wayside_2.numBlocks = len(Wayside_2.track_blocks)
    Wayside_2.wayside_name = "Wayside 2"

    track_blocks3 = create_track_blocks(num_blocks)
    Wayside_3 = TrackController(track_blocks3)
    Wayside_3.numBlocks = len(Wayside_3.track_blocks)
    Wayside_3.wayside_name = "Wayside 3"

    track_blocks5 = create_track_blocks(num_blocks)
    Wayside_5 = TrackController(track_blocks5)
    Wayside_5.numBlocks = len(Wayside_5.track_blocks)
    Wayside_5.wayside_name = "Wayside 5"

    track_blocks6 = create_track_blocks(num_blocks)
    Wayside_6 = TrackController(track_blocks6)
    Wayside_6.numBlocks = len(Wayside_6.track_blocks)
    Wayside_6.wayside_name = "Wayside 6"

    waysides = [Wayside_1, Wayside_2, Wayside_3, Wayside_5, Wayside_6]

    app = QApplication(sys.argv)
    window = ProgrammerUI(waysides)
    window.show()

    app.exec()

if __name__ == "__main__":
    main()