"""
N-Queens via a Genetic Algorithm.

Encoding:
    Each individual is a permutation of {0, 1, ..., N-1}. The position in
    the list is the column, the value is the row. A permutation guarantees
    no two queens share a column AND no two queens share a row, so the only
    conflicts left are diagonal ones. This is a very common trick for the
    N-Queens problem and makes the GA much more focused than a naive
    encoding.

Fitness:
    f(ind) = (max_possible_pairs) - diagonal_attacks(ind)
    where max_possible_pairs = N*(N-1)/2. Higher fitness is better, and a
    solution has fitness == max_possible_pairs (zero diagonal attacks).

Operators:
    - Tournament selection (size k).
    - Order Crossover (OX1) which preserves the permutation property.
    - Swap mutation: swap two random positions.
    - Elitism: copy the best individual into the next generation unchanged.
"""

import random
import time
import tracemalloc


def _diag_attacks(perm):
    n = len(perm)
    d1 = {}
    d2 = {}
    for c, r in enumerate(perm):
        d1[r - c] = d1.get(r - c, 0) + 1
        d2[r + c] = d2.get(r + c, 0) + 1
    a = 0
    for k in d1.values():
        if k > 1:
            a += k * (k - 1) // 2
    for k in d2.values():
        if k > 1:
            a += k * (k - 1) // 2
    return a


def _max_pairs(n):
    return n * (n - 1) // 2


def _fitness(perm):
    return _max_pairs(len(perm)) - _diag_attacks(perm)


def _random_permutation(n, rng):
    p = list(range(n))
    rng.shuffle(p)
    return p


def _tournament(population, fitnesses, rng, k=3):
    contenders = rng.sample(range(len(population)), k)
    best = max(contenders, key=lambda i: fitnesses[i])
    return population[best]


def _order_crossover(p1, p2, rng):
    """OX1 crossover: keep a random slice of p1, fill the rest from p2 in
    p2's order. Produces a valid permutation child.
    """
    n = len(p1)
    a, b = sorted(rng.sample(range(n), 2))
    child = [-1] * n
    child[a:b + 1] = p1[a:b + 1]
    used = set(child[a:b + 1])
    fill = [g for g in p2 if g not in used]
    idx = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = fill[idx]
            idx += 1
    return child


def _swap_mutate(perm, rng, p_mut):
    if rng.random() < p_mut:
        i, j = rng.sample(range(len(perm)), 2)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def solve_ga(
    n,
    pop_size=None,
    p_crossover=0.9,
    p_mutation=None,
    tournament_k=3,
    elitism=2,
    max_generations=None,
    time_limit=None,
    seed=None,
):
    """Run a genetic algorithm until a perfect solution is found, the
    generation budget is exhausted, or the time limit is hit.
    """
    rng = random.Random(seed)
    if pop_size is None:
        pop_size = min(400, max(50, n * 4))
    if p_mutation is None:
        # A little more mutation pressure for larger boards.
        p_mutation = min(0.9, 0.2 + 0.6 * (n / (n + 50)))
    if max_generations is None:
        max_generations = 5000 + 50 * n
    target = _max_pairs(n)
    start = time.perf_counter()

    population = [_random_permutation(n, rng) for _ in range(pop_size)]
    fitnesses = [_fitness(ind) for ind in population]

    best_idx = max(range(pop_size), key=lambda i: fitnesses[i])
    best = population[best_idx]
    best_fit = fitnesses[best_idx]

    generations = 0
    while generations < max_generations:
        if best_fit == target:
            return best, generations
        if time_limit is not None and (time.perf_counter() - start) > time_limit:
            return None, generations
        # Build the next generation
        # Elitism
        ranked = sorted(range(pop_size), key=lambda i: fitnesses[i], reverse=True)
        next_pop = [list(population[i]) for i in ranked[:elitism]]
        while len(next_pop) < pop_size:
            parent1 = _tournament(population, fitnesses, rng, k=tournament_k)
            parent2 = _tournament(population, fitnesses, rng, k=tournament_k)
            if rng.random() < p_crossover:
                child = _order_crossover(parent1, parent2, rng)
            else:
                child = list(parent1)
            _swap_mutate(child, rng, p_mutation)
            next_pop.append(child)
        population = next_pop
        fitnesses = [_fitness(ind) for ind in population]
        best_idx = max(range(pop_size), key=lambda i: fitnesses[i])
        if fitnesses[best_idx] > best_fit:
            best_fit = fitnesses[best_idx]
            best = population[best_idx]
        generations += 1
    if best_fit == target:
        return best, generations
    return None, generations


def is_valid_solution(state):
    if state is None:
        return False
    n = len(state)
    if sorted(state) != list(range(n)):
        return False
    return _diag_attacks(state) == 0


def run(n, time_limit=None, seed=None):
    tracemalloc.start()
    t0 = time.perf_counter()
    state, gens = solve_ga(n, time_limit=time_limit, seed=seed)
    elapsed = time.perf_counter() - t0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "Genetic",
        "n": n,
        "time_sec": elapsed,
        "peak_memory_kb": peak / 1024,
        "solved": is_valid_solution(state),
        "solution": state,
        "generations": gens,
    }


if __name__ == "__main__":
    for n in (8, 10, 30, 50):
        r = run(n, time_limit=30, seed=42)
        print(f"N={n}: solved={r['solved']}  time={r['time_sec']:.3f}s  "
              f"peak={r['peak_memory_kb']:.1f} KB  gens={r['generations']}")
