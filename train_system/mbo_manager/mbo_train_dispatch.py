# train_system/mbo_manager/mbo_train_dispatch.py

from train_system.common.train_dispatch import TrainDispatch
from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper

class MBOTrainDispatch(TrainDispatch):
    def __init__(self, train_id: int, line: Line, 
                 time_keeper: TimeKeeper) -> None:
        super().__init__(train_id, line, time_keeper)

        self.position = 0
        self.commanded_speed = 0