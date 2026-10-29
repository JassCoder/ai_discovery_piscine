#!/usr/bin/env python3

import sys
from pathlib import Path

try:
    from module2.weather_api import format_weather, get_weather
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from weather_api import format_weather, get_weather


def main() -> int:
    try:
        latitude = float(input("Latitude?: "))
        longitude = float(input("Longitude?: "))
        weather = get_weather(latitude, longitude)
        print("The current weather for this location is:")
        print(format_weather(weather))
    except (EOFError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: unable to contact the weather service ({error})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
