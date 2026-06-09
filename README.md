# Uyuni Lights for Home Assistant

A [HACS](https://hacs.xyz/) custom integration to control **Uyuni** infrared LED
lights (flameless candles, tea lights and other Uyuni lights that share the same
remote) from Home Assistant.

It is built on the [`infrared` entity platform](https://www.home-assistant.io/integrations/infrared/)
introduced in Home Assistant **2026.4**, the same foundation used by the
built‑in `lg_infrared` integration. The integration itself sends no raw timings —
it hands `NEC` commands to an infrared **emitter** entity provided by another
integration (for example an [ESPHome](https://esphome.io/) IR blaster), which
does the actual transmitting.

## What you get

For each configured emitter the integration creates one device with:

| Entity | Type | Description |
| ------ | ---- | ----------- |
| Uyuni Lights | `light` | On/off (assumed state, since the lights give no feedback). |
| Dim up / Dim down | `button` | Nudge the brightness one step. Each press sends exactly one IR command. |
| 4 / 6 / 8 / 10 hour timer | `button` | Sends the corresponding auto‑off timer command. |

## Requirements

- Home Assistant **2026.4** or newer (for the `infrared` platform).
- An infrared **emitter** entity already set up in Home Assistant (e.g. ESPHome
  with a `remote_transmitter`). Without one, the config flow will tell you that
  no infrared emitters were found.

The `infrared-protocols` library used to encode the NEC frames is pulled in
automatically by Home Assistant's `infrared` integration, which this component
depends on — there is nothing extra to install.

## Installation (HACS)

1. In HACS, add this repository as a **custom repository** (category
   *Integration*): `https://github.com/hennamann/uyuni-ha`.
2. Install **Uyuni Lights** and restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for
   **Uyuni Lights**.
4. Pick the infrared emitter that points at your lights and submit.

You can add the integration multiple times if you have emitters in different
rooms.

## How dimming works

The Uyuni remote only offers *relative* dimming (dim up / dim down) — there is no
"set to 50%" command and the lights report nothing back. Rather than fake an
absolute brightness slider (which would fire a burst of IR presses and drift out
of sync), dimming is exposed as two dedicated **Dim up** and **Dim down**
buttons. Each press sends a single IR command, exactly like the physical remote,
so the behaviour is predictable and never gets out of step. Drop the buttons next
to the light in a dashboard card, or call them from automations and scripts.

## Decoded IR commands

All commands use the NEC protocol with address `0x01`:

| Function | NEC command |
| -------- | ----------- |
| On | `0x00` |
| Off | `0x02` |
| 4 hour timer | `0x04` |
| 6 hour timer | `0x08` |
| 8 hour timer | `0x0C` |
| 10 hour timer | `0x10` |
| Dim down | `0x0A` |
| Dim up | `0x0B` |

## Disclaimer

This is an unofficial integration and is not affiliated with Uyuni Lighting.
