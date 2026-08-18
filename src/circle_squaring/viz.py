"""Render the equidecomposition: disk and square, pieces in matching colors."""

from __future__ import annotations

import colorsys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .pieces import Piece


def piece_colors(count: int) -> list[tuple[float, float, float]]:
    """Distinct, stable colors; hue walks by golden angle so neighbors differ."""
    colors = []
    for i in range(count):
        hue = (i * 0.381966) % 1.0
        sat = 0.85 if i % 2 == 0 else 0.55
        val = 0.95 if i % 3 else 0.75
        colors.append(colorsys.hsv_to_rgb(hue, sat, val))
    return colors


def render(pieces: list[Piece], n: int, out_path: str, title: str = "") -> None:
    img = np.ones((n, n, 3))
    colors = piece_colors(len(pieces))
    for piece, color in zip(pieces, colors):
        for x, y in piece.points:
            img[y, x] = color
        for x, y in piece.points:
            tx = (x + piece.delta[0]) % n
            ty = (y + piece.delta[1]) % n
            img[ty, tx] = color

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(img, origin="lower", interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
