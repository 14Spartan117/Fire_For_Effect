"""
Career projection utilities: promotion chains, base-pay schedules,
and the binary-search savings-rate solver.
"""

from typing import List, Tuple

import numpy as np

from config import PROMOTION_TIMELINE, PROGRESSION
from data.loader import get_base_pay


# ── Promotion chain helpers ──────────────────────────────────────────────────

def get_progression_chain(rank: str) -> List[str]:
    if rank in ("O-1E", "O-2E", "O-3E"):
        return PROGRESSION["officer_e"]
    if rank.startswith("O"):
        return PROGRESSION["officer"]
    if rank.startswith("W"):
        return PROGRESSION["warrant"]
    return PROGRESSION["enlisted"]


def build_monthly_base_pay_schedule(
    start_rank: str, start_tis: float, career_months: int
) -> List[float]:
    """
    Project monthly base pay forward using typical promotion timelines.
    """
    chain = get_progression_chain(start_rank)
    chain_start = chain.index(start_rank) if start_rank in chain else 0

    schedule: List[float] = []
    for m in range(career_months):
        tis = start_tis + m / 12.0
        current_rank = chain[chain_start]
        for rank in chain[chain_start:]:
            if tis >= PROMOTION_TIMELINE.get(rank, 999):
                current_rank = rank
            else:
                break
        schedule.append(get_base_pay(current_rank, tis))
    return schedule


# ── Savings-rate solver ──────────────────────────────────────────────────────

def solve_savings_rate(
    target_nest_egg: float,
    current_tsp: float,
    base_pay_schedule: List[float],
    civilian_monthly: float,
    mil_months: int,
    total_months: int,
    expected_real_rate: float,
    inflation_rate: float,
) -> Tuple[float, List[float]]:
    """
    Binary-search for the constant % of income that grows
    current_tsp to target_nest_egg over total_months.

    Returns (savings_pct, contribution_schedule).
    """
    monthly_real = (1 + expected_real_rate) ** (1 / 12) - 1

    # Full income schedule: military phase + civilian phase
    income_schedule = list(base_pay_schedule)
    for _ in range(total_months - mil_months):
        income_schedule.append(civilian_monthly)

    def simulate(pct: float) -> float:
        balance = current_tsp
        for m in range(total_months):
            contrib = pct * income_schedule[m]
            balance = balance * (1 + monthly_real) + contrib
        return balance

    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if simulate(mid) < target_nest_egg:
            lo = mid
        else:
            hi = mid

    pct = (lo + hi) / 2
    contrib_schedule = [pct * inc for inc in income_schedule]
    return pct, contrib_schedule
