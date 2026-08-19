"""CLI: run a discrete circle-squaring experiment and render the pieces.

    python -m circle_squaring --n 128 --side 40 --d 3 --seed 0 --out out
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .anim import render_animation
from .graph import random_vectors
from .local_rounding import toast_matching
from .matching import bounded_matching, min_cost_matching
from .pieces import extract_pieces, verify
from .shapes import disk_and_square
from .toast import build_toast
from .viz import render, render_toast


def main() -> None:
    parser = argparse.ArgumentParser(description="Discrete circle squaring demo")
    parser.add_argument("--n", type=int, default=128, help="torus side length N")
    parser.add_argument("--side", type=int, default=40, help="square side (area = side^2)")
    parser.add_argument("--d", type=int, default=3, help="number of translation vectors")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed for the vectors")
    parser.add_argument("--r-max", type=int, default=8, help="max matching radius in G_d")
    parser.add_argument(
        "--matcher",
        choices=["min-cost", "hopcroft-karp", "toast"],
        default="min-cost",
        help="min-cost minimizes total displacement (fewest pieces); "
        "toast runs the paper-style local online rounding",
    )
    parser.add_argument(
        "--rounds", type=int, default=30, help="toast: diffusion rounds for the real flow"
    )
    parser.add_argument("--block", type=int, default=5, help="toast: lattice block side")
    parser.add_argument("--crust", type=int, default=13, help="toast: final block side")
    parser.add_argument(
        "--no-gif", action="store_true", help="skip the sliding-pieces animation"
    )
    parser.add_argument("--frames", type=int, default=40, help="animation frames")
    parser.add_argument("--out", type=str, default="out", help="output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    disk, square = disk_and_square(args.n, args.side)
    vectors = random_vectors(args.d, args.n, args.seed)
    toast_stats: dict = {}
    if args.matcher == "toast":
        match_l, radius, table = toast_matching(
            disk,
            square,
            vectors,
            args.n,
            rounds=args.rounds,
            block=args.block,
            crust=args.crust,
            stats_out=toast_stats,
        )
    else:
        match = min_cost_matching if args.matcher == "min-cost" else bounded_matching
        match_l, radius, table = match(disk, square, vectors, args.n, r_max=args.r_max)
    pieces = extract_pieces(disk, square, match_l, table, args.n)
    verify(pieces, disk, square, args.n)
    elapsed = time.time() - t0

    stats = {
        "n": args.n,
        "side": args.side,
        "points_per_shape": args.side**2,
        "d": args.d,
        "seed": args.seed,
        "matcher": args.matcher,
        "vectors": vectors,
        "radius": radius,
        "num_pieces": len(pieces),
        "largest_pieces": [len(p.points) for p in pieces[:10]],
        "elapsed_sec": round(elapsed, 2),
    }
    if toast_stats:
        stats["toast"] = toast_stats
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2))

    title = (
        f"N={args.n}, {args.side}²={args.side**2} points, d={args.d}, "
        f"r={radius}: {len(pieces)} pieces, translations only"
    )
    render(pieces, args.n, str(out_dir / "pieces.png"), title=title)
    written = ["pieces.png", "stats.json"]
    if args.matcher == "toast":
        blocks = build_toast(vectors, args.n, block=args.block, crust=args.crust)
        render_toast(blocks, args.n, str(out_dir / "toast.png"))
        written.append("toast.png")
    if not args.no_gif:
        render_animation(pieces, args.n, str(out_dir / "animation.gif"), frames=args.frames)
        written.append("animation.gif")

    print(f"verified equidecomposition: {len(pieces)} pieces at radius {radius}")
    print(f"wrote {', '.join(str(out_dir / f) for f in written)} in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
