"""The deako integration."""
from __future__ import annotations

import logging

from pydeako.deako import Deako, FindDevicesTimeout
from pydeako.discover import DeakoDiscoverer

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DISCOVERER_ID, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up deako from a config entry."""
    hass_data = hass.data.setdefault(DOMAIN, {})
    if hass_data is None or not isinstance(hass_data, dict):
        hass_data = {}
        hass.data[DOMAIN] = hass_data

    if hass_data.get(DISCOVERER_ID) is None:
        _zc = await zeroconf.async_get_instance(hass)
        _dd = DeakoDiscoverer(_zc)
        hass_data[DISCOVERER_ID] = _dd

    discoverer: DeakoDiscoverer = hass_data.get(DISCOVERER_ID)

    connection = Deako(discoverer.get_address)
    await connection.connect()
    try:
        await connection.find_devices()
    except FindDevicesTimeout as exc:
        _LOGGER.warning("No devices expected")
        await connection.disconnect()
        raise ConfigEntryNotReady(exc) from exc

    devices = connection.get_devices()
    if len(devices) == 0:
        await connection.disconnect()
        raise ConfigEntryNotReady(devices)

    hass.data[DOMAIN][entry.entry_id] = connection

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.data[DOMAIN][entry.entry_id].disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
