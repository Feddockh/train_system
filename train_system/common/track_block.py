# train_system/common/track_block.py

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import List
from train_system.common.crossing_signal import CrossingSignal
from train_system.common.track_failures import TrackFailure
from train_system.track_model.beacon import Beacon

crossing_signal_map = {
    CrossingSignal.ON: True,
    CrossingSignal.OFF: False,
    CrossingSignal.NA: None
}

class TrackBlock(QObject):

    # Signals to notify updates
    suggested_speed_updated = pyqtSignal(int)
    authority_updated = pyqtSignal(int)
    occupancy_updated = pyqtSignal(bool)
    switch_position_updated = pyqtSignal(int)
    crossing_signal_updated = pyqtSignal(CrossingSignal)
    under_maintenance_updated = pyqtSignal(bool)
    track_failure_updated = pyqtSignal(TrackFailure)

    def __init__(self, line: str, section: str, number: int, length: int,
                 grade: float, speed_limit: int, elevation: float, 
                 cumulative_elevation: float, connecting_blocks: List[int],
                 next_blocks: List[int] = None, station: str = None,
                 station_side: str = None, switch_options: List[int] = None,
                 beacon: Beacon = None) -> None:

        super().__init__()

        # Static parameters
        self.line = line
        self.section = section
        self.number = number
        self.length = length # meters
        self.grade = grade # %
        self.speed_limit = speed_limit # km/h
        self.elevation = elevation # meters
        self.cumulative_elevation = cumulative_elevation # meters
        self.connecting_blocks = connecting_blocks
        self.next_blocks = next_blocks
        self.station = station
        self.station_side = station_side
        self.switch_options = switch_options

        # Calculated parameters
        self.traversal_time = self.length / (self.speed_limit / 3.6) # seconds
        self.beacon = beacon

        # Dynamic parameters
        self._suggested_speed = 0
        self._authority = 0
        self._occupancy = False
        self._switch_position = None
        self._crossing_signal = CrossingSignal.NA
        self._crossing_signal_bool = None
        self._under_maintenance = False
        self._light_signal = None
        self._track_failure = TrackFailure.NONE

        self.crossing_signal_updated.connect(self.update_crossing_signal_bool)

    def __repr__(self) -> str:

        """
        Returns a string representation of the TrackBlock object.
        
        Returns:
            str: String representation of the TrackBlock object.
        """

        return (
            f"Line:                    {self.line}\n"
            f"Section:                 {self.section}\n"
            f"Number:                  {self.number}\n"
            f"Length:                  {self.length}\n"
            f"Grade:                   {self.grade}\n"
            f"Speed Limit:             {self.speed_limit}\n"
            f"Elevation:               {self.elevation}\n"
            f"Cumulative Elevation:    {self.cumulative_elevation}\n"
            f"Connecting Track Blocks: {self.connecting_blocks}\n"
            f"Next Track Blocks:       {self.next_blocks}\n"
            f"Station:                 {self.station}\n"
            f"Station Side:            {self.station_side}\n"
            f"Switch Options:          {self.switch_options}\n"
            f"Beacon:                  {self.beacon}\n"
            f"Suggested Speed:         {self._suggested_speed}\n"
            f"Authority:               {self._authority}\n"
            f"Occupancy:               {self._occupancy}\n"
            f"Switch Position:         {self._switch_position}\n" 
            f"Crossing Signal:         {self._crossing_signal}\n"
            f"Under Maintenance:       {self._under_maintenance}\n"
            f"Failure:                 {self._track_failure}"
        )

    def __eq__(self, other: object) -> bool:

        """
        Checks if two TrackBlock objects are equal.
        
        Args:
            other (TrackBlock): The other TrackBlock object to compare with.
        
        Returns:
            bool: True if the objects are equal, False otherwise.
        
        Raises:
            TypeError: If the other object is not a TrackBlock.
        """

        if not isinstance(other, TrackBlock):
            raise TypeError(
                f"Expected a TrackBlock object, but got {type(other).__name__}"
            )
        return (self.line, self.section, self.number) == (
            other.line, other.section, other.number
        )

    @property
    def suggested_speed(self) -> int:
        return self._suggested_speed

    @suggested_speed.setter
    def suggested_speed(self, value: int) -> None:
        if self._suggested_speed != value:
            self._suggested_speed = value
            self.suggested_speed_updated.emit(value)

    @property
    def authority(self) -> int:
        return self._authority

    @authority.setter
    def authority(self, value: int) -> None:
        if self._authority != value:
            self._authority = value
            self.authority_updated.emit(value)

    @property
    def occupancy(self) -> bool:
        return self._occupancy
    
    @occupancy.setter
    def occupancy(self, value: bool) -> None:
        self._occupancy = value
        self.occupancy_updated.emit(value)

    @property
    def switch_position(self) -> int:
        return self._switch_position

    @switch_position.setter
    def switch_position(self, value: int) -> None:
        if self._switch_position != value:
            self._switch_position = value
            self.switch_position_updated.emit(value)

    @property
    def crossing_signal(self) -> CrossingSignal:
        return self._crossing_signal

    @crossing_signal.setter
    def crossing_signal(self, value: CrossingSignal) -> None:
        if self._crossing_signal != value:
            self._crossing_signal = value
            self.crossing_signal_updated.emit(value)

    @property
    def crossing_signal_bool(self) -> bool:
        return crossing_signal_map[self._crossing_signal]

    @crossing_signal_bool.setter
    def crossing_signal_bool(self, value: bool) -> None:
        for signal, bool_value in crossing_signal_map.items():
            if bool_value == value:
                self.crossing_signal = signal
                break

    @pyqtSlot(CrossingSignal)
    def update_crossing_signal_bool(self, signal: CrossingSignal) -> None:
        self._crossing_signal_bool = crossing_signal_map[signal]
            
    @property
    def under_maintenance(self) -> bool:
        return self._under_maintenance
    
    @under_maintenance.setter
    def under_maintenance(self, value: bool) -> None:
        self._under_maintenance = value
        self.under_maintenance_updated.emit(value)

    @property
    def track_failure(self) -> TrackFailure:
        return self._track_failure
    
    @track_failure.setter
    def track_failure(self, value: TrackFailure) -> None:
        self._track_failure = value
        self.track_failure_updated.emit(value)
