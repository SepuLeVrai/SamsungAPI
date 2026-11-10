"""Binary sensor: screen is truly ON, not merely ping-responsive."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SamsungTVPowerCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create the screen-on sensor for one TV."""
    async_add_entities([SamsungTVScreenOnSensor(entry.runtime_data, entry)])


class SamsungTVScreenOnSensor(
    CoordinatorEntity[SamsungTVPowerCoordinator], BinarySensorEntity
):
    """ON only after the REST API has continuously reported ON."""

    _attr_has_entity_name = True
    _attr_translation_key = "screen_on"
    _attr_icon = "mdi:television"

    def __init__(self, coordinator: SamsungTVPowerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_screen_on"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=entry.title,
            manufacturer="Samsung",
            model="Tizen (REST PowerState)",
            configuration_url=f"http://{coordinator.host}:8001/api/v2/",
        )

    @property
    def is_on(self) -> bool | None:
        """Return confirmed screen state, or None if unsupported."""
        return self.coordinator.data.on

    @property
    def available(self) -> bool:
        """Do not claim an ON/OFF state if PowerState is unsupported."""
        return self.coordinator.data is not None and self.coordinator.data.on is not None

    @property
    def extra_state_attributes(self) -> dict:
        """Expose the raw REST observation for debugging."""
        return {
            "api_power_state": self.coordinator.data.api_state,
            "api_source": self.coordinator.data.source,
        }
