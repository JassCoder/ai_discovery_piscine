#!/usr/bin/env python3

import argparse
import random
import re
import subprocess
import sys
from dataclasses import dataclass


MIN_FREQUENCY = 45.0
MAX_FREQUENCY = 50.0
FREQUENCIES_PER_INDIVIDUAL = 4
LOCATION_NAMES = ("dorms", "kitchen", "showers", "cluster", "entrance")


@dataclass
class EvaluatedIndividual:
    frequencies: tuple[float, ...]
    scores: tuple[float, ...]

    @property
    def fitness(self) -> float:
        return sum(self.scores)


def random_individual() -> tuple[float, ...]:
    return tuple(
        random.uniform(MIN_FREQUENCY, MAX_FREQUENCY)
        for _ in range(FREQUENCIES_PER_INDIVIDUAL)
    )


def create_population(size: int) -> list[tuple[float, ...]]:
    if size < 2:
        raise ValueError("Population size must be at least 2.")
    return [random_individual() for _ in range(size)]


def evaluate(individual: tuple[float, ...], executable: str) -> tuple[float, ...]:
    command = [executable, *(f"{value:.2f}" for value in individual)]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError(f"Could not run {executable}: {error}") from error

    scores = []
    for location in LOCATION_NAMES:
        match = re.search(
            rf"^\s*{location}\s*:\s*([-+]?\d+(?:\.\d+)?)\s*$",
            result.stdout,
            re.MULTILINE | re.IGNORECASE,
        )
        if match is None:
            raise RuntimeError(f"Missing score for {location}.")
        scores.append(float(match.group(1)))
    return tuple(scores)


def crossover(
    first: tuple[float, ...], second: tuple[float, ...]
) -> tuple[float, ...]:
    point = random.randint(1, FREQUENCIES_PER_INDIVIDUAL - 1)
    return first[:point] + second[point:]


def mutate(
    individual: tuple[float, ...], mutation_rate: float
) -> tuple[float, ...]:
    values = list(individual)
    for index, value in enumerate(values):
        if random.random() < mutation_rate:
            values[index] = random.uniform(MIN_FREQUENCY, MAX_FREQUENCY)
    return tuple(values)


def evolve(
    population: list[tuple[float, ...]],
    executable: str,
    generations: int,
    mutation_rate: float,
) -> EvaluatedIndividual:
    best: EvaluatedIndividual | None = None
    for generation in range(1, generations + 1):
        evaluated = [
            EvaluatedIndividual(individual, evaluate(individual, executable))
            for individual in population
        ]
        evaluated.sort(key=lambda individual: individual.fitness, reverse=True)
        best = evaluated[0] if best is None or evaluated[0].fitness > best.fitness else best
        print(
            f"Generation {generation}: "
            f"{' '.join(f'{value:.2f}' for value in best.frequencies)} "
            f"(fitness {best.fitness:.3f})"
        )

        survivors = evaluated[: max(2, len(evaluated) // 5)]
        next_population = [item.frequencies for item in survivors]
        while len(next_population) < len(population):
            parents = random.sample(survivors, 2)
            child = mutate(
                crossover(parents[0].frequencies, parents[1].frequencies),
                mutation_rate,
            )
            next_population.append(child)
        population = next_population
    if best is None:
        raise RuntimeError("At least one generation is required.")
    return best


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimize antenna frequencies.")
    parser.add_argument("--executable", default="./cellular")
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--population", type=int, default=1000)
    parser.add_argument("--mutation-rate", type=float, default=0.1)
    args = parser.parse_args()
    if args.generations < 1:
        parser.error("--generations must be positive")
    if not 0 <= args.mutation_rate <= 1:
        parser.error("--mutation-rate must be between 0 and 1")
    try:
        best = evolve(
            create_population(args.population),
            args.executable,
            args.generations,
            args.mutation_rate,
        )
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print("Best settings found:")
    print(" ".join(f"{value:.2f}" for value in best.frequencies))
    for name, score in zip(LOCATION_NAMES, best.scores):
        print(f"{name}: {score:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
