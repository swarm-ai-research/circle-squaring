# Notes on arXiv:2202.01412 (Máthé–Noel–Pikhurko)

*Circle Squaring with Pieces of Small Boundary and Low Borel Complexity.*
Based on the paper's introduction, Section 1.2 proof outline, and Section 2
preliminaries (v4, Nov 2025; published in Advances in Mathematics 484, 2026).

## Results

**Theorem 1.2.** In the plane, a closed disk and a closed square of the same
area are equidecomposable using translations so that every piece has boundary
of upper Minkowski dimension at most **1.987**, belongs to **𝓑(Σ⁰₂)** (Boolean
combinations of F_σ sets), and has **positive Lebesgue measure**. In particular
every piece is Jordan measurable — so arbitrarily large fractions of the
decomposition can be described exactly with finitely many bits.

**Theorem 1.3** (general form). For bounded `A, B ⊆ ℝᵏ` with
`λ(A) = λ(B) > 0` and `dim□(∂A), dim□(∂B) < k`, the sets are equidecomposable
by translations with (a) piece boundaries of dimension ≤ `k − ζ` (any
`ζ < 1/73` works for circle squaring), (b) pieces in a controlled low Borel
class, and (c) all pieces of positive measure under a mild extra hypothesis.

This improves Marks–Unger (Annals 2017), whose Borel pieces sat in 𝓑(Σ⁰₄) —
two hierarchy levels higher — and had no boundary-dimension control.

## Proof pipeline

1. **Torus reduction.** Scale `A`, `B` to diameter < 1/2, place disjointly in
   `[0,1)ᵏ`, work in `𝕋ᵏ = ℝᵏ/ℤᵏ`. Torus translations then agree with genuine
   translations.

2. **The graph `G_d`.** Pick random vectors `x₁,…,x_d ∈ 𝕋ᵏ` (for the circle
   `d = k + 1 = 3`). Connect `u` to `u + Σ nᵢxᵢ`, `n ∈ {−1,0,1}^d \ {0}`.
   Free action, so each component is a copy of the `ℤ^d` lattice; `G_d` is a
   Borel graph (descriptive graph combinatorics).

3. **Reduction to a bounded matching / flow** (Lemma 2.16, from Marks–Unger).
   A bijection `A → B` moving each point ≤ `r` steps in `G_d` gives an
   equidecomposition into ≤ `(2r+1)^d` pieces — pieces indexed by the integer
   displacement vector, each moved by one translation. Equivalently: a bounded
   integer-valued flow with demand `+1` on `A`, `−1` on `B`, `0` elsewhere.

4. **Laczkovich's discrepancy lemma** (Lemma 2.1). If `dim□(∂X) < k`, then
   with probability 1 the random vectors give, for every discrete
   `(n+1)`-cube `F`,
   `| |F ∩ X| − |F|·λ(X) | ≤ c·(n+1)^{d−1−ε}` —
   strictly below the cube's boundary size `~n^{d−1}`. Every large lattice
   cube holds almost exactly the right mass of `A` and `B`: a Hall condition
   with room to spare. This 1990s estimate powers the entire line of work.

5. **Real flows, locally.** Marks–Unger build a real-valued demand-meeting flow
   `f_∞` as a pointwise limit of flows `f_m` that are *local* — bounded-radius
   functions of `A` and `B`. Local functions of sets with small boundary have
   small boundary (Observation 2.6), so the game is to round to integers while
   staying local. The limit `f_∞` itself is not local; only the `f_m` are.

6. **Toast-sequence rounding — the paper's core novelty.** Build Jordan
   measurable sets `J₁, J₂, …`, each a finite union of strips
   `[a,b) × [0,1)^{k−1}`, with co-null union, forming a *toast sequence*
   (Def. 2.14): uniformly bounded finite components in `G_d`, layers either
   well-nested or ≥ 3 apart. Then run an **online algorithm**: at step `i`,
   commit final integer flow values on all edges meeting `Jᵢ`, using only a
   bounded neighborhood and the approximation `f_{mᵢ}` — no lookahead, no
   revision. If the cumulative error of `f_{mᵢ}` on each toast component is
   kept small, rounding to the nearest integer at any inconsistency stays
   exactly compatible with all past and future commitments. Every decision is
   local ⇒ pieces are Boolean combinations of translates of `A`, `B`, and
   strips ⇒ small boundary and low complexity.

7. **The null residue.** The toast covers only a co-null set. To get Borel
   pieces everywhere (not just AC-completion), the authors re-run the whole
   Marks–Unger argument on the null complement, having left "wiggle room" in
   the `Jᵢ` — the paper's most technical part, and where the two-level Borel
   complexity gain is realized.

8. **Positive measure** (part c). For each translation `t` used, pre-reserve a
   non-null set `A_t ⊆ (B − t) ∩ A` forced into that piece; check the main
   argument still runs on the rest.

## Sharpness

- `dim□(∂A) < k` cannot be relaxed to Hausdorff dimension ≤ `k−1`
  (Laczkovich: a countable union of convergent cubes not equidecomposable to a
  cube).
- Continuum many Jordan domains of volume 1 with everywhere-differentiable
  boundary, pairwise non-equidecomposable under any amenable isometry group
  (Laczkovich) — so translations-only results need the boundary hypothesis.
- Dubins–Hirsch–Karush: the disk is not *scissor-congruent* to a square
  (interior-disjoint Jordan-domain pieces); Gardner: no solution with a
  locally discrete isometry group. Open: the minimum number of pieces
  (known ≥ 3; Marks speculates possibly < 20).

## History

| Year | Result | Pieces / quality |
|---|---|---|
| 1925 | Tarski poses the problem | — |
| 1963 | Dubins–Hirsch–Karush | impossible with scissor cuts |
| 1990 | Laczkovich | ~10⁵⁰ pieces, AC, nonmeasurable |
| 2017 | Grabowski–Máthé–Pikhurko | measurable pieces, null set left over |
| 2017 | Marks–Unger | Borel pieces (𝓑(Σ⁰₄)), ~10²⁰⁰ |
| 2022 | Máthé–Noel–Pikhurko | 𝓑(Σ⁰₂), boundaries of dim ≤ 1.987, positive measure |
