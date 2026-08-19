# Toast-style local rounding on the finite torus

`--matcher toast` implements the finite analogue of the central construction
in Máthé–Noel–Pikhurko (arXiv:2202.01412): turning a *local real-valued* flow
into an *exact integer* flow by an online algorithm that commits final values
region by region, with no lookahead and no revision. This note maps each
ingredient to its continuum counterpart and records what the finite model can
and cannot capture.

## The pipeline (`local_rounding.py`, `toast.py`)

| Paper (continuum) | This demo (finite torus) |
|---|---|
| Local approximations `f_m` to a demand-meeting real flow (Marks–Unger) | `diffusion_flow`: m rounds of lazy diffusion of `χ = 1_A − 1_B` on `G_d`; each round is 1-local, so `f` is an m-local function of A, B. Invariant `div f + ρ = χ` held exactly; residual `‖ρ‖∞` decays geometrically (~2·10⁻³ after 30 rounds at N=128). |
| Toast sequence: strip-built sets with bounded, well-separated components (Def. 2.14) | `build_toast`: cover by images of 5³ lattice boxes under `n⃗ ↦ Σ nᵢxᵢ` — the sets with genuine `G_d`-structure (embedded 3D king-move grids). Euclidean tiles are useless here: under random-jump generators their induced `G_d`-subgraphs are nearly edgeless. |
| Online rounding: at step i, commit final integer values on all edges meeting `J_i`, from bounded-radius information; small cumulative errors are absorbed by rounding to the nearest consistent integer | `online_round`: same commitment discipline. Tentative value = `round(f)`; each block vertex's integer error is repaired by unit pushes along uncommitted edges to an opposite-sign vertex in-block or into still-free territory. Repairs are local (max path 12 at N=128). |
| Re-running Marks–Unger machinery on the co-null leftover | The **crust**: a reserved 13³ lattice box processed last. Its internal edges are untouched until then, its induced graph is connected, and conservation forces its errors to sum to zero — so the final step always closes. |
| Bounded integer flow → bijection → pieces (Lemma 2.16) | `decompose`: exact flow splits into |A| unit disk→square paths (cycles excised); summed generator labels give each piece's translation. |

The result is checked, not hoped: `div g = χ` is asserted exactly, and the
downstream `verify()` confirms the pieces tile both shapes.

## The ordering theorem (what replaced "separation")

The paper's separation conditions guarantee that independent local decisions
never conflict. At finite scale true separation is impossible — `G_d` on
`Z_128²` has diameter ~4 — and its absence bites: with a naive processing
order the rounding **strands** (a late block holds an error vertex whose
entire neighborhood is already committed; observed at N=64, block 88 of 192).

The fix is an ordering with a one-line proof. Peel shells inward by
`G_d`-distance to the crust, outermost first:

> Every vertex at distance t has, by BFS structure, a neighbor at distance
> t − 1, which is processed strictly later — hence still free, with the
> connecting edge uncommitted, when the vertex's own block commits. So error
> routing always has a depth-1 escape. The crust closes last: balanced by
> conservation, routable by connectedness.

A first attempted fix — process vertices *without* crust neighbors first —
fails instructively: the crust's `G_d`-neighborhood is not a spread-out
random set but just the dilated lattice box, so almost no vertex has a crust
neighbor. Both failures are worth keeping in mind when reading the paper:
they are the finite shadows of exactly the difficulties its toast
construction is engineered to avoid.

## Measured results (N=128, side 40, seed 0, defaults)

- 1374 blocks (5³ lattice boxes ∩ shells) + crust; total runtime ~1 s
- 3,848 unit repairs, max repair path **12** (locality is real)
- max deviation of the integer flow from the real flow: **7.0**
- diffusion residual `‖ρ‖∞`: 2·10⁻³ after 30 rounds
- **186 pieces at radius 26** — versus 19 pieces for the global min-cost
  matcher on the same instance

That last line is the demo's best lesson: locality costs pieces. The paper
pays ~10²⁰⁰ pieces for a construction whose every piece is locally
determined; here the same trade appears at toy scale as 186 vs. 19.

## What the finite model still cannot capture

- **Meaningful locality radii.** `f` is m-local with m = 30, but the whole
  graph has diameter ~4, so "local" is trivially "global" at this scale. The
  continuum statement — pieces that are bounded-radius Boolean combinations
  of translates of A, B, and strips — has no finite-N content.
- **Borel complexity and boundary dimension.** Finite sets are all alike;
  Σ⁰₂ vs Σ⁰₄ and Minkowski dimension 1.987 live strictly in the continuum.
- **True toast separation.** Components at pairwise distance ≥ 3 with nesting
  (Def. 2.14) requires room that exists only as N → ∞; the shell ordering is
  a provable finite substitute, not an implementation of Def. 2.14.
