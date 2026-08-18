"""CLI: run a discrete circle-squaring experiment and render the pieces.

    python -m circle_squaring --n 128 --side 40 --d 3 --seed 0 --out out
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .graph import random_vectors
from .matching import bounded_matching
from .pieces import extract_pieces, verify
from .shapes import disk_and_square
from .viz import render


def main() -> None:
    parser = argparse.ArgumentParser(description="Discrete circle squaring demo")
    parser.add_argument("--n", type=int, default=128, help="torus side length N")
    parser.add_argument("--side", type=int, default=40, help="square side (area = side^2)")
    parser.add_argument("--d", type=int, default=3, help="number of translation vectors")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed for the vectors")
    parser.add_argument("--r-max", type=int, default=8, help="max matching radius in G_d")
    parser.add_argument("--out", type=str, default="out", help="output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    disk, square = disk_and_square(args.n, args.side)
    vectors = random_vectors(args.d, args.n, args.seed)
    match_l, radius, table = bounded_matching(
        disk, square, vectors, args.n, r_max=args.r_max
    )
    pieces = extract_pieces(disk, square, match_l, table, args.n)
    verify(pieces, disk, square, args.n)
    elapsed = time.time() - t0

    stats = {
        "n": args.n,
        "side": args.side,
        "points_per_shape": args.side**2,
        "d": args.d,
        "seed": args.seed,
        "vectors": vectors,
        "radius": radius,
        "num_pieces": len(pieces),
        "largest_pieces": [len(p.points) for p in pieces[:10]],
        "elapsed_sec": round(elapsed, 2),
    }
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2))

    title = (
        f"N={args.n}, {args.side}²={args.side**2} points, d={args.d}, "
        f"r={radius}: {len(pieces)} pieces, translations only"
    )
    render(pieces, args.n, str(out_dir / "pieces.png"), title=title)

    print(f"verified equidecomposition: {len(pieces)} pieces at radius {radius}")
    print(f"wrote {out_dir / 'pieces.png'} and {out_dir / 'stats.json'} in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
