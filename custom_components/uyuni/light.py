"""Light platform for the Uyuni Lights integration."""

from __future__ import annotations

from typing import Any

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CMD_OFF, CMD_ON, CONF_INFRARED_ENTITY_ID, IR_ADDRESS
from .entity import UyuniEntity

# IR transmissions are serialized so the lights are not sent overlapping bursts.
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Uyuni light from a config entry."""
    async_add_entities([UyuniLight(entry, entry.data[CONF_INFRARED_ENTITY_ID])])


class UyuniLight(
    UyuniEntity, InfraredEmitterConsumerEntity, RestoreEntity, LightEntity
):
    """A Uyuni infrared LED light.

    The lights are infrared-only and give no feedback, so the on/off state is
    tracked optimistically (assumed state). Dimming is relative-only on these
    lights and is exposed through dedicated Dim up/Dim down buttons rather than a
    brightness slider, so it is intentionally not handled here.
    """

    _attr_name = None
    _attr_assumed_state = True
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize the Uyuni light."""
        super().__init__(entry, unique_id_suffix="light")
        self._infrared_emitter_entity_id = infrared_entity_id
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Restore the last known on/off state."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            self._attr_is_on = last_state.state == STATE_ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the lights on."""
        await self._send_command(NECCommand(address=IR_ADDRESS, command=CMD_ON))
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the lights off."""
        await self._send_command(NECCommand(address=IR_ADDRESS, command=CMD_OFF))
        self._attr_is_on = False
        self.async_write_ha_state()
