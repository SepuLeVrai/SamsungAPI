"""Constants for Samsung TV Local Power."""

from homeassistant.const import Platform

DOMAIN = "samsung_tv_true_power"
PLATFORMS = (Platform.BINARY_SENSOR, Platform.SENSOR)

CONF_ON_CONFIRM_SECONDS = "on_confirm_seconds"
CONF_LOST_CONNECTION_OFF_SECONDS = "lost_connection_off_seconds"
CONF_POLL_INTERVAL_SECONDS = "poll_interval_seconds"

DEFAULT_ON_CONFIRM_SECONDS = 15
DEFAULT_LOST_CONNECTION_OFF_SECONDS = 30
DEFAULT_POLL_INTERVAL_SECONDS = 5
