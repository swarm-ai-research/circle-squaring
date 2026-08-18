"""Bounded-distance perfect matching between the disk and the square.

The paper reduces circle squaring to finding a bijection A -> B moving every
point at most r steps in G_d (their Lemma 2.16 phrases it as a bounded
integer-valued flow). Here we find that bijection directly with
Hopcroft-Karp, escalating the radius r until a perfect matching exists --
the discrete stand-in for Laczkovich's discrepancy bounds, which guarantee
a finite r suffices in the continuum with probability 1.

Matchings found at radius r are kept and extended at radius r + 1, so the
final bijection is biased toward short displacements and few pieces.

`min_cost_matching` goes further: among all perfect matchings at the smallest
workable radius, it finds one minimizing the total displacement cost
sum(1 + ||n||_1), which concentrates the bijection on the cheapest few
displacements and typically cuts the piece count well below Hopcroft-Karp's.
"""

from __future__ import annotations

from .graph import Vec, displacement_table

INF = float("inf")


def hopcroft_karp(
    adj: list[list[int]],
    n_right: int,
    match_l: list[int] | None = None,
    match_r: list[int] | None = None,
) -> tuple[list[int], list[int]]:
    """Maximum bipartite matching, optionally extending an existing one."""
    n_left = len(adj)
    if match_l is None:
        match_l = [-1] * n_left
    if match_r is None:
        match_r = [-1] * n_right
    dist = [0.0] * n_left

    def bfs() -> bool:
        queue = []
        for u in range(n_left):
            if match_l[u] == -1:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = INF
        found = False
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            for v in adj[u]:
                w = match_r[v]
                if w == -1:
                    found = True
                elif dist[w] == INF:
                    dist[w] = dist[u] + 1
                    queue.append(w)
        return found

    def dfs(u: int) -> bool:
        for v in adj[u]:
            w = match_r[v]
            if w == -1 or (dist[w] == dist[u] + 1 and dfs(w)):
                match_l[u] = v
                match_r[v] = u
                return True
        dist[u] = INF
        return False

    while bfs():
        for u in range(n_left):
            if match_l[u] == -1:
                dfs(u)
    return match_l, match_r


def bounded_matching(
    a_points: list[Vec],
    b_points: list[Vec],
    vectors: list[Vec],
    n: int,
    r_max: int = 8,
) -> tuple[list[int], int, dict[Vec, tuple[int, ...]]]:
    """Perfect matching A -> B along G_d edges of the smallest workable radius.

    Returns (match_l, r, table) where match_l[i] is the index in b_points
    matched to a_points[i], r is the final radius, and table maps each
    displacement to its canonical integer label.
    """
    b_index = {b: i for i, b in enumerate(b_points)}
    match_l: list[int] | None = None
    match_r: list[int] | None = None
    for r in range(1, r_max + 1):
        table = displacement_table(vectors, r, n)
        adj: list[list[int]] = []
        for ax, ay in a_points:
            row = []
            for dx, dy in table:
                b = ((ax + dx) % n, (ay + dy) % n)
                j = b_index.get(b)
                if j is not None:
                    row.append(j)
            adj.append(row)
        match_l, match_r = hopcroft_karp(adj, len(b_points), match_l, match_r)
        if all(v != -1 for v in match_l):
            return match_l, r, table
    raise RuntimeError(
        f"no perfect matching up to radius {r_max}; "
        "try larger r_max, more vectors, or a different seed"
    )


def min_cost_matching(
    a_points: list[Vec],
    b_points: list[Vec],
    vectors: list[Vec],
    n: int,
    r_max: int = 8,
) -> tuple[list[int], int, dict[Vec, tuple[int, ...]]]:
    """Minimum-cost perfect matching A -> B; same interface as bounded_matching.

    Edge cost is 1 + ||n||_1 for the displacement's canonical label, so the
    optimum reuses the cheapest displacements as much as possible. Solved with
    scipy's sparse LAPJVsp; the radius escalates until a perfect matching
    exists, then one more optimization pass runs at that radius.
    """
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import min_weight_full_bipartite_matching

    b_index = {b: i for i, b in enumerate(b_points)}
    for r in range(1, r_max + 1):
        table = displacement_table(vectors, r, n)
        rows, cols, costs = [], [], []
        for i, (ax, ay) in enumerate(a_points):
            for (dx, dy), n_vec in table.items():
                j = b_index.get(((ax + dx) % n, (ay + dy) % n))
                if j is not None:
                    rows.append(i)
                    cols.append(j)
                    costs.append(1 + sum(abs(c) for c in n_vec))
        graph = csr_matrix(
            (np.array(costs), (np.array(rows), np.array(cols))),
            shape=(len(a_points), len(b_points)),
        )
        try:
            row_ind, col_ind = min_weight_full_bipartite_matching(graph)
        except ValueError:  # no perfect matching at this radius
            continue
        match_l = [-1] * len(a_points)
        for i, j in zip(row_ind, col_ind):
            match_l[i] = int(j)
        return match_l, r, table
    raise RuntimeError(
        f"no perfect matching up to radius {r_max}; "
        "try larger r_max, more vectors, or a different seed"
    )
