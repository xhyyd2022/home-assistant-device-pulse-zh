"""Button platform for Device Pulse."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ConfigEntryRuntimeData
from .const import (
    CONF_ENTRY_TYPE,
    CONF_SENSORS_TOTAL_FAILED_PINGS_ENABLED,
    DEFAULT_SENSORS_TOTAL_FAILED_PINGS_ENABLED,
    ENTRY_TYPE_NETWORK_SUMMARY,
)
from .entities import DeviceResetTotalFailedPingsButton
from .utils import remove_config_entry_orphan_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry[ConfigEntryRuntimeData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    if config_entry.data.get(CONF_ENTRY_TYPE) == ENTRY_TYPE_NETWORK_SUMMARY:
        return

    entities = []
    if config_entry.options.get(
        CONF_SENSORS_TOTAL_FAILED_PINGS_ENABLED,
        DEFAULT_SENSORS_TOTAL_FAILED_PINGS_ENABLED,
    ):
        entities = [
            DeviceResetTotalFailedPingsButton(
                monitored.coordinator,
                monitored.device,
                config_entry.runtime_data.integration,
            )
            for monitored in config_entry.runtime_data.monitored.values()
        ]

    if entities:
        async_add_entities(entities)

    remove_config_entry_orphan_entities(hass, config_entry, entities, "button")
