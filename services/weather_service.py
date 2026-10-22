import requests
import datetime
import math

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

def get_weather_code_info(code):
    return WMO_CODES.get(code, {"desc": "Variable weather", "icon": "🌤️", "suitability": "Moderate"})

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

def generate_mock_weather(location_key="ludhiana", location_name="Ludhiana (Punjab)"):
    """
    Realistic fallback simulation when external API is unreachable or rate limited.
    """
    now = datetime.datetime.now()
    hourly = []
    for i in range(24):
        hour_dt = now + datetime.timedelta(hours=i)
        temp_cycle = 24 + 7 * math.sin((hour_dt.hour - 8) * math.pi / 12)
        hum_cycle = 65 - 20 * math.sin((hour_dt.hour - 8) * math.pi / 12)
        hourly.append({
            "time": hour_dt.strftime("%I %p"),
            "temp": round(temp_cycle, 1),
            "humidity": max(35, min(92, round(hum_cycle))),
            "wind": round(8 + 5 * math.cos(i * 0.5), 1),
            "rain_prob": 10 if i < 12 else 25,
            "icon": "☀️" if 6 <= hour_dt.hour <= 18 else "🌙"
        })

    daily = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i in range(7):
        day_dt = now + datetime.timedelta(days=i)
        code = 1 if i % 3 != 0 else (2 if i == 3 else 61)
        w_info = get_weather_code_info(code)
        daily.append({
            "day": day_dt.strftime("%a, %b %d"),
            "code": code,
            "desc": w_info["desc"],
            "icon": w_info["icon"],
            "max_temp": 31 - (i % 3),
            "min_temp": 19 + (i % 2),
            "rain_sum": 0.0 if code < 50 else 4.2,
            "rain_prob": 10 + i * 5 if code < 50 else 65
        })

    current_temp = 28.5
    current_humidity = 62
    current_wind = 11.2

    agro = calculate_agro_metrics(current_temp, current_humidity, current_wind, 15)

    return {
        "location_key": location_key,
        "location_name": location_name,
        "current": {
            "temperature": current_temp,
            "feels_like": 30.1,
            "humidity": current_humidity,
            "wind_speed": current_wind,
            "wind_direction": "NW",
            "pressure": 1012,
            "uv_index": 6.4,
            "weather_code": 1,
            "description": "Mainly Clear",
            "icon": "🌤️",
            "time": now.strftime("%I:%M %p, %b %d")
        },
        "daily": daily,
        "hourly": hourly[:12],
        "agro": agro,
        "source": "AgriPulse Meteorological Simulator (Offline Mode)"
    }

def fetch_weather(location_key="ludhiana"):
    """
    Fetches real-time weather data from Open-Meteo with fallback.
    """
    loc = AGRI_LOCATIONS.get(location_key, AGRI_LOCATIONS["ludhiana"])
    lat = loc["lat"]
    lon = loc["lon"]
    loc_name = loc["name"]

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m,surface_pressure&"
            f"hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m&"
            f"daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,uv_index_max&"
            f"timezone=auto"
        )
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return generate_mock_weather(location_key, loc_name)

        data = response.json()
        current_data = data.get("current", {})
        daily_data = data.get("daily", {})
        hourly_data = data.get("hourly", {})

        cur_code = current_data.get("weather_code", 0)
        cur_info = get_weather_code_info(cur_code)
        cur_temp = current_data.get("temperature_2m", 25)
        cur_hum = current_data.get("relative_humidity_2m", 60)
        cur_wind = current_data.get("wind_speed_10m", 10)

        daily = []
        time_list = daily_data.get("time", [])
        for i in range(min(7, len(time_list))):
            d_time = time_list[i]
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

        hourly = []
        h_times = hourly_data.get("time", [])
        now_hour = datetime.datetime.now().hour
        for i in range(min(12, len(h_times))):
            idx = (now_hour + i) % len(h_times)
            try:
                t_str = h_times[idx]
                dt_h = datetime.datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
                h_code = hourly_data.get("weather_code", [0])[idx]
                hourly.append({
                    "time": dt_h.strftime("%I %p"),
                    "temp": round(hourly_data.get("temperature_2m", [25])[idx], 1),
                    "humidity": hourly_data.get("relative_humidity_2m", [50])[idx],
                    "wind": round(hourly_data.get("wind_speed_10m", [10])[idx], 1),
                    "rain_prob": hourly_data.get("precipitation_probability", [0])[idx],
                    "icon": get_weather_code_info(h_code)["icon"]
                })
            except Exception:
                pass

        first_day_rain = daily[0]["rain_prob"] if daily else 10
        agro = calculate_agro_metrics(cur_temp, cur_hum, cur_wind, first_day_rain)

        return {
            "location_key": location_key,
            "location_name": loc_name,
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
                "time": datetime.datetime.now().strftime("%I:%M %p, %b %d")
            },
            "daily": daily,
            "hourly": hourly,
            "agro": agro,
            "source": "Open-Meteo Live Satellite & Station Feed"
        }

    except Exception as e:
        # Graceful fallback to rich simulation
        return generate_mock_weather(location_key, loc_name)

def get_active_weather_alerts(weather_data):
    """
    Analyzes weather data to produce actionable crop & livestock advisories.
    """
    alerts = []
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
    if high_temp_day or cur.get("temperature", 0) >= 38:
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
    low_temp_day = next((d for d in daily if d.get("min_temp", 20) <= 6), None)
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
    if cur.get("wind_speed", 0) > 28:
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
