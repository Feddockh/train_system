from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class Engineer(QObject):
        kp_updated = pyqtSignal(int)
        ki_updated = pyqtSignal(int)
        
        def __init__(self, kp=400, ki=20):
            # super().__init__()
            self.kp = kp
            self.ki = ki

        ## Mutator functions
        def set_kp(self, kp: float):
            if kp >= 0:
                self.kp = kp
                # self.kp_updated.emit(self.kp)
            else: raise ValueError("kp must be non-negative")
        def set_ki(self, ki: float):
            if ki >= 0:
                self.ki = ki
                # self.ki_updated.emit(self.ki)
            else: raise ValueError("ki must be non-negative")
        def set_engineer(self, kp: float, ki: float):
            self.set_kp(kp)
            self.set_ki(ki)

        ## Accessor functions
        def get_kp(self):
            return self.kp
        def get_ki(self):
            return self.ki
        def get_engineer(self):
            return self.get_kp(), self.get_ki()



## Engineer class to hold Kp and Ki
# class Engineer():
    
#     def __init__(self, kp=25, ki=0.5):
#         self.trains = 100
#         super().__init__()
#         # list of kp and ki the size of trains
#         self.kp = [kp] * self.trains
#         self.ki = [ki] * self.trains
        
#     ## Mutator functions
#     def set_kp(self, kp: float, train_id: int):
#         if kp >= 0:
#             self.kp[train_id] = kp
#     def set_ki(self, ki: float):
#         if ki >= 0:
#             self.ki = ki
#     def set_engineer(self, kp: float, ki: float):
#         self.set_kp(kp)
#         self.set_ki(ki)

#     ## Accessor functions
#     def get_kp(self, train_id: int):
#         return self.kp[train_id]
#     def get_ki(self, train_id: int):
#         return self.ki[train_id]
#     def get_engineer(self, train_id: int):
#         return self.get_kp(train_id), self.get_ki(train_id)