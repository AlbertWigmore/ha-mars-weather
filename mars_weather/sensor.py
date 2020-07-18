""" Mars Weather """
from datetime import timedelta

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_API_KEY
from homeassistant.helpers.entity import Entity

ATTRIBUTION = "Data provided by NASA API"
DEFAULT_NAME = "Mars Weather"
SCAN_INTERVAL = timedelta(hours=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    client = InsightClient(config.get(CONF_API_KEY))

    add_entities([InsightSensor(client)])


class InsightSensor(Entity):
    """ Mars Insight Sensor. """

    def __init__(self, client):
        """Initialize the sensor."""
        self._attributes = {}
        self._client = client
        self._state = None

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        sol, data = self._client.get_weather()

        self._state = sol
        self._attributes['first_utc'] = data[sol]['First_UTC']
        self._attributes['last_utc'] = data[sol]['Last_UTC']
        self._attributes['season'] = data[sol]['Season']
        self._attributes['avg_temp'] = data[sol]['AT']['av']
        self._attributes['avg_windspeed'] = data[sol]['HWS']['av']
        self._attributes['avg_pressure'] = data[sol]['PRE']['av']
        self._attributes['wind_direction'] = data[sol]['WD']['most_common']['compass_degrees']
        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION

    @property
    def device_state_attributes(self):
        """Return attributes for the sensor."""
        return self._attributes

    @property
    def name(self):
        """Return the name of the sensor."""
        return DEFAULT_NAME

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state


class InsightClient():
    """ Insight API Client """

    def __init__(self, api_key):
        """ Initialise """
        self.api_key = api_key

    def get_weather(self):
        """ Get Weather Data """
        r = requests.get(f"https://api.nasa.gov/insight_weather/?api_key={self.api_key}&feedtype=json&ver=1.0")
        #TODO - check valid response
        #TODO - check available data

        data = r.json()
        most_recent_sol = max(data['sol_keys'])

        return(most_recent_sol, data)
