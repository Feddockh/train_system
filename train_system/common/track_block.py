# train_system/common/track_block.py

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import List
from train_system.common.track_failures import TrackFailure
from train_system.track_model.beacon import Beacon
from train_system.common.track_switch import TrackSwitch
from train_system.common.station import Station
from train_system.common.authority import Authority


class TrackBlock(QObject):
    suggested_speed_updated = pyqtSignal(int, int)
    authority_updated = pyqtSignal(int, object)
    occupancy_updated = pyqtSignal(int, bool)
    crossing_signal_updated = pyqtSignal(int, bool)
    light_signal_updated = pyqtSignal(int, bool)
    under_maintenance_updated = pyqtSignal(int, bool)
    track_failure_updated = pyqtSignal(int, TrackFailure)

    def __init__(self, line: str, section: str, number: int, length: int,
                 grade: float, speed_limit: int, elevation: float, 
                 cumulative_elevation: float, underground: bool, 
                 crossing_signal: bool, light_signal: bool,
                 connecting_blocks: List[int],
                 station: Station = None, switch: TrackSwitch = None,
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
        self.underground = underground
        self.connecting_blocks = connecting_blocks
        self.station = station
        self.switch = switch
        self.beacon = beacon

        # Calculated parameters
        self.traversal_time = self.length / (self.speed_limit / 3.6) # meters/seconds


        # Dynamic 
        self._suggested_speed = 0
        self._authority: Authority = Authority(0)
        self._occupancy = False
        self._crossing_signal = None if crossing_signal is False else False
        self._light_signal = None if light_signal is False else False
        self._under_maintenance = False
        self._track_failure = TrackFailure.NONE
        self._plc_unsafe = False

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
            f"Underground:             {self.underground}\n"
            f"Station:                 {self.station}\n"
            f"Switch:                  {self.switch}\n"
            f"Beacon:                  {self.beacon}\n"
            f"Suggested Speed:         {self._suggested_speed}\n"
            f"Authority:               {self._authority}\n"
            f"Occupancy:               {self._occupancy}\n"
            f"Crossing Signal:         {self._crossing_signal}\n"
            f"Light Signal:            {self._light_signal}\n"
            f"Under Maintenance:       {self._under_maintenance}\n"
            f"Track Failure:           {self._track_failure}"
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

    def __deepcopy__(self, memo):
        # Create a new instance of TrackBlock
        new_copy = TrackBlock(
            self.line, self.section, self.number, self.length, 
            self.grade, self.speed_limit, self.elevation, 
            self.cumulative_elevation, self.underground, 
            self._crossing_signal is not None, self._light_signal is not None, 
            self.connecting_blocks, self.station, self.switch, self.beacon
        )
        
        # Copy the dynamic attributes manually
        new_copy._suggested_speed = self._suggested_speed
        new_copy._authority = Authority(self._authority.get_distance(), self._authority.get_stop_block())
        new_copy._occupancy = self._occupancy
        new_copy._crossing_signal = self._crossing_signal
        new_copy._light_signal = self._light_signal
        new_copy._under_maintenance = self._under_maintenance
        new_copy._track_failure = self._track_failure
        new_copy._plc_unsafe = self._plc_unsafe
        
        # Return the new instance
        return new_copy

    @property
    def suggested_speed(self) -> int:
        return self._suggested_speed

    @suggested_speed.setter
    def suggested_speed(self, value: int) -> None:
        if self._suggested_speed != value:
            self._suggested_speed = value
            self.suggested_speed_updated.emit(self.number, value)

    @property
    def authority(self) -> Authority:
        return self._authority

    @authority.setter
    def authority(self, value: Authority) -> None:
        if self._authority != value:
            self._authority = value
            self.authority_updated.emit(self.number, value)

    @property
    def occupancy(self) -> bool:
        return self._occupancy
    
    @occupancy.setter
    def occupancy(self, value: bool) -> None:
        if self._occupancy != value:
            self._occupancy = value
            self.occupancy_updated.emit(self.number, value)

    @property
    def crossing_signal(self) -> bool:
        return self._crossing_signal

    @crossing_signal.setter
    def crossing_signal(self, value: bool) -> None:
        if self._crossing_signal != value:
            self._crossing_signal = value
            self.crossing_signal_updated.emit(self.number, value)
            
    @property
    def light_signal(self) -> bool:
        return self._light_signal
    
    @light_signal.setter
    def light_signal(self, value: bool) -> None:
        if self._light_signal != value:
            self._light_signal = value
            self.light_signal_updated.emit(self.number, value)

    @property
    def under_maintenance(self) -> bool:
        return self._under_maintenance
    
    @under_maintenance.setter
    def under_maintenance(self, value: bool) -> None:
        if self._under_maintenance != value:
            self._under_maintenance = value
            self.under_maintenance_updated.emit(self.number, value)

    @property
    def track_failure(self) -> TrackFailure:
        return self._track_failure
    
    @track_failure.setter
    def track_failure(self, value: TrackFailure) -> None:
        if self._track_failure != value:
            self._track_failure = value
            self.track_failure_updated.emit(self.number, value)
