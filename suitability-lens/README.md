# The Suitability Lens

An interactive companion to the "Does cautious mean cautious?" analysis. Three
client cases showing market risk against goal risk, the drift that bites each, a
current-conditions signal read from the latest data, and a client-facing review
note.

- **Margaret, 66** (objective drift): a retiree whose most cautious portfolio is
  the least likely to fund a 30-year retirement.
- **Tom, 28** (diversification drift): a house saver whose bond cushion no longer
  cushions over a short horizon.
- **Priya, 45** (concentration drift): an adventurous investor carrying hidden
  concentration risk the label never shows.

Everything is computed in Python from the same data and engine as the analysis,
then embedded into a single self-contained `index.html`. No server, no external
calls.

## Rebuild

```bash
pip install pandas numpy matplotlib pytest
cd suitability-lens
python3 build_cases.py            # uses the committed data snapshot
python3 build_cases.py --fetch    # refreshes data to the latest close first
python3 -m pytest -q              # run the checks
```

`build_cases.py` writes `cases.json` and the self-contained `index.html`. Open
`index.html` in any browser.

## Files

- `clients.py` — the three client cases (pure data).
- `engine.py` — computation: market-risk lens, goal-risk lens, current-conditions
  signals. Imports the analysis modules; reimplements nothing.
- `notes.py` — the client-facing review notes.
- `build_cases.py` — assembles `cases.json` and calls the renderer.
- `template.html` / `render.py` — the self-contained page and how it is built.
- `test_*.py` — checks for each piece.
