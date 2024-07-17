"""The deako integration."""

from __future__ import annotations

import logging

from pydeako.deako import Deako, DeviceListTimeout, FindDevicesTimeout
from pydeako.discover import DeakoDiscoverer, DevicesNotFoundException

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import ADDRESS, CONNECTION, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up deako."""
    # reuse connection from discovery if it exists
    connection = (hass.data.get(DOMAIN) or {}).get(CONNECTION)

    if connection is None:
        address = entry.data.get(ADDRESS)
        if address is not None:

            async def get_address() -> str:
                assert isinstance(address, str)
                return address
        else:
            _zc = await zeroconf.async_get_instance(hass)
            discoverer = DeakoDiscoverer(_zc)
            get_address = discoverer.get_address

        connection = Deako(get_address)

        try:
            await connection.connect()
            await connection.find_devices()
        except (DevicesNotFoundException, DeviceListTimeout, FindDevicesTimeout) as exc:
            await connection.disconnect()
            raise ConfigEntryNotReady(exc) from exc

    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][CONNECTION] = connection

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.data[DOMAIN][CONNECTION].disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data.pop(DOMAIN)

    return unload_ok
