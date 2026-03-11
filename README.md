# F.I.R.E. for Effect

**Financial Independence, Retire Early -- tailored for military service members.**

A Streamlit-based financial planning app that helps soldiers understand their pay, project retirement readiness, build conscious budgets, and take concrete action toward financial independence.

## Project Structure

```
fire_for_effect/
├── app.py                  # Main entry point (run this)
├── config.py               # Constants: ranks, pay tables, promotion timelines
├── requirements.txt
├── military_data.json      # Pay tables, BAH rates, zip-to-MHA mapping (not in repo -- provide your own)
│
├── data/
│   ├── __init__.py
│   └── loader.py           # Load & query military_data.json
│
├── analytics/
│   ├── __init__.py
│   └── tracking.py         # Anonymous session analytics via Google Sheets
│
├── models/
│   ├── __init__.py
│   ├── allocations.py      # TSP fund allocation & blended return logic
│   ├── projections.py      # Promotion chains, pay schedules, savings-rate solver
│   ├── pension.py          # High-3 pension estimator
│   └── monte_carlo.py      # TSP data scraper & Monte Carlo simulator
│
└── ui/
    ├── __init__.py
    ├── state.py            # Session state initialisation
    ├── consent.py          # Consent / disclaimer screen
    ├── tab_income.py       # Tab 1: What Do You Make?
    ├── tab_retirement.py   # Tab 2: How Much Do You Need to Save?
    ├── tab_budget.py       # Tab 3: Where Does It Go?
    ├── tab_quiz.py         # Tab 4: Know the Game (quiz)
    ├── tab_action.py       # Tab 5: The Way Ahead (checklist)
    ├── tab_feedback.py     # Tab 6: Feedback form
    └── tab_plan.py         # Tab 7: Your Plan (PDF export)
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/<your-username>/fire-for-effect.git
cd fire-for-effect

# Install dependencies
pip install -r requirements.txt

# Place your military_data.json in the project root

# Run the app
streamlit run app.py
```

## Data File

`military_data.json` must contain three top-level keys:

- `base_pay` -- nested `{ rank: { tis_years: monthly_pay } }`
- `zip_to_mha` -- `{ zip_code: { "mha": mha_code } }`
- `bah_rates` -- `{ mha_code: { rank: { "with": amount, "without": amount } } }`

## Analytics (Optional)

Session analytics are written to a Google Sheet via a service-account key stored in Streamlit secrets (`st.secrets["gcp_service_account"]`). If no secret is configured, analytics are silently skipped.

## Secrets

Create `.streamlit/secrets.toml` for local development:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
# ... rest of the JSON key fields
```

## License

MIT
