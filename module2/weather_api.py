"""Small Open-Meteo client shared by the Module 2 exercises."""

import json
from urllib.parse import urlencode
from urllib.request import urlopen


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _get_json(url: str, params: dict[str, str]) -> dict:
    query = urlencode(params)
    with urlopen(f"{url}?{query}", timeout=10) as response:
        return json.load(response)


def get_weather(latitude: float, longitude: float) -> dict[str, float]:
    data = _get_json(
        WEATHER_URL,
        {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "current": (
                "temperature_2m,relative_humidity_2m,cloud_cover,"
                "wind_speed_10m"
            ),
        },
    )
    current = data.get("current")
    if not isinstance(current, dict):
        raise ValueError("The weather service returned no current weather.")

    fields = {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "cloud": current.get("cloud_cover"),
        "wind": current.get("wind_speed_10m"),
    }
    if any(value is None for value in fields.values()):
        raise ValueError("The weather service returned incomplete data.")
    return {key: float(value) for key, value in fields.items()}


def find_location(name: str) -> tuple[str, float, float]:
    data = _get_json(
        GEOCODING_URL,
        {"name": name, "count": "1", "language": "en", "format": "json"},
    )
    results = data.get("results", [])
    if not results:
        raise ValueError(f"Location not found: {name}")

    result = results[0]
    try:
        return (
            str(result["name"]),
            float(result["latitude"]),
            float(result["longitude"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("The geocoding service returned invalid data.") from error


def format_weather(weather: dict[str, float]) -> str:
    return (
        f"- temperature(C): {weather['temperature']:.1f}\n"
        f"- humidity: {weather['humidity']:.0f}%\n"
        f"- cloud: {weather['cloud']:.0f}%\n"
        f"- wind: {weather['wind']:.1f}km/h"
    )
