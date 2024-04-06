import json
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from .services import WeatherService, PitchHealth
from .schema import Pitch, PitchLocation, TurfType
from .constants import MAINTENANCE_TIME


class PitchHealthTest(TestCase):

    def setUp(self) -> None:
        now = datetime.now()
        self.pitch = Pitch(
            name="test pitch",
            location=PitchLocation(
                city='berlin', country='Germany'
            ),
            turf_type=TurfType.artificial,
            last_maintenance_date=now-timedelta(days=4),
            next_scheduled_maintenance=now,
            current_condition=5,
            replacement_date=now-timedelta(days=6),
            need_to_change_turf=False,
            pitch_analyzed_last=now-timedelta(days=6)
        )
        return super().setUp()

    @patch.object(WeatherService, 'search_weather_from_last_maintenance')
    def test_rain_hours_from_last_maintenance(self, weather_method_mock):
        mock_data_file = open('./mock_data.json')
        mock_data = json.load(mock_data_file)
        weather_method_mock.return_value = mock_data
        rain_hours = WeatherService.calculate_rain_hours_from_last_maintanance(
            self.pitch
        )
        assert rain_hours == 7

    @patch.object(WeatherService, 'search_weather_from_last_maintenance')
    def test_get_mock_weather_data(self, weather_method_mock):
        '''For testing external api calls I implemented a service mock
           using unnittest.mock'''
        mock_data_file = open('./mock_data.json')
        mock_data = json.load(mock_data_file)
        weather_method_mock.return_value = mock_data
        data = WeatherService.search_weather_from_last_maintenance()
        assert data == mock_data

    def test_pitch_made_maintenance(self):
        now = datetime.now()
        pitch = self.pitch
        PitchHealth.do_maintenance(pitch)
        assert pitch.last_maintenance_date.date() == \
            (now+timedelta(hours=MAINTENANCE_TIME)).date()
        assert pitch.current_condition == 9
        assert pitch.pitch_analyzed_last is None

    def test_pitch_turf_replaced(self):
        today = datetime.now().date()
        pitch = self.pitch
        PitchHealth.change_turf(pitch)
        assert pitch.current_condition == 10
        assert pitch.replacement_date.date() == today
        assert pitch.next_scheduled_maintenance is None
        assert pitch.pitch_analyzed_last is None
        assert pitch.need_to_change_turf is False

    @patch.object(WeatherService, 'search_weather_from_last_maintenance')
    def test_check_turf_health_pitch_analyzed_today(self, weather_method_mock):
        mock_data_file = open('./mock_data.json')
        mock_data = json.load(mock_data_file)
        weather_method_mock.return_value = mock_data

        today = datetime.now().date()
        self.pitch.pitch_analyzed_last = datetime.now()
        PitchHealth.check_turf_health(self.pitch)
        assert self.pitch.pitch_analyzed_last.date() == today

    @patch.object(WeatherService, 'search_weather_from_last_maintenance')
    def test_check_turf_health_need_maintenance(self, weather_method_mock):
        mock_data_file = open('./mock_data.json')
        mock_data = json.load(mock_data_file)
        weather_method_mock.return_value = mock_data

        self.pitch.current_condition = 10
        PitchHealth.check_turf_health(self.pitch)
        assert self.pitch.current_condition == 8

    @patch.object(WeatherService, 'search_weather_from_last_maintenance')
    def test_check_turf_health_need_change_turf(self, weather_method_mock):
        mock_data_file = open('./mock_data.json')
        mock_data = json.load(mock_data_file)
        weather_method_mock.return_value = mock_data

        self.pitch.current_condition = 4
        PitchHealth.check_turf_health(self.pitch)
        assert self.pitch.current_condition == 2
        assert self.pitch.need_to_change_turf is True

    def test_points_more_than_10(self):
        self.pitch.current_condition = 10
        PitchHealth.do_maintenance(self.pitch)
        assert self.pitch.current_condition == 10

    @patch.object(WeatherService, 'search_weather_from_last_maintenance')
    def test_points_less_than_1(self, weather_method_mock):
        mock_data_file = open('./mock_data.json')
        mock_data = json.load(mock_data_file)
        weather_method_mock.return_value = mock_data

        self.pitch.current_condition = 2
        PitchHealth.check_turf_health(self.pitch)
        assert self.pitch.current_condition == 1
