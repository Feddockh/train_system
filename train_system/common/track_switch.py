# train_system/common/track_switch.py

from PyQt6.QtCore import pyqtSignal, QObject
from typing import List

class TrackSwitch(QObject):
    position_updated = pyqtSignal(int)

    def __init__(self, line: str, number: int, parent_block: int, 
                 child_blocks: List[int], initial_child: int) -> None:
        super().__init__()

        self.line = line
        self.number = number
        self.parent_block = parent_block
        self.child_blocks = child_blocks
        self.connected_blocks = [parent_block] + child_blocks
        self.position = initial_child
    
    def __repr__(self) -> str:
        return f"Track Switch: {self.parent_block} -> {self.position}"

    def toggle(self) -> None:
        if self.position == self.child_blocks[0]:
            self.position = self.child_blocks[1]
        else:
            self.position = self.child_blocks[0]
        self.position_updated.emit(self.position)

    def is_connected(self, block_a: int, block_b: int) -> bool:
        
        # Check that the blocks are connected to the switch
        if (block_a != self.parent_block or block_b not in self.child_blocks) and \
            (block_b != self.parent_block or block_a not in self.child_blocks):
            return False
        
        # Check that the blocks are connected to different sides of the switch
        if block_a == self.parent_block:
            return block_b == self.position
        else:
            return block_a == self.position
        
    def next_block_id(self, current_block: int) -> int:
        if current_block == self.parent_block:
            return self.position
        elif current_block == self.position:
            return self.parent_block
        else:
            return None