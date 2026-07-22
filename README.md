# Does "cautious" mean cautious?

Testing whether risk-graded model portfolios delivered on their risk labels, and where they did not, using almost 23 years of public market data (October 2003 to July 2026).

> Nothing here is investment advice. It is a historical analysis built entirely from free, public data.

---

## The question

When a wealth manager profiles a private client, the client is placed on a risk scale (for example cautious, balanced, adventurous) and mapped to a model portfolio. That label is a promise about how much risk the client will actually live through.

This project asks a simple question: **did the labels hold up?** When a portfolio is called "cautious," was the risk a cautious client experienced actually consistent with that word, in good markets and bad?

The short answer: the labels are honest about the *ranking* of risk, but they hide two things a client would care about. In 2022 a cautious portfolio lost far more than its name suggests. And since 2023 a "balanced" equity holding has quietly become a concentrated bet on a handful of AI companies, with no label ever changing.

## Why it matters for a private client

Risk profiling is the core of suitability. Get it wrong in either direction and you have failed the client. Label a portfolio too safe and a cautious client takes a loss they were never prepared for, panics, and sells at the bottom. Label it too conservatively and an adventurous client with the tolerance to hold more risk is held back from returns they could suitably have earned.

A label is static. The risk underneath it is not. This project measures three ways that gap opened up.

## Findings

### Finding 0: the labels get the ranking right

Across the full period, the portfolios line up exactly as their labels promise. More equity meant more volatility and deeper drawdowns, every step of the way.

| Portfolio | CAGR | Volatility | Max drawdown | Worst 12 months |
|-----------|------|-----------|--------------|-----------------|
| Defensive (20% equity) | 4.6% | 5.5% | −18.1% | −16.9% |
| Cautious (40%) | 6.0% | 7.9% | −23.6% | −22.9% |
| Balanced (60%) | 7.3% | 11.2% | −36.2% | −31.0% |
| Growth (80%) | 8.4% | 15.0% | −47.7% | −41.0% |
| Adventurous (100%) | 9.5% | 19.2% | −58.1% | −51.0% |

So far the labels are doing their job. The interesting part is where they stop.

### Finding 1: in 2022, "cautious" was not cautious

A cautious portfolio leans on bonds to cushion equity losses. That cushion depends on bonds and equities not falling at the same time. Usually they do not. In 2022 they did, because rising interest rates hit both at once.

The result: the cautious portfolio, with only 40% in equities, lost almost as much as the all-equity one.

| Year | Cautious (40% equity) | Adventurous (100%) | Cautious loss as share of all-equity loss |
|------|----------------------|--------------------|-------------------------------------------|
| **2008** | −11.1% | −38.8% | **29%** (bonds cushioned) |
| **2022** | −14.6% | −17.8% | **82%** (bonds fell too) |

In 2008 the bond cushion worked exactly as a cautious client would expect: they took under a third of the pain the aggressive investor took. In 2022 they took more than four fifths of it. Same label, same 40% equity, completely different experience. A client anchored to the word "cautious" was not prepared for 2022, and the label gave them no warning.

This holds up two ways. It survives using a globally diversified equity mix rather than the US alone (I tested both, and the ratios barely move). And it is if anything conservative for a UK client: UK government bonds had their worst year on record in 2022, falling harder than the US bonds used here, so a UK cautious portfolio would have breached its label by more, not less.

![The bond cushion in 2008 vs 2022](figures/bond_cushion_2008_vs_2022.png)

### Finding 2: a "balanced" equity holding became an AI bet

Between 2023 and 2025, money poured into a small number of AI mega-caps and the semiconductor and memory supply chain behind them. Because standard equity indices weight companies by size, those few winners came to dominate the index, and every client holding a plain equity fund became more concentrated in one theme. Their risk label never changed.

You can see the effect by comparing the normal cap-weighted S&P 500 (SPY) with its equal-weighted twin (RSP), where every company counts the same. If the two move together, breadth is healthy. If the cap-weighted version pulls ahead, a few giants are carrying the market.

- In **2023** the cap-weighted index beat the equal-weighted one by **12.9 percentage points**.
- In **2024** it beat it again by **12.8 percentage points**.

Two straight years of double-digit gaps is a large, unusual concentration. The point for suitability: a "balanced" client in 2025 holds a materially different risk to a "balanced" client in 2019, and nobody re-profiled them.

![Concentration: SPY vs RSP](figures/concentration_spy_vs_rsp.png)

### Finding 3: the AI theme rewarded only the clients who could hold it

Suitability cuts both ways. A genuinely high-tolerance client could reasonably have tilted toward the semiconductor theme, and would have been well rewarded. Semiconductors (SOXX) returned **+68.8% in 2023**.

But that return was only *available* to someone who could sit through the drawdowns to collect it. The same holding fell **−36.4% in 2022** and **−50.4% in 2008**, with a worst peak-to-trough fall of **−67%** over the period and volatility of 31%, close to double the all-equity portfolio's.

That is the real lesson, and it is a suitability lesson, not a stock tip. The theme did not decide the outcome. The client's risk profile did. A cautious client who chased it would almost certainly have sold near the bottom and locked in the loss. Only a client whose profile genuinely supported that volatility could have held on and been paid for it.

![The semis theme: reward and drawdown](figures/semis_reward_vs_drawdown.png)

## Headline result

Over almost 23 years, a "cautious" model portfolio took **82% of the all-equity loss in 2022** once its bond cushion failed, against just **29% in 2008** when the cushion worked. The risk label stayed the same while the risk underneath it changed completely. The same period shows the AI/semiconductor theme returning **69% in 2023** but demanding a **67% drawdown** to hold, which only a suitably profiled client could bear.

## Method

**Portfolios.** Five risk-graded portfolios defined by equity weight, rebalanced to target every year, plus one semiconductor-tilted sleeve to represent a theme bet a suitably adventurous client might hold. The equity portion is a **global blend**, not the US alone, because that is what a UK wealth manager's model portfolios actually hold: every unit of equity is split 60% US, 30% developed markets outside the US, and 10% emerging markets, roughly global market-cap weight.

| Portfolio | Equity (global blend) | Bonds |
|-----------|-----------------------|-------|
| Defensive | 20% | 80% |
| Cautious | 40% | 60% |
| Balanced | 60% | 40% |
| Growth | 80% | 20% |
| Adventurous | 100% | 0% |
| Semis-tilt | 70% global equity + 30% semis | 0% |

So a "cautious" 40% equity portfolio is really 24% US, 12% developed-ex-US, 4% emerging, and 60% bonds. This is still a simplification of a real model portfolio, but a fair one: the equity/bond bands match how risk-graded portfolios are structured, and the equity is genuinely global.

**Data.** Free total-return series (dividends reinvested) from Yahoo Finance: SPY (US equity), EFA (developed markets ex-US), EEM (emerging markets), AGG (US aggregate bonds), plus RSP (equal-weighted US equity) for the concentration test and SOXX (semiconductors) for the theme test. The common window is October 2003 to July 2026, set by the youngest series. It covers the 2008 crisis, the 2020 COVID crash, the 2022 rate shock, and the 2023 to 2025 AI boom.

**Risk measures.** Annualised volatility, maximum drawdown, worst rolling 12-month return, and calendar-year returns, computed per portfolio and within each stress episode.

## Limitations

What this project does **not** prove. This section is deliberately long, because being clear about the boundaries is the point.

- **Index proxies, not real portfolios.** These are simplified two- and three-asset allocations built from broad indices, not any firm's actual model portfolios, which hold more asset classes and are actively managed.
- **No fees, no tax.** Platform charges, fund costs, and ISA or pension wrappers are not modelled. All of them matter to a real client.
- **Bonds and currency.** The equity side is global, but the bond side uses US aggregate bonds, where a UK portfolio would hold gilts and global bonds. Everything is measured in US dollars, so the sterling experience of a UK investor, including currency moves, is not modelled. As noted above, using UK gilts would deepen the 2022 finding rather than soften it.
- **Volatility and drawdown are imperfect stand-ins for risk.** A client's real risk is whether they meet their goals and can stomach the path. These statistics do not capture capacity for loss or behaviour under stress.
- **The past is not a forecast.** Every finding here is descriptive. That the theme rewarded a high-tolerance client from 2023 to 2025 says nothing about the next five years.
- **Annual rebalancing is a modelling choice.** A different rule would change the numbers, though not the story.

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
