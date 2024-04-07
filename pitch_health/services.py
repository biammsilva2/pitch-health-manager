from os import getenv
from datetime import datetime, timedelta

from requests import get
from loguru import logger

from .schema import Pitch
from .constants import RainTimePerTurfType, TURF_DAMAGE_POINTS, \
                       MAINTENANCE_CUT_SCORE, TURF_REPLACEMENT_SCORE, \
                       DryingTimePerTurfType, MAINTENANCE_POINTS, \
                       MAINTENANCE_TIME


class WeatherService:
    url = 'https://weather.visualcrossing.com/' +\
          'VisualCrossingWebServices/rest/services/timeline'
    api_key = getenv('VISUAL_CROSSING_API_KEY')

    @classmethod
    def search_weather_from_last_maintenance(cls, pitch: Pitch) -> dict:
        if pitch.pitch_analyzed_last:
            initial_date = pitch.pitch_analyzed_last.date()
        else:
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
        logger.info(f"Pitch {pitch.id} - External weather API reached")
        max_precipitation_perc = 0
        for day in result.get('days'):
            precipitation_perc = day.get('precipcover')
            max_precipitation_perc = max(
                max_precipitation_perc,
                precipitation_perc
            )
        return int(0.24 * max_precipitation_perc)


class PitchHealth:

    @classmethod
    def check_turf_health(cls, pitch: Pitch) -> Pitch:
        # verify the time of last analysis to make it again
        # in case it rains again even after a maintenance was scheduled
        pitch_was_analyzed_today = False
        if pitch.pitch_analyzed_last is not None:
            pitch_was_analyzed_today = \
                pitch.pitch_analyzed_last.date() == datetime.now().date()
        if not pitch.need_to_change_turf and not pitch_was_analyzed_today:

            hours = WeatherService.calculate_rain_hours_from_last_maintanance(
                pitch
            )
            rain_cut_value = RainTimePerTurfType[pitch.turf_type].value
            if hours >= rain_cut_value:
                logger.info(f'Pitch {pitch.id} - turf has damaged by the rain')
                mulltiplicator = hours//rain_cut_value
                pitch.update_points(TURF_DAMAGE_POINTS*mulltiplicator*-1)
            if pitch.current_condition <= TURF_REPLACEMENT_SCORE:
                # require change of turf
                logger.info(f'Pitch {pitch.id} - require change of turf')
                pitch.need_to_change_turf = True
            elif pitch.current_condition < MAINTENANCE_CUT_SCORE:
                # require maintenance
                # WOULD_DO: check weather forecast for future rain
                logger.info(f'Pitch {pitch.id} - require maintenance')
                drying_time = DryingTimePerTurfType[pitch.turf_type].value
                pitch.next_scheduled_maintenance = \
                    datetime.now() + timedelta(hours=drying_time)
                pitch.pitch_analyzed_last = datetime.now()
        return pitch

    @classmethod
    def do_maintenance(cls, pitch: Pitch) -> Pitch:
        pitch.update_points(MAINTENANCE_POINTS)
        pitch.last_maintenance_date = datetime.now() + \
            timedelta(hours=MAINTENANCE_TIME)
        pitch.pitch_analyzed_last = None
        logger.info(f'Pitch {pitch.id} - maintenance made')
        return pitch

    @classmethod
    def change_turf(cls, pitch: Pitch) -> Pitch:
        pitch.current_condition = 10
        pitch.replacement_date = datetime.now()
        pitch.next_scheduled_maintenance = None
        pitch.need_to_change_turf = False
        pitch.pitch_analyzed_last = None
        logger.info(f'Pitch {pitch.id} - had turf change')
        return pitch
