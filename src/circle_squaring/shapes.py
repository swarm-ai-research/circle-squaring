"""Area-matched shapes on the discrete torus Z_N x Z_N.

The continuum theorem needs lambda(A) = lambda(B); the discrete analogue is
|A| = |B| exactly. We take B to be a genuine side x side square and A to be
the side^2 grid points nearest to a chosen center under the torus metric --
a pixel-perfect "disk" whose cardinality matches the square's by construction.
"""

from __future__ import annotations


def torus_dist2(p: tuple[int, int], q: tuple[int, int], n: int) -> int:
    """Squared distance between p and q on the torus Z_n x Z_n."""
    dx = abs(p[0] - q[0])
    dy = abs(p[1] - q[1])
    dx = min(dx, n - dx)
    dy = min(dy, n - dy)
    return dx * dx + dy * dy


def make_square(n: int, side: int, corner: tuple[int, int]) -> list[tuple[int, int]]:
    x0, y0 = corner
    return [((x0 + i) % n, (y0 + j) % n) for i in range(side) for j in range(side)]


def make_disk(
    n: int, count: int, center: tuple[int, int], forbidden: set[tuple[int, int]]
) -> list[tuple[int, int]]:
    """The `count` grid points nearest to `center`, avoiding `forbidden`.

    Ties are broken lexicographically, so the shape is deterministic.
    """
    candidates = [
        (x, y) for x in range(n) for y in range(n) if (x, y) not in forbidden
    ]
    candidates.sort(key=lambda p: (torus_dist2(p, center, n), p))
    return candidates[:count]


def disk_and_square(
    n: int, side: int
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Disjoint area-matched disk A and square B on the torus Z_n x Z_n."""
    if side * side > n * n // 2:
        raise ValueError("side too large: shapes cannot be disjoint")
    corner = (n // 2 + n // 8, n // 2 - side // 2)
    square = make_square(n, side, corner)
    center = (n // 4, n // 2)
    disk = make_disk(n, side * side, center, forbidden=set(square))
    assert len(disk) == len(square) == side * side
    assert not set(disk) & set(square)
    return disk, square
