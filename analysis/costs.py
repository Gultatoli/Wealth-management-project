"""
Costs: fees and tax.

The rest of the project is about risks that are uncertain and hard to see. Fees
and tax are the opposite: a near-certain drag that a client can actually
control. This module quantifies both on the balanced portfolio, over the same
window as the main analysis, and shows how they eat into a long-run result.

Fees are modelled exactly. Tax is modelled as a clearly-labelled illustration,
because a real tax outcome depends on the client's wrapper, income, allowances
and rates. The point is the size of the wrapper decision, not a precise figure.

Run (after fetch_data.py):
    python3 costs.py
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import analyse as A  # reuse the portfolios and data loading

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
HERE = os.path.dirname(__file__)

FEES = [0.005, 0.010, 0.015]           # 0.5%, 1.0%, 1.5% all-in annual
INVEST = 100_000                        # illustrate on GBP 100,000

# Illustrative tax assumptions for a UK higher-rate taxpayer (2026 rates), used
# only to size the ISA-versus-taxable-account decision.
INCOME_YIELD = 0.025                     # assumed income (dividends + interest) yield
INCOME_TAX = 0.35                        # blended higher-rate on that income
CGT_RATE = 0.24                          # capital gains tax on the final gain


def apply_annual_drag(value, drag):
    """Reduce a gross value series by a continuous annual percentage drag
    (works for a fee or a tax-as-drag)."""
    gross = value.pct_change().fillna(0)
    daily = 1 - (1 - drag) ** (1 / A.TRADING_DAYS)
    net = (1 + gross) * (1 - daily) - 1
    return (1 + net).cumprod()


def main():
    prices = A.load_prices()
    values = {n: A.portfolio_value(prices, w) for n, w in A.PORTFOLIOS.items()}
    bal = values["Balanced (60/40)"]
    years = (bal.index[-1] - bal.index[0]).days / 365.25
    gross_mult = bal.iloc[-1] / bal.iloc[0]

    lines = []
    def out(s=""):
        print(s); lines.append(s)

    out("# Costs: fees and tax\n")
    out(f"Balanced portfolio, {bal.index[0].date()} to {bal.index[-1].date()} "
        f"({years:.1f} years). Gross, a £{INVEST:,} investment grew to "
        f"£{INVEST*gross_mult:,.0f} (a {A.cagr(bal)*100:.1f}% CAGR).\n")

    # ---- Fees ----
    out("## Fees - a certain, compounding drag\n")
    out(f"| Annual fee | Final value of £{INVEST:,} | Lost to fees | Share of the gain lost |")
    out("|-----------|----------------------------|--------------|------------------------|")
    for fee in FEES:
        net_mult = apply_annual_drag(bal, fee).iloc[-1]
        gross_val = INVEST * gross_mult
        net_val = INVEST * net_mult
        cost = gross_val - net_val
        share = cost / (gross_val - INVEST) * 100
        out(f"| {fee*100:.1f}% | £{net_val:,.0f} | £{cost:,.0f} | {share:.0f}% |")
    out()
    net1 = INVEST * apply_annual_drag(bal, 0.010).iloc[-1]
    out(f"A 1% annual fee turned a £{INVEST*gross_mult:,.0f} result into "
        f"£{net1:,.0f}, a loss of £{INVEST*gross_mult-net1:,.0f} on a £{INVEST:,} "
        f"investment over {years:.0f} years. The fee is only 1% a year, but it "
        f"compounds against the whole pot every year, so the damage is far larger "
        f"than 1%. This is the one cost a client can see and control, and it is "
        f"often the largest certain number in the whole plan.\n")

    # ---- Tax: the wrapper decision (illustrative) ----
    out("## Tax - the wrapper decision (illustrative)\n")
    out(f"Illustrative only, for a UK higher-rate taxpayer: assume the portfolio "
        f"yields {INCOME_YIELD*100:.1f}% a year in income taxed at {INCOME_TAX*100:.0f}% "
        f"in a taxable account, plus {CGT_RATE*100:.0f}% capital gains tax on the "
        f"final gain. An ISA pays neither. Fees are set aside here so the tax "
        f"effect is isolated.\n")
    income_drag = INCOME_YIELD * INCOME_TAX
    isa_final = INVEST * gross_mult
    gia_pre_cgt_val = INVEST * apply_annual_drag(bal, income_drag).iloc[-1]
    income_cost = isa_final - gia_pre_cgt_val
    cgt_if_realised = max(0.0, (gia_pre_cgt_val - INVEST)) * CGT_RATE
    out(f"The robust part is the recurring income tax. Taxing {INCOME_YIELD*100:.1f}% "
        f"of income at {INCOME_TAX*100:.0f}% acts like an extra ~{income_drag*100:.2f}% "
        f"annual fee. Over {years:.0f} years that alone cost about "
        f"£{income_cost:,.0f}, on top of any management fee, and an ISA avoids it "
        f"entirely. That is a similar size to a 1% management fee.")
    out(f"\nCapital gains tax is on top but is more controllable. Realising the "
        f"whole gain in one year would add roughly £{cgt_if_realised:,.0f} of CGT, "
        f"but phasing disposals across tax years, using the annual exemption, and "
        f"using both spouses' allowances all reduce it. An ISA removes it "
        f"completely.")
    out(f"\nSo the ISA wrapper was worth somewhere between about "
        f"£{income_cost:,.0f} (income tax only) and £{income_cost+cgt_if_realised:,.0f} "
        f"(income tax plus a one-off CGT bill) on a £{INVEST:,} investment. The "
        f"exact figure depends on allowances and how gains are realised, so read "
        f"it as a scale. The point is that the wrapper decision is worth a large, "
        f"fully controllable amount over a long horizon.\n")

    # ---- Combined: fee drag on the decumulation goal ----
    out("## Why this matters: fees raise goal risk\n")
    out("Fees do not only shrink a final pot. In drawdown they lower the "
        "probability the money lasts. A 1% fee is a certain reduction in return, "
        "so it is a certain increase in the chance of running out. Costs are the "
        "one lever here that is fully in the adviser's and client's control.\n")

    # ---- chart: gross vs net (1% fee) ----
    gross_path = INVEST * (bal / bal.iloc[0])
    net_path = INVEST * apply_annual_drag(bal, 0.010)
    plt.figure(figsize=(10, 6))
    plt.plot(gross_path.index, gross_path, color="#1f4e79", linewidth=1.6, label="gross (no fee)")
    plt.plot(net_path.index, net_path, color="#B0413E", linewidth=1.6, label="after a 1% annual fee")
    plt.fill_between(gross_path.index, net_path, gross_path, color="#B0413E", alpha=0.12)
    plt.title(f"The compounding cost of a 1% fee (£{INVEST:,} in the balanced portfolio)")
    plt.ylabel("Portfolio value (£)")
    plt.legend(loc="upper left")
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, "fee_drag.png"), dpi=120, bbox_inches="tight")
    plt.close()

    with open(os.path.join(HERE, "costs_results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\nWrote costs_results.md and ../figures/fee_drag.png")


if __name__ == "__main__":
    main()
