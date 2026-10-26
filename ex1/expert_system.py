import sys


def main() -> None:
    if len(sys.argv) < 3:
        print("we need two arguments")
        sys.exit(1)

    try:
        min_temp = float(sys.argv[1])
        max_temp = float(sys.argv[2])
    except ValueError:
        print("Error: It should be numeric value")
        sys.exit(1)

    indoor_temp = None
    for line in sys.stdin:
        clean_line = line.strip()
        if not clean_line:
            continue

        ext_temp = float(clean_line)
        if indoor_temp is None:
            indoor_temp = ext_temp

        if indoor_temp < min_temp:
            action = "heating"
            indoor_temp += 0.5
        elif indoor_temp > max_temp:
            action = "cooling"
            indoor_temp -= 0.5
        else:
            action = "nothing"
            if indoor_temp < ext_temp:
                indoor_temp = min(indoor_temp + 0.25, ext_temp)
            elif indoor_temp > ext_temp:
                indoor_temp = max(indoor_temp - 0.25, ext_temp)

        print(f"{ext_temp} - {action} - {round(indoor_temp, 2)}", flush=True)


if __name__ == "__main__":
    main()
