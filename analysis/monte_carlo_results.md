# Monte Carlo results (historical block bootstrap)

10,000 paths, 30-year horizon, 6-month blocks, sampled from 2003-10-31 to 2026-07-31.
Monthly rebalancing; returns are nominal. The decumulation test uses a GBP 500,000 pot, a 4% initial withdrawal growing 2.5% a year.

## Accumulation - value of £1 after 30 years (range of outcomes)

| Portfolio | 5th pct | 25th | Median | 75th | 95th |
|-----------|--------|------|--------|------|------|
| Defensive (20%) | £2.4 | £3.2 | £3.8 | £4.6 | £5.9 |
| Cautious (40%) | £2.9 | £4.3 | £5.6 | £7.3 | £10.5 |
| Balanced (60%) | £3.2 | £5.6 | £8.2 | £11.6 | £19.1 |
| Growth (80%) | £3.4 | £7.0 | £11.5 | £18.2 | £35.0 |
| Adventurous (100%) | £3.4 | £8.7 | £15.9 | £28.1 | £63.2 |

Even inside one label, the spread is large: a 'balanced' £1 lands anywhere from about £3.2 to £19.1 (5th to 95th percentile) after 30 years.

## Decumulation - probability a £500k pot lasts 30 years (4% inflation-linked)

| Portfolio | Probability of lasting 30 years | Median years it lasted |
|-----------|--------------------------------|------------------------|
| Defensive (20%) | 75% | 30+ |
| Cautious (40%) | 89% | 30+ |
| Balanced (60%) | 92% | 30+ |
| Growth (80%) | 92% | 30+ |
| Adventurous (100%) | 91% | 30+ |

Highest survival probability: Growth (80%) at 92%. Note the most cautious portfolio is not automatically the safest for a drawdown client: too little growth can lose to inflation and longevity just as too much risk can lose to a bad early sequence.

