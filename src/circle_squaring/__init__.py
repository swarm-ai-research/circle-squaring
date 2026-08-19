"""Discrete analogue of Tarski's circle squaring via bounded-distance matching."""

from .anim import render_animation
from .graph import displacement_table, random_vectors
from .local_rounding import toast_matching
from .matching import bounded_matching, hopcroft_karp, min_cost_matching
from .pieces import Piece, extract_pieces, verify
from .shapes import disk_and_square
from .toast import build_toast

__all__ = [
    "Piece",
    "bounded_matching",
    "build_toast",
    "disk_and_square",
    "displacement_table",
    "extract_pieces",
    "hopcroft_karp",
    "min_cost_matching",
    "random_vectors",
    "render_animation",
    "toast_matching",
    "verify",
]
