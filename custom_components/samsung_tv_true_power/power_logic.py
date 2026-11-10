"""Pure parser and power-state filter (no Home Assistant dependency).

A reachable IP address is never evidence that the screen is on.
Only an explicit REST device.PowerState="on" can turn on the sensor.
"""

from __future__ import annotations

KNOWN_OFF = frozenset({"standby", "off", "poweroff"})


def parse_power_state(payload: object) -> str:
    """Extract the normalized PowerState, otherwise mark it unsupported."""
    if not isinstance(payload, dict):
        return "unsupported"
    device = payload.get("device")
    if not isinstance(device, dict):
        return "unsupported"
    value = device.get("PowerState")
    if not isinstance(value, str):
        return "unsupported"
    normalized = value.strip().lower()
    if normalized == "on" or normalized in KNOWN_OFF:
        return normalized
    return "unsupported"


class PowerFilter:
    """Debounce ON, immediately accept standby and handle disconnections.

    For the LED use case, extended loss of API connectivity eventually
    produces presumed OFF (not a confirmed screen state); diagnostics
    distinguish this from an explicit standby response.
    """

    def __init__(self, on_confirm_seconds: int, offline_off_seconds: int) -> None:
        self.on_confirm_seconds = on_confirm_seconds
        self.offline_off_seconds = offline_off_seconds
        self.on: bool | None = None
        self._on_since: float | None = None
        self._unreachable_since: float | None = None

    def update(self, state: str, now: float) -> bool | None:
        """Consume a REST observation at monotonic time 'now'."""
        if state == "on":
            self._unreachable_since = None
            if self._on_since is None:
                self._on_since = now
            if self.on is None:
                self.on = False
            if now - self._on_since >= self.on_confirm_seconds:
                self.on = True

        elif state in KNOWN_OFF:
            self._unreachable_since = None
            self._on_since = None
            self.on = False

        elif state == "unreachable":
            self._on_since = None
            if self._unreachable_since is None:
                self._unreachable_since = now
            if now - self._unreachable_since >= self.offline_off_seconds:
                self.on = False

        else:
            # API reachable but unable to report PowerState: do not guess.
            self._on_since = None
            self._unreachable_since = None
            self.on = None

        return self.on
