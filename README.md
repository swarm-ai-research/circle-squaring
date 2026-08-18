# circle-squaring

A computational demo of **Tarski's circle squaring**, modeled on the construction in
Máthé, Noel & Pikhurko, *Circle Squaring with Pieces of Small Boundary and Low Borel
Complexity* ([arXiv:2202.01412](https://arxiv.org/abs/2202.01412), Advances in
Mathematics 484, 2026).

The continuum theorem: a disk and a square of equal area are equidecomposable
**by translations alone**, with Borel pieces of positive measure whose boundaries
have upper Minkowski dimension below 2. This repo runs the same pipeline on a
discrete torus, where every step is finite and checkable, and draws the pieces.

![example](assets/example.png)

*1600 points, 35 pieces, every piece moved by a single translation. Same color =
same piece.*

## What it does

Working on the discrete torus `Z_N × Z_N`:

1. **Shapes** (`shapes.py`) — a `side × side` square `B`, and a "disk" `A` defined as
   the `side²` grid points nearest a center: exact area matching, the discrete
   `λ(A) = λ(B)`.
2. **Translation graph** (`graph.py`) — `d` random vectors `x_1..x_d` generating the
   graph `G_d`: `u` is adjacent to `u + Σ nᵢxᵢ` for small integer `nᵢ`. Vector sets
   that only generate a sublattice are rejected (rank 2 mod every prime dividing `N`)
   — the discrete analogue of the paper's "no rational dependencies" property (2.11).
3. **Bounded matching** (`matching.py`) — a perfect matching `A → B` along `G_d`
   edges via Hopcroft–Karp, escalating the radius `r = 1, 2, …` and extending the
   matching at each stage, so displacements stay short. This replaces the paper's
   bounded integer-valued flow (their Lemma 2.16 reduction); the fact that a small
   `r` works is the discrete shadow of Laczkovich's discrepancy bounds.
4. **Pieces** (`pieces.py`) — matched pairs grouped by displacement: each piece is
   translated by a single vector `Σ nᵢxᵢ`. `verify()` checks the pieces partition
   the disk and their translates partition the square exactly.
5. **Render** (`viz.py`) — both shapes colored by piece.

## Usage

```sh
PYTHONPATH=src python3 -m circle_squaring --n 128 --side 40 --d 3 --seed 0 --out out
```

Outputs `out/pieces.png` and `out/stats.json`. Typical run: 1600 points squared
into a square in ~0.05 s with ~35 pieces at radius 2.

Tests:

```sh
python3 tests/test_equidecomposition.py    # or: pytest tests/
```

Requires Python ≥ 3.10, numpy, matplotlib.

## What this is *not*

Honesty section. The hard parts of the real theorem have no finite content to
simulate, and this demo does not attempt them:

- **Axiom-of-choice-free structure.** On a finite torus everything is trivially
  "Borel". The paper's achievement — pieces that are Boolean combinations of F_σ
  sets with boundaries of Minkowski dimension < 2 — lives in the continuum.
- **Local rounding.** We find the matching *globally* with Hopcroft–Karp. The
  paper's central innovation is an *online, local* rounding of real-valued flows
  along a "toast sequence" of strip-built sets, so that each piece is a bounded-radius
  local function of the disk, the square, and the strips. See
  [docs/paper-notes.md](docs/paper-notes.md) for a walkthrough.
- **The null residue.** The continuum construction covers only a co-null set
  locally and re-runs Marks–Unger machinery on the leftover null set; a finite
  model has no null sets.

What *does* survive discretization — and is the point of the demo — is the
combinatorial core: random translation vectors make the disk and square so
evenly interleaved in `G_d` that a bounded-displacement bijection exists, and
grouping it by displacement *is* the equidecomposition.

## Layout

```
src/circle_squaring/   shapes, graph, matching, pieces, viz, CLI
tests/                 pipeline and unit tests (plain python or pytest)
docs/paper-notes.md    proof walkthrough of arXiv:2202.01412
assets/example.png     committed example render
```

## References

- A. Máthé, J. A. Noel, O. Pikhurko, arXiv:2202.01412.
- M. Laczkovich, *Equidecomposability and discrepancy: a solution of Tarski's
  circle-squaring problem*, Crelle 404 (1990).
- A. Marks, S. Unger, *Borel circle squaring*, Annals of Mathematics 186 (2017).
- Quanta Magazine, [*An Ancient Geometry Problem Falls to New Mathematical
  Techniques*](https://www.quantamagazine.org/an-ancient-geometry-problem-falls-to-new-mathematical-techniques-20220208/) (2022).
