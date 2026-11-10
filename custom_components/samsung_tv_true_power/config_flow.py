"""UI config flow: one Samsung TV per entry."""

from __future__ import annotations

from ipaddress import IPv4Address, ip_address

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_LOST_CONNECTION_OFF_SECONDS,
    CONF_ON_CONFIRM_SECONDS,
    CONF_POLL_INTERVAL_SECONDS,
    DEFAULT_LOST_CONNECTION_OFF_SECONDS,
    DEFAULT_ON_CONFIRM_SECONDS,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DOMAIN,
)


class SamsungTVTruePowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up several TVs without requiring Samsung pairing."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Configure a TV using its fixed IPv4 address."""
        errors = {}
        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            name = str(user_input[CONF_NAME]).strip()
            try:
                address = ip_address(host)
                if (
                    not isinstance(address, IPv4Address)
                    or address.is_loopback
                    or address.is_multicast
                    or address.is_unspecified
                ):
                    raise ValueError("Not a usable TV IPv4 address")
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                if not name:
                    errors["base"] = "invalid_name"
                else:
                    host = str(address)
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=name,
                        data={CONF_HOST: host, CONF_NAME: name},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_NAME, default="Samsung TV"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Show sampling and confirmation settings per TV."""
        return SamsungTVTruePowerOptionsFlow()


class SamsungTVTruePowerOptionsFlow(config_entries.OptionsFlow):
    """Configure filtering without editing YAML or reinstalling."""

    async def async_step_init(self, user_input=None):
        """Update options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ON_CONFIRM_SECONDS,
                        default=self.config_entry.options.get(
                            CONF_ON_CONFIRM_SECONDS,
                            DEFAULT_ON_CONFIRM_SECONDS,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=180)),
                    vol.Required(
                        CONF_LOST_CONNECTION_OFF_SECONDS,
                        default=self.config_entry.options.get(
                            CONF_LOST_CONNECTION_OFF_SECONDS,
                            DEFAULT_LOST_CONNECTION_OFF_SECONDS,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                    vol.Required(
                        CONF_POLL_INTERVAL_SECONDS,
                        default=self.config_entry.options.get(
                            CONF_POLL_INTERVAL_SECONDS,
                            DEFAULT_POLL_INTERVAL_SECONDS,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=3, max=60)),
                }
            ),
        )
