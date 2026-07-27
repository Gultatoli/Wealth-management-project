"""
Download the two extra series this module needs on top of the ones the main
analysis already uses.

The main analysis works with equities and aggregate bonds. Measuring what a
manager does needs one more thing: somewhere to put money that is not the
portfolio. A client who panics sells into cash. A retiree with a cash bucket
holds cash. Neither is a bond fund, so neither can be proxied with AGG.

  SHY   1-3 year US Treasuries. Short duration, still a bond fund. Used for the
        short-bond variant of the cash bucket test.
  ^IRX  The 13-week US Treasury bill discount yield, in percent. This is the
        cash rate itself rather than a fund, and Yahoo carries it back beyond
        the start of the analysis window, which the cash ETFs do not (BIL only
        begins in 2007). We turn the yield into a daily total-return index in
        common.py, so the "cash" leg earns the actual rate that prevailed on
        each day, including the 5% of 2007 and the near-zero of 2010 to 2021.

Reuses the fetch logic in ../analysis/fetch_data.py rather than repeating it,
so there is one place where the download behaviour lives.

Run:
    python3 fetch_extra.py
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import fetch_data as F  # noqa: E402  (path set above)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def save(rows, filename, value_column):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", value_column])
        writer.writerows(rows)
    print(f"{filename:10s} {len(rows):5d} rows  {rows[0][0]} -> {rows[-1][0]}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    # SHY is a normal total-return price series, same shape as the other ETFs.
    save(F.fetch("SHY"), "SHY.csv", "adj_close")
    # ^IRX is a yield, not a price. The column name says so, because treating a
    # yield as if it were a price would be a silent and expensive mistake.
    save(F.fetch("^IRX"), "IRX.csv", "yield_pct")


if __name__ == "__main__":
    main()
