"""Light platform for the Uyuni Tea Lights integration."""

from __future__ import annotations

import asyncio
from typing import Any

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    BRIGHTNESS_STEPS,
    CMD_DIM_DOWN,
    CMD_DIM_UP,
    CMD_OFF,
    CMD_ON,
    CONF_INFRARED_ENTITY_ID,
    IR_ADDRESS,
    IR_SEND_DELAY,
)
from .entity import UyuniEntity

# IR transmissions are serialized so the lights are not flooded with overlapping
# bursts when, for example, the brightness is stepped several levels at once.
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Uyuni light from a config entry."""
    async_add_entities([UyuniLight(entry, entry.data[CONF_INFRARED_ENTITY_ID])])


def _nec(command: int) -> NECCommand:
    """Build a NEC command for the Uyuni address."""
    return NECCommand(address=IR_ADDRESS, command=command)


class UyuniLight(
    UyuniEntity, InfraredEmitterConsumerEntity, RestoreEntity, LightEntity
):
    """A Uyuni LED tea light controlled over infrared.

    The lights are infrared-only and give no feedback, so the on/off and
    brightness state is tracked optimistically (assumed state). Brightness is
    driven by sending the relative dim up/down keys, which means the slider is a
    best effort and can drift if the lights are also operated by their remote.
    """

    _attr_name = None
    _attr_assumed_state = True
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize the Uyuni light."""
        super().__init__(entry, unique_id_suffix="light")
        self._infrared_emitter_entity_id = infrared_entity_id
        self._attr_is_on = False
        # Assume the lights start at full brightness until told otherwise.
        self._level = BRIGHTNESS_STEPS
        self._attr_brightness = self._level_to_brightness(self._level)

    @staticmethod
    def _level_to_brightness(level: int) -> int:
        """Convert an internal level (1..STEPS) to a brightness (1..255)."""
        return max(1, round(level / BRIGHTNESS_STEPS * 255))

    @staticmethod
    def _brightness_to_level(brightness: int) -> int:
        """Convert a brightness (1..255) to an internal level (1..STEPS)."""
        return max(1, round(brightness / 255 * BRIGHTNESS_STEPS))

    async def async_added_to_hass(self) -> None:
        """Restore the last known state."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            self._attr_is_on = last_state.state == STATE_ON
            if (brightness := last_state.attributes.get(ATTR_BRIGHTNESS)) is not None:
                self._level = self._brightness_to_level(int(brightness))
                self._attr_brightness = self._level_to_brightness(self._level)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the lights on, optionally setting the brightness."""
        turned_on = False
        if not self._attr_is_on:
            await self._send_command(_nec(CMD_ON))
            self._attr_is_on = True
            turned_on = True

        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            if turned_on:
                await asyncio.sleep(IR_SEND_DELAY)
            await self._async_set_level(self._brightness_to_level(brightness))

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the lights off."""
        await self._send_command(_nec(CMD_OFF))
        self._attr_is_on = False
        self.async_write_ha_state()

    async def _async_set_level(self, target_level: int) -> None:
        """Step the brightness to the target level using the dim keys."""
        target_level = min(max(target_level, 1), BRIGHTNESS_STEPS)
        delta = target_level - self._level
        if delta:
            command = CMD_DIM_UP if delta > 0 else CMD_DIM_DOWN
            for step in range(abs(delta)):
                if step:
                    await asyncio.sleep(IR_SEND_DELAY)
                await self._send_command(_nec(command))
            self._level = target_level
        self._attr_brightness = self._level_to_brightness(target_level)
