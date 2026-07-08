"""Button platform for Device Pulse."""

from custom_components.device_pulse.const import ENTITY_TAG_RESET_TOTAL_FAILED_PINGS

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory

from .base import BaseCoordinatorEntity


class DeviceResetTotalFailedPingsButton(BaseCoordinatorEntity, ButtonEntity):
    """Button that resets the total failed pings counter."""

    @property
    def _tag(self) -> str:
        """TAG for the button type."""
        return ENTITY_TAG_RESET_TOTAL_FAILED_PINGS

    @property
    def _name_suffix(self) -> str:
        """Suffix for the button name."""
        return "Reset Total Failed Pings"

    def _configure(self) -> None:
        """Additional initialization for the button."""
        self._attr_icon = "mdi:counter"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    async def async_press(self) -> None:
        """Handle the button press."""
        self.coordinator.reset_total_failed_pings(self.entity_id)
