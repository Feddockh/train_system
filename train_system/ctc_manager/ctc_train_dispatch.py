# train_system/ctc_manager/ctc_train_dispatch.py

from train_system.common.train_dispatch import TrainDispatch
from train_system.common.line import Line
from train_system.common.time_keeper import TimeKeeper

class CTCTrainDispatch(TrainDispatch):
    def __init__(self, train_id: int, line: Line, 
                 time_keeper: TimeKeeper) -> None:
        super().__init__(train_id, line, time_keeper)

        self.suggested_speed = 0

    def update(self, suggested_speed: int, authority: int) -> None:
        self.suggested_speed = suggested_speed
        self.authority = authority