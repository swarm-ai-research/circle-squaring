"""Toast-style local rounding: the finite analogue of the paper's core proof.

Pipeline (mirroring Section 1.2 of arXiv:2202.01412):

1. `diffusion_flow` -- a real-valued flow meeting the demand chi = 1_A - 1_B
   approximately, built by m rounds of lazy diffusion on G_d. Each round is a
   1-local operation, so the flow is an m-local function of A and B: the
   finite stand-in for Marks-Unger's locally constructed approximations f_m.

2. `online_round` -- the toast rounding. Blocks arrive one at a time; every
   not-yet-committed edge touching the current block receives its FINAL
   integer value immediately (no lookahead, no revision). Tentative values
   come from rounding the diffusion flow; each block vertex's leftover
   integer error is repaired by pushing unit flows along uncommitted edges,
   either to an opposite-sign vertex in the block or out into still-free
   territory, which absorbs it the way the continuum algorithm's "wiggle
   room" does. The crust (last block) has no free territory left, but its
   errors sum to zero by conservation and its induced graph is connected,
   so internal routing always finishes. The result satisfies div g = chi
   EXACTLY -- checked, not hoped.

3. `decompose` -- the exact integer flow splits into |A| unit paths from the
   disk to the square (cycles excised on the fly); grouping matched pairs by
   displacement yields the pieces.

`toast_matching` chains the three and matches the interface of the other
matchers in `matching.py`.
"""

from __future__ import annotations

from collections import deque
from itertools import product

import numpy as np

from .graph import Vec
from .toast import build_toast

Label = tuple[int, ...]


def canonical_generators(vectors: list[Vec], n: int) -> list[tuple[Label, Vec]]:
    """One representative per +-pair of the (3^d - 1) generators of G_d."""
    d = len(vectors)
    gens = []
    for n_vec in product((-1, 0, 1), repeat=d):
        nz = [c for c in n_vec if c != 0]
        if not nz or nz[0] < 0:
            continue  # skip zero and keep the +representative of each pair
        gx = sum(c * v[0] for c, v in zip(n_vec, vectors)) % n
        gy = sum(c * v[1] for c, v in zip(n_vec, vectors)) % n
        gens.append((n_vec, (gx, gy)))
    return gens


def demand(a_points: list[Vec], b_points: list[Vec], n: int) -> np.ndarray:
    chi = np.zeros((n, n), dtype=np.int64)
    for x, y in a_points:
        chi[x, y] += 1
    for x, y in b_points:
        chi[x, y] -= 1
    return chi


def divergence(g: np.ndarray, gens: list[tuple[Label, Vec]]) -> np.ndarray:
    """div(g)[u] = net outflow at u; g[k, x, y] is flow along edge u -> u + gen_k."""
    div = np.zeros(g.shape[1:], dtype=g.dtype)
    for k, (_, (gx, gy)) in enumerate(gens):
        div += g[k] - np.roll(g[k], (gx, gy), axis=(0, 1))
    return div


def diffusion_flow(
    chi: np.ndarray, gens: list[tuple[Label, Vec]], rounds: int
) -> tuple[np.ndarray, np.ndarray]:
    """m rounds of lazy diffusion; returns (flow f, residual demand rho).

    Invariant maintained exactly: div(f) + rho = chi. The residual shrinks
    geometrically (spectral gap of the random Cayley graph); whatever is left
    is absorbed by the integer repairs in `online_round`.
    """
    n = chi.shape[0]
    deg = 2 * len(gens) + 1  # lazy: keep 1/deg, send 1/deg along each of the 2K arcs
    rho = chi.astype(np.float64)
    f = np.zeros((len(gens), n, n), dtype=np.float64)
    for _ in range(rounds):
        for k, (_, (gx, gy)) in enumerate(gens):
            f[k] += (rho - np.roll(rho, (-gx, -gy), axis=(0, 1))) / deg
        new = rho / deg
        for _, (gx, gy) in gens:
            new += np.roll(rho, (gx, gy), axis=(0, 1)) / deg
            new += np.roll(rho, (-gx, -gy), axis=(0, 1)) / deg
        rho = new
    return f, rho


def online_round(
    f: np.ndarray,
    chi: np.ndarray,
    blocks: list[list[Vec]],
    gens: list[tuple[Label, Vec]],
    n: int,
    max_bfs_depth: int = 12,
) -> tuple[np.ndarray, dict]:
    """Commit final integer values block by block; returns (g, stats)."""
    g = np.rint(f).astype(np.int64)
    committed = np.zeros(f.shape, dtype=bool)
    done = np.zeros((n, n), dtype=bool)
    repairs = 0
    max_path = 0

    for block in blocks:
        in_s = np.zeros((n, n), dtype=bool)
        for x, y in block:
            in_s[x, y] = True
        # Edge (u, u+gen_k) is active iff it touches the block and is uncommitted.
        active = np.zeros(f.shape, dtype=bool)
        for k, (_, (gx, gy)) in enumerate(gens):
            head_in_s = np.roll(in_s, (-gx, -gy), axis=(0, 1))  # in_s at u + gen
            active[k] = (in_s | head_in_s) & ~committed[k]

        err = {}
        div = divergence(g, gens)
        for v in block:
            e = int(chi[v] - div[v])
            if e:
                err[v] = e

        def neighbors(u: Vec):
            ux, uy = u
            for k, (_, (gx, gy)) in enumerate(gens):
                if active[k, ux, uy]:  # forward along edge u -> u+gen
                    yield ((ux + gx) % n, (uy + gy) % n), k, (ux, uy), +1
                tx, ty = (ux - gx) % n, (uy - gy) % n
                if active[k, tx, ty]:  # backward along edge (u-gen) -> u
                    yield (tx, ty), k, (tx, ty), -1

        for v in list(err):
            while err.get(v, 0) != 0:
                s = 1 if err[v] > 0 else -1  # push s units of extra outflow from v
                parent: dict[Vec, tuple] = {v: None}
                target = None
                queue = deque([(v, 0)])
                while queue:
                    u, depth = queue.popleft()
                    is_target = u != v and (
                        (not done[u] and not in_s[u])
                        or (in_s[u] and err.get(u, 0) * s < 0)
                    )
                    if is_target:
                        target = u
                        break
                    if depth >= max_bfs_depth:
                        continue
                    for w, k, tail, orient in neighbors(u):
                        if w not in parent:
                            parent[w] = (u, k, tail, orient)
                            queue.append((w, depth + 1))
                if target is None:
                    raise RuntimeError(
                        "toast repair stuck: no free or opposite-sign vertex "
                        "reachable; try a larger crust or more diffusion rounds"
                    )
                # Apply the unit push from v to target along the parent chain.
                path_len = 0
                u = target
                while parent[u] is not None:
                    prev, k, tail, orient = parent[u]
                    g[k][tail] += s * orient
                    u = prev
                    path_len += 1
                max_path = max(max_path, path_len)
                repairs += 1
                err[v] -= s
                if in_s[target]:
                    err[target] = err.get(target, 0) + s
        committed |= active
        done |= in_s

    final_div = divergence(g, gens)
    if not np.array_equal(final_div, chi):
        raise AssertionError("online rounding failed to meet demands exactly")
    stats = {
        "repairs": repairs,
        "max_repair_path": max_path,
        "max_deviation": float(np.max(np.abs(g - f))),
        "blocks": len(blocks),
    }
    return g, stats


def decompose(
    g: np.ndarray,
    a_points: list[Vec],
    b_points: list[Vec],
    gens: list[tuple[Label, Vec]],
    n: int,
) -> tuple[list[int], dict[Vec, Label]]:
    """Split the exact integer flow into |A| unit disk->square paths.

    Standard flow decomposition: walk positive remaining flow from each
    source until an unmatched sink; revisiting a vertex excises the loop
    (which cancels a cycle of g and is harmless). Each path's summed
    generator labels give the piece label for its displacement.
    """
    rem = g.copy()
    b_index = {b: j for j, b in enumerate(b_points)}
    matched = [False] * len(b_points)
    match_l = [-1] * len(a_points)
    table: dict[Vec, Label] = {}
    d = len(gens[0][0])

    for i, a in enumerate(a_points):
        u = a
        path: list[tuple[int, Vec, int]] = []  # (k, tail, orient)
        seen = {a: 0}
        while True:
            j = b_index.get(u)
            if j is not None and not matched[j]:
                break
            ux, uy = u
            step = None
            for k, (_, (gx, gy)) in enumerate(gens):
                if rem[k, ux, uy] > 0:
                    step = (k, (ux, uy), +1, ((ux + gx) % n, (uy + gy) % n))
                    break
                tx, ty = (ux - gx) % n, (uy - gy) % n
                if rem[k, tx, ty] < 0:
                    step = (k, (tx, ty), -1, (tx, ty))
                    break
            if step is None:
                raise AssertionError("flow decomposition stuck: conservation violated")
            k, tail, orient, w = step
            rem[k][tail] -= orient
            path.append((k, tail, orient))
            u = w
            if u in seen:  # excise the loop; its flow units stay cancelled
                del path[seen[u]:]
                seen = {p: idx for idx, p in enumerate(_path_vertices(a, path, gens, n))}
            else:
                seen[u] = len(path)
        j = b_index[u]
        matched[j] = True
        match_l[i] = j
        label = tuple(
            sum(orient * gens[k][0][c] for k, _, orient in path) for c in range(d)
        )
        delta = ((u[0] - a[0]) % n, (u[1] - a[1]) % n)
        best = table.get(delta)
        key = (max(map(abs, label)), sum(map(abs, label)), label)
        if best is None or key < (max(map(abs, best)), sum(map(abs, best)), best):
            table[delta] = label
    return match_l, table


def _path_vertices(start: Vec, path, gens, n: int) -> list[Vec]:
    out = [start]
    u = start
    for k, tail, orient in path:
        _, (gx, gy) = gens[k]
        if orient > 0:
            u = ((u[0] + gx) % n, (u[1] + gy) % n)
        else:
            u = ((u[0] - gx) % n, (u[1] - gy) % n)
        out.append(u)
    return out


def toast_matching(
    a_points: list[Vec],
    b_points: list[Vec],
    vectors: list[Vec],
    n: int,
    rounds: int = 30,
    block: int = 5,
    crust: int = 13,
    stats_out: dict | None = None,
) -> tuple[list[int], int, dict[Vec, Label]]:
    """Full toast pipeline; same interface as the matchers in matching.py."""
    gens = canonical_generators(vectors, n)
    chi = demand(a_points, b_points, n)
    f, rho = diffusion_flow(chi, gens, rounds)
    blocks = build_toast(vectors, n, block=block, crust=crust)
    g, stats = online_round(f, chi, blocks, gens, n, max_bfs_depth=max(12, crust + 2))
    match_l, table = decompose(g, a_points, b_points, gens, n)
    radius = max(max(map(abs, label)) for label in table.values())
    if stats_out is not None:
        stats_out.update(stats)
        stats_out["diffusion_rounds"] = rounds
        stats_out["residual_linf"] = float(np.max(np.abs(rho)))
    return match_l, radius, table
