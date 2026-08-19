"""Toast structure: cover the torus by images of small lattice boxes.

The paper's toast sequence (Definition 2.14) is built from strips whose
G_d-components are finite, uniformly bounded, and well separated. On a small
finite torus true separation is impossible (G_d has tiny diameter), but the
part that matters for the rounding algorithm survives: a cover by blocks with
genuine G_d-structure. A Euclidean tile is useless here -- the generators are
random jumps, so its induced G_d-subgraph is nearly edgeless. Instead each
block is the image of a small box in Z^d under n -> sum(n_i * x_i): inside
the injectivity radius this embeds as a d-dimensional grid with king-move
adjacency, connected and repair-friendly.

The final block (the "crust") is a larger reserved lattice box, processed
last. Its internal edges are untouched until then, its induced graph is
connected, and global flow conservation forces its integer errors to balance
-- so the last rounding step always succeeds. This mirrors the role of the
Marks-Unger rerun on the null residue in the continuum proof.

The processing order carries the guarantee the paper gets from its
separation conditions: blocks are peeled inward by G_d-distance to the
crust, outermost shell first. Every vertex at distance t has, by the BFS
tree structure, a neighbor at distance t - 1 -- which is processed strictly
later and is therefore still free when the vertex's own block commits. That
free neighbor is the escape hatch for error routing, so no repair can ever
strand. (A naive order genuinely strands: a late block can hold an error
vertex whose entire neighborhood is already committed -- observed, not
hypothetical.) The nesting of shells is the finite echo of the paper's
nested toast layers.
"""

from __future__ import annotations

from itertools import product

from .graph import Vec


def lattice_box_image(
    seed: Vec, dims: int, vectors: list[Vec], n: int
) -> list[Vec]:
    """Image of seed + {0..dims-1}^d under n -> sum(n_i x_i), deduplicated."""
    d = len(vectors)
    seen: set[Vec] = set()
    out: list[Vec] = []
    for n_vec in product(range(dims), repeat=d):
        x = (seed[0] + sum(c * v[0] for c, v in zip(n_vec, vectors))) % n
        y = (seed[1] + sum(c * v[1] for c, v in zip(n_vec, vectors))) % n
        if (x, y) not in seen:
            seen.add((x, y))
            out.append((x, y))
    return out


def _neighbor_offsets(vectors: list[Vec], n: int) -> list[Vec]:
    d = len(vectors)
    offsets = set()
    for n_vec in product((-1, 0, 1), repeat=d):
        if all(c == 0 for c in n_vec):
            continue
        gx = sum(c * v[0] for c, v in zip(n_vec, vectors)) % n
        gy = sum(c * v[1] for c, v in zip(n_vec, vectors)) % n
        if (gx, gy) != (0, 0):
            offsets.add((gx, gy))
    return sorted(offsets)


def _greedy_cover(
    domain: set[Vec], block: int, vectors: list[Vec], n: int
) -> list[list[Vec]]:
    uncovered = set(domain)
    blocks: list[list[Vec]] = []
    for x in range(n):
        for y in range(n):
            if (x, y) not in uncovered:
                continue
            box = [
                p for p in lattice_box_image((x, y), block, vectors, n) if p in uncovered
            ]
            uncovered -= set(box)
            blocks.append(box)
    return blocks


def crust_distances(
    crust_set: set[Vec], vectors: list[Vec], n: int
) -> dict[Vec, int]:
    """BFS distance in G_d from every vertex to the crust."""
    from collections import deque

    offsets = _neighbor_offsets(vectors, n)
    dist = {v: 0 for v in crust_set}
    queue = deque(crust_set)
    while queue:
        x, y = queue.popleft()
        for gx, gy in offsets:
            w = ((x + gx) % n, (y + gy) % n)
            if w not in dist:
                dist[w] = dist[(x, y)] + 1
                queue.append(w)
    if len(dist) != n * n:
        raise ValueError("G_d is not connected; vectors do not span the torus")
    return dist


def build_toast(
    vectors: list[Vec], n: int, block: int = 5, crust: int = 13
) -> list[list[Vec]]:
    """Ordered disjoint cover of Z_n x Z_n; see the module docstring.

    Shells at G_d-distance t from the crust are each covered by greedy
    block^d lattice boxes and processed outermost first; the crust box
    itself comes last.
    """
    crust_set = set(lattice_box_image((0, 0), crust, vectors, n))
    dist = crust_distances(crust_set, vectors, n)
    shells: dict[int, set[Vec]] = {}
    for v, t in dist.items():
        if t > 0:
            shells.setdefault(t, set()).add(v)
    blocks: list[list[Vec]] = []
    for t in sorted(shells, reverse=True):
        blocks += _greedy_cover(shells[t], block, vectors, n)
    blocks.append(sorted(crust_set))
    return blocks
