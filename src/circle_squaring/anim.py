"""Animate the equidecomposition: pieces slide from the disk to the square.

Each piece travels in a straight line along the shortest torus representative
of its displacement, with smoothstep easing and hold frames at both ends.
Mid-flight overlaps are expected (the pieces only tile at t = 0 and t = 1).
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from .pieces import Piece
from .viz import piece_colors


def _smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def _centered(delta: int, n: int) -> int:
    """Representative of delta mod n in (-n/2, n/2], for short visual travel."""
    return delta - n if delta > n // 2 else delta


def render_animation(
    pieces: list[Piece],
    n: int,
    out_path: str,
    frames: int = 40,
    hold: int = 10,
    scale: int = 4,
    ms_per_frame: int = 50,
) -> None:
    colors = [
        tuple(int(255 * c) for c in color) for color in piece_colors(len(pieces))
    ]
    moves = [
        (piece, (_centered(piece.delta[0], n), _centered(piece.delta[1], n)))
        for piece in pieces
    ]

    images = []
    ts = [0.0] * hold + [i / (frames - 1) for i in range(frames)] + [1.0] * hold
    for t in ts:
        s = _smoothstep(t)
        img = np.full((n, n, 3), 255, dtype=np.uint8)
        # Large pieces first so small ones stay visible during overlaps.
        for (piece, (mx, my)), color in zip(moves, colors):
            ox = int(round(s * mx))
            oy = int(round(s * my))
            for x, y in piece.points:
                img[(y + oy) % n, (x + ox) % n] = color
        img = np.flipud(img)  # y up, matching the PNG renderer
        frame = Image.fromarray(img).resize((n * scale, n * scale), Image.NEAREST)
        images.append(frame)

    images[0].save(
        out_path,
        save_all=True,
        append_images=images[1:],
        duration=ms_per_frame,
        loop=0,
    )
