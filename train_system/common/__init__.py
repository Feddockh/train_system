# train_system/common/__init__.py

PACKAGE_VERSION = "1.0"

from .track_block import TrackBlock
from .dispatch_mode import DispatchMode

__all__ = ['TrackBlock', 'DispatchMode']

print("common has been initialized")
