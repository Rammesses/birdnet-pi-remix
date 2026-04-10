"""Configuration constants for BirdNET-Pi Remix display daemon."""

# SPI display
DISPLAY_CS   = 8    # GPIO 8,  Pin 24
DISPLAY_DC   = 24   # GPIO 24, Pin 18
DISPLAY_RST  = 25   # GPIO 25, Pin 22
DISPLAY_BL   = 12   # GPIO 12, Pin 32 (hardware PWM for backlight)

# Display dimensions
DISPLAY_WIDTH  = 160
DISPLAY_HEIGHT = 128

# Buttons (active-low, internal pull-up)
BUTTON_A = 16   # GPIO 16, Pin 36 — brightness / wake
BUTTON_B = 26   # GPIO 26, Pin 37 — history toggle
BUTTON_C = 21   # GPIO 21, Pin 40 — hold=shutdown

# I²C power monitor
INA219_ADDRESS = 0x40

# MQTT
MQTT_BROKER          = "localhost"
MQTT_PORT            = 1883
MQTT_TOPIC_DETECTION = "birdnet/detection"
MQTT_TOPIC_BATTERY   = "birdnet/battery"
MQTT_TOPIC_WIFI      = "birdnet/wifi_status"

# Timing
DETECTION_TIMEOUT_S  = 30   # Return to IDLE after this many seconds without a new detection
DIM_TIMEOUT_S        = 60   # Dim display after this many seconds without a button press
RENDER_FPS           = 15

# Power thresholds (volts)
VOLTAGE_WARNING      = 3.5
VOLTAGE_SHUTDOWN     = 3.3
POWER_CHECK_INTERVAL = 30   # seconds

# Colours (RGB tuples for Pillow)
COL_BG             = (13,  27,  14)   # Forest Night
COL_TEXT_PRIMARY   = (240, 236, 216)  # Bone White
COL_TEXT_SECONDARY = (139, 168, 136)  # Sage
COL_ACCENT         = (232, 200, 74)   # Birch Yellow
COL_CONF_FILL      = (76,  175, 80)   # Moss Green
COL_CONF_BG        = (30,  51,  32)   # Dark Moss
COL_SPEC_LOW       = (26,  58,  92)   # Deep Blue
COL_SPEC_HIGH      = (240, 160, 48)   # Sky Amber
COL_BATT_GOOD      = (102, 187, 106)  # Leaf Green
COL_BATT_LOW       = (255, 167, 38)   # Amber
COL_BATT_CRIT      = (239, 83,  80)   # Red
COL_DIVIDER        = (42,  74,  42)   # Dark Sage
COL_HINT           = (86,  120, 86)   # Dim Sage
