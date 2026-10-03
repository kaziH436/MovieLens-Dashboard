# Build log (raw process notes)

Not a polished report — keep this for next week's writeup.

## Moment 1 — Planning prompt (2026-10-03)

**Prompt I gave (assignment, summarized):** Live Streamlit Community Cloud URL. MovieLens `movie_ratings.csv`. Four charts (genre distribution, genre mean ratings, mean rating by release year, top 5 movies with rating-count floors of 50 then 150). Widgets required. Keep a real prompt log.

**What the AI planned first:**
- Unique-movie genre counts for Q1 (not a 19-slice pie).
- Rating-level means for Q2.
- Use `year` (release), not `rating_year`, for Q3.
- One min-ratings slider for Q4 instead of two static charts.
- Altair + pandas + Streamlit; cache the CSV load.

**What I changed / didn't:** Kept that plan. After adding the CSV, columns were `user_id` / `movie_id` (not `userId` / `movieId`), plus extras (`decade`, `rating_year`). Dataset is ~10.9 MB / 100k rows — small enough for GitHub.

## Moment 2 — First `app.py` implementation

**Prompt:** Implement the attached plan; do not edit the plan file; finish the todos.

**What it produced on the first try:**
- Single `app.py`: cached `load_ratings` / `explode_genres` / unique movies.
- Sidebar: genre multi-select (all selected), release-year slider (Q3), min-ratings slider default 50 (Q4).
- Four Altair charts + a short 50-vs-150 caption under Q4.
- `requirements.txt` (unpinned mins after Python 3.14 had no wheel for pandas 2.2.3), `runtime.txt` (`python-3.12` for Streamlit Cloud), `.gitignore`, this log, README.

**First-run issues to check (and fix if they show up):**
- `year` comes in as floats (`1996.0`) — coerce to nullable int.
- Empty genre multi-select should not crash — `st.stop()` after a warning.
- Q1 must sort by count, not alphabet.
- Q3 x-axis must be release year; hover includes `n_ratings` so sparse early years are obvious.

## Moment 3 — What we changed and why

- **Q1 = unique movies, not rating volume.** The question is “movies that were rated,” not “how many ratings each genre got.” Multi-genre titles still count in each genre; caption says totals exceed 1,682.
- **No pie chart.** 19 genres; horizontal bars, sorted.
- **Q4 slider instead of two frozen charts.** Assignment asks what changes at 50 vs 150; slider + a caption comparing those two floors answers it without duplicating the page.
- **Genre filter also applies to Q4** so the widgets actually change all four views.
- **Did not commit/push in the first implementation pass** — GitHub push and Streamlit Cloud login still need an explicit go-ahead; Cloud cannot deploy local files.
