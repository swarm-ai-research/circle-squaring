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


def test_min_cost_matching_verifies_and_uses_fewer_or_equal_pieces():
    from circle_squaring import min_cost_matching

    n, side = 64, 16
    disk, square = disk_and_square(n, side)
    vectors = random_vectors(3, n, seed=0)

    hk_match, _, hk_table = bounded_matching(disk, square, vectors, n)
    hk_pieces = extract_pieces(disk, square, hk_match, hk_table, n)

    mc_match, radius, mc_table = min_cost_matching(disk, square, vectors, n)
    assert sorted(mc_match) == list(range(side * side))
    mc_pieces = extract_pieces(disk, square, mc_match, mc_table, n)
    verify(mc_pieces, disk, square, n)
    assert len(mc_pieces) <= len(hk_pieces)
    assert all(max(abs(c) for c in p.label) <= radius for p in mc_pieces)


def test_animation_writes_gif(tmp_path=None):
    import tempfile
    from pathlib import Path

    from circle_squaring import min_cost_matching, render_animation

    n, side = 64, 12
    disk, square = disk_and_square(n, side)
    vectors = random_vectors(3, n, seed=0)
    match_l, _, table = min_cost_matching(disk, square, vectors, n)
    pieces = extract_pieces(disk, square, match_l, table, n)
    out_dir = Path(tmp_path) if tmp_path else Path(tempfile.mkdtemp())
    gif = out_dir / "anim.gif"
    render_animation(pieces, n, str(gif), frames=6, hold=2, scale=2)
    assert gif.stat().st_size > 0
    assert gif.read_bytes()[:6] in (b"GIF87a", b"GIF89a")


def test_toast_covers_torus_with_bounded_blocks():
    from circle_squaring import build_toast

    n = 64
    vectors = random_vectors(3, n, seed=0)
    blocks = build_toast(vectors, n, block=5, crust=9)
    flat = [p for block in blocks for p in block]
    assert len(flat) == n * n  # disjoint cover, nothing missing
    assert len(set(flat)) == n * n
    assert all(len(block) <= 5**3 for block in blocks[:-1])
    assert len(blocks[-1]) <= 9**3


def test_diffusion_flow_invariant():
    import numpy as np

    from circle_squaring.local_rounding import (
        canonical_generators,
        demand,
        diffusion_flow,
        divergence,
    )

    n = 64
    disk, square = disk_and_square(n, 16)
    vectors = random_vectors(3, n, seed=0)
    gens = canonical_generators(vectors, n)
    assert len(gens) == (3**3 - 1) // 2
    chi = demand(disk, square, n)
    f, rho = diffusion_flow(chi, gens, rounds=20)
    assert np.allclose(divergence(f, gens) + rho, chi)  # exact bookkeeping
    assert np.max(np.abs(rho)) < 0.05  # residual actually shrinks


def test_toast_matching_full_pipeline():
    from circle_squaring import toast_matching

    n, side = 64, 16
    disk, square = disk_and_square(n, side)
    vectors = random_vectors(3, n, seed=0)
    stats: dict = {}
    match_l, radius, table = toast_matching(
        disk, square, vectors, n, rounds=20, block=5, crust=9, stats_out=stats
    )
    assert sorted(match_l) == list(range(side * side))
    pieces = extract_pieces(disk, square, match_l, table, n)
    verify(pieces, disk, square, n)
    assert stats["max_deviation"] < 6  # integer flow stays near the real flow
    assert stats["max_repair_path"] <= 12  # repairs are local


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
