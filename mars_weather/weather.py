""" Mars Weather """
from datetime import timedelta

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    PLATFORM_SCHEMA,
    WeatherEntity,
)
from homeassistant.const import (
    CONF_API_KEY,
    TEMP_FAHRENHEIT,
)


ATTRIBUTION = 'Data provided by NASA API'
DEFAULT_NAME = 'Mars Weather'
ICON = 'mdi:satellite-uplink'
SCAN_INTERVAL = timedelta(hours=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    client = InsightClient(config.get(CONF_API_KEY))

    add_entities([InsightWeather(client)])



class InsightWeather(WeatherEntity):
    """ Mars Insight Weather """

    def __init__(self, client):
        self._client = client
        self._data = None

        self._sol = None
        self._temperature = None
        self._pressure = None
        self._wind_speed = None
        self._wind_bearing = None
        self.update()

    @property
    def name(self):
        """ Return name of Weather sensor. """
        return "Mars Weather"

    @property
    def condition(self):
        """ Return the current condition """
        return f'Sol {self._sol}'

    @property
    def temperature(self):
        """ Return the temperature. """
        return self._temperature

    @property
    def temperature_unit(self):
        """ Return the unit of measurement. """
        return TEMP_FAHRENHEIT

    @property
    def pressure(self):
        """ Return the pressure. """
        return self._pressure

    @property
    def humidity(self):
        """ Return the Humidity. """
        return None

    @property
    def wind_speed(self):
        """ Return the wind speed. """
        return self._wind_speed

    @property
    def wind_bearing(self):
        """ Return the wind bearing. """
        return self._wind_bearing

    @property
    def attribution(self):
        """ Return the attribution. """
        return ATTRIBUTION

    def update(self):
        """ Get the latest data from Mars InSight. """
        sol, data = self._client.get_weather()

        self._sol = sol
        self._temperature = data[sol]['AT']['av']
        self._pressure = data[sol]['PRE']['av']
        self._wind_speed = data[sol]['HWS']['av']
        self._wind_direction = data[sol]['WD']['most_common']['compass_degrees']


class InsightClient():
    """ Insight API Client """

    def __init__(self, api_key):
        """ Initialise """
        self.api_key = api_key

    def get_weather(self):
        """ Get Weather Data """
        r = requests.get(f'https://api.nasa.gov/insight_weather/?api_key={self.api_key}&feedtype=json&ver=1.0')
        #TODO - check valid response
        #TODO - check available data

        data = r.json()
        most_recent_sol = max(data['sol_keys'])

        return(most_recent_sol, data)
