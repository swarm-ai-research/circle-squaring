"""Extract and verify the equidecomposition from a bounded matching.

Each piece is the set of disk points matched at one displacement; translating
piece P by its displacement lands it inside the square, and together the
translated pieces tile the square exactly. `verify` checks all of this and
raises on any violation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .graph import Vec


@dataclass
class Piece:
    label: tuple[int, ...]  # canonical integer vector n with delta = sum n_i x_i
    delta: Vec  # torus translation applied to this piece
    points: list[Vec]  # subset of the disk


def extract_pieces(
    a_points: list[Vec],
    b_points: list[Vec],
    match_l: list[int],
    table: dict[Vec, tuple[int, ...]],
    n: int,
) -> list[Piece]:
    by_delta: dict[Vec, list[Vec]] = {}
    for i, a in enumerate(a_points):
        b = b_points[match_l[i]]
        delta = ((b[0] - a[0]) % n, (b[1] - a[1]) % n)
        by_delta.setdefault(delta, []).append(a)
    pieces = [
        Piece(label=table[delta], delta=delta, points=pts)
        for delta, pts in by_delta.items()
    ]
    pieces.sort(key=lambda p: -len(p.points))
    return pieces


def verify(pieces: list[Piece], a_points: list[Vec], b_points: list[Vec], n: int) -> None:
    """Assert the pieces are a genuine equidecomposition of A into B."""
    covered_a: set[Vec] = set()
    covered_b: set[Vec] = set()
    for piece in pieces:
        pts = set(piece.points)
        if covered_a & pts:
            raise AssertionError("pieces overlap inside the disk")
        covered_a |= pts
        moved = {((x + piece.delta[0]) % n, (y + piece.delta[1]) % n) for x, y in pts}
        if len(moved) != len(pts):
            raise AssertionError("translation collapsed points")
        if covered_b & moved:
            raise AssertionError("translated pieces overlap inside the square")
        covered_b |= moved
    if covered_a != set(a_points):
        raise AssertionError("pieces do not cover the disk")
    if covered_b != set(b_points):
        raise AssertionError("translated pieces do not cover the square")
