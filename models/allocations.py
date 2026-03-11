"""
TSP fund allocation logic: lifecycle glide-path and blended return calculator.
"""

from config import FUND_NOMINAL_RATES


def get_lifecycle_allocation(years_to_retire: float) -> dict:
    """Return target fund weights based on years until retirement."""
    if years_to_retire > 20:
        return {"C": 0.50, "S": 0.25, "I": 0.25, "F": 0.0, "G": 0.0}
    elif years_to_retire > 10:
        return {"C": 0.40, "S": 0.15, "I": 0.15, "F": 0.2, "G": 0.1}
    elif years_to_retire > 0:
        return {"C": 0.20, "S": 0.05, "I": 0.05, "F": 0.3, "G": 0.4}
    else:
        return {"C": 0.0, "S": 0.0, "I": 0.0, "F": 0.3, "G": 0.7}


def get_time_weighted_blended_return(alloc_dict: dict, total_months: int) -> float:
    """
    Average nominal return over total_months, accounting for the lifecycle
    glide path shifting month-by-month as retirement approaches.
    Use this for the solver so it matches what the Monte Carlo actually simulates.
    """
    if total_months <= 0:
        return 0.0
    return sum(
        get_blended_nominal_return(alloc_dict, (total_months - m) / 12)
        for m in range(total_months)
    ) / total_months


def get_blended_nominal_return(alloc_dict: dict, years_to_retire: float) -> float:
    """
    Weighted nominal return for a custom allocation dict.
    L-fund portion is expanded via get_lifecycle_allocation().
    Keys: C, S, I, F, G, L  (values should sum to 1.0).
    """
    l_weight = alloc_dict.get("L", 0.0)
    lc_alloc = get_lifecycle_allocation(years_to_retire) if l_weight > 0 else {}

    total = 0.0
    for fund, weight in alloc_dict.items():
        if fund == "L":
            for sub_fund, sub_weight in lc_alloc.items():
                total += weight * sub_weight * FUND_NOMINAL_RATES.get(sub_fund, 0.0)
        else:
            total += weight * FUND_NOMINAL_RATES.get(fund, 0.0)
    return total
