"""Poll the local Samsung Tizen REST API (no WebSocket pairing)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging
from time import monotonic

from aiohttp import ClientError, ClientTimeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_LOST_CONNECTION_OFF_SECONDS,
    CONF_ON_CONFIRM_SECONDS,
    CONF_POLL_INTERVAL_SECONDS,
    DEFAULT_LOST_CONNECTION_OFF_SECONDS,
    DEFAULT_ON_CONFIRM_SECONDS,
    DEFAULT_POLL_INTERVAL_SECONDS,
)
from .power_logic import PowerFilter, parse_power_state

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TvPowerSnapshot:
    """Confirmed state, last raw REST value and connection source."""

    on: bool | None
    api_state: str
    source: str | None


class SamsungTVPowerCoordinator(DataUpdateCoordinator[TvPowerSnapshot]):
    """Read PowerState periodically, with no cloud or access token."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host: str = entry.data["host"]
        self._filter = PowerFilter(
            on_confirm_seconds=entry.options.get(
                CONF_ON_CONFIRM_SECONDS, DEFAULT_ON_CONFIRM_SECONDS
            ),
            offline_off_seconds=entry.options.get(
                CONF_LOST_CONNECTION_OFF_SECONDS,
                DEFAULT_LOST_CONNECTION_OFF_SECONDS,
            ),
        )
        poll_interval = entry.options.get(
            CONF_POLL_INTERVAL_SECONDS, DEFAULT_POLL_INTERVAL_SECONDS
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"Samsung TV Power {entry.title}",
            update_interval=timedelta(seconds=poll_interval),
        )

    async def _read_rest_power(self) -> tuple[str, str | None]:
        """Read the confirmed HTTP:8001 endpoint, including in standby."""
        session = async_get_clientsession(self.hass)
        url = f"http://{self.host}:8001/api/v2/"
        try:
            async with session.get(
                url, timeout=ClientTimeout(total=3)
            ) as response:
                if response.status != 200:
                    return "unsupported", "http:8001"
                payload = await response.json(content_type=None)
                return parse_power_state(payload), "http:8001"
        except (ClientError, asyncio.TimeoutError, OSError, ValueError):
            return "unreachable", None

    async def _async_update_data(self) -> TvPowerSnapshot:
        """Publish filtered ON/OFF and the underlying REST diagnostics."""
        api_state, source = await self._read_rest_power()
        is_on = self._filter.update(api_state, monotonic())
        return TvPowerSnapshot(on=is_on, api_state=api_state, source=source)
