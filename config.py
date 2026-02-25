from secrets import WIFI_SSID, WIFI_PASSWORD  # noqa: F401 (re-exported)

WIFI_TIMEOUT  = 15          # seconds

LOCATIONS = [
    {"name": "Tel-Aviv",   "lat": 32.0853, "lon": 34.7818},
    {"name": "Jerusalem",  "lat": 31.7683, "lon": 35.2137},
    {"name": "Eilat",      "lat": 29.5581, "lon": 34.9482},
]

# LCD GPIO pin assignments (4-bit parallel mode)
LCD_RS = 0   # GP0
LCD_EN = 1   # GP1
LCD_D4 = 2   # GP2
LCD_D5 = 3   # GP3
LCD_D6 = 4   # GP4
LCD_D7 = 5   # GP5
LCD_COLS, LCD_ROWS = 16, 2

DISPLAY_CYCLE_MS  = 5_000    # ms each location is shown
FETCH_INTERVAL_MS = 600_000  # ms between API refreshes (10 min)
WIFI_RETRY_MS     = 30_000   # ms between WiFi reconnect attempts
