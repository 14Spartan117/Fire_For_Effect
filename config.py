"""
Global configuration constants for F.I.R.E. for Effect.
"""

PAGE_CONFIG = {
    "page_title": "F.I.R.E. for Effect",
    "page_icon": "\U0001F396\uFE0F",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}

RANKS = [
    "E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9",
    "W-1", "W-2", "W-3", "W-4", "W-5",
    "O-1", "O-1E", "O-2", "O-2E", "O-3", "O-3E", "O-4", "O-5", "O-6", "O-7",
]

BAS_ENLISTED = 515.00
BAS_OFFICER = 360.00

SHEET_ID = "1dFytsNBUepFXsIR4LOXIpsUZfqHfwhO32URiS37m--M"

# Nominal CAGR by fund (inception-to-date, tspfolio.com)
FUND_NOMINAL_RATES = {
    "C": 0.113,
    "S": 0.094,
    "I": 0.063,
    "F": 0.054,
    "G": 0.047,
}

# Full distribution parameters for parametric Monte Carlo
# Source: tspfolio.com, since-inception data through 3/5/2026
# geo_mean = target nominal CAGR (what the solver uses)
# sigma    = annualized standard deviation
# mu       = arithmetic mean for proxy sampling = geo_mean + sigma^2/2
#            Corrects for variance drag so proxy geometric return matches solver
FUND_STATS = {
    'C': {'mu': 0.11847, 'sigma': 0.181, 'geo_mean': 0.107},
    'S': {'mu': 0.11518, 'sigma': 0.202, 'geo_mean': 0.099},
    'I': {'mu': 0.08059, 'sigma': 0.171, 'geo_mean': 0.068},
    'F': {'mu': 0.05268, 'sigma': 0.043, 'geo_mean': 0.053},
    'G': {'mu': 0.04602, 'sigma': 0.003, 'geo_mean': 0.047},
}

# Promotion timelines: TIS (years) at which pay changes (~1 yr after selection board)
PROMOTION_TIMELINE = {
    "E-1": 0, "E-2": 0.5, "E-3": 1.5, "E-4": 2.0,
    "E-5": 4.0, "E-6": 8.0, "E-7": 14.0, "E-8": 18.0, "E-9": 23.0,
    "W-1": 0, "W-2": 3.0, "W-3": 8.0, "W-4": 14.0, "W-5": 20.0,
    "O-1": 0, "O-1E": 0, "O-2": 2.0, "O-2E": 2.0,
    "O-3": 4.0, "O-3E": 4.0, "O-4": 11.0, "O-5": 17.0, "O-6": 23.0, "O-7": 31.0,
}

PROGRESSION = {
    "officer":   ["O-1", "O-2", "O-3", "O-4", "O-5", "O-6", "O-7"],
    "officer_e": ["O-1E", "O-2E", "O-3E", "O-4", "O-5", "O-6", "O-7"],
    "warrant":   ["W-1", "W-2", "W-3", "W-4", "W-5"],
    "enlisted":  ["E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9"],
}
