"""P73 Memory Geometry Controller — mechanical geometry->policy mapping.

Registered design: intuition-mechanism/docs/MEMORY_CONTROLLER.md (2026-09-29,
post-review).  Maps measured representation geometry to a memory policy where
every rule is bound to a registered law (L1-L6) and every threshold comes from
a registered measurement (P52/P53/P55/P64/P73-*/P74/P113, V7A/V7C) — zero
free parameters left to discretion.

Inputs (all measured, no fits):
    r    R/mind   class spread / min inter-class distance          [L1]
    nn   NN/mind  intra-class spacing / mind                       [L1]
    ts   two-scale flag (core+fringe present)                      [L2]
    cov  reachable fraction at current capacity (P55 probes)       [L3]
    clr  novel-clearance ratio (clearance / THRESH)                [L4]
    lq   query length / l_min (l_min = #free-statistic-entries)    [L5]
    ff   fringe fraction (entries not redundantly covered)         [L6]
    eps  write/read noise (measured flip rate)                     [L4, V7]
    D    embedding dimension of the registered crossover curve      (6 or 12)
    cap  current per-class capacity (harness-measured; optional — when
         omitted, starvation is inferred from coverage: cov < 1 means the
         store is still below the P55 plateau, i.e. on the starved side)

Outputs (dict): type, capacity, eviction, verification, query_gate,
novelty_screening — plus `notes` (rule provenance) and `feasibility_gate`
(R8: the harness must check substrate expressibility BEFORE executing).

This module is pure: no I/O, no clocks, no randomness.
"""
import bisect

# --- P74 measured capacity crossover curve cap*(r, D) -------------------------
# Per-class capacity at which the prototype and exemplar arms cross.
# D=6  -> 1/3/5/5 at r = 0.15/0.25/0.35/0.45
# D=12 -> 1/2/8/12 at the same r knots.
# Intermediate r: linear interpolation.  Below the first knot the curve is
# floored at 1 (a per-class capacity below 1 is not a store); above the last
# knot the last segment's slope continues (D=6 is flat there, D=12 keeps
# growing).  Only registered dimensions are accepted — no invented curves.
CAP_STAR_KNOTS = {
    6: ((0.15, 1.0), (0.25, 3.0), (0.35, 5.0), (0.45, 5.0)),
    12: ((0.15, 1.0), (0.25, 2.0), (0.35, 8.0), (0.45, 12.0)),
}


def cap_star(r, D=6):
    """Per-class crossover capacity cap*(r, D) (P74), piecewise-linear."""
    try:
        knots = CAP_STAR_KNOTS[D]
    except KeyError:
        raise ValueError(
            f"no registered cap*(r, D) curve for D={D}; "
            f"registered dimensions: {sorted(CAP_STAR_KNOTS)}") from None
    rs = [k[0] for k in knots]
    if r <= rs[0]:
        return 1.0
    if r >= rs[-1]:
        (r0, c0), (r1, c1) = knots[-2], knots[-1]
        return c1 + (c1 - c0) / (r1 - r0) * (r - r1)
    i = bisect.bisect_right(rs, r)
    r0, c0 = knots[i - 1]
    r1, c1 = knots[i]
    return c0 + (c1 - c0) / (r1 - r0) * (r - r0)


# --- registered thresholds (each from a measurement, not a fit) ---------------
R_SEP_MAX = 0.5      # Law-1 separation viability of the mean-ball (P52/P73-c)
FF_MANDATORY = 0.1   # ff above this: prototype denoising insufficient (R1-v4 task rule)
TIE_LO, TIE_HI = 0.4, 0.55  # non-starved tie zone: ordering flips across seeds


def controller(r, nn, ts, cov, clr, lq, ff, eps, D=6, cap=None):
    """Map measured geometry to the memory policy (P73 registered rules).

    Returns dict with keys: type, capacity, eviction, verification,
    query_gate, novelty_screening (plus notes and feasibility_gate).
    """
    notes = []
    capx = cap_star(r, D)

    # -- starvation (R1).  STARVED = per-class capacity <= cap*(r, D).  When
    # the harness does not pass cap, fall back to the coverage proxy: cov < 1
    # means the store has not reached the P55 plateau, so it is still on the
    # growing (starved) side of the crossover.
    if cap is None:
        starved = cov < 1.0
        starved_src = f"cov={cov} < 1 (P55 plateau not reached; cap not measured)"
    else:
        starved = cap <= capx
        starved_src = f"cap={cap} <= cap*={capx:g}" if starved else \
                      f"cap={cap} > cap*={capx:g}"

    # -- R1 type: STARVED and r <= 0.5 -> prototype (a capacity-1 exemplar
    # store IS a noisy prototype; the denoised mean dominates it
    # unconditionally [P52/P73-c]).  NON-STARVED -> exemplar with core-first
    # eviction at any r [P73-b].  ff > FF_MANDATORY forces exemplar: prototype
    # denoising is insufficient when the fringe is that large.
    if ff > FF_MANDATORY:
        mtype = "exemplar"
        notes.append(f"ff={ff} > {FF_MANDATORY}: exemplar mandatory — "
                     "prototype denoising insufficient [L6]")
    elif starved and r <= R_SEP_MAX:
        mtype = "prototype"
        notes.append(f"STARVED ({starved_src}) and r={r} <= {R_SEP_MAX}: "
                     "denoised mean dominates capacity-1 exemplar [P52/P73-c]")
    else:
        mtype = "exemplar"
        if not starved and TIE_LO <= r <= TIE_HI:
            notes.append(f"tie zone r~{TIE_LO}-{TIE_HI} non-starved: ordering "
                         "flips across seeds (honest no-law, degenerate choice)")

    # -- R2 capacity: grow until the marginal entry adds less than delta
    # coverage (P55 plateau); never past it.  Expected capacity ~ fringe
    # fraction x reachable support, NOT ~ total input.  [L3, L6; P55/P66]
    if mtype == "prototype":
        capacity = {
            "cap_star": capx,
            "mode": "fixed",
            "per_class": 1,
            "rule": "capacity-1 denoised mean per class",
        }
    else:
        capacity = {
            "cap_star": capx,
            "mode": "grow-to-plateau",
            "per_class": None,
            "target_fraction": ff,
            "rule": "grow until marginal entry adds < delta coverage (P55); "
                    "target ~ ff x reachable support; never past the plateau",
        }

    # -- R3 eviction.  Core-first requires density heterogeneity AND a core to
    # protect: without the two-scale structure the P113 end-to-end result
    # (core-first = LRU = 30% < random 41.5% on uniform density) binds, so
    # fall back to random.  If the ff-signal degenerates (no core remains),
    # fall back to LRU.  Never evict by recency alone while a core exists.
    # [L6; P72/P72-b/P66/P113]
    if mtype == "prototype":
        eviction = "none"
    elif not ts:
        eviction = "random"
        notes.append("no two-scale structure (uniform density): random "
                     "eviction — core-first has no advantage [P113]")
    elif ff >= 1.0:
        eviction = "lru"
        notes.append("ff=1.0: thin-coverage degenerate — no core remains, "
                     "LRU fallback [R3 guard]")
    else:
        eviction = "core-first"

    # -- R4 write verification.  Depth is NOT a sensitive knob (V7C clean 2x2:
    # depth effect -0.99, CI [-2.29, +0.31], sign-undetermined), so the
    # controller does not tune depth; the coverage/support axis carries the
    # sensitivity.  Mechanical gate: thresholded verification inside the
    # separated regime, none outside.  `eps` is deliberately NOT a threshold
    # input — it is carried for the harness's feasibility/feasibility-gate use.
    verification = "thresholded" if r <= R_SEP_MAX else "none"
    if verification == "thresholded" and cov >= 1.0:
        notes.append("full support: deep writes acceptable as tie-breaker "
                     "(V7A +0.29-0.45, n.s.)")

    # -- R5 query gate.  lq < 1 -> the query is shorter than the measured
    # l_min (#free-statistic-entries [P64]; production knee 6-12 tokens
    # [P70-b]): mark retrieval unreliable (report, do not answer from memory).
    query_gate = "unreliable" if lq < 1 else "proceed"

    # -- R6 novelty screening.  Enable only when clr > 1 AND known-coverage is
    # healthy — both arms inside their Law-1 viability: mean-ball separated
    # (r <= 0.5) and intra-class spacing below inter-class distance (nn < 1).
    # Outside that window novelty output is blind (clr <= 1) or vacuous
    # (unviable arms) [P53]; screening features must be contrast features [P54].
    arms_viable = r <= R_SEP_MAX and nn < 1
    if clr > 1 and arms_viable:
        novelty_screening = "enabled"
        notes.append("novelty window open (clr>1, both arms Law-1 viable); "
                     "screening features must be contrast features [P54]")
    else:
        novelty_screening = "disabled"
        notes.append("clr<=1: novelty blind [P53]" if clr <= 1 else
                     "known-coverage outside Law-1 viability: novelty vacuous [P53]")

    # -- R8 substrate feasibility.  The controller's obligation is the explicit
    # gate; the predicates (entry-size limits, chunk atomicity, key structure)
    # are substrate-specific and belong to the harness.  A policy that cannot
    # be expressed must be rejected BEFORE the run [G1].
    return {
        "type": mtype,
        "capacity": capacity,
        "eviction": eviction,
        "verification": verification,
        "query_gate": query_gate,
        "novelty_screening": novelty_screening,
        "feasibility_gate": "required (harness-side predicates, R8/G1)",
        "notes": notes,
    }
