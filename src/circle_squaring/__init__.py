"""Discrete analogue of Tarski's circle squaring via bounded-distance matching."""

from .graph import displacement_table, random_vectors
from .matching import bounded_matching, hopcroft_karp
from .pieces import Piece, extract_pieces, verify
from .shapes import disk_and_square

__all__ = [
    "Piece",
    "bounded_matching",
    "disk_and_square",
    "displacement_table",
    "extract_pieces",
    "hopcroft_karp",
    "random_vectors",
    "verify",
]
