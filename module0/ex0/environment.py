import sys
import math
import time
import random


SEASONS: dict[str, dict[str, float]] = {
    "winter": {"avg": 0.0, "amp": 5.0},
    "spring": {"avg": 11.5, "amp": 6.5},
    "summer": {"avg": 22.5, "amp": 7.5},
    "autumn": {"avg": 8.0, "amp": 6.0},
    "fall": {"avg": 8.0, "amp": 6.0},
}


def parse_season() -> dict[str, float]:
    if len(sys.argv) != 2:
        print("Usage: environment.py <season>")
        sys.exit(1)

    arg = sys.argv[1].lower()
    num_map = {
        "0": "winter",
        "1": "spring",
        "2": "summer",
        "3": "autumn",
    }
    season_key = num_map.get(arg, arg)

    if season_key not in SEASONS:
        print(
            f"Error: Invalid season '{sys.argv[1]}'."
            " Choose winter, spring, summer or autumn."
        )
        sys.exit(1)

    return SEASONS[season_key]


def simulate_day(config: dict[str, float]) -> None:
    total_slices = 48  # 24 hours * 2 (30 min slices)

    for slices_index in range(total_slices):
        radians = (slices_index - 18) * (2 * math.pi / total_slices)
        base_temp = config["avg"] + config["amp"] * math.sin(radians)

        noise = random.uniform(-0.3, 0.3)
        current_temp = round(base_temp + noise, 1)

        print(f"{current_temp}", flush=True)
        time.sleep(1)


def main() -> None:
    simulate_day(parse_season())


if __name__ == "__main__":
    main()
