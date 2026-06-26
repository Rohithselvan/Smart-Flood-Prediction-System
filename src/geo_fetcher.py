"""
geo_fetcher.py
Local version:
✔ No API key required
✔ Works fully on local system
✔ Fetches terrain + weather dynamically
"""

import requests
import math


# ─────────────────────────────────────────────
# 1. Geocode → area name to lat/lon
# ─────────────────────────────────────────────
def geocode(area_name):
    """Returns (lat, lon, display_name)"""

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": area_name,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "FloodPredictionApp/1.0"
    }

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()

    results = resp.json()

    if not results:
        raise ValueError(f"Location not found: {area_name}")

    r = results[0]

    lat = float(r["lat"])
    lon = float(r["lon"])
    name = r.get("display_name", area_name)

    return lat, lon, name


# ─────────────────────────────────────────────
# 2. Terrain Features (Elevation API)
# ─────────────────────────────────────────────
def fetch_terrain(lat, lon):

    delta = 0.005  # ~500m

    points = []
    for dlat in [-delta, 0, delta]:
        for dlon in [-delta, 0, delta]:
            points.append({
                "latitude": round(lat + dlat, 6),
                "longitude": round(lon + dlon, 6)
            })

    url = "https://api.open-elevation.com/api/v1/lookup"

    resp = requests.post(
        url,
        json={"locations": points},
        timeout=15
    )
    resp.raise_for_status()

    elevations = [r["elevation"] for r in resp.json()["results"]]

    # Grid
    e = elevations
    center = e[4]

    # Slope
    dz_dx = (e[5] - e[3]) / (2 * 500)
    dz_dy = (e[7] - e[1]) / (2 * 500)

    slope = math.degrees(math.atan(math.sqrt(dz_dx**2 + dz_dy**2)))

    # Aspect
    aspect = math.degrees(math.atan2(-dz_dy, dz_dx))
    if aspect < 0:
        aspect += 360

    # Curvature
    curvature = (e[1] + e[3] + e[5] + e[7] - 4 * center) / (500 ** 2)

    # TWI
    slope_rad = math.radians(max(slope, 0.001))
    fa_approx = max(1.0, 100 * math.exp(-slope / 10))
    twi = math.log(fa_approx / math.tan(slope_rad))

    drainage = min(elevations)

    return {
        "Slope": round(slope, 4),
        "Curvature": round(curvature, 6),
        "Aspect": round(aspect, 2),
        "TWI": round(twi, 4),
        "FA": round(fa_approx, 2),
        "Drainage": round(drainage, 2),
        "elevation": round(center, 2)
    }


# ─────────────────────────────────────────────
# 3. Weather (Open-Meteo API)
# ─────────────────────────────────────────────
def fetch_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation",
        "forecast_days": 3,
        "timezone": "auto"
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    times = data["hourly"]["time"]
    precip = data["hourly"]["precipitation"]

    # Group by day
    days = {}

    for t, p in zip(times, precip):
        day = t[:10]
        days.setdefault(day, []).append(p or 0)

    forecast = []

    for day, values in sorted(days.items())[:3]:
        forecast.append({
            "date": day,
            "total_mm": round(sum(values), 2),
            "max_hourly_mm": round(max(values), 2),
            "hours_rain": sum(1 for v in values if v > 0.1)
        })

    return forecast


# ─────────────────────────────────────────────
# 4. Master Function
# ─────────────────────────────────────────────
def fetch_all(area_name):

    lat, lon, display_name = geocode(area_name)

    terrain = fetch_terrain(lat, lon)
    forecast = fetch_weather(lat, lon)

    return {
        "lat": lat,
        "lon": lon,
        "display_name": display_name,
        "terrain": terrain,
        "forecast": forecast
    }