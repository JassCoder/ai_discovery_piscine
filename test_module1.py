

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EX00 = ROOT / 'module1/puzzle_solver.py'
EX01 = ROOT / 'module1/puzzle_solver_ad.py'
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
CASES = (
    ('two moves from the centre', (1, 2, 3, 4, 0, 6, 7, 5, 8), 2),
    ('two moves from the bottom left', (1, 2, 3, 4, 5, 6, 0, 7, 8), 2),
    ('one move away', (1, 2, 3, 4, 5, 6, 7, 0, 8), 1),
)


def run(path, state=None):
    command = [sys.executable, str(path)]
    if state is not None:
        command.extend(map(str, state))
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30,
    )


def steps_from(output):
    blocks = re.findall(r'^Step\s+(\d+):\s*\n((?:[^\n]*\n){2}[^\n]*)', output, re.M)
    steps = []
    for expected_number, (number, block) in enumerate(blocks, 1):
        if int(number) != expected_number:
            raise AssertionError(f'Incorrect step numbering: {number} != {expected_number}')
        try:
            state = tuple(int(x) for x in block.split())
        except ValueError as error:
            raise AssertionError(f'Non-numeric puzzle state at step {number}') from error
        if len(state) != 9 or set(state) != set(range(9)):
            raise AssertionError(f'Invalid grid at step {number}: {state}')
        steps.append(state)
    return steps


def initial_from(output):
    match = re.search(r'^Initial state of the puzzle:\s*\n((?:[^\n]*\n){2}[^\n]*)', output, re.M)
    if match is None:
        raise AssertionError('Missing initial puzzle heading/grid')
    try:
        values = tuple(int(x) for x in match.group(1).split())
    except ValueError as error:
        raise AssertionError('Invalid initial puzzle') from error
    if len(values) != 9 or set(values) != set(range(9)):
        raise AssertionError(f'Invalid initial state: {values}')
    return values


def legal_transition(before, after):
    a, b = before.index(0), after.index(0)
    r1, c1 = divmod(a, 3)
    r2, c2 = divmod(b, 3)
    if abs(r1 - r2) + abs(c1 - c2) != 1:
        return False
    expected = list(before)
    expected[a], expected[b] = expected[b], expected[a]
    return tuple(expected) == after


def validate_solution(test, result, initial, advanced, expected_moves):
    test.assertEqual(result.returncode, 0, result.stderr)
    test.assertEqual(initial_from(result.stdout), initial)
    test.assertIn('Solving the puzzle...', result.stdout)
    test.assertNotIn('Puzzle is unsolvable!', result.stdout)
    steps = steps_from(result.stdout)
    prefix = 'Shortest path found:' if advanced else 'Solution found in'
    label = 'moves' if advanced else 'steps.'
    pattern = rf'{re.escape(prefix)}\s*(\d+)\s*{re.escape(label)}'
    found = re.search(pattern, result.stdout)
    test.assertIsNotNone(found, f'Missing solution count: {prefix}')
    test.assertEqual(int(found.group(1)), len(steps), 'Reported steps differ from printed steps')
    test.assertEqual(len(steps), expected_moves, 'Expected shortest move count')
    previous = initial
    for index, state in enumerate(steps, 1):
        test.assertTrue(legal_transition(previous, state), f'Illegal move at step {index}')
        previous = state
    test.assertEqual(previous, GOAL, 'Final state must be goal')

    if advanced:
        found_lengths = [int(n) for n in re.findall(r'^Solving in (\d+) moves\s*$', result.stdout, re.M)]
        test.assertTrue(found_lengths, 'Advanced exercise must report a discovered path length')
        test.assertEqual(len(found_lengths), len(set(found_lengths)), 'Repeated path lengths')
        test.assertTrue(all(n >= expected_moves for n in found_lengths))
        test.assertEqual(found_lengths[-1], expected_moves, 'Final discovered length must be shortest')

    return steps


class TestModule1(unittest.TestCase):
    def test_files_exist(self):
        self.assertTrue(EX00.is_file(), f'Missing: {EX00}')
        self.assertTrue(EX01.is_file(), f'Missing: {EX01}')

    def test_both_exercises_same_shortest_result(self):
        for name, state, moves in CASES:
            with self.subTest(case=name):
                basic = run(EX00, state)
                advanced = run(EX01, state)
                steps_basic = validate_solution(self, basic, state, False, moves)
                steps_advanced = validate_solution(self, advanced, state, True, moves)
                self.assertEqual(len(steps_basic), len(steps_advanced))
                # Different shortest sequences are allowed if both reach GOAL legally.

    def test_unsolvable_both(self):
        state = (1, 2, 3, 4, 5, 6, 8, 7, 0)
        for path in (EX00, EX01):
            with self.subTest(solver=path.name):
                result = run(path, state)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(initial_from(result.stdout), state)
                self.assertIn('Puzzle is unsolvable!', result.stdout)
                self.assertEqual(steps_from(result.stdout), [])

    def test_bad_inputs_both(self):
        invalid = [
            (1, 2, 3),
            (1, 2, 3, 4, 5, 6, 7, 7, 0),
            (1, 2, 3, 4, 5, 6, 7, 8, 9),
            (1, 2, 3, 4, 5, 6, 7, 8, 'abc'),
        ]
        for path in (EX00, EX01):
            for args in invalid:
                with self.subTest(solver=path.name, args=args):
                    result = run(path, args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Error:', result.stderr)

    def test_random_initial_state_both(self):
        for path in (EX00, EX01):
            with self.subTest(solver=path.name):
                result = run(path)
                self.assertEqual(result.returncode, 0, result.stderr)
                state = initial_from(result.stdout)
                self.assertIn('Solving the puzzle...', result.stdout)
                if 'Puzzle is unsolvable!' not in result.stdout:
                    steps = steps_from(result.stdout)
                    previous = state
                    for move in steps:
                        self.assertTrue(legal_transition(previous, move))
                        previous = move
                    self.assertEqual(previous, GOAL)


if __name__ == '__main__':
    unittest.main(verbosity=2)