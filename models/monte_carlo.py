"""
Parametric Monte Carlo retirement simulator.

Draws fresh Normal(mu, sigma) returns for every fund, every month, every trial.
Eliminates bootstrap pool-sampling bias. Median converges to solver projection
by construction because arithmetic means are calibrated via variance drag correction.
"""

import numpy as np

from config import FUND_STATS
from models.allocations import get_lifecycle_allocation


def get_fund_monthly_params():
    """
    Convert annual FUND_STATS to monthly (arith_mean, sigma) pairs.

    Arithmetic mean = monthly_geo + sigma^2/2 so geometric compounding
    matches the target CAGR used by the solver.
    """
    params = {}
    for fund, v in FUND_STATS.items():
        mg = (1 + v['geo_mean']) ** (1 / 12) - 1      # monthly geometric mean
        ms = v['sigma'] / np.sqrt(12)                    # monthly sigma
        params[fund] = (mg + ms ** 2 / 2, ms)           # (monthly arith mean, monthly sigma)
    return params


FUND_MONTHLY_PARAMS = get_fund_monthly_params()


def scrape_and_prep_tsp_data():
    """
    Returns fund monthly params.  MC generates fresh returns each trial -- no pool drift.
    Name retained for call-site compatibility with the bootstrap version.
    """
    return FUND_MONTHLY_PARAMS, "Parametric Proxy"


def run_real_monte_carlo(
    current_age: int,
    retire_age: int,
    initial_bal: float,
    monthly_contrib,
    fund_params: dict,
    l_fund_weight: float,
    manual_alloc: dict,
    inflation_rate: float = 0.025,
    trials: int = 1000,
) -> np.ndarray:
    """
    Parametric Monte Carlo -- draws fresh returns from Normal(mu, sigma) each trial.
    Eliminates pool-sampling bias. Median converges to solver projection by construction.

    Parameters
    ----------
    fund_params : dict
        {fund: (monthly_arith_mean, monthly_sigma)} from FUND_MONTHLY_PARAMS
    l_fund_weight : float
        Fraction allocated to L-Fund (lifecycle). 0.0 = fully manual.
    manual_alloc : dict
        {fund: weight} for C/S/I/F/G (excluding L).
    """
    months = int((retire_age - current_age) * 12)
    monthly_infl = (1 + inflation_rate) ** (1 / 12) - 1
    funds = ['C', 'S', 'I', 'F', 'G']

    # Normalize contribution schedule
    if np.isscalar(monthly_contrib):
        contrib_schedule = np.full(months, float(monthly_contrib))
    else:
        contrib_schedule = np.array(monthly_contrib, dtype=float)
        if len(contrib_schedule) < months:
            contrib_schedule = np.pad(
                contrib_schedule, (0, months - len(contrib_schedule)), 'edge'
            )
        else:
            contrib_schedule = contrib_schedule[:months]

    # Pre-calculate monthly allocation weights (gliding L-fund)
    monthly_allocs = []
    for i in range(months):
        alloc = manual_alloc.copy()
        if l_fund_weight > 0:
            years_left = (months - i) / 12
            lc_alloc = get_lifecycle_allocation(years_left)
            for f, w in lc_alloc.items():
                alloc[f] = alloc.get(f, 0) + (l_fund_weight * w)
        monthly_allocs.append([alloc.get(f, 0) for f in funds])
    allocs_arr = np.array(monthly_allocs)  # shape (months, 5)

    # Extract per-fund distribution params
    mu_arr = np.array([fund_params[f][0] for f in funds])    # monthly arith means
    sigma_arr = np.array([fund_params[f][1] for f in funds]) # monthly sigmas

    # Pre-allocate results
    results = np.zeros((trials, months + 1))
    results[:, 0] = initial_bal

    for t in range(trials):
        # Draw fresh independent returns for every fund every month
        raw_returns = np.random.normal(mu_arr, sigma_arr, size=(months, 5))

        balance = initial_bal
        for i in range(months):
            nom_ret = np.dot(raw_returns[i], allocs_arr[i])
            real_ret = (1 + nom_ret) / (1 + monthly_infl) - 1
            balance = balance * (1 + real_ret) + contrib_schedule[i]
            results[t, i + 1] = balance

    return results
