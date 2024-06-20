# train_system/common/track_block.py

from PyQt6.QtCore import QObject, pyqtSignal
from train_system.common.crossing_signal import CrossingSignal
from train_system.common.station import Station

class TrackBlock(QObject):

    # Create PYQT signals for occupancy and maintenance changes
    occupancyChanged = pyqtSignal()
    maintenanceChanged = pyqtSignal()

    def __init__(self, line: str, section: chr, number: int, length: int,
                 grade: float, speed_limit: int, elevation: float, 
                 cumulative_elevation: float, infrastructure: str = None,
                 station_side: str = None) -> None:
        
        """
        Initializes the TrackBlock object.
        
        Args:
            line (str): Identifier for the train line.
            section (str): Section of the track block.
            number (int): Block number.
            length (int): Length of the block in meters.
            grade (float): Grade of the block in percentage.
            speed_limit (int): Speed limit for the block in km/h.
            elevation (float): Elevation of the block in meters.
            cumulative_elevation (float): Cumulative elevation change up to
                this block in meters.
            infrastructure (str, optional): Infrastructure details like
                switches and crossings.
            station_side (str, optional): Side of the station if the block is
                near a station.
        
        Returns:
            None
        """

        super().__init__()

        # Parameters that are passed in by constructor
        self.line = line
        self.section = section
        self.number = number
        self.length = length
        self.grade = grade
        self.speed_limit = speed_limit
        self.elevation = elevation
        self.cumulative_elevation = cumulative_elevation
        self.infrastructure = infrastructure
        self.connecting_blocks = []
        self.station: Station = None
        self.station_side = station_side

        # Parameters that we determine
        self.suggested_speed = 0
        self.authority = 0
        self._occupancy = False
        self.switch_position = None
        self.crossing_signal = CrossingSignal.NA
        self._under_maintenance = False

    def __repr__(self) -> str:

        """
        Returns a string representation of the TrackBlock object.
        
        Returns:
            str: String representation of the TrackBlock object.
        """

        connecting_blocks = []
        if len(self.connecting_blocks) > 0:
            for connecting_block in self.connecting_blocks:
                connecting_blocks.append(connecting_block.number)

        return (
            f"Line:                         {self.line}\n"
            f"Block Section:                {self.section}\n"
            f"Block Number:                 {self.number}\n"
            f"Block Length:                 {self.length}\n"
            f"Block Grade:                  {self.grade}\n"
            f"Block Speed Limit:            {self.speed_limit}\n"
            f"Block Elevation:              {self.elevation}\n"
            f"Block Cumulative Elevation:   {self.cumulative_elevation}\n"
            f"Block Infrastructure:         {self.infrastructure}\n"
            f"Connecting Track Blocks:      {connecting_blocks}\n"
            f"Block Station:                {self.station.name}\n"
            f"Block Station Side:           {self.station_side}\n"
            f"Suggested Speed:              {self.authority}\n"
            f"Authority:                    {self.authority}\n"
            f"Occupancy:                    {self.occupancy}\n"
            f"Switch Position:              {self.switch_position}\n" 
            f"Crossing Signal:              {self.crossing_signal}\n"
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
    
    def set_suggested_speed(self, suggested_speed: int) -> None:

        """
        Sets the suggested speed for the track block.
        
        Args:
            suggested_speed (int): The suggested speed to set.
        
        Returns:
            None
        """

        self.suggested_speed = suggested_speed

    def set_authority(self, authority: int) -> None:

        """
        Sets the authority for the track block.
        
        Args:
            authority (int): The authority to set.
        
        Returns:
            None
        """

        self.authority = authority

    def set_switch_position(self, switch_position: object) -> None:

        """
        Sets the switch position for the track block.
        
        Args:
            switch_position (TrackBlock): The track block that the switch
            connects to.
        
        Returns:
            None
        
        Raises:
            TypeError: If the switch_position is not a TrackBlock.
        """

        if not isinstance(switch_position, TrackBlock):
            raise TypeError(
                f"Expected a TrackBlock object, but got {type(switch_position).__name__}"
            )
        self.switch_position = switch_position

    def set_crossing_signal(self, crossing_signal: CrossingSignal) -> None:

        """
        Sets the crossing signal status for the track block.
        
        Args:
            crossing_signal (CrossingSignal): The crossing signal status.
        
        Returns:
            None
        """

        self.crossing_signal = crossing_signal

    @property
    def occupancy(self):
        return self._occupancy

    @occupancy.setter
    def occupancy(self, value):
        if self._occupancy != value:
            self._occupancy = value
            self.occupancyChanged.emit()

    @property
    def under_maintenance(self):
        return self._under_maintenance

    @under_maintenance.setter
    def under_maintenance(self, value):
        self._under_maintenance = value
        self.maintenanceChanged.emit()