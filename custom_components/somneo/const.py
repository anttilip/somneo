
from homeassistant.const import (UnitOfTemperature, PERCENTAGE, LIGHT_LUX, UnitOfSoundPressure)
from typing import Final

DOMAIN: Final = 'somneo'
VERSION: Final = "0.3"

DEFAULT_NAME: Final = "Somneo"

CONF_SENS: Final = 'sensors'

ALARM: Final = 'alarm'
PW: Final = 'powerwake'
ALARMS: Final = 'alarms'
HOURS: Final = 'hours'
MINUTES: Final = 'minutes'
WORKDAYS: Final = 'workdays'
WEEKEND: Final = 'weekend'
TOMORROW: Final = 'tomorrow'
EVERYDAY: Final = 'daily'
UNKNOWN: Final = 'unknown'
PW_DELTA: Final = 'powerwake_delta'

ALARMS_ICON: Final = 'hass:alarm'
PW_ICON: Final = 'hass:alarm-plus'
HOURS_ICON: Final = 'hass:counter'
MINUTES_ICON: Final = 'hass:counter'
WORKDAYS_ICON: Final = 'hass:calendar-range'
WEEKEND_ICON: Final = 'hass:calendar-range'

ATTR_ALARM: Final = 'alarm'
ATTR_CURVE: Final = 'curve'
ATTR_LEVEL: Final = 'level'
ATTR_DURATION: Final = 'duration'
ATTR_SOURCE: Final = 'source'
ATTR_CHANNEL: Final = 'channel'


SENSORS: Final = {'temperature': UnitOfTemperature.CELSIUS, 'humidity': PERCENTAGE, 'luminance': LIGHT_LUX, 'noise': UnitOfSoundPressure.DECIBEL}

NOTIFICATION_ID: Final = "somneosensor_notification"
NOTIFICATION_TITLE: Final = "SomneoSensor Setup"



