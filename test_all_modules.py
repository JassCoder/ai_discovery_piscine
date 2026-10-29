import io
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from module0.ex0 import environment
from module0.ex1 import expert_system
from module2 import weather_api
from module2.ex3 import weather_bot
from module3.ex0 import genetic_algorithms


class TestModule0(unittest.TestCase):
    def test_environment_accepts_named_and_numbered_seasons(self):
        with patch.object(sys, "argv", ["environment.py", "spring"]):
            self.assertEqual(environment.parse_season(), environment.SEASONS["spring"])
        with patch.object(sys, "argv", ["environment.py", "2"]):
            self.assertEqual(environment.parse_season(), environment.SEASONS["summer"])

    def test_environment_simulates_48_temperature_values(self):
        with patch("module0.ex0.environment.print") as print_mock:
            with patch("module0.ex0.environment.time.sleep"):
                with patch("module0.ex0.environment.random.uniform", return_value=0):
                    environment.simulate_day(environment.SEASONS["winter"])
        self.assertEqual(print_mock.call_count, 48)
        values = [float(call.args[0]) for call in print_mock.call_args_list]
        self.assertEqual(len(values), 48)
        self.assertTrue(all(-5 <= value <= 5 for value in values))

    def test_expert_system_heats_and_cools(self):
        heating = subprocess.run(
            [sys.executable, "module0/ex1/expert_system.py", "13", "15"],
            input="7.5\n",
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        cooling = subprocess.run(
            [sys.executable, "module0/ex1/expert_system.py", "13", "15"],
            input="16\n",
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(heating.returncode, 0)
        self.assertEqual(cooling.returncode, 0)
        self.assertIn("heating", heating.stdout)
        self.assertIn("cooling", cooling.stdout)

    def test_expert_system_rejects_reversed_thresholds(self):
        result = subprocess.run(
            [sys.executable, "module0/ex1/expert_system.py", "20", "10"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("minimum temperature", result.stdout)


class TestModule1Files(unittest.TestCase):
    def test_existing_module1_suite_passes(self):
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "test_module1.py"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class TestModule2(unittest.TestCase):
    def test_virtual_environment_exists(self):
        python = ROOT / "module2/.venv/bin/python"
        activate = ROOT / "module2/.venv/bin/activate"
        self.assertTrue(python.is_file(), f"Missing {python}")
        self.assertTrue(activate.is_file(), f"Missing {activate}")

    def test_weather_api_parses_current_weather(self):
        response = {
            "current": {
                "temperature_2m": 11,
                "relative_humidity_2m": 64,
                "cloud_cover": 72,
                "wind_speed_10m": 13,
            }
        }
        with patch.object(weather_api, "_get_json", return_value=response) as get_json:
            weather = weather_api.get_weather(48.86, 2.33)
        self.assertEqual(weather["temperature"], 11)
        self.assertEqual(weather["humidity"], 64)
        get_json.assert_called_once()

    def test_geolocation_returns_first_result(self):
        response = {
            "results": [{"name": "Paris", "latitude": 48.86, "longitude": 2.33}]
        }
        with patch.object(weather_api, "_get_json", return_value=response):
            self.assertEqual(
                weather_api.find_location("Paris"), ("Paris", 48.86, 2.33)
            )

    def test_weather_bot_extracts_location_and_describes_weather(self):
        self.assertEqual(
            weather_bot.extract_location("What is the weather in Paris?"),
            "Paris",
        )
        description = weather_bot.describe_weather(
            "Paris",
            {"temperature": 11, "humidity": 64, "cloud": 72, "wind": 13},
        )
        self.assertIn("Paris", description)
        self.assertIn("11.0 degrees", description)
        self.assertIn("13.0km/h", description)

    def test_weather_api_reports_missing_data(self):
        with patch.object(weather_api, "_get_json", return_value={"current": {}}):
            with self.assertRaises(ValueError):
                weather_api.get_weather(0, 0)


class TestModule3(unittest.TestCase):
    def test_population_and_mutation_stay_in_frequency_range(self):
        population = genetic_algorithms.create_population(10)
        self.assertEqual(len(population), 10)
        self.assertTrue(
            all(
                len(individual) == 4
                and all(45 <= value <= 50 for value in individual)
                for individual in population
            )
        )
        mutated = genetic_algorithms.mutate((45, 46, 47, 48), 1)
        self.assertTrue(all(45 <= value <= 50 for value in mutated))

    def test_evaluate_reads_all_five_cellular_scores(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "cellular"
            executable.write_text(
                "#!/bin/sh\n"
                "printf 'Cellular quality\\n'\n"
                "printf 'dorms   : 1.0\\n'\n"
                "printf 'kitchen : 2.0\\n'\n"
                "printf 'showers : 3.0\\n'\n"
                "printf 'cluster : 4.0\\n'\n"
                "printf 'entrance: 5.0\\n'\n"
            )
            executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
            scores = genetic_algorithms.evaluate((46, 47, 48, 49), str(executable))
        self.assertEqual(scores, (1, 2, 3, 4, 5))

    def test_genetic_algorithm_evolves_and_keeps_population_size(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "cellular"
            executable.write_text(
                "#!/bin/sh\n"
                "printf 'dorms: 1\\nkitchen: 1\\nshowers: 1\\n"
                "cluster: 1\\nentrance: 1\\n'\n"
            )
            executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
            population = genetic_algorithms.create_population(4)
            best = genetic_algorithms.evolve(
                population, str(executable), generations=2, mutation_rate=0.1
            )
        self.assertEqual(best.scores, (1, 1, 1, 1, 1))
        self.assertEqual(len(best.frequencies), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
