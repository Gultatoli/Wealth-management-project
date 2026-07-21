"""
Download daily total-return price series from Yahoo Finance.

For each ticker we save one CSV into ../data/ with two columns:
    date, adj_close

"adj_close" is Yahoo's dividend- and split-adjusted close. Using it means a
price series already assumes dividends are reinvested, which is what we want:
it is a total-return series, the honest way to measure how an investor actually
did.

Why not the `yfinance` library? Its HTTP backend does not cope with the network
proxy in some environments. To stay robust we call Yahoo's public chart API
directly with `requests`. The same script runs unchanged on a normal machine.

Run:
    python3 fetch_data.py
"""

import csv
import os
import time
from datetime import datetime, timezone

import requests

# ---------------------------------------------------------------------------
# What we download and why each series is here.
# ---------------------------------------------------------------------------
TICKERS = {
    "SPY": "US large-cap equity (S&P 500), cap-weighted",
    "RSP": "US large-cap equity, EQUAL-weighted (for the concentration test)",
    "AGG": "US aggregate bonds (the 'ballast' in a cautious portfolio)",
    "SOXX": "US semiconductors (proxy for the AI / memory hardware theme)",
}

# A small buffer before the common window so annual rebalancing has a clean
# starting point. The analysis itself trims to the shared date range.
START = datetime(2003, 1, 1, tzinfo=timezone.utc)

# In this cloud environment outbound HTTPS is re-signed by a proxy, so requests
# must trust its certificate bundle. On a normal machine this file will not
# exist and we fall back to the system trust store.
CA_BUNDLE = "/root/.ccr/ca-bundle.crt"

# Yahoo rate-limits requests that do not look like a browser, so send a UA.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _verify():
    """Return the CA bundle path if we are behind the proxy, else True."""
    return CA_BUNDLE if os.path.exists(CA_BUNDLE) else True


def fetch(ticker):
    """Return a list of (date_string, adj_close_float) for one ticker."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {
        "period1": int(START.timestamp()),
        "period2": int(datetime.now(timezone.utc).timestamp()),
        "interval": "1d",
        "events": "div",
    }
    last_status = None
    for attempt in range(5):
        resp = requests.get(url, params=params, headers=HEADERS,
                            verify=_verify(), timeout=30)
        last_status = resp.status_code
        if resp.status_code == 200:
            result = resp.json()["chart"]["result"][0]
            stamps = result["timestamp"]
            adj = result["indicators"]["adjclose"][0]["adjclose"]
            rows = []
            for t, a in zip(stamps, adj):
                if a is None:
                    continue  # Yahoo occasionally returns gaps; skip them
                day = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d")
                rows.append((day, round(float(a), 6)))
            return rows
        # Back off and retry on a transient error (e.g. a 429 rate limit).
        time.sleep(2 ** attempt)
    raise RuntimeError(f"{ticker}: failed after retries (last status {last_status})")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for ticker, description in TICKERS.items():
        rows = fetch(ticker)
        path = os.path.join(DATA_DIR, f"{ticker}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "adj_close"])
            writer.writerows(rows)
        first, last = rows[0][0], rows[-1][0]
        print(f"{ticker:5s} {len(rows):5d} rows  {first} -> {last}   ({description})")
        time.sleep(1)  # be polite to Yahoo between tickers


if __name__ == "__main__":
    main()
