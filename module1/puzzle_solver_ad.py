
import heapq
import random
import sys
from itertools import count


GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def generate_puzzle() -> tuple[int, ...]:
    numbers = list(range(9))
    random.shuffle(numbers)
    return tuple(numbers)


def display_puzzle(state: tuple[int, ...]) -> None:
    for i in range(0, 9, 3):
        print(*state[i:i + 3])


def count_inversions(state: tuple[int, ...]) -> int:
    inversions = 0

    for i in range(9):
        for j in range(i + 1, 9):
            if state[i] != 0 and state[j] != 0:
                if state[i] > state[j]:
                    inversions += 1

    return inversions


def is_solvable(state: tuple[int, ...]) -> bool:
    return count_inversions(state) % 2 == 0


def get_valid_moves(state: tuple[int, ...]) -> list[int]:
    zero_index = state.index(0)
    row = zero_index // 3
    col = zero_index % 3

    moves = []

    if row > 0:
        moves.append(zero_index - 3)
    if row < 2:
        moves.append(zero_index + 3)
    if col > 0:
        moves.append(zero_index - 1)
    if col < 2:
        moves.append(zero_index + 1)

    return moves


def make_move(
    state: tuple[int, ...], target_index: int
) -> tuple[int, ...]:
    numbers = list(state)
    zero_index = numbers.index(0)

    numbers[zero_index], numbers[target_index] = (
        numbers[target_index],
        numbers[zero_index],
    )

    return tuple(numbers)


def manhattan_distance(state: tuple[int, ...]) -> int:
    distance = 0

    for index, value in enumerate(state):
        if value == 0:
            continue

        goal_index = value - 1

        current_row = index // 3
        current_col = index % 3
        goal_row = goal_index // 3
        goal_col = goal_index % 3

        distance += abs(current_row - goal_row)
        distance += abs(current_col - goal_col)

    return distance


def reconstruct_path(
    parents: dict,
    goal: tuple[int, ...],
) -> list[tuple[int, ...]]:
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parents[current]

    path.reverse()
    return path[1:]


def greedy_search(
    initial_state: tuple[int, ...],
) -> list[tuple[int, ...]] | None:
    queue = []
    counter = count()
    parents = {initial_state: None}

    heapq.heappush(
        queue,
        (manhattan_distance(initial_state),
         next(counter), initial_state),
    )

    while queue:
        _, _, current = heapq.heappop(queue)

        if current == GOAL:
            return reconstruct_path(parents, current)

        for target in get_valid_moves(current):
            next_state = make_move(current, target)

            if next_state not in parents:
                parents[next_state] = current

                heapq.heappush(
                    queue,
                    (manhattan_distance(next_state),
                     next(counter), next_state),
                )

    return None


def a_star(
    initial_state: tuple[int, ...],
) -> list[tuple[int, ...]] | None:
    queue = []
    counter = count()

    g_score = {initial_state: 0}
    parents = {initial_state: None}

    heapq.heappush(
        queue,
        (manhattan_distance(initial_state),
         0, next(counter), initial_state),
    )

    while queue:
        _, cost, _, current = heapq.heappop(queue)

        if cost != g_score[current]:
            continue

        if current == GOAL:
            return reconstruct_path(parents, current)

        for target in get_valid_moves(current):
            next_state = make_move(current, target)
            new_cost = cost + 1

            if new_cost < g_score.get(next_state, float("inf")):
                g_score[next_state] = new_cost
                parents[next_state] = current

                priority = new_cost + manhattan_distance(next_state)

                heapq.heappush(
                    queue,
                    (priority, new_cost,
                     next(counter), next_state),
                )

    return None


def solve_puzzle(
    initial_state: tuple[int, ...],
) -> list[tuple[int, ...]] | None:
    if not is_solvable(initial_state):
        return None

    first_path = greedy_search(initial_state)

    if first_path is not None:
        print(f"Solving in {len(first_path)} moves")

    shortest_path = a_star(initial_state)

    if shortest_path is None:
        return None

    if first_path is None or len(first_path) != len(shortest_path):
        print(f"Solving in {len(shortest_path)} moves")

    return shortest_path


def parse_initial_state() -> tuple[int, ...]:
    if len(sys.argv) == 1:
        return generate_puzzle()

    if len(sys.argv) != 10:
        raise ValueError("Provide exactly 9 integers from 0 to 8.")

    try:
        state = tuple(int(value) for value in sys.argv[1:])
    except ValueError:
        raise ValueError("All values must be integers.") from None

    if set(state) != set(range(9)):
        raise ValueError("Each number from 0 to 8 must appear once.")

    return state


def main() -> None:
    try:
        initial_state = parse_initial_state()
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print("Initial state of the puzzle:")
    display_puzzle(initial_state)
    print("Solving the puzzle...")

    solution = solve_puzzle(initial_state)

    if solution is None:
        print("Puzzle is unsolvable!")
        return

    print(f"Shortest path found: {len(solution)} moves")

    for step, state in enumerate(solution, start=1):
        print(f"Step {step}:")
        display_puzzle(state)


if __name__ == "__main__":
    main()
