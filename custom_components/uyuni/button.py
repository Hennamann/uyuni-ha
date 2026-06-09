"""Button platform for the Uyuni Lights integration."""

from __future__ import annotations

from dataclasses import dataclass

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CMD_DIM_DOWN,
    CMD_DIM_UP,
    CMD_TIMER_4H,
    CMD_TIMER_6H,
    CMD_TIMER_8H,
    CMD_TIMER_10H,
    CONF_INFRARED_ENTITY_ID,
    IR_ADDRESS,
)
from .entity import UyuniEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class UyuniButtonEntityDescription(ButtonEntityDescription):
    """Describes a Uyuni button entity."""

    command_code: int


BUTTON_DESCRIPTIONS: tuple[UyuniButtonEntityDescription, ...] = (
    UyuniButtonEntityDescription(
        key="dim_up", translation_key="dim_up", command_code=CMD_DIM_UP
    ),
    UyuniButtonEntityDescription(
        key="dim_down", translation_key="dim_down", command_code=CMD_DIM_DOWN
    ),
    UyuniButtonEntityDescription(
        key="timer_4h", translation_key="timer_4h", command_code=CMD_TIMER_4H
    ),
    UyuniButtonEntityDescription(
        key="timer_6h", translation_key="timer_6h", command_code=CMD_TIMER_6H
    ),
    UyuniButtonEntityDescription(
        key="timer_8h", translation_key="timer_8h", command_code=CMD_TIMER_8H
    ),
    UyuniButtonEntityDescription(
        key="timer_10h", translation_key="timer_10h", command_code=CMD_TIMER_10H
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Uyuni buttons from a config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    async_add_entities(
        UyuniButton(entry, infrared_entity_id, description)
        for description in BUTTON_DESCRIPTIONS
    )


class UyuniButton(UyuniEntity, InfraredEmitterConsumerEntity, ButtonEntity):
    """A Uyuni button that transmits a single IR command."""

    entity_description: UyuniButtonEntityDescription

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_entity_id: str,
        description: UyuniButtonEntityDescription,
    ) -> None:
        """Initialize the Uyuni button."""
        super().__init__(entry, unique_id_suffix=description.key)
        self._infrared_emitter_entity_id = infrared_entity_id
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the IR command for this button."""
        await self._send_command(
            NECCommand(address=IR_ADDRESS, command=self.entity_description.command_code)
        )
