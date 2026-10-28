import random

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

def generate_puzzle() -> tuple[int, ...]:
    numbers = list(range(9))
    random.shuffle(numbers)
    return tuple(numbers)

def display_puzzle(state: tuple[int, ...]) -> None:
    for i in range(0, 9, 3):
        print(*state[i:i + 3])


def count_inversions(state: tuple[int, ...]):
    inversions = 0
    
    for i in range(9):
        for j in range(i + 1, 9):
            if state[i] != 0 and state[j] != 0:
                if state[i] > state[j]:
                    inversions += 1
    return inversions


def is_solvable(state: tuple[int, ...]) -> bool:
    inversions = count_inversions(state)
    return inversions % 2 == 0


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


def main() -> None:
    initial_state = generate_puzzle()

    print("Initial state of the puzzle:")
    display_puzzle(initial_state)

    print("Solving the puzzle...")

    if not is_solvable(initial_state):
        print("Puzzle is unsolvable!")
        return

    print("Puzzle is solvable!")
    print("Valid moves:", get_valid_moves(initial_state))

if __name__ == "__main__":
    main()
