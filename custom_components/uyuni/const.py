"""Constants for the Uyuni Tea Lights integration."""

DOMAIN = "uyuni"

CONF_INFRARED_ENTITY_ID = "infrared_entity_id"

# NEC address shared by every Uyuni command (decoded from the remote).
IR_ADDRESS = 0x01

# NEC command bytes decoded from the Uyuni remote with a Flipper Zero.
CMD_ON = 0x00
CMD_OFF = 0x02
CMD_TIMER_4H = 0x04
CMD_TIMER_6H = 0x08
CMD_TIMER_8H = 0x0C
CMD_TIMER_10H = 0x10
CMD_DIM_DOWN = 0x0A
CMD_DIM_UP = 0x0B

# Number of discrete brightness levels reachable with the dim up/down keys.
# The lights only expose relative dimming, so brightness is tracked optimistically.
BRIGHTNESS_STEPS = 10

# Delay (seconds) between consecutive IR transmissions so the lights keep up
# when several commands are sent in a row (e.g. stepping the brightness).
IR_SEND_DELAY = 0.2
