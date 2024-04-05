from os import getenv
from datetime import datetime, timedelta

from requests import get

from .schema import Pitch
from .constants import RainTimePerTurfType, TURF_DAMAGE_POINTS, \
                       MAINTENANCE_CUT_SCORE, TURF_REPLACEMENT_SCORE, \
                       DryingTimePerTurfType, MAINTENANCE_POINTS


class WeatherService:
    url = 'https://weather.visualcrossing.com/' +\
          'VisualCrossingWebServices/rest/services/timeline'
    api_key = getenv('VISUAL_CROSSING_API_KEY')

    @classmethod
    def search_weather_from_last_maintenance(cls, pitch: Pitch) -> dict:
        initial_date = pitch.last_maintenance_date.date()
        end_date = datetime.now().date()
        result = get(
            f'{cls.url}/{pitch.location.city}/{initial_date}/{end_date}',
            params={'key': cls.api_key}
        )
        if result.ok:
            return result.json()
        raise ValueError('Weather API unreachable, check if API Key is set')

    @classmethod
    def calculate_rain_hours_from_last_maintanance(cls, pitch: Pitch) -> int:
        '''
        Precipitation Coverage

        This is the proportion of time for which measurable
        precipitation was recorded during the time period,
        expressed as a percentage. For example, if within a 24
        hour day there are six hours of measurable rainfall,
        the precipitation coverage is 25% (6/24*100). This
        information is only available for historical weather
        observation data and historical summaries.

        That means that hours of rain is equal to:
        24 * precipitation_percentage / 100
        which is equal to 0.24 * precipitation_percentage
        '''
        result = cls.search_weather_from_last_maintenance(
            pitch
        )
        max_precipitation_perc = 0
        for day in result.get('days'):
            precipitation_perc = day.get('precipcover')
            max_precipitation_perc = max(
                max_precipitation_perc,
                precipitation_perc
            )
        return 0.24 * max_precipitation_perc


class PitchHealth:

    @classmethod
    def check_turf_health(cls, pitch: Pitch) -> None:
        if not pitch.need_to_change_turf:
            hours = WeatherService.calculate_rain_hours_from_last_maintanance(
                pitch
            )
            rain_cut_value = RainTimePerTurfType[pitch.turf_type].value
            if hours >= rain_cut_value:
                mulltiplicator = hours//rain_cut_value
                pitch.update_points(TURF_DAMAGE_POINTS*mulltiplicator*-1)
            if pitch.current_condition <= TURF_REPLACEMENT_SCORE:
                pitch.need_to_change_turf = True
            elif pitch.current_condition < MAINTENANCE_CUT_SCORE:
                # require maintenance
                # TODO: check weather forecast for future rain
                drying_time = DryingTimePerTurfType[pitch.turf_type].value
                pitch.next_scheduled_maintenance = \
                    datetime.now() + timedelta(hours=drying_time)
            pitch.save()
        return pitch

    @classmethod
    def do_maintenance(cls, pitch: Pitch) -> None:
        pitch.update_points(MAINTENANCE_POINTS)
        pitch.last_maintenance_date = datetime.now()
        pitch.save()

    @classmethod
    def change_turf(cls, pitch: Pitch) -> None:
        pitch.current_condition = 10
        pitch.replacement_date = datetime.now()
        pitch.next_scheduled_maintenance = None
        pitch.save()
    
    @classmethod
    def analyze_all_pitches(cls):
        pass
