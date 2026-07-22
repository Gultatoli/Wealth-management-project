# Does "cautious" mean cautious?

Testing what risk-graded model portfolio labels do and do not tell a private client, using almost 23 years of public market data (October 2003 to July 2026).

> Nothing here is investment advice. It is a historical analysis built from free, public data, using simplified index portfolios rather than any firm's real model portfolios.

---

## The question

When a wealth manager profiles a private client, the client is placed on a risk scale (for example cautious, balanced, adventurous) and mapped to a model portfolio. The label is meant to communicate how much risk the client is taking.

This project asks what that label actually communicates. The finding, in one line:

**A risk label ranks risk reliably, but it cannot communicate the full range of outcomes a portfolio can produce, and the risk underneath a fixed label drifts over time.**

Two things follow. "Cautious" was still genuinely less risky than "adventurous" over the whole period, so the ranking holds. But in a specific regime (2022) a cautious portfolio lost far more, and recovered more slowly, than its name suggests. And a "balanced" equity holding in 2025 is a different bet from a "balanced" holding in 2019, with no label ever changing.

## What a risk label is, and is not

A single word like "cautious" collapses several separate ideas that a suitability process is supposed to keep apart:

- **Risk tolerance** — how much loss the client can emotionally sit through.
- **Capacity for loss** — how much loss the client can financially afford.
- **Time horizon** — how long the money can stay invested.
- **Risk requirement** — how much risk the client actually needs to meet their goals.
- **Portfolio risk** — the risk actually embedded in the holdings, which changes with markets.

The label mainly speaks to the last one, and only as a static ranking. This analysis shows where that gap between a fixed label and a moving reality matters.

## Findings

### Finding 0: the labels rank risk correctly

Across the full period the portfolios line up exactly as their labels promise. More equity meant more volatility and deeper drawdowns, every step of the way. This is the part the labels get right, and it matters: the argument that follows is not that labels are useless.

| Portfolio | CAGR | Volatility | Max drawdown | Worst 12 months |
|-----------|------|-----------|--------------|-----------------|
| Defensive (20% equity) | 4.6% | 5.5% | −18.1% | −16.9% |
| Cautious (40%) | 6.0% | 7.9% | −23.6% | −22.9% |
| Balanced (60%) | 7.3% | 11.2% | −36.2% | −31.0% |
| Growth (80%) | 8.4% | 15.0% | −47.7% | −41.0% |
| Adventurous (100%) | 9.5% | 19.2% | −58.1% | −51.0% |

A cautious portfolio really was far less risky than an all-equity one: a third of the volatility, and less than half the worst drawdown. Keep that in mind through the next section, because it is the honest counterweight to it.

### Finding 1: in 2022 the bond cushion gave far less protection than the label implies

A cautious portfolio leans on bonds to cushion equity losses. That cushion depends on bonds and equities not falling together. Usually they do not. In 2022 they did, as rising interest rates hit both at once.

| Year | Cautious (40% equity) | Adventurous (100%) | Cautious loss as a share of the all-equity loss |
|------|----------------------|--------------------|-------------------------------------------------|
| **2008** | −11.1% | −38.8% | **29%** (bonds cushioned) |
| **2022** | −14.6% | −17.8% | **82%** (bonds fell too) |

Read that last column carefully. It is the share of *that calendar year's loss*, not a measure of overall risk. In 2022 the cautious portfolio produced 82% of the all-equity portfolio's loss for the year, having produced only 29% of it in 2008. The bond cushion that worked in 2008 largely failed in 2022.

What this does **not** say is that cautious became as risky as all-equity. Over the full period the cautious portfolio still had 7.9% volatility against 19.2%, and a −23.6% worst drawdown against −58.1%. The fair conclusion is narrower and more useful: the label "cautious" correctly signalled lower risk on average, but on its own it would not have warned a client that a double-digit annual loss was possible in a year when diversification broke down.

**The part a client would feel most: recovery was slower, not faster, for the cautious investor.** Because equities rebounded in the 2023 to 2024 rally while bonds stayed depressed, the more cautious portfolios spent *longer* underwater after 2022, not less.

| Portfolio | Time to recover its early-2022 peak |
|-----------|-------------------------------------|
| Defensive (20% equity) | 2.6 years |
| Cautious (40%) | 2.4 years |
| Balanced (60%) | 2.1 years |
| Adventurous (100%) | 2.0 years |

A cautious client who cares less about the size of a drawdown than about how long their money is stuck below where it started got the worse deal in this episode, despite holding the "safer" portfolio.

![The bond cushion in 2008 vs 2022](figures/bond_cushion_2008_vs_2022.png)

### Finding 2: a balanced portfolio's equity became concentrated in US mega-cap technology

Because standard equity indices weight companies by size, a handful of very large winners can come to dominate the index and quietly raise every holder's concentration, with no risk label changing.

You can see the effect by comparing the normal cap-weighted S&P 500 (SPY) with its equal-weighted twin (RSP), where every company counts the same. When the cap-weighted version pulls far ahead, the largest few companies are carrying the market.

- **2023:** SPY returned +26.7% against RSP's +13.8%, a gap of **12.9 points**.
- **2024:** SPY returned +25.6% against RSP's +12.8%, a gap of **12.8 points**.

The cap-weighted index nearly doubled the equal-weighted one two years running. That is a large, unusual concentration into the biggest companies, most of which were the major beneficiaries of the AI investment cycle.

Two honest boundaries on this claim. This measures concentration into *mega-cap companies*, not into "AI" as such: proving an AI-specific bet would need a holdings-level breakdown of how much of the index those companies represent and how much of the return came from them, which needs constituent data this project does not use. And the suitability point stands regardless of the label you put on the cause: a "balanced" client in 2025 holds a materially more concentrated equity exposure than a "balanced" client in 2019, and nobody re-profiled them.

![Concentration: SPY vs RSP](figures/concentration_spy_vs_rsp.png)

### Finding 3: the theme rewarded only clients whose whole profile supported it

Suitability cuts both ways. A client with the right profile could reasonably have tilted toward the semiconductor theme and been well rewarded. But the reward and the risk have to be quoted for the same thing, so this splits into two clearly different objects.

**The pure theme (semiconductors, SOXX, i.e. 100% in the sector):**
- Returned **+68.8% in 2023**, but fell **−36.4% in 2022** and **−50.4% in 2008**, with a worst drawdown of **−67%** and volatility of 31%, close to double the all-equity portfolio.

**A realistic tilt (70% global equity + 30% semiconductors):**
- Returned **+36.0% in 2023**, roughly twice the balanced portfolio, but its worst drawdown was **−58.7%** against the all-equity portfolio's −58.1%. Even a 30% tilt pushed the drawdown well past the aggressive baseline.

The point is the trade-off, not the theme. Whether a semiconductor allocation is suitable does not reduce to "does the client have a high risk tolerance." It depends on tolerance, capacity for loss, time horizon, and the return the client actually needs, all being consistent with an allocation that can fall by more than half and stay down for years. A client who scores high on tolerance but low on capacity, or who has a short horizon, should not hold it however much they like the story.

![The semis theme: reward and drawdown](figures/semis_reward_vs_drawdown.png)

### A risk-adjusted view

Judging the portfolios by return per unit of risk, rather than raw return, adds a useful check. The ratios are close across the risk-graded portfolios, which is itself informative: taking more risk bought more return, but not much more return *per unit of risk*.

| Portfolio | Sharpe | Sortino | Calmar | Longest spell underwater |
|-----------|--------|---------|--------|--------------------------|
| Defensive (20%) | 0.48 | 0.57 | 0.25 | 2.8 years |
| Cautious (40%) | 0.52 | 0.66 | 0.25 | 2.5 years |
| Balanced (60%) | 0.51 | 0.63 | 0.20 | 3.2 years |
| Growth (80%) | 0.48 | 0.60 | 0.18 | 5.2 years |
| Adventurous (100%) | 0.47 | 0.57 | 0.16 | 5.9 years |

(Sharpe and Sortino assume a 2% cash rate; the exact figure does not change the ranking.)

## Headline result

Over almost 23 years, the risk labels ranked risk correctly, but in 2022 a "cautious" portfolio produced **82% of the all-equity portfolio's loss for the year** (against 29% in 2008) once bonds stopped diversifying, and then spent **longer underwater than the aggressive portfolios** because its bond ballast stayed depressed while equities rallied. Meanwhile a plain equity holding grew far more concentrated in a few mega-caps, so a "balanced" label in 2025 covers a different exposure than it did in 2019. A static label ranks risk well but cannot communicate the full distribution of outcomes, nor keep a client's suitability current as markets move.

## Method

**Portfolios.** Five risk-graded portfolios defined by equity weight, rebalanced to target every year, plus one semiconductor-tilted sleeve. The equity portion is a **global blend**, not the US alone, because that is closer to what a UK wealth manager's model portfolios hold: every unit of equity is split 60% US, 30% developed markets outside the US, and 10% emerging markets, roughly global market-cap weight.

| Portfolio | Equity (global blend) | Bonds |
|-----------|-----------------------|-------|
| Defensive | 20% | 80% |
| Cautious | 40% | 60% |
| Balanced | 60% | 40% |
| Growth | 80% | 20% |
| Adventurous | 100% | 0% |
| Semis-tilt | 70% global equity + 30% semiconductors | 0% |

So a "cautious" 40% equity portfolio is really 24% US, 12% developed-ex-US, 4% emerging, and 60% bonds. The equity/bond bands match how risk-graded portfolios are structured, and the equity is genuinely global, but this is still a simplification of a real model portfolio.

**Data.** Free total-return series (dividends reinvested) from Yahoo Finance: SPY (US equity), EFA (developed ex-US), EEM (emerging), AGG (US aggregate bonds), plus RSP (equal-weighted US) for the concentration test and SOXX (semiconductors) for the theme test. The common window, October 2003 to July 2026, covers the 2008 crisis, the 2020 COVID crash, the 2022 rate shock, and the 2023 to 2025 AI boom.

**Measures.** CAGR, annualised volatility, maximum drawdown, worst rolling 12-month return, calendar-year returns, Sharpe, Sortino, Calmar, and time spent below a previous high.

## Limitations

What this project does **not** prove. This section is deliberately long, because the boundaries are the point.

- **Simplified portfolios.** Two- and three-asset allocations from broad indices, not any firm's real model portfolios, which hold more asset classes and are actively managed.
- **Bonds and currency are a US proxy, so the UK conclusion is a caveat, not a result.** The bond side uses US aggregate bonds, and everything is in US dollars. A real UK portfolio might hold gilts, global bonds, credit, short-duration or hedged bonds, and cash, and currency hedging alone can change bond returns substantially. UK gilts are widely reported to have had a record fall in 2022, which suggests the direction of the 2022 finding would hold for a UK investor, but this project does not model a UK bond allocation and the result should not be read as the precise UK experience.
- **Concentration is measured, AI attribution is not.** Finding 2 demonstrates mega-cap concentration through the cap-weighted versus equal-weighted gap. It does not prove an AI-specific bet; that would need a holdings-level decomposition of index weights and return contribution, which is the natural next step.
- **No fees or tax.** Platform charges, fund costs, and ISA or pension wrappers are not modelled, and all of them matter to a real client.
- **Volatility and drawdown are imperfect stand-ins for risk.** A client's real risk is whether they meet their goals and can hold the path. These statistics do not capture capacity for loss or behaviour under stress.
- **The past is not a forecast.** Every finding is descriptive. That the theme rewarded a high-tolerance client from 2023 to 2025 says nothing about the next five years.
- **Annual rebalancing is a modelling choice.** A different rule would move the numbers, though not the story.

## Reproducing the analysis

```
pip install -r requirements.txt
cd analysis
python3 fetch_data.py     # downloads the data into ../data/
python3 analyse.py        # prints the results, writes results.md and ../figures/
```

Every number in this README comes from `analysis/analyse.py`, and the full printout is saved in `analysis/results.md`.

## Data sources

Public market data from Yahoo Finance. No paid or proprietary data is used.
