"""Platform for switch integration. (on/off alarms & on/off alarms on workdays and/or weekends"""
import logging
from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import ATTR_CHANNEL, DOMAIN, ATTR_LEVEL, ATTR_CURVE, ATTR_DURATION, ATTR_SOURCE, ALARMS_ICON, PW_ICON
from .entity import SomneoEntity


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data['dev_info']  

    alarms = []
    pw = []
    for alarm in list(coordinator.data['alarms']):
        alarms.append(SomneoAlarmToggle(coordinator, unique_id, name, device_info, alarm))
        pw.append(SomneoPowerWakeToggle(coordinator, unique_id, name, device_info, alarm))   

    async_add_entities(alarms, True)
    async_add_entities(pw, True)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        'set_light_alarm',
        {
            vol.Optional(ATTR_CURVE): cv.string, 
            vol.Optional(ATTR_LEVEL): cv.positive_int, 
            vol.Optional(ATTR_DURATION): cv.positive_int, 
        },
        'set_light_alarm'
    )

    platform.async_register_entity_service(
        'set_sound_alarm',
        {
            vol.Optional(ATTR_SOURCE): cv.string, 
            vol.Optional(ATTR_LEVEL): cv.positive_int, 
            vol.Optional(ATTR_CHANNEL): cv.string, 
        },
        'set_sound_alarm'
    )

    platform.async_register_entity_service(
        'remove_alarm',
        {},
        'remove_alarm'
    )

    platform.async_register_entity_service(
        'add_alarm',
        {},
        'add_alarm'
    )

    platform.async_register_entity_service(
        'set_powerwake',
        {
            vol.Optional('state'): cv.boolean,
            vol.Optional('delta'): cv.positive_int,
        },
        'set_powerwake'
    )

class SomneoAlarmToggle(SomneoEntity, SwitchEntity):
    _attr_icon = ALARMS_ICON
    _attr_should_poll = True

    def __init__(self, coordinator, unique_id, name, device_info, alarm):
        """Initialize the switches. """
        super().__init__(coordinator, unique_id, name, device_info, alarm)

        self._attr_name = alarm.capitalize()
        self._alarm = alarm

    @property
    def is_on(self) -> bool:
        """Return the state of the device."""
        return self.coordinator.data['alarms'][self._alarm]

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes of the sensor."""
        return {'hour': self.coordinator.data['alarms_hour'][self._alarm],
            'minute': self.coordinator.data['alarms_minute'][self._alarm],
            'day': self.coordinator.data['alarms_day'][self._alarm],
            'powerwake': self.coordinator.data['powerwake'][self._alarm],
            'powerwake_delta': self.coordinator.data['powerwake_delta'][self._alarm]}
        
    async def async_turn_on(self, **kwargs: Any):
        """Called when user Turn On the switch from UI."""
        await self.coordinator.async_toggle_alarm(self._alarm, True)

    async def async_turn_off(self, **kwargs: Any):
        """Called when user Turn Off the switch from UI."""
        await self.coordinator.async_toggle_alarm(self._alarm, False)

    # Define service-calls
    async def set_light_alarm(self, curve: str = 'sunny day', level: int = 20, duration: int = 30):
        """Adjust the light settings of an alarm."""
        await self.coordinator.async_set_light_alarm(self._alarm, curve = curve, level = level, duration = duration)

    async def set_sound_alarm(self, source: str = 'wake-up', level: int = 12, channel: str = 'forest birds'):
        """Adjust the sound settings of an alarm."""
        await self.coordinator.async_set_sound_alarm(self._alarm, source = source, level = level, channel = channel)

    async def remove_alarm(self):
        """Function to remove alarm from list in wake-up app"""
        await self.coordinator.async_remove_alarm(self._alarm)

    async def add_alarm(self):
        """Function to add alarm to list in wake-up app"""
        await self.coordinator.async_add_alarm(self._alarm)

    async def set_powerwake(self, state: bool, delta: int = 10):
        """Adjust the powerwake settings of an alarm."""
        await self.coordinator.async_set_powerwake(self._alarm, state, delta = delta)

class SomneoPowerWakeToggle(SomneoEntity, SwitchEntity):
    _attr_icon = PW_ICON
    _attr_should_poll = True

    def __init__(self, coordinator, unique_id, name, device_info, alarm):
        """Initialize the switches. """
        super().__init__(coordinator, unique_id, name, device_info, alarm + '_PW')

        self._attr_name = alarm.capitalize() + ' powerwake'
        self._alarm = alarm

    @property
    def is_on(self) -> bool:
        """Return the state of the device."""
        return self.coordinator.data['powerwake'][self._alarm]

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes of the sensor."""
        return {'powerwake_delta': self.coordinator.data['powerwake_delta'][self._alarm]}
        
    async def async_turn_on(self, **kwargs: Any):
        """Called when user Turn On the switch from UI."""
        await self.coordinator.async_toggle_powerwake(self._alarm, True)

    async def async_turn_off(self, **kwargs: Any):
        """Called when user Turn Off the switch from UI."""
        await self.coordinator.async_toggle_powerwake(self._alarm, False)