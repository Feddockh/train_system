# train_system/common/__init__.py

PACKAGE_VERSION = "1.0"

from .train import Train
from .track import Track

__all__ = ['Train', 'Track']

print("common has been initialized")
