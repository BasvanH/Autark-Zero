"""Simple enum class."""
from enum import Enum


class Strategy(Enum):
    """Can be used for tacking computations."""
    NO_TACKING = 0
    TACKING = 1
    TACKING_ANGLE_LEFT = 0
    TACKING_ANGLE_RIGHT = 0
