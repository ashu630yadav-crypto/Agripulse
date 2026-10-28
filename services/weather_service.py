import datetime
import time
from urllib.parse import quote

import requests

# Popular agricultural hubs with coordinates
AGRI_LOCATIONS = {
    "ludhiana": {"name": "Ludhiana (Punjab)", "lat": 30.9010, "lon": 75.8573, "region": "Northern Plains"},
    "nashik": {"name": "Nashik (Maharashtra)", "lat": 19.9975, "lon": 73.7898, "region": "Western Region"},
    "varanasi": {"name": "Varanasi (Uttar Pradesh)", "lat": 25.3176, "lon": 82.9739, "region": "Gangetic Plain"},
    "indore": {"name": "Indore (Madhya Pradesh)", "lat": 22.7196, "lon": 75.8577, "region": "Central Plateau"},
    "guntur": {"name": "Guntur (Andhra Pradesh)", "lat": 16.3067, "lon": 80.4365, "region": "Coastal South"},
    "nagpur": {"name": "Nagpur (Maharashtra)", "lat": 21.1458, "lon": 79.0882, "region": "Central Plains"},
    "patna": {"name": "Patna (Bihar)", "lat": 25.5941, "lon": 85.1376, "region": "Eastern Plains"},
    "jaipur": {"name": "Jaipur (Rajasthan)", "lat": 26.9124, "lon": 75.7873, "region": "Arid / Semi-Arid"},
    "karnal": {"name": "Karnal (Haryana)", "lat": 29.6857, "lon": 76.9905, "region": "Wheat-Rice Belt"},
    "coimbatore": {"name": "Coimbatore (Tamil Nadu)", "lat": 11.0168, "lon": 76.9558, "region": "Southern Highlands"}
}

# WMO Weather interpretation codes
WMO_CODES = {
    0: {"desc": "Clear sky", "icon": "☀️", "suitability": "Good"},
    1: {"desc": "Mainly clear", "icon": "🌤️", "suitability": "Good"},
    2: {"desc": "Partly cloudy", "icon": "⛅", "suitability": "Good"},
    3: {"desc": "Overcast", "icon": "☁️", "suitability": "Moderate"},
    45: {"desc": "Foggy", "icon": "🌫️", "suitability": "Poor"},
    48: {"desc": "Depositing rime fog", "icon": "🌫️", "suitability": "Poor"},
    51: {"desc": "Light drizzle", "icon": "🌦️", "suitability": "Poor"},
    53: {"desc": "Moderate drizzle", "icon": "🌦️", "suitability": "Poor"},
    55: {"desc": "Dense drizzle", "icon": "🌧️", "suitability": "Unsuitable"},
    61: {"desc": "Slight rain", "icon": "🌧️", "suitability": "Poor"},
    63: {"desc": "Moderate rain", "icon": "🌧️", "suitability": "Unsuitable"},
    65: {"desc": "Heavy rain", "icon": "⛈️", "suitability": "Unsuitable"},
    71: {"desc": "Slight snow fall", "icon": "🌨️", "suitability": "Unsuitable"},
    73: {"desc": "Moderate snow fall", "icon": "🌨️", "suitability": "Unsuitable"},
    75: {"desc": "Heavy snow fall", "icon": "❄️", "suitability": "Unsuitable"},
    80: {"desc": "Slight rain showers", "icon": "🌦️", "suitability": "Poor"},
    81: {"desc": "Moderate rain showers", "icon": "🌧️", "suitability": "Unsuitable"},
    82: {"desc": "Violent rain showers", "icon": "⛈️", "suitability": "Unsuitable"},
    95: {"desc": "Thunderstorm", "icon": "⚡", "suitability": "Danger"},
    96: {"desc": "Thunderstorm with slight hail", "icon": "⛈️", "suitability": "Danger"},
    99: {"desc": "Thunderstorm with heavy hail", "icon": "⛈️", "suitability": "Danger"}
}

# wttr.in publishes World Weather Online condition codes. Translating them into WMO codes
# keeps the advisory engine provider-independent.
WWO_TO_WMO = {
    113: 0, 116: 2, 119: 3, 122: 3, 143: 45, 176: 61, 185: 45, 200: 95,
    227: 71, 230: 73, 248: 45, 260: 63, 263: 80, 266: 61, 281: 66, 284: 66,
    293: 80, 296: 61, 299: 81, 302: 63, 305: 81, 308: 82, 311: 63, 314: 65,
    317: 66, 320: 75, 323: 71, 326: 71, 329: 73, 332: 75, 335: 75, 338: 75,
    342: 75, 343: 82, 350: 66, 353: 80, 356: 81, 359: 82, 362: 66, 364: 82,
    368: 80, 371: 81, 374: 71, 377: 71, 386: 95, 389: 96, 392: 99, 395: 99
}

WEATHER_CACHE_TTL = 600
GEOCODE_CACHE_TTL = 86400

_weather_cache = {}
_geocode_cache = {}
_last_good = {}

# wttr.in rejects requests that do not identify themselves.
HEADERS = {
    "User-Agent": "AgriPulse/1.0 (agricultural decision support; https://github.com/ashu630yadav-crypto/Agripulse)"
}

NO_DATA = "—"


def get_weather_code_info(code):
    return WMO_CODES.get(code, {"desc": "Variable weather", "icon": "🌤️", "suitability": "Moderate"})


def _wmo_from_wwo(raw_code):
    try:
        return WWO_TO_WMO.get(int(raw_code), 3)
    except (TypeError, ValueError):
        return 3


def _to_number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_agro_metrics(temp, humidity, wind_speed, rain_chance):
    """
    Computes agricultural advisory metrics:
    - Spraying suitability index
    - Fungal infection risk
    - Evapotranspiration level
    - Farm workability
    """
    # Spraying index
    if rain_chance > 40 or wind_speed > 20:
        spray_status = "Unsuitable"
        spray_reason = "High drift risk (wind >20 km/h) or wash-off danger (rain >40%)"
        spray_badge = "badge-danger"
    elif wind_speed > 12 or humidity > 85 or temp > 33:
        spray_status = "Marginal"
        spray_reason = "Moderate wind drift or high heat causing rapid droplet evaporation"
        spray_badge = "badge-warning"
    else:
        spray_status = "Ideal"
        spray_reason = "Calm winds, safe humidity, no rain predicted in next 6 hours"
        spray_badge = "badge-success"

    # Fungal Disease Risk
    if humidity > 80 and 18 <= temp <= 28:
        fungal_risk = "High"
        fungal_desc = "Optimal spore germination conditions for rust, blight & powdery mildew"
        fungal_badge = "badge-danger"
    elif humidity > 70 or (16 <= temp <= 30 and rain_chance > 30):
        fungal_risk = "Moderate"
        fungal_desc = "Elevated humidity; monitor field borders and dense canopy"
        fungal_badge = "badge-warning"
    else:
        fungal_risk = "Low"
        fungal_desc = "Dry canopy conditions reduce pathogen propagation"
        fungal_badge = "badge-success"

    # Evapotranspiration estimate (Penman-Monteith simplification mm/day)
    et0 = max(1.5, min(9.5, round(0.18 * temp + 0.05 * wind_speed - 0.04 * humidity + 2.5, 1)))

    return {
        "spray_status": spray_status,
        "spray_reason": spray_reason,
        "spray_badge": spray_badge,
        "fungal_risk": fungal_risk,
        "fungal_desc": fungal_desc,
        "fungal_badge": fungal_badge,
        "et0": et0,
        "soil_moisture_estimate": "Adequate" if rain_chance > 30 or humidity > 65 else "Decreasing"
    }


def _geocode(place_name):
    """Resolves any city or town name typed by a farmer into coordinates."""
    cache_key = place_name.lower().strip()
    cached = _geocode_cache.get(cache_key)
    if cached and time.time() - cached[0] < GEOCODE_CACHE_TTL:
        return cached[1]

    url = ("https://geocoding-api.open-meteo.com/v1/search?name="
           f"{quote(cache_key)}&count=1&language=en&format=json")
    try:
        response = requests.get(url, timeout=8, headers=HEADERS)
        results = response.json().get("results") or []
    except Exception:
        return None

    if not results:
        return None

    hit = results[0]
    label = ", ".join(str(p) for p in [hit.get("name"), hit.get("admin1"), hit.get("country_code")] if p)
    place = {"name": label, "lat": hit["latitude"], "lon": hit["longitude"], "region": hit.get("admin1") or ""}
    _geocode_cache[cache_key] = (time.time(), place)
    return place


def resolve_location(query):
    """Accepts a preset key, a preset city name, or any free-text place."""
    cache_key = str(query or "ludhiana").lower().strip()
    if cache_key in AGRI_LOCATIONS:
        loc = AGRI_LOCATIONS[cache_key]
        return {"name": loc["name"], "lat": loc["lat"], "lon": loc["lon"], "region": loc["region"]}

    for loc in AGRI_LOCATIONS.values():
        if cache_key == loc["name"].lower().split(" (")[0].strip():
            return {"name": loc["name"], "lat": loc["lat"], "lon": loc["lon"], "region": loc["region"]}

    return _geocode(cache_key)


def _fetch_from_wttr(place):
    """Primary live source: station observations from World Weather Online via wttr.in."""
    url = f"https://wttr.in/{place['lat']},{place['lon']}?format=j1"
    response = requests.get(url, timeout=10, headers=HEADERS)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}")
    data = response.json()

    raw_cur = data["current_condition"][0]
    cur_code = _wmo_from_wwo(raw_cur.get("weatherCode"))
    cur_info = get_weather_code_info(cur_code)
    cur_temp = _to_number(raw_cur.get("temp_C"), 25.0)
    cur_hum = int(_to_number(raw_cur.get("humidity"), 60))
    cur_wind = _to_number(raw_cur.get("windspeedKmph"), 10)

    now = datetime.datetime.now()
    observed = ""
    for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M"):
        try:
            observed = datetime.datetime.strptime(raw_cur.get("localObsDateTime", ""), fmt).strftime("%I:%M %p, %b %d")
            break
        except ValueError:
            continue

    daily = []
    flat_hours = []
    for day in data.get("weather", []):
        try:
            day_dt = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
        except (KeyError, ValueError):
            continue
        slots = day.get("hourly") or []

        noon = slots[4] if len(slots) > 4 else (slots[0] if slots else {})
        d_code = _wmo_from_wwo(noon.get("weatherCode"))
        d_info = get_weather_code_info(d_code)
        daily.append({
            "day": day_dt.strftime("%a, %b %d"),
            "code": d_code,
            "desc": d_info["desc"],
            "icon": d_info["icon"],
            "max_temp": _to_number(day.get("maxtempC"), 30),
            "min_temp": _to_number(day.get("mintempC"), 18),
            "rain_sum": round(sum(_to_number(s.get("precipMM")) for s in slots), 1),
            "rain_prob": max([int(_to_number(s.get("chanceofrain"))) for s in slots] or [0])
        })

        for s in slots:
            slot_dt = day_dt + datetime.timedelta(hours=int(_to_number(s.get("time"))) // 100)
            flat_hours.append((slot_dt, s))

    floor_dt = now.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=3)
    hourly = [
        {
            "time": slot_dt.strftime("%I %p"),
            "temp": _to_number(s.get("tempC"), 25),
            "humidity": int(_to_number(s.get("humidity"), 50)),
            "wind": _to_number(s.get("windspeedKmph"), 10),
            "rain_prob": int(_to_number(s.get("chanceofrain"))),
            "icon": get_weather_code_info(_wmo_from_wwo(s.get("weatherCode")))["icon"]
        }
        for slot_dt, s in sorted(flat_hours, key=lambda item: item[0])
        if slot_dt >= floor_dt
    ][:12]

    today_rain_prob = daily[0]["rain_prob"] if daily else 10

    return {
        "location_key": None,
        "location_name": place["name"],
        "region": place.get("region") or "",
        "current": {
            "temperature": cur_temp,
            "feels_like": _to_number(raw_cur.get("FeelsLikeC"), cur_temp),
            "humidity": cur_hum,
            "wind_speed": cur_wind,
            "wind_direction": raw_cur.get("winddir16Point", "Variable"),
            "pressure": _to_number(raw_cur.get("pressure"), 1012),
            "uv_index": _to_number(raw_cur.get("uvIndex"), 5.5),
            "weather_code": cur_code,
            "description": ((raw_cur.get("weatherDesc") or [{}])[0].get("value") or cur_info["desc"]).strip(),
            "icon": cur_info["icon"],
            "time": observed or now.strftime("%I:%M %p, %b %d")
        },
        "daily": daily,
        "hourly": hourly,
        "agro": calculate_agro_metrics(cur_temp, cur_hum, cur_wind, today_rain_prob),
        "resolution": "3-hourly",
        "source": "wttr.in (World Weather Online)"
    }


def _fetch_from_open_meteo(place):
    """Secondary live source: ECMWF/ICON model blend via Open-Meteo."""
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={place['lat']}&longitude={place['lon']}&"
        "current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,surface_pressure&"
        "hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m&"
        "daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,uv_index_max&"
        "timezone=auto"
    )
    response = requests.get(url, timeout=10, headers=HEADERS)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}")

    data = response.json()
    if data.get("error"):
        raise RuntimeError(str(data.get("reason", "request rejected")))

    current_data = data.get("current", {})
    daily_data = data.get("daily", {})
    hourly_data = data.get("hourly", {})

    cur_code = current_data.get("weather_code", 0)
    cur_info = get_weather_code_info(cur_code)
    cur_temp = current_data.get("temperature_2m", 25)
    cur_hum = current_data.get("relative_humidity_2m", 60)
    cur_wind = current_data.get("wind_speed_10m", 10)

    daily = []
    for i, d_time in enumerate(daily_data.get("time", [])[:7]):
        dt_obj = datetime.datetime.strptime(d_time, "%Y-%m-%d")
        d_code = daily_data.get("weather_code", [0])[i]
        w_info = get_weather_code_info(d_code)
        daily.append({
            "day": dt_obj.strftime("%a, %b %d"),
            "code": d_code,
            "desc": w_info["desc"],
            "icon": w_info["icon"],
            "max_temp": round(daily_data.get("temperature_2m_max", [30])[i], 1),
            "min_temp": round(daily_data.get("temperature_2m_min", [18])[i], 1),
            "rain_sum": daily_data.get("precipitation_sum", [0])[i],
            "rain_prob": daily_data.get("precipitation_probability_max", [0])[i]
        })

    now = datetime.datetime.now()
    hourly = []
    for idx, t_str in enumerate(hourly_data.get("time", [])):
        dt_h = datetime.datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
        if dt_h < now - datetime.timedelta(hours=1):
            continue
        hourly.append({
            "time": dt_h.strftime("%I %p"),
            "temp": round(hourly_data.get("temperature_2m", [25])[idx], 1),
            "humidity": hourly_data.get("relative_humidity_2m", [50])[idx],
            "wind": round(hourly_data.get("wind_speed_10m", [10])[idx], 1),
            "rain_prob": hourly_data.get("precipitation_probability", [0])[idx],
            "icon": get_weather_code_info(hourly_data.get("weather_code", [0])[idx])["icon"]
        })
        if len(hourly) >= 12:
            break

    first_day_rain = daily[0]["rain_prob"] if daily else 10

    return {
        "location_key": None,
        "location_name": place["name"],
        "region": place.get("region") or "",
        "current": {
            "temperature": cur_temp,
            "feels_like": current_data.get("apparent_temperature", cur_temp),
            "humidity": cur_hum,
            "wind_speed": cur_wind,
            "wind_direction": "Variable",
            "pressure": current_data.get("surface_pressure", 1012),
            "uv_index": daily_data.get("uv_index_max", [6])[0] if daily_data.get("uv_index_max") else 5.5,
            "weather_code": cur_code,
            "description": cur_info["desc"],
            "icon": cur_info["icon"],
            "time": now.strftime("%I:%M %p, %b %d")
        },
        "daily": daily,
        "hourly": hourly,
        "agro": calculate_agro_metrics(cur_temp, cur_hum, cur_wind, first_day_rain),
        "resolution": "hourly",
        "source": "Open-Meteo (ECMWF model blend)"
    }


def _unavailable(place_name, reasons):
    """
    Honest empty state. AgriPulse drives spray and irrigation decisions, so it must never
    present invented numbers as live conditions; every figure is blanked instead.
    """
    return {
        "location_key": None,
        "location_name": place_name,
        "region": "",
        "current": {
            "temperature": NO_DATA,
            "feels_like": NO_DATA,
            "humidity": NO_DATA,
            "wind_speed": NO_DATA,
            "wind_direction": NO_DATA,
            "pressure": NO_DATA,
            "uv_index": NO_DATA,
            "weather_code": None,
            "description": "Live data unavailable",
            "icon": "❔",
            "time": NO_DATA
        },
        "daily": [],
        "hourly": [],
        "agro": {
            "spray_status": "Unavailable",
            "spray_reason": "No live weather reading, so a spraying window cannot be evaluated.",
            "spray_badge": "badge-info",
            "fungal_risk": "Unavailable",
            "fungal_desc": "No live humidity reading, so fungal infection risk cannot be estimated.",
            "fungal_badge": "badge-info",
            "et0": NO_DATA,
            "soil_moisture_estimate": "Unknown"
        },
        "resolution": "hourly",
        "source": "No live source reachable",
        "degraded": True,
        "stale": False,
        "provider_errors": reasons
    }


def get_weather(query="ludhiana"):
    """
    Live agro-meteorology for any place name. Results are cached per coordinate so a busy
    day of page views costs one upstream call rather than one per visit.
    """
    place = resolve_location(query)
    if place is None:
        missing = _unavailable(f"“{query}”", ["no place matched that name"])
        missing["invalid_location"] = True
        return missing

    key = (round(float(place["lat"]), 3), round(float(place["lon"]), 3))
    cached = _weather_cache.get(key)
    if cached and time.time() - cached[0] < WEATHER_CACHE_TTL:
        return cached[1]

    reasons = []
    for fetcher in (_fetch_from_wttr, _fetch_from_open_meteo):
        try:
            payload = fetcher(place)
            payload["degraded"] = False
            payload["stale"] = False
            _weather_cache[key] = (time.time(), payload)
            _last_good[key] = payload
            return payload
        except Exception as exc:
            reasons.append(f"{fetcher.__name__.replace('_fetch_from_', '')}: {type(exc).__name__} {exc}")

    last = _last_good.get(key)
    if last:
        stale = dict(last)
        stale["stale"] = True
        stale["source"] = f"{last['source']} — cached reading, live sources down"
        stale["provider_errors"] = reasons
        return stale

    return _unavailable(place["name"], reasons)


def get_active_weather_alerts(weather_data):
    """
    Analyzes weather data to produce actionable crop & livestock advisories.
    """
    alerts = []

    if weather_data.get("degraded"):
        invalid = weather_data.get("invalid_location")
        loc_name = weather_data.get("location_name", "your region")
        return [{
            "id": "data_unavailable",
            "type": "Place Not Found" if invalid else "Weather Feeds Unreachable",
            "severity": "Notice",
            "severity_badge": "badge-info",
            "icon": "🔍" if invalid else "📡",
            "headline": (f"No weather data for {loc_name}" if invalid
                         else f"No live weather reading for {loc_name}"),
            "description": ("The place name could not be matched. Type a town or district name, or pick one of the "
                            "listed regions." if invalid else
                            "Every weather source failed, so advisories that depend on live data are paused rather "
                            "than estimated. AgriPulse does not publish simulated conditions as farm guidance."),
            "actions": ([
                "Re-type the location with its district or city name (for example \u201cNashik\u201d or \u201cGuntur\u201d).",
                "Use the region dropdown for the ten major agricultural hubs."
            ] if invalid else [
                "Confirm conditions with another source (Kisan Call Centre 1800-180-1551 or your district agri office) before spraying or irrigating.",
                "Reload this page in a few minutes to pick up the next live reading."
            ]),
            "impacted_crops": ["All crops \u2014 advisory paused until data returns"]
        }]

    cur = weather_data.get("current", {})
    daily = weather_data.get("daily", [])
    loc = weather_data.get("location_name", "Your Region")

    # 1. Rain / Storm Alert
    high_rain_day = next((d for d in daily if d.get("rain_sum", 0) > 20 or d.get("rain_prob", 0) > 75), None)
    if high_rain_day:
        alerts.append({
            "id": "rain_alert",
            "type": "Heavy Rainfall & Waterlogging",
            "severity": "High",
            "severity_badge": "badge-danger",
            "icon": "⛈️",
            "headline": f"Heavy Precipitation Forecast for {high_rain_day['day']} in {loc}",
            "description": f"Expected rain up to {high_rain_day['rain_sum']} mm with a {high_rain_day['rain_prob']}% probability.",
            "actions": [
                "Clear field drainage trenches immediately to prevent stagnant water around root zones.",
                "Suspend chemical fertilizer broadcasting and pesticide spraying to prevent runoff wash-out.",
                "Ensure harvested grain stored in open yards is moved to elevated sheds or covered with UV-proof tarpaulins."
            ],
            "impacted_crops": ["Cotton", "Vegetables (Tomato, Chilli)", "Pulses", "Newly sown wheat"]
        })

    # 2. Heatwave Alert
    high_temp_day = next((d for d in daily if d.get("max_temp", 0) >= 38), None)
    if high_temp_day or _to_number(cur.get("temperature"), 0) >= 38:
        max_t = high_temp_day['max_temp'] if high_temp_day else cur.get("temperature")
        alerts.append({
            "id": "heat_alert",
            "type": "Extreme Heatwave & Moisture Stress",
            "severity": "Warning",
            "severity_badge": "badge-warning",
            "icon": "🔥",
            "headline": f"Extreme Heat Conditions ({max_t}°C) Anticipated",
            "description": "High solar radiation accelerates evapotranspiration causing flower drop and moisture stress.",
            "actions": [
                "Irrigate fields during late evening or early morning to minimize evaporative water loss.",
                "Apply organic mulching (paddy straw, sugarcane bagasse) around horticultural plants.",
                "Provide shady resting shelters and continuous clean water for dairy cattle and poultry."
            ],
            "impacted_crops": ["Horticulture crops", "Flowering Vegetables", "Maize", "Fodder"]
        })

    # 3. Frost / Cold Wave Alert
    low_temp_day = next((d for d in daily if d.get("min_temp", 99) <= 6), None)
    if low_temp_day:
        alerts.append({
            "id": "frost_alert",
            "type": "Cold Wave & Frost Hazard",
            "severity": "High",
            "severity_badge": "badge-danger",
            "icon": "❄️",
            "headline": f"Night Frost Risk: Min Temp dropping to {low_temp_day['min_temp']}°C",
            "description": "Surface radiation cooling can freeze cell sap in tender vegetable leaves and mustard blossoms.",
            "actions": [
                "Give light night irrigation to raise field temperature through heat capacity of water.",
                "Create smoke screens (smoke burning dried weeds/straw) on north-western boundary at sunset.",
                "Cover sensitive nursery beds with plastic tunnels or thatch coverings."
            ],
            "impacted_crops": ["Mustard", "Potato", "Tomato", "Papaya", "Green Peas"]
        })

    # 4. High Wind Alert
    if _to_number(cur.get("wind_speed"), 0) > 28:
        alerts.append({
            "id": "wind_alert",
            "type": "High Wind & Crop Lodging Risk",
            "severity": "Moderate",
            "severity_badge": "badge-warning",
            "icon": "💨",
            "headline": f"Gusty Winds ({cur.get('wind_speed')} km/h) Detected",
            "description": "Strong gusts can cause lodging in tall crops (Sugarcane, tall Wheat, Banana) and shatter ripening grains.",
            "actions": [
                "Provide earthing-up and bamboo staking support for tall banana and sugarcane plants.",
                "Do not irrigate fields before high winds, as saturated roots loosen soil and cause severe lodging.",
                "Secure greenhouse polyhouse sheets and shade net structures."
            ],
            "impacted_crops": ["Sugarcane", "Banana", "Tall cereals", "Fruit orchards"]
        })

    # 5. Default Agro Advisory if no extreme weather
    if not alerts:
        alerts.append({
            "id": "favorable_alert",
            "type": "Favorable Farming Weather Advisory",
            "severity": "Advisory",
            "severity_badge": "badge-success",
            "icon": "🌱",
            "headline": f"Optimal Field Conditions across {loc}",
            "description": "Stable temperature and moderate humidity are conducive for vegetative growth, top-dressing, and weeding.",
            "actions": [
                "Ideal window for scheduled fertigation and micronutrient foliar spray.",
                "Conduct regular field scouting for early pest nymph detection.",
                "Proceed with planned intercultural operations and land preparation."
            ],
            "impacted_crops": ["All regional seasonal crops"]
        })

    return alerts
