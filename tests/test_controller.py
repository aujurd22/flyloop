"""P73 controller tests: P01 dominance at law boundaries, P03 no-regression
in interior regimes, and the P74 cap*(r, D) crossover interpolation.
Run: python -m pytest tests/test_controller.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from flyloop.controller import CAP_STAR_KNOTS, cap_star, controller  # noqa: E402


# ---- fixed policies (the P01 comparison family) ------------------------------
def fixed_prototype(**kw):
    return "prototype"


def fixed_exemplar(**kw):
    return "exemplar"


def fixed_verification_thresholded(**kw):
    return "thresholded"


def fixed_eviction_lru(**kw):
    return "lru"


def base(**over):
    """A geometry deep inside the non-starved exemplar interior."""
    kw = dict(r=0.30, nn=0.4, ts=True, cov=1.0, clr=3.0, lq=4.0,
              ff=0.05, eps=0.1, D=6, cap=50)
    kw.update(over)
    return controller(**kw)


# ---- P74: cap*(r, D) interpolation -------------------------------------------
class TestCapStar:
    def test_exact_knots_d6(self):
        for r, c in CAP_STAR_KNOTS[6]:
            assert cap_star(r, D=6) == pytest.approx(c)

    def test_exact_knots_d12(self):
        for r, c in CAP_STAR_KNOTS[12]:
            assert cap_star(r, D=12) == pytest.approx(c)

    def test_linear_interpolation_midpoints(self):
        # D=6: 1/3/5/5 -> midpoints 2, 4, 5
        assert cap_star(0.20, D=6) == pytest.approx(2.0)
        assert cap_star(0.30, D=6) == pytest.approx(4.0)
        assert cap_star(0.40, D=6) == pytest.approx(5.0)
        # D=12: 1/2/8/12 -> midpoints 1.5, 5, 10
        assert cap_star(0.20, D=12) == pytest.approx(1.5)
        assert cap_star(0.30, D=12) == pytest.approx(5.0)
        assert cap_star(0.40, D=12) == pytest.approx(10.0)

    def test_fractional_interpolation(self):
        # a quarter of the way from knot 1 to knot 2, D=6: 1 + 0.25*2 = 1.5
        assert cap_star(0.175, D=6) == pytest.approx(1.5)
        # three quarters of the way from 2 to 8, D=12: 2 + 0.75*6 = 6.5
        assert cap_star(0.325, D=12) == pytest.approx(6.5)

    def test_floored_below_first_knot(self):
        assert cap_star(0.10, D=6) == pytest.approx(1.0)
        assert cap_star(0.00, D=12) == pytest.approx(1.0)

    def test_extrapolated_above_last_knot(self):
        # D=6 last segment is flat (5 -> 5)
        assert cap_star(0.60, D=6) == pytest.approx(5.0)
        assert cap_star(1.00, D=6) == pytest.approx(5.0)
        # D=12 last segment slope: (12-8)/0.10 = 40 per unit r
        assert cap_star(0.50, D=12) == pytest.approx(14.0)
        assert cap_star(0.55, D=12) == pytest.approx(16.0)

    def test_monotone_nondecreasing(self):
        for D in (6, 12):
            grid = [cap_star(r / 100, D=D) for r in range(0, 101)]
            assert all(a <= b for a, b in zip(grid, grid[1:]))

    def test_unregistered_dimension_rejected(self):
        with pytest.raises(ValueError):
            cap_star(0.25, D=8)

    def test_controller_carries_cap_star(self):
        assert base()["capacity"]["cap_star"] == pytest.approx(cap_star(0.30, D=6))
        assert base(D=12)["capacity"]["cap_star"] == pytest.approx(cap_star(0.30, D=12))


# ---- P73-P01: the controller switches at law boundaries, fixed policies can't
class TestP01DominanceAtBoundaries:
    def test_r_boundary_flips_type_under_starvation(self):
        # starved (cap <= cap*): prototype below r=0.5, exemplar above it.
        # A fixed policy holds one arm across the whole boundary.
        low = base(r=0.45, cap=1, ff=0.0)
        high = base(r=0.55, cap=1, ff=0.0)
        assert low["type"] == "prototype"
        assert high["type"] == "exemplar"
        assert low["type"] != fixed_exemplar(r=0.45)
        assert high["type"] != fixed_prototype(r=0.55)

    def test_r_boundary_is_exact(self):
        assert base(r=0.50, cap=1, ff=0.0)["type"] == "prototype"
        assert base(r=0.51, cap=1, ff=0.0)["type"] == "exemplar"

    def test_cap_star_boundary_flips_type(self):
        # r=0.25, D=6 -> cap*=3: capacity 3 is STARVED, capacity 4 is not.
        assert base(r=0.25, cap=3, ff=0.0)["type"] == "prototype"
        assert base(r=0.25, cap=4, ff=0.0)["type"] == "exemplar"
        assert base(r=0.25, cap=3, ff=0.0)["type"] != fixed_exemplar(r=0.25)
        assert base(r=0.25, cap=4, ff=0.0)["type"] != fixed_prototype(r=0.25)

    def test_lq_boundary_gates_retrieval(self):
        # lq < 1 -> unreliable (fixed no-gate policies always proceed).
        assert base(lq=0.99)["query_gate"] == "unreliable"
        assert base(lq=0.99)["query_gate"] != "proceed"
        assert base(lq=1.00)["query_gate"] == "proceed"

    def test_ff_boundary_mandates_exemplar(self):
        # ff > 0.1 forces exemplar even in the starved prototype window.
        assert base(r=0.20, cap=1, ff=0.05)["type"] == "prototype"
        assert base(r=0.20, cap=1, ff=0.15)["type"] == "exemplar"
        assert base(r=0.20, cap=1, ff=0.15)["type"] != fixed_prototype(r=0.20)

    def test_ts_boundary_flips_eviction(self):
        # without two-scale structure, core-first is wrong (P113): random.
        assert base(ts=True)["eviction"] == "core-first"
        assert base(ts=False)["eviction"] == "random"
        assert base(ts=False)["eviction"] != fixed_eviction_lru(r=0.30)


# ---- P73-P03: interior regimes match the best fixed policy -------------------
class TestP03NoRegressionInInterior:
    def test_interior_exemplar_regime(self):
        out = base()
        assert out["type"] == fixed_exemplar(r=0.30)
        assert out["eviction"] == "core-first"
        assert out["verification"] == fixed_verification_thresholded(r=0.30)
        assert out["query_gate"] == "proceed"
        assert out["novelty_screening"] == "enabled"
        # no boundary logic fired
        assert all("tie zone" not in n and "STARVED" not in n for n in out["notes"])

    def test_interior_prototype_regime(self):
        out = base(r=0.15, cap=1, ff=0.0)
        assert out["type"] == fixed_prototype(r=0.15)
        assert out["capacity"]["per_class"] == 1
        assert out["eviction"] == "none"

    def test_interior_unseparated_regime(self):
        out = base(r=0.80, cap=50)
        assert out["type"] == "exemplar"
        assert out["verification"] == "none"
        assert out["eviction"] == "core-first"
        assert out["query_gate"] == "proceed"

    def test_interior_novelty_window_closed(self):
        assert base(clr=0.8)["novelty_screening"] == "disabled"
        assert base(nn=1.2)["novelty_screening"] == "disabled"
        assert base(clr=3.0, nn=0.4)["novelty_screening"] == "enabled"

    def test_capacity_growth_rule_in_exemplar_interior(self):
        out = base()
        assert out["capacity"]["mode"] == "grow-to-plateau"
        assert out["capacity"]["target_fraction"] == pytest.approx(0.05)
