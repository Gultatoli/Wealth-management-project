# Does "cautious" mean cautious?

Testing whether risk-graded model portfolios delivered on their risk labels, and where they did not, using ~20 years of public market data.

> **Status:** work in progress. The method and framing below are settled. Numbers marked `[TBD]` are placeholders and will be filled from the analysis, not asserted in advance. Nothing in this repository is investment advice.

---

## The question

When a wealth manager profiles a private client, the client is placed on a risk scale (for example cautious, balanced, adventurous) and mapped to a model portfolio. That label is a promise about how much risk the client will actually live through.

This project asks a simple question: **did the labels hold up?** When a portfolio is called "cautious," was the risk a cautious client experienced actually consistent with that word, across good markets and bad?

The answer turns out to be "mostly, but not always," and the exceptions are the interesting part.

## Why it matters for a private client

Risk profiling is the core of suitability. Get it wrong in either direction and you have failed the client:

- Label a portfolio too safe, and a cautious client takes a loss they were never prepared for, panics, and sells at the bottom.
- Label it too conservatively, and an adventurous client with the tolerance and time horizon to hold more risk is quietly held back from returns they could suitably have earned.

A label is static. The risk underneath it is not. This analysis tests three ways that gap opened up in the last two decades.

## What the analysis tests

Three findings, one spine: **risk labels stay fixed, but the risk beneath them drifts.**

1. **Cautious portfolios in 2022.** The year bonds and equities fell together. A cautious portfolio leans on bonds to cushion equity losses. In 2022 that cushion failed. The test measures how far the drawdown of a cautious portfolio exceeded what its label implies. `[TBD]`

2. **Passive equity became an AI concentration bet.** Between roughly 2023 and 2025, money flowed into a handful of AI mega-caps and the memory and semiconductor supply chain behind them. Standard cap-weighted equity indices became far more concentrated in one theme, without any client's risk label changing. The test measures this concentration through the gap between a cap-weighted index and its equal-weighted twin. `[TBD]`

3. **The AI/semiconductor theme and who could suitably hold it.** A genuinely high-tolerance client could suitably have held a semiconductor tilt and been rewarded in 2023 to 2025. The point is not that the theme won. The point is that the returns were only *available* to a client who could sit through the drawdowns to collect them: the same names fell around a third in 2022 and again in the 2000 dot-com bust. The test measures the full picture, upside and drawdown, to show which risk profile could actually hold the position. `[TBD]`

The thread through all three: **the suitability decision, matching the portfolio to the client, drove the outcome more than the choice of assets did.**

## Method

**Portfolios.** Five risk-graded model portfolios defined by equity weight, from defensive to adventurous, rebalanced annually. Plus one thematic sleeve (semiconductors) to represent a high-conviction tilt a suitably adventurous client might hold.

| Portfolio | Equity | Bonds |
|-----------|--------|-------|
| Defensive | 20% | 80% |
| Cautious | 40% | 60% |
| Balanced | 60% | 40% |
| Growth | 80% | 20% |
| Adventurous | 100% | 0% |
| Thematic (semis tilt) | see notes | |

**Data.** Free, publicly available total-return series (dividends reinvested) via Yahoo Finance. Broad US equity, aggregate bonds, an equal-weighted equity index for the concentration test, and a semiconductor index for the thematic sleeve. Exact tickers and the common date window are documented in the analysis and depend on data availability.

**Period.** Roughly 2005 to 2025, the longest clean window the chosen series share. It covers the 2008 financial crisis, the 2020 COVID crash, the 2022 rate shock, and the 2023 to 2025 AI boom.

**Risk measures.** Annualised volatility, maximum drawdown, and worst rolling 12-month return, computed per portfolio and within each stress episode.

## Headline result

`[TBD]` One sentence with a number, filled from the analysis. This is the line that goes on the CV.

## Limitations

What this project does **not** prove. This section is deliberately long, because being clear about the boundaries is the point.

- **Index proxies, not real portfolios.** These are simplified allocations built from broad indices, not any specific firm's model portfolios. Real ones hold more asset classes and are managed actively.
- **No fees, no tax.** Platform charges, fund costs, and the effect of ISA or pension wrappers are not modelled here. All of them matter over a real client's horizon.
- **US-centric data.** The longest clean histories are US series. A UK client holds globally, and currency effects are not modelled. Global indices are heavily US-weighted, so the concentration finding still travels, but this is a genuine simplification.
- **Volatility and drawdown are imperfect stand-ins for risk.** A client's real risk is whether they meet their goals and whether they can stomach the path. Statistics do not capture capacity for loss or behaviour under stress.
- **The past is not a forecast.** Every finding here is descriptive. That a theme rewarded a high-tolerance client from 2023 to 2025 says nothing about the next five years.
- **Annual rebalancing is a modelling choice.** Different rebalancing rules would change the numbers.

## Reproducing the analysis

`[TBD]` Once the analysis is written, this section will give the exact steps to reproduce every number and chart from scratch.

## Data sources

Public market data via Yahoo Finance. No paid or proprietary data is used.
