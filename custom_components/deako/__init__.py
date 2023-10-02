"""The deako integration."""
from __future__ import annotations

import logging

from pydeako.deako import Deako, NoExpectedDevices
from pydeako.discover import DeakoDiscoverer

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up deako from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(
            DOMAIN,
            {},
        )

    _zc = await zeroconf.async_get_instance(hass)
    discoverer = DeakoDiscoverer(_zc)

    connection = Deako(discoverer.get_address)
    await connection.connect()
    try:
        await connection.find_devices()
    except NoExpectedDevices as exc:
        _LOGGER.warning("No devices expected")
        await connection.disconnect()
        raise ConfigEntryNotReady(exc) from exc

    devices = connection.get_devices()
    if len(devices) == 0:
        await connection.disconnect()
        raise ConfigEntryNotReady()

    hass.data[DOMAIN][entry.entry_id] = connection

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            hass.add_job(hass.config_entries.async_forward_entry_setup(entry, platform))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.data[DOMAIN][entry.entry_id].disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
