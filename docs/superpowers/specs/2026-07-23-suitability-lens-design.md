# The Suitability Lens — design

**Date:** 2026-07-23
**Status:** approved for planning
**Companion to:** the "Does cautious mean cautious?" analysis (root `README.md`)

## Purpose

The paper diagnoses a problem: a static risk label ranks market risk but does not
describe the risk a client actually faces, because the portfolio's risks and the
client's needs both move while the label stays still. The Suitability Lens turns that
diagnosis into a tool a discretionary manager would act with. It takes three real
client situations, shows the two kinds of risk side by side (market risk and goal
risk), flags the drift that bites each client, reads out present-day conditions that
would trigger a decision, and ends with a plain-English review note of the kind a
manager sends a private client.

It exists to prove two things in an interview at once: that the author can think like
a portfolio manager (construct, weigh, decide) and that the author can be trusted in
front of a client (translate, explain, recommend). Both halves of the discretionary
fund management job, in one artifact.

## Who it is for

- The primary reader is an interviewer at a UK private-client wealth manager
  (Rathbones, RBC Brewin Dolphin, Brooks Macdonald, Quilter Cheviot, Evelyn Partners),
  opening a link on a phone.
- The secondary reader is the author, using it to rehearse the reasoning out loud.

### Success criteria

1. An interviewer with no context understands the market-risk-versus-goal-risk point
   within the first screen.
2. Every number on the page traces back to the same data and engine as the paper, so
   the two never contradict each other.
3. Each client ends in a *different* discretionary decision, so the tool shows
   judgment rather than one repeated move.
4. The page is fully self-contained: no external calls, works offline, works on mobile,
   renders in light and dark.
5. Nothing on the page overstates what the numbers are. Every figure is labelled
   illustrative, USD, and as-of a stated date.

## The three client cases

Each client showcases one of the paper's three drifts and ends in its own decision.

### Margaret, 66 — the retiree (objective drift)
- Just retired. Pot of £600,000. Wants roughly £24,000 a year (4%), rising with
  inflation, for a 30-year retirement. Risk-profiled **cautious**.
- The tension: her market risk is genuinely low, but her *goal* risk is high. The
  paper's Finding 4 showed the most cautious portfolio was the least likely to last a
  long retirement (74% survival versus about 92% for balanced or growth).
- Discretionary lever: a risk-band slider (cautious to growth). As it moves, market
  risk rises and goal risk falls, so the trade-off is visible in real time.
- The decision: take *more* market risk to reduce goal risk. The counterintuitive call.

### Tom, 28 — the house saver (diversification drift)
- Has £40,000, adds £500 a month, wants a house deposit in about 6 years. Risk-profiled
  **balanced**.
- The tension: over a short horizon, market risk is the live threat, not goal risk. A
  "balanced" label leans on bonds cushioning equities, but the paper's Finding 1 showed
  that cushion failed in 2022 when stock-bond correlation flipped positive.
- Discretionary lever: a control over how much of the risk sits in the bond sleeve,
  showing that the 2022-style cushion is not what the label implies over his horizon.
- The decision: de-risk toward the goal as the horizon shortens, and do not assume the
  bond sleeve protects the way it used to.

### Priya, 45 — the concentrated investor (concentration drift)
- Long horizon, risk-profiled **adventurous**, but her equity sleeve has drifted into a
  mega-cap and semiconductor-heavy bet (the paper's SOXX / stress sleeve).
- The tension: two "adventurous" clients can hold very different real risk. The paper's
  Finding 3 showed the semis tilt returned +69% in 2023 but carried a -67% max drawdown
  and 31% volatility.
- Discretionary lever: a concentration slider (diversified to semis-tilt). Market risk
  climbs sharply while the label stays "adventurous" throughout.
- The decision: trim concentration the client did not know she was carrying.

## Architecture

Three layers. The first two run once in Python at build time; the third is a static
page the browser drives.

### 1. Data layer — refresh to latest close
- Reuse `analysis/fetch_data.py` (`TICKERS`, `fetch`, `main`) to pull the latest Yahoo
  chart data for SPY, EFA, EEM, AGG, RSP, SOXX into `data/*.csv`.
- Every build stamps a single as-of date (the latest common close across the CSVs).
  This is the meaning of "live" that is honest here: current as of the last rebuild,
  labelled as such, not a real-time feed.

### 2. Compute layer — `suitability-lens/build_cases.py`
Imports the existing modules rather than reimplementing anything.
- From `analysis/analyse.py`: `load_prices`, `portfolio_value`, `graded`, `PORTFOLIOS`,
  `STRESS`, `RISK_BANDS`, `annual_vol`, `max_drawdown`, `worst_rolling_year`,
  `longest_underwater_days`, the rolling stock-bond correlation, and the SPY-versus-RSP
  concentration comparison.
- From `analysis/monte_carlo.py`: `monthly_returns`, `bootstrap_paths`, `survival_prob`,
  and the accumulation fan.
- For each client it computes a **grid** across an allocation axis (7 to 9 steps, from
  the client's most-cautious to most-growth or diversified-to-concentrated variant).
  At each step it records the market-risk stats (from the 23-year history) and the
  goal-risk figure (from the block bootstrap). The slider later snaps to these steps,
  so every "live" update is an instant lookup, not in-browser simulation, and every
  value is one the engine actually produced.
- It also computes the **current-conditions signals** (see next section).
- Output: one JSON blob (`suitability-lens/cases.json` for inspection) embedded directly
  into the page at build time.

### 3. Page layer — `suitability-lens/index.html` (built from a template)
- Self-contained HTML with inline CSS and JS. No external libraries, fonts, or images.
  Charts are hand-rolled inline SVG (a goal-outcome fan and a market-versus-goal gauge)
  driven by the embedded JSON. Theme-aware (light and dark). Mobile-first, single
  column, no horizontal scroll.
- Structure: framing line, three client tabs, and per client: the profile, the two-lens
  risk readout, the drift flag with its number, the current-conditions panel, the
  discretionary slider, and the review note.

## The current-conditions layer

Two elements, both built from the freshest data, answering "a manager uses live
conditions to adjust portfolios."

### Refreshed-to-latest (meaning #2)
The whole tool is rebuilt on the latest close and stamped "data as of DD Mon YYYY".
Rebuilds happen in a session, since the author cannot run Python on mobile. This is
stated plainly on the page.

### Live-regime monitor (meaning #3)
A "current conditions" panel per client that turns each drift into a present-day signal:
- **Correlation regime** (for Margaret and Tom): the most recent rolling stock-bond
  correlation. When positive, the bond diversification the cautious and balanced labels
  rely on is currently compromised, so the drift is a live concern, not a historical
  one. Example readout: "Right now stock-bond correlation is +0.2. The diversification a
  cautious label relies on is compromised today."
- **Concentration level** (for Priya): the most recent SPY-versus-RSP spread as a proxy
  for how concentrated the market is in its largest names. A wide recent spread means
  the concentration drift is elevated now.

Each signal has an explicit "elevated / normal" reading and one sentence on what it
means for that client's decision. The panel is honest that these are indicators built
from public index proxies, not proprietary signals.

## The client review notes

The differentiator, and the client-trust half of the job. One short note per client,
written the way a discretionary manager writes to a private client:
- States the current position, the concern, the recommended change, and the trade-off
  in the client's own terms.
- Humanizer rules apply in full: no em dashes, no buzzwords, plain English, specific
  numbers, varied sentence length. Run the `the-humanizer` skill over each note before
  shipping.
- Example trade-off sentence for Margaret: "This means bigger ups and downs along the
  way, in exchange for a materially higher chance your money lasts the full 30 years."

## Data flow

```
fetch_data.py  ->  data/*.csv (as of latest close)
                       |
build_cases.py  imports analyse.py + monte_carlo.py
                       |
   +-- per-client allocation grid: market-risk stats + goal-risk probs
   +-- current-conditions signals: correlation regime, concentration level
                       |
                 cases.json  --embedded-->  index.html (static, self-contained)
                       |
        committed to repo  +  published as an Artifact link
```

## Honesty guardrails

Carried straight from the paper, non-negotiable:
- Every figure labelled illustrative, USD, and as-of a stated date.
- "Nothing here is investment advice" on the page.
- Risk bands are illustrative, in the style of the industry, not any firm's proprietary
  bands (as already stated in `analyse.py`).
- The goal-risk figures are simulation output, sensitivity-dependent, not a promise. The
  page states the conditions under which the retiree finding holds (long horizon, 4%+
  withdrawals) rather than presenting it as universal.
- No fake precision. Percentages rounded the way the paper rounds them.

## Delivery

- New folder `suitability-lens/` containing: `build_cases.py`, the HTML template, the
  built `index.html`, and `cases.json`.
- Committed to branch `claude/building-session-dtbmbc`.
- Published as an Artifact for a live, mobile-openable link.
- A short companion section added to the root `README.md` linking the tool, so the repo
  tells one story: the paper diagnoses, the tool acts.
- A refreshed PDF of the README is regenerated if the README changes.

## Scope — explicitly not doing (YAGNI)

- No real-time price feed in the browser. Not possible in a published artifact (no
  external-data capability on this account) and it would not strengthen the argument.
- No robo-adviser or automated advice logic. The tool illustrates reasoning; it does not
  advise.
- No full "run the book" multi-year simulator. Three clients, one page.
- No login, accounts, or persistence.
- No new asset classes, currencies, or a sterling/gilt rebuild. Those remain optional
  future work in the paper's own backlog.

## Testing and verification

- `build_cases.py` runs clean and regenerates `cases.json` deterministically (fixed RNG
  seed for the bootstrap, matching the paper).
- Spot-check that headline numbers in `cases.json` match the paper's published figures
  (Margaret's survival probabilities, Priya's semis drawdown and volatility) so the tool
  and paper never disagree.
- Open `index.html` in Chromium headless and confirm it renders with no console errors
  and no external network requests.
- Confirm the page is readable on a narrow (mobile) viewport and in dark mode.
- Run `the-humanizer` over all client-facing prose.
