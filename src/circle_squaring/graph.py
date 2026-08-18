"""The translation graph G_d on the discrete torus.

Continuum version (Mathe-Noel-Pikhurko, arXiv:2202.01412): fix random vectors
x_1..x_d in T^k and connect u to u + sum(n_i * x_i) for small integer n_i.
Discrete analogue: random vectors in Z_N^2, arithmetic mod N. Each admissible
integer vector n (with ||n||_inf <= r) induces one torus translation delta;
a matched pair at displacement delta belongs to the piece labeled by the
canonical n producing it.
"""

from __future__ import annotations

from itertools import product

import numpy as np

Vec = tuple[int, int]


def _prime_factors(n: int) -> list[int]:
    factors = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        factors.append(n)
    return factors


def _spans_torus(vectors: list[Vec], n: int) -> bool:
    """True iff integer combinations of the vectors reach all of Z_n x Z_n.

    Equivalent to the vectors having rank 2 mod every prime dividing n --
    the discrete analogue of the paper's "no rational dependencies" condition
    (their property (2.11)). Without it, points outside the generated
    sublattice can never be matched.
    """
    for p in _prime_factors(n):
        rank_two = False
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                (a, b), (c, e) = vectors[i], vectors[j]
                if (a * e - b * c) % p != 0:
                    rank_two = True
        if not rank_two:
            return False
    return True


def random_vectors(d: int, n: int, seed: int) -> list[Vec]:
    if d < 2:
        raise ValueError("need d >= 2 vectors to span the torus")
    rng = np.random.default_rng(seed)
    while True:
        vectors: list[Vec] = []
        while len(vectors) < d:
            v = (int(rng.integers(0, n)), int(rng.integers(0, n)))
            if v != (0, 0) and v not in vectors:
                vectors.append(v)
        if _spans_torus(vectors, n):
            return vectors


def displacement_table(
    vectors: list[Vec], r: int, n: int
) -> dict[Vec, tuple[int, ...]]:
    """Map each realizable torus displacement to its canonical integer label.

    Enumerates n_vec in {-r..r}^d and computes delta = sum(n_i * x_i) mod N.
    When several labels collide on one delta, the one minimizing
    (||n||_inf, ||n||_1, lex) wins, so pieces prefer short labels.
    The zero displacement is dropped: A and B are disjoint, so it never
    matches anything, and dropping it keeps every piece a real move.
    """
    d = len(vectors)
    table: dict[Vec, tuple[int, ...]] = {}
    for n_vec in product(range(-r, r + 1), repeat=d):
        if all(c == 0 for c in n_vec):
            continue
        dx = sum(c * v[0] for c, v in zip(n_vec, vectors)) % n
        dy = sum(c * v[1] for c, v in zip(n_vec, vectors)) % n
        delta = (dx, dy)
        if delta == (0, 0):
            continue
        key = (max(abs(c) for c in n_vec), sum(abs(c) for c in n_vec), n_vec)
        if delta not in table or key < (
            max(abs(c) for c in table[delta]),
            sum(abs(c) for c in table[delta]),
            table[delta],
        ):
            table[delta] = n_vec
    return table
