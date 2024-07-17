"""Config flow for deako."""

import logging
from typing import Any

from pydeako.deako import Deako, DeviceListTimeout, FindDevicesTimeout
from pydeako.discover import DeakoDiscoverer, DevicesNotFoundException
import voluptuous as vol

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from .const import ADDRESS, CONNECTION, DEFAULT_PORT, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DeakoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Deako integration config flow."""

    VERSION = 1
    connection: Deako | None = None

    address: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if user_input is None:
            return self._async_show_setup_form()

        await self.async_set_unique_id(DOMAIN)
        host = user_input.get(CONF_HOST)
        if host is not None:
            self.address = f"{host}:{DEFAULT_PORT}"
            self._abort_if_unique_id_configured(
                updates={ADDRESS: self.address},
                reload_on_update=True,
            )
        else:
            self._abort_if_unique_id_configured()

        return await self._finalize()

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        # only one instance of deako integration should exist, device is a bridge
        if self.hass.data.get(DOMAIN) is not None:
            return self.async_abort(reason="already_configured")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        self._set_confirm_only()
        return self.async_show_form(
            step_id="zeroconf_confirm",
        )

    async def async_step_zeroconf_confirm(
        self, _: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by zeroconf."""
        return await self._finalize()

    @callback
    def _async_create_entry(self) -> ConfigFlowResult:
        data: dict[str, Any] = {}

        if self.address is not None:
            data[ADDRESS] = self.address

        self.hass.data.setdefault(
            DOMAIN,
            {
                CONNECTION: self.connection,  # let setup reuse connection
            },
        )

        return self.async_create_entry(
            title="Deako integration",
            data=data,
        )

    @callback
    def _async_show_setup_form(
        self, errors: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOST): str,
                }
            ),
            errors=errors or {},
        )

    async def _finalize(self) -> ConfigFlowResult:
        if self.address is not None:
            address = self.address

            async def get_address() -> str:
                return address
        else:
            _zc = await zeroconf.async_get_instance(self.hass)
            discoverer = DeakoDiscoverer(_zc)
            get_address = discoverer.get_address

        connection = Deako(get_address)

        try:
            await connection.connect()
            await connection.find_devices()
            self.connection = connection
        except (DevicesNotFoundException, DeviceListTimeout, FindDevicesTimeout) as exc:
            _LOGGER.error(exc)
            await connection.disconnect()
            await self.async_set_unique_id()
            return self.async_abort(reason="cannot_connect")

        return self._async_create_entry()
