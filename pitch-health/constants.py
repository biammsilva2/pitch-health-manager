from enum import Enum


MAINTENANCE_POINTS = 4
MAINTENANCE_TIME = 6  # hours
TURF_REPLACEMENT_SCORE = 2
TURF_DAMAGE_POINTS = 2
MAINTENANCE_CUT_SCORE = 10


class RainTimePerTurfType(Enum):
    artificial = 6
    hybrid = 4
    natural = 3


class DryingTimePerTurfType(Enum):
    artificial = 12
    hybrid = 24
    natural = 36
