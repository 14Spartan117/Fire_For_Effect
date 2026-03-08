"""
Military pension estimator using the High-3 average method.
"""

from config import PROMOTION_TIMELINE
from data.loader import get_base_pay
from models.projections import get_progression_chain


def calc_high3_pension(
    retire_rank: str, yrs_at_retire: float, multiplier: float
) -> float:
    """
    Average base pay over the 3 years before retirement, accounting for
    the promotion timeline so rank reflects actual pay received.
    """
    chain = get_progression_chain(retire_rank)
    chain_idx = chain.index(retire_rank) if retire_rank in chain else 0

    pays = []
    for yr_offset in [3, 2, 1]:
        tis_check = yrs_at_retire - yr_offset
        current_rank = chain[0]
        for r in chain[: chain_idx + 1]:
            if tis_check >= PROMOTION_TIMELINE.get(r, 999):
                current_rank = r
            else:
                break
        pays.append(get_base_pay(current_rank, tis_check))

    avg_base = sum(pays) / 3
    return avg_base * (yrs_at_retire * multiplier)
