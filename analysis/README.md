# analysis/

The analysis behind the top-level README. Every figure quoted there comes from
one of these scripts, and the full printouts are saved next to them so any
number can be traced without rerunning anything.

Run in this order:

```bash
pip install -r ../requirements.txt
python3 fetch_data.py     # downloads the total-return series into ../data/
python3 analyse.py        # the historical analysis: results.md and most figures
python3 monte_carlo.py    # the forward-looking simulation and its figures
python3 costs.py          # fees and tax drag
```

## Files

- `fetch_data.py`: downloads split and dividend adjusted daily closes from
  Yahoo's chart API for SPY, EFA, EEM, RSP, AGG and SOXX. Calls the API directly
  with `requests` rather than through `yfinance`, which does not cope with some
  network proxies.
- `analyse.py`: builds the five risk-graded portfolios plus the semiconductor
  sleeve, measures return and risk, and runs the three drift tests. Writes
  `results.md` and most of `../figures/`.
- `monte_carlo.py`: the forward-looking work. A historical block bootstrap,
  6-month blocks and 10,000 paths, covering both accumulation and a 30-year
  drawdown, with sensitivity tables across withdrawal rates and horizons.
  Writes `monte_carlo_results.md`.
- `costs.py`: fees and the tax wrapper decision, modelled on the balanced
  portfolio. Writes `costs_results.md`. Reuses `analyse.py` rather than
  rebuilding the portfolios.

## Outputs

- `results.md`, `monte_carlo_results.md`, `costs_results.md`: the printouts, so
  the numbers in the top-level README can be checked against source.
- `../figures/`: the charts.

Both companion tools import from here rather than reimplementing anything, so
the paper and the tools cannot disagree about a figure.
