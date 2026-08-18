import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from circle_squaring import (
    bounded_matching,
    disk_and_square,
    displacement_table,
    extract_pieces,
    random_vectors,
    verify,
)
from circle_squaring.shapes import torus_dist2


def test_shapes_area_matched_and_disjoint():
    disk, square = disk_and_square(64, 20)
    assert len(disk) == len(square) == 400
    assert not set(disk) & set(square)


def test_torus_dist_wraps():
    assert torus_dist2((0, 0), (63, 0), 64) == 1
    assert torus_dist2((1, 1), (3, 62), 64) == 4 + 9


def test_displacement_table_prefers_short_labels():
    table = displacement_table([(1, 0), (0, 1)], 2, 64)
    assert table[(1, 0)] == (1, 0)
    assert table[(1, 1)] == (1, 1)
    assert (0, 0) not in table


def test_full_pipeline_small():
    n, side = 64, 16
    disk, square = disk_and_square(n, side)
    vectors = random_vectors(3, n, seed=0)
    match_l, radius, table = bounded_matching(disk, square, vectors, n)
    assert sorted(match_l) == list(range(side * side))  # a bijection
    pieces = extract_pieces(disk, square, match_l, table, n)
    verify(pieces, disk, square, n)
    assert sum(len(p.points) for p in pieces) == side * side
    assert all(max(abs(c) for c in p.label) <= radius for p in pieces)


def test_seed_changes_vectors_but_pipeline_still_verifies():
    n, side = 64, 16
    disk, square = disk_and_square(n, side)
    for seed in (1, 2):
        vectors = random_vectors(3, n, seed=seed)
        match_l, _, table = bounded_matching(disk, square, vectors, n)
        pieces = extract_pieces(disk, square, match_l, table, n)
        verify(pieces, disk, square, n)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    print("all tests passed")
