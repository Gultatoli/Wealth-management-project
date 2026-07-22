# Monte Carlo results (historical block bootstrap)

10,000 paths, 30-year horizon, 6-month blocks, sampled from 2003-10-31 to 2026-07-31.
Monthly rebalancing; returns are nominal. The decumulation test uses a GBP 500,000 pot, a 4% initial withdrawal growing 2.5% a year.

## Accumulation - value of £1 after 30 years (range of outcomes)

| Portfolio | 5th pct | 25th | Median | 75th | 95th |
|-----------|--------|------|--------|------|------|
| Defensive (20%) | £2.4 | £3.2 | £3.8 | £4.6 | £5.9 |
| Cautious (40%) | £2.8 | £4.3 | £5.6 | £7.3 | £10.6 |
| Balanced (60%) | £3.1 | £5.7 | £8.1 | £11.7 | £19.3 |
| Growth (80%) | £3.3 | £7.1 | £11.5 | £18.4 | £35.4 |
| Adventurous (100%) | £3.3 | £8.7 | £15.9 | £28.3 | £63.2 |

Even inside one label, the spread is large: a 'balanced' £1 lands anywhere from about £3.1 to £19.3 (5th to 95th percentile) after 30 years.

## Decumulation - probability a £500k pot lasts 30 years (4% inflation-linked)

| Portfolio | Probability of lasting 30 years | Median years it lasted |
|-----------|--------------------------------|------------------------|
| Defensive (20%) | 74% | 30+ |
| Cautious (40%) | 89% | 30+ |
| Balanced (60%) | 92% | 30+ |
| Growth (80%) | 92% | 30+ |
| Adventurous (100%) | 91% | 30+ |

Highest survival probability: Growth (80%) at 92%. Note the most cautious portfolio is not automatically the safest for a drawdown client: too little growth can lose to inflation and longevity just as too much risk can lose to a bad early sequence.

## Sensitivity - does the result survive different assumptions?

### Survival probability by withdrawal rate (30-year horizon)

| Portfolio | 3.0% | 3.5% | 4.0% | 4.5% | 5.0% |
|---|---|---|---|---|---|
| Defensive (20%) | 99% | 93% | 74% | 46% | 20% |
| Cautious (40%) | 99% | 96% | 89% | 76% | 59% |
| Balanced (60%) | 99% | 96% | 92% | 85% | 75% |
| Growth (80%) | 98% | 95% | 92% | 87% | 81% |
| Adventurous (100%) | 97% | 95% | 91% | 87% | 82% |

### Survival probability by horizon (4% withdrawal)

| Portfolio | 20 yrs | 30 yrs | 40 yrs |
|---|---|---|---|
| Defensive (20%) | 100% | 74% | 27% |
| Cautious (40%) | 99% | 89% | 69% |
| Balanced (60%) | 99% | 92% | 82% |
| Growth (80%) | 98% | 92% | 86% |
| Adventurous (100%) | 97% | 91% | 87% |

Across all 15 withdrawal/horizon combinations, the most cautious (Defensive) portfolio had the lowest survival probability in 9 of them. The effect is real but conditional, not universal. It appears at longer horizons (30 to 40 years) and moderate-to-high withdrawal rates (4% and above), and it disappears over short horizons or at low withdrawals, where every portfolio survives comfortably. So the honest claim is a conditional one: for a long-horizon client drawing a meaningful income, the most cautious portfolio can be the least likely to last. That is a statement about the client's objective, not about the portfolio in isolation.

