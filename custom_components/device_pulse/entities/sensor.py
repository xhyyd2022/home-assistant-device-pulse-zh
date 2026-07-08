"""Sensor platform for Device Pulse."""

import logging

from custom_components.device_pulse.const import (
    ENTITY_ATTR_COUNT_STARTED_AT,
    ENTITY_TAG_PINGS_FAILED_COUNT,
    ENTITY_TAG_TOTAL_FAILED_PINGS_COUNT,
    ENTITY_TAG_DISCONNECTED_SINCE,
    ENTITY_TAG_LAST_RESPONSE_TIME,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.unit_conversion import UnitOfTime
from homeassistant.util import dt as dt_util

from .base import BaseCoordinatorEntity

_LOGGER = logging.getLogger(__name__)


class DeviceFailedPingsSensor(BaseCoordinatorEntity, SensorEntity):
    """Sensor that shows failed pings when device is offline."""

    @property
    def _tag(self) -> str:
        """TAG for the sensor type."""
        return ENTITY_TAG_PINGS_FAILED_COUNT

    @property
    def _name_suffix(self) -> str:
        """Suffix for the sensor name."""
        return "Failed Pings"

    def _configure(self) -> None:
        """Additional initialization for the sensor."""
        self._attr_icon = "mdi:alert-circle"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return failed pings count."""
        return self.coordinator.failed_pings


class DeviceTotalFailedPingsSensor(BaseCoordinatorEntity, SensorEntity, RestoreEntity):
    """Sensor that shows the total failed pings count."""

    @property
    def _tag(self) -> str:
        """TAG for the sensor type."""
        return ENTITY_TAG_TOTAL_FAILED_PINGS_COUNT

    @property
    def _name_suffix(self) -> str:
        """Suffix for the sensor name."""
        return "Total Failed Pings"

    def _configure(self) -> None:
        """Additional initialization for the sensor."""
        self._attr_icon = "mdi:counter"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        if last_state := await self.async_get_last_state():
            failed_pings_since_startup = self.coordinator.total_failed_pings
            try:
                restored_total = int(last_state.state)
            except (TypeError, ValueError):
                restored_total = 0

            self.coordinator.total_failed_pings = (
                restored_total + failed_pings_since_startup
            )

            self.coordinator.total_failed_pings_started_at = (
                last_state.attributes.get(ENTITY_ATTR_COUNT_STARTED_AT)
                or dt_util.now().isoformat()
            )

    @property
    def native_value(self):
        """Return total failed pings count."""
        return self.coordinator.total_failed_pings

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            **super().extra_state_attributes,
            ENTITY_ATTR_COUNT_STARTED_AT: self.coordinator.total_failed_pings_started_at,
        }


class DeviceDisconnectedSinceSensor(BaseCoordinatorEntity, SensorEntity):
    """Sensor that shows when device went offline."""

    @property
    def _tag(self) -> str:
        """TAG for the sensor type."""
        return ENTITY_TAG_DISCONNECTED_SINCE

    @property
    def _name_suffix(self) -> str:
        """Suffix for the sensor name."""
        return "Offline Since"

    def _configure(self) -> None:
        """Additional initialization for the sensor."""
        self._attr_icon = "mdi:clock-alert"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        """Return offline since timestamp."""
        return (
            self.coordinator.failed_started_at
            if not self.coordinator.data.is_alive
            else None
        )


class DeviceLastResponseTimeSensor(BaseCoordinatorEntity, SensorEntity):
    """Sensor that shows last ping response time when online."""

    @property
    def _tag(self) -> str:
        """TAG for the sensor type."""
        return ENTITY_TAG_LAST_RESPONSE_TIME

    @property
    def _name_suffix(self) -> str:
        """Suffix for the sensor name."""
        return "Last Response Time"

    def _configure(self) -> None:
        """Additional initialization for the sensor."""
        self._attr_icon = "mdi:speedometer"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_native_unit_of_measurement = UnitOfTime.MILLISECONDS

    @property
    def native_value(self):
        """Return last response time only when online."""
        if (
            self.coordinator.data.is_alive
            and self.coordinator.last_response_time is not None
        ):
            return self.coordinator.last_response_time

        return None
