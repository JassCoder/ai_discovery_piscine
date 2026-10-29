#!/usr/bin/env python3

import re
import sys
from pathlib import Path

try:
    from module2.weather_api import find_location, get_weather
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from weather_api import find_location, get_weather


def extract_location(question: str) -> str | None:
    match = re.search(
        r"\b(?:in|at|for)\s+([A-Za-z][A-Za-z .'-]*?)(?:\?|$)",
        question,
        re.IGNORECASE,
    )
    if match is None:
        return None
    return match.group(1).strip(" .")


def describe_weather(name: str, weather: dict[str, float]) -> str:
    cloud = weather["cloud"]
    if cloud < 20:
        cloud_description = "few clouds"
    elif cloud < 70:
        cloud_description = "some clouds"
    else:
        cloud_description = "a lot of clouds"
    return (
        f"The current weather in {name} is a temperature of "
        f"{weather['temperature']:.1f} degrees (C), a humidity of "
        f"{weather['humidity']:.0f}%, there are {cloud_description} in the sky "
        f"and a wind of {weather['wind']:.1f}km/h."
    )


def main() -> int:
    print("Ask?: ", end="", flush=True)
    for question in sys.stdin:
        question = question.strip()
        if question.lower() in {"quit", "exit", "q"}:
            return 0
        location = extract_location(question)
        if location is None or "weather" not in question.lower():
            print("Error: ask about the weather in a location.")
        else:
            try:
                name, latitude, longitude = find_location(location)
                print(describe_weather(name, get_weather(latitude, longitude)))
            except (OSError, ValueError) as error:
                print(f"Error: {error}", file=sys.stderr)
        print("Ask?: ", end="", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
