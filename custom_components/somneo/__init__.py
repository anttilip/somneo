""" Support for Philips Somneo devices."""
from __future__ import annotations

from datetime import timedelta, datetime
import logging
import asyncio

from pysomneo import Somneo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UNKNOWN, WEEKEND, WORKDAYS, TOMORROW, EVERYDAY

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.NUMBER, Platform.SELECT, Platform.SENSOR, Platform.SWITCH]
SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the Somneo component."""
    host = entry.data[CONF_HOST]
    
    coordinator = SomneoCoordinator(hass, host)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class SomneoCoordinator(DataUpdateCoordinator[None]):
    """Representation of a Somneo Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
    ) -> None:
        """Initialize Somneo client."""
        self.somneo = Somneo(host)
        self.state_lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self._async_update,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )

    async def _async_update(self):
        """Fetch the latest data."""
        if self.state_lock.locked():
            return

        return await self.hass.async_add_executor_job(self.somneo.fetch_data)

    async def async_turn_on_light(self, brightness) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_light, True, brightness)
            await self.async_request_refresh()

    async def async_turn_off_light(self) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_light, False)
            await self.async_request_refresh()

    async def async_turn_on_nightlight(self) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_night_light, True)
            await self.async_request_refresh()

    async def async_turn_off_nightlight(self) -> None:
        """Turn the device on."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_night_light, False)
            await self.async_request_refresh()

    async def async_toggle_alarm(self, alarm: str, state: bool) -> None:
        """Toggle alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_alarm, alarm, state)
            await self.async_request_refresh()

    def set_powerwake(self, alarm: str, state: bool, delta: int):
        """Toggle powerwake (default 10 minutes)"""
        self.somneo.set_powerwake(alarm, onoff=state, delta=delta)

    async def async_toggle_powerwake(self, alarm: str, state: bool):
        """Toggle powerwake (default 10 minutes)"""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.set_powerwake, alarm, state, 10)
            await self.async_request_refresh()

    def set_alarm(self, alarm: str, hour: int | None, minute: int | None) -> None:
        """Set alarm time."""
        self.somneo.set_alarm(alarm, hour = hour, minute = minute)
        
    async def async_set_alarm(self, alarm: str, hours: int | None = None, minutes: int | None = None):
        """Set alarm time."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.set_alarm, alarm, hours, minutes)
            await self.async_request_refresh()

    async def async_set_powerwake(self, alarm: str, state: bool, delta: int):
        """Set powerwake time"""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.set_powerwake, alarm, state, delta)
            await self.async_request_refresh()

    async def async_set_snooze_time(self, time):
        """Set snooze time."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.set_snooze_time, int(time))
            await self.async_request_refresh()

    async def async_set_alarm_day(self, alarm, day):
        """Set the day of the alarm."""
        async with self.state_lock:
            if day == WORKDAYS:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_workdays, alarm)
                _LOGGER.debug('Optie is werkday')
            elif day == WEEKEND:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_weekend, alarm)
                _LOGGER.debug('Optie is weekend')
            elif day == TOMORROW:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_tomorrow, alarm)
                _LOGGER.debug('Optie is morgen')
            elif day == EVERYDAY:
                await self.hass.async_add_executor_job(self.somneo.set_alarm_everyday, alarm)
                _LOGGER.debug('Optie is elke dag')

            await self.async_request_refresh()

    def set_light_alarm(self, alarm: str, curve: str, level: int, duration: int) -> None:
        """Adjust the light settings of an alarm."""
        self.somneo.set_light_alarm(
                alarm,
                curve = curve, 
                level = level, 
                duration = duration
                )

    async def async_set_light_alarm(self, alarm: str, curve: str = 'sunny day', level: int = 20, duration: int = 30):
        """Adjust the light settings of an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.set_light_alarm,
                alarm,
                curve, 
                level, 
                duration
                )

    def set_sound_alarm(self, alarm: str, source: str, level: int, channel: str):
        """Adjust the sound settings of an alarm."""
        self.somneo.set_sound_alarm(
            alarm, 
            source = source, 
            level = level, 
            channel = channel
            )

    async def async_set_sound_alarm(self, alarm: str, source = 'wake-up', level = 12, channel = 'forest birds'):
        """Adjust the sound settings of an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.set_sound_alarm,
                alarm, 
                source, 
                level, 
                channel
                )

    async def async_remove_alarm(self, alarm: str):
        """Function to remove alarm from list in wake-up app"""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.remove_alarm, alarm)

    async def async_add_alarm(self, alarm: str):
        """Function to add alarm to list in wake-up app"""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.add_alarm, alarm)

