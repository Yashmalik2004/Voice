"""
Weather lookup tool.

Uses the free Open-Meteo API (no API key required):
  1. Geocode the location name -> coordinates (lat/lon)
  2. Fetch current temperature, conditions, humidity, and wind speed
"""

import logging
import httpx
from livekit.agents import function_tool, RunContext, ToolError

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WW)
WMO_WEATHER_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@function_tool()
async def lookup_weather(
    context: RunContext,
    location: str,
) -> dict:
    """Look up current weather for any city or location in the world.

    Args:
        location: City name or location to get weather for (e.g., 'New York', 'London', 'Tokyo').
    """
    logger.info("Looking up weather for location: %s", location)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Step 1: Geocode location name to coordinates
            geo_response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location.strip(), "count": 1, "language": "en"},
            )
            geo_data = geo_response.json()
        except Exception as e:
            logger.error("Failed to geocode location %s: %s", location, e)
            raise ToolError(f"Unable to search location '{location}'. Please try again.")

        if not geo_data.get("results"):
            raise ToolError(f"Could not find coordinates for '{location}'. Please verify the city name.")

        result = geo_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        place_name = result["name"]
        country = result.get("country", "")
        full_location = f"{place_name}, {country}" if country else place_name

        try:
            # Step 2: Fetch current weather for those coordinates
            weather_response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                },
            )
            weather = weather_response.json()
        except Exception as e:
            logger.error("Failed to fetch forecast for %s: %s", full_location, e)
            raise ToolError(f"Unable to retrieve weather forecast for '{full_location}'.")

        current = weather.get("current", {})
        temp_f = current.get("temperature_2m")
        temp_c = round((temp_f - 32) * 5 / 9, 1) if temp_f is not None else None
        feels_like_f = current.get("apparent_temperature")
        weather_code = current.get("weather_code", 0)
        conditions_desc = WMO_WEATHER_CODES.get(weather_code, "Clear")

        return {
            "location": full_location,
            "temperature_fahrenheit": temp_f,
            "temperature_celsius": temp_c,
            "feels_like_fahrenheit": feels_like_f,
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_speed_mph": current.get("wind_speed_10m"),
            "conditions": conditions_desc,
        }
