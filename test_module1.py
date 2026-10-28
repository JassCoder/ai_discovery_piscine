
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent

SOLVERS = {
    "ex00": ROOT / "module1/puzzle_solver.py",
    "ex01": ROOT / "module1/puzzle_solver_ad.py",
}

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def run_solver(path, state=None):
    command = [sys.executable, str(path)]

    if state is not None:
        command.extend(map(str, state))

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30,
    )


def get_steps(output):
    steps = []

    pattern = (
        r"Step \d+:\s*\n"
        r"(\d+ \d+ \d+)\s*\n"
        r"(\d+ \d+ \d+)\s*\n"
        r"(\d+ \d+ \d+)"
    )

    for match in re.finditer(pattern, output):
        values = tuple(
            int(n)
            for line in match.groups()
            for n in line.split()
        )
        steps.append(values)

    return steps


def is_legal_move(before, after):
    if sorted(before) != list(range(9)):
        return False

    if sorted(after) != list(range(9)):
        return False

    zero_before = before.index(0)
    zero_after = after.index(0)

    row1, col1 = divmod(zero_before, 3)
    row2, col2 = divmod(zero_after, 3)

    if abs(row1 - row2) + abs(col1 - col2) != 1:
        return False

    expected = list(before)
    expected[zero_before], expected[zero_after] = (
        expected[zero_after],
        expected[zero_before],
    )

    return tuple(expected) == after


class TestModule1(unittest.TestCase):

    def test_files_exist(self):
        for name, path in SOLVERS.items():
            with self.subTest(exercise=name):
                self.assertTrue(path.is_file())

    def test_solvable_two_moves(self):
        start = (1, 2, 3, 4, 0, 6, 7, 5, 8)

        for name, path in SOLVERS.items():
            with self.subTest(exercise=name):
                result = run_solver(path, start)

                self.assertEqual(result.returncode, 0)
                self.assertIn("2 steps" if name == "ex00"
                              else "2 moves", result.stdout)

                steps = get_steps(result.stdout)

                self.assertEqual(len(steps), 2)
                self.assertEqual(steps[-1], GOAL)

                previous = start

                for state in steps:
                    self.assertTrue(
                        is_legal_move(previous, state)
                    )
                    previous = state

    def test_unsolvable(self):
        start = (1, 2, 3, 4, 5, 6, 8, 7, 0)

        for name, path in SOLVERS.items():
            with self.subTest(exercise=name):
                result = run_solver(path, start)

                self.assertEqual(result.returncode, 0)
                self.assertIn(
                    "Puzzle is unsolvable!",
                    result.stdout,
                )

    def test_already_solved(self):
        for name, path in SOLVERS.items():
            with self.subTest(exercise=name):
                result = run_solver(path, GOAL)

                self.assertEqual(result.returncode, 0)
                self.assertIn(
                    "0 steps" if name == "ex00"
                    else "0 moves",
                    result.stdout,
                )
                self.assertEqual(get_steps(result.stdout), [])

    def test_one_move(self):
        start = (1, 2, 3, 4, 5, 6, 7, 0, 8)

        for name, path in SOLVERS.items():
            with self.subTest(exercise=name):
                result = run_solver(path, start)
                steps = get_steps(result.stdout)

                self.assertEqual(result.returncode, 0)
                self.assertEqual(steps, [GOAL])

    def test_invalid_arguments(self):
        cases = [
            ["1", "2", "3"],
            ["1", "2", "3", "4", "5", "6", "7", "7", "0"],
            ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            ["1", "2", "3", "4", "5", "6", "7", "8", "abc"],
        ]

        for name, path in SOLVERS.items():
            for args in cases:
                with self.subTest(exercise=name, args=args):
                    result = run_solver(path, args)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Error:", result.stderr)

    def test_random_generation(self):
        for name, path in SOLVERS.items():
            with self.subTest(exercise=name):
                result = run_solver(path)

                self.assertEqual(result.returncode, 0)
                self.assertIn(
                    "Initial state of the puzzle:",
                    result.stdout,
                )

                lines = result.stdout.splitlines()
                initial = tuple(
                    int(n)
                    for line in lines[1:4]
                    for n in line.split()
                )

                self.assertEqual(
                    sorted(initial),
                    list(range(9)),
                )

    def test_advanced_shortest_path(self):
        path = SOLVERS["ex01"]

        start = (1, 2, 3, 4, 5, 6, 0, 7, 8)
        result = run_solver(path, start)

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "Shortest path found: 2 moves",
            result.stdout,
        )
        self.assertEqual(len(get_steps(result.stdout)), 2)

    def test_advanced_solution_reporting(self):
        path = SOLVERS["ex01"]
        start = (1, 2, 3, 4, 0, 6, 7, 5, 8)

        result = run_solver(path, start)

        self.assertEqual(result.returncode, 0)
        self.assertRegex(
            result.stdout,
            r"Solving in \d+ moves",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
