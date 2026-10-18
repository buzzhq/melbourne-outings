# Ron's Melbourne Outings

Weekly guide to outings around Melbourne: hikes, bike trails, music, new tours on sale, stand-up comedy, sports, basketball, musicals & theatre, exhibitions and markets.

Live: https://buzzhq.github.io/melbourne-outings/ (GitHub Pages, `main` branch, repo root).

## Layout
- `index.html`: archive page. Renders the edition list from `editions.json` via `fetch` (newest first), with a static no-JS fallback list baked in between `<!-- EDITIONS -->` markers.
- `editions/YYYY-MM-DD.html`: one page per edition (generated).
- `editions.json`: machine-readable list of editions (`date`, `edition`, `file`, `title`, `top_picks`, `item_count`).
- `data/YYYY-MM-DD.json`: source data for each edition.
- `outings.css`: standalone stylesheet shared by every page.
- `tools/build.py`: generator (Python 3, no dependencies).

## Adding a new edition (weekly)
1. Create `data/YYYY-MM-DD.json` (copy the previous week's file as a template). Fields per item:
   ```json
   {"section": "Music", "top": true, "name": "Artist / event (shown bold, links to url)",
    "url": "https://…", "when": "Sat 14 Nov, 7:30pm", "end": "2026-11-14",
    "venue": "Rod Laver Arena", "price": "$99–$149", "note": "One short sentence."}
   ```
   - `section` is one of: `Hikes`, `Bike`, `Music`, `Tours`, `Comedy`, `Sport`, `Basketball`, `Theatre`, `Exhibitions`, `Markets`.
   - `top: true` puts the item in **Top picks** (and in the index summary). Aim for about 3.
   - `end` is the last date (ISO `YYYY-MM-DD`) of the event. After that date the card is greyed out automatically (Melbourne time). Omit it for "any day" items such as hikes and rides.
   - Bump `edition` by 1 and set `date` to the edition date.
2. Build: `python3 tools/build.py data/YYYY-MM-DD.json`
   This writes `editions/YYYY-MM-DD.html` from the same template, appends or updates the entry in `editions.json` (kept newest first) and refreshes the fallback list in `index.html`.
   (Without the script: copy the last edition page, edit the cards, and append an entry to `editions.json`. The index renders from the JSON on its own.)
3. Commit and push:
   ```bash
   git add data editions editions.json index.html
   git commit -m "Edition YYYY-MM-DD" && git push
   ```
   Pages redeploys in a minute or two.
