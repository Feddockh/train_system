# train_system/mbo_manager/mbo_train_dispatch.py

from train_system.common.train_dispatch import TrainDispatch
from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper

class MBOTrainDispatch(TrainDispatch):
    def __init__(self, time_keeper: TimeKeeper, train_id: int,
                 line: Line) -> None:
        super().__init__(time_keeper, train_id, line)

        self.position = 0
        self.commanded_speed = 0