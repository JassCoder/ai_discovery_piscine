import sys


SEASONS:dict[str, dict[str, float]] = {
        "winter": {"avg": 0.0 , "amp": 5.0},
        "spring": {"avg": 11.5 , "amp": 6.5}, 
        "summer": {"avg": 22.5 , "amp": 7.5},
        "autumn": {"avg": 8.0, "amp": 6.0},
        "fall": {"avg": 8.0 , "amp": 6.0},
        }

def parse_season() -> dict[str, float]:
    if len(sys.argv) < 2:
        print("Usage: environment.py <season>")
        sys.exit(1)