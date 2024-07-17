from PyQt6.QtCore import QObject, pyqtSignal

class Train(QObject):
    
    position_signal = pyqtSignal(str, float, int)  # train_id, position, block

    def __init__(self):
        super().__init__()
        #values to test
        self.train_id = "Train1"
        self.position = 0.0 #0 m from yard
        self.block = 153 #from yard block?
        
        #need to add destination
        self.destination = 65 #Glenbury that has glenbury

    def update_position(self, new_position, new_block):
        
        self.position = new_position
        self.block = new_block
        self.position_signal.emit(self.train_id, self.position, self.block)