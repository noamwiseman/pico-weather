import time
import network
from machine import Pin
from gpio_lcd import GpioLcd

from config import (
    WIFI_SSID, WIFI_PASSWORD, WIFI_TIMEOUT,
    LOCATIONS,
    LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
    LCD_COLS, LCD_ROWS,
    DISPLAY_CYCLE_MS, FETCH_INTERVAL_MS, WIFI_RETRY_MS,
)
from weather import fetch_weather, wmo_to_str


def connect_wifi(lcd):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Connecting WiFi")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.time() + WIFI_TIMEOUT
    while not wlan.isconnected():
        if time.time() >= deadline:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("No WiFi")
            return False
        time.sleep(0.5)
    return True


def render_display(lcd, loc_index, data):
    name = LOCATIONS[loc_index]["name"]
    lcd.clear()
    if data is None:
        lcd.move_to(0, 0)
        lcd.putstr("{:<13} --C".format(name[:13]))
        lcd.move_to(0, 1)
        lcd.putstr("No data     H:--%" )
        return

    current = data["current"]
    temp = int(round(current["temperature_2m"]))
    hum  = int(round(current["relative_humidity_2m"]))
    cond = wmo_to_str(current["weather_code"])

    lcd.move_to(0, 0)
    lcd.putstr("{:<13}{:>2d}C".format(name[:13], temp))

    lcd.move_to(0, 1)
    if hum == 100:
        lcd.putstr("{:<10}H:100%".format(cond))
    else:
        lcd.putstr("{:<11}H:{:>2d}%".format(cond, hum))


def main():
    # --- LCD init ---
    lcd = GpioLcd(
        rs_pin=Pin(LCD_RS), enable_pin=Pin(LCD_EN),
        d4_pin=Pin(LCD_D4), d5_pin=Pin(LCD_D5),
        d6_pin=Pin(LCD_D6), d7_pin=Pin(LCD_D7),
        num_lines=LCD_ROWS, num_columns=LCD_COLS,
    )
    lcd.putstr("Booting...")

    # --- WiFi ---
    connect_wifi(lcd)

    # --- State ---
    n = len(LOCATIONS)
    cache           = [None] * n
    last_fetch_ms   = [0] * n
    current_loc     = 0
    display_start_ms = time.ticks_ms()
    last_wifi_retry  = time.ticks_ms()

    # Render initial display immediately
    render_display(lcd, current_loc, cache[current_loc])

    wlan = network.WLAN(network.STA_IF)

    while True:
        now = time.ticks_ms()

        # 1. WiFi watchdog
        if not wlan.isconnected():
            if time.ticks_diff(now, last_wifi_retry) >= WIFI_RETRY_MS:
                last_wifi_retry = now
                connect_wifi(lcd)
                # Re-render after reconnect attempt
                render_display(lcd, current_loc, cache[current_loc])

        # 2. Fetch stale or missing data for all locations
        if wlan.isconnected():
            for i in range(n):
                age = time.ticks_diff(now, last_fetch_ms[i])
                if cache[i] is None or age >= FETCH_INTERVAL_MS:
                    loc = LOCATIONS[i]
                    data, err = fetch_weather(loc["lat"], loc["lon"])
                    last_fetch_ms[i] = time.ticks_ms()
                    if data is not None:
                        cache[i] = data
                    elif err is not None and i == current_loc:
                        # Show error briefly on line 2
                        lcd.move_to(0, 1)
                        lcd.putstr("Err:{:<12}".format(err))
                        time.sleep_ms(2000)
                        render_display(lcd, current_loc, cache[current_loc])
                    # Always break after one fetch per loop tick to avoid blocking too long
                    break

        # 3. Display cycle
        if time.ticks_diff(now, display_start_ms) >= DISPLAY_CYCLE_MS:
            current_loc = (current_loc + 1) % n
            display_start_ms = time.ticks_ms()
            render_display(lcd, current_loc, cache[current_loc])

        time.sleep_ms(100)


main()
