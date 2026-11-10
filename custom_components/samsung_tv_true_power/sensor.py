"""Diagnostic entity: raw API state (on/standby/unreachable/unsupported)."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SamsungTVPowerCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create a diagnostic sensor per TV."""
    async_add_entities([SamsungTVApiStateSensor(entry.runtime_data, entry)])


class SamsungTVApiStateSensor(
    CoordinatorEntity[SamsungTVPowerCoordinator], SensorEntity
):
    """Show REST PowerState without mistaking network activity for power."""

    _attr_has_entity_name = True
    _attr_translation_key = "api_status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:api"

    def __init__(self, coordinator: SamsungTVPowerCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_api_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=entry.title,
            manufacturer="Samsung",
            model="Tizen (REST PowerState)",
        )

    @property
    def native_value(self) -> str:
        """Return unfiltered REST diagnostic."""
        return self.coordinator.data.api_state

    @property
    def extra_state_attributes(self) -> dict:
        """Include filter output to distinguish assumed OFF from standby."""
        return {
            "api_source": self.coordinator.data.source,
            "tv_on_confirmed": self.coordinator.data.on,
        }
