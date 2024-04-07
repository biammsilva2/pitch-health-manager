from enum import Enum


WEATHER_API_URL = 'https://weather.visualcrossing.com/' +\
          'VisualCrossingWebServices/rest/services/timeline'


# how much points increased by maintenance
MAINTENANCE_POINTS = 4

# hours for the maintenance to take place
MAINTENANCE_TIME = 6

# how many points is time to change turf
TURF_REPLACEMENT_SCORE = 2

# how much points should be decreased when
# damaged by rain
TURF_DAMAGE_POINTS = 2

# score when turf is perfect
MAINTENANCE_CUT_SCORE = 10


# how much time it takes to damage the turf
# by turf type
class RainTimePerTurfType(Enum):
    artificial = 6
    hybrid = 4
    natural = 3


# how much time it takes to dry the turf
# by turf type
class DryingTimePerTurfType(Enum):
    artificial = 12
    hybrid = 24
    natural = 36
