import urequests

WMO_CODES = {
    0: "Clear",    1: "MClear",   2: "PCloud",   3: "Cloudy",
    45: "Fog",     48: "DepFog",
    51: "LDrizl",  53: "MDrizl",  55: "HDrizl",
    61: "LRain",   63: "MRain",   65: "HRain",
    66: "FzRain",  67: "HFzRain",
    71: "LSnow",   73: "MSnow",   75: "HSnow",   77: "Grains",
    80: "LShwr",   81: "MShwr",   82: "HShwr",
    85: "LSnwSh",  86: "HSnwSh",
    95: "Storm",   96: "StHail",  99: "StHHail",
}


def wmo_to_str(code):
    return WMO_CODES.get(code, "Unknown")


def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude={}&longitude={}"
        "&current=temperature_2m,relative_humidity_2m,weather_code"
    ).format(lat, lon)
    try:
        r = urequests.get(url, timeout=10)
        try:
            data = r.json()
        finally:
            r.close()
        return data, None
    except Exception as e:
        return None, type(e).__name__
