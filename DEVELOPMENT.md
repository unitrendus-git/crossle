# Crossle — handoff and development notes

Last updated: 2026-10-14 (first release)

Crossle is a word game that sits between Wordle and Wordscapes. A small crossword grid of 3–6 hidden five-letter words is solved with Wordle-style feedback. Green letters lock into the grid and fill in any crossing word. The whole grid shares one guess budget.

## Where things live

| What | Where |
|---|---|
| Live game (public, no account) | https://unitrendus-git.github.io/crossle/ |
| Source repo | https://github.com/unitrendus-git/crossle (public, branch `main`, Pages serves `/`) |
| Claude preview copy (private) | https://claude.ai/artifact/CotZhHpiuYzh3Kmh3wVsFk — older build, see "Known gaps" |

Deploying is just pushing to `main`. GitHub Pages rebuilds in about 1–2 minutes. There is no build step.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole game: CSS, markup and script. No libraries. |
| `words.js` | `window.CROSSLE_ANS` (answer pool, ~2,027 words) and `window.CROSSLE_VAL` (extra accepted guesses, ~2,664). Space-separated strings. |
| `manifest.webmanifest`, `icon.svg` | Home-screen install metadata. |
| `.nojekyll` | Tells Pages to serve files as-is. |
| `tools/build_words.py` | Rebuilds `words.js` from SCOWL. Reproduces the live list exactly. |
| `tools/simulate_budgets.py` | Simulates solves per grid shape to set guess budgets. |

## How the game works (code map of `index.html`)

1. **Templates (`TPL`).** Each difficulty has grid shapes defined as word slots `[dir,row,col]` on a 5×5 board, each with a guess budget `b`.
   - Easy: H, I (3 words, 13 guesses)
   - Medium: Frame, Comb, Rake, E (4 words, 16 guesses)
   - Hard: Waffle (6 words, 21), Ladder and Gate (5 words, 19)
2. **Seeded generation (`buildPuzzle`).** The puzzle code, for example `m-d20261014` or `h-k3j9xq`, is hashed into a seeded RNG. The RNG picks a template and fills it by backtracking over the answer list, using a per-position letter index (`IDX`) for speed. The same code always produces the same grid on every device. That is what makes the daily grid and friend codes work. Generation takes about 12 ms on average in Node, with a 4,000-step cap per attempt and up to 30 reseeded attempts.
3. **Scoring (`score`).** Standard Wordle rules, including repeated letters, computed against one slot's answer only.
4. **Applying a guess (`apply`).** Greens go into `G.known` (cell → letter). A slot counts as solved when all of its cells are known, which can happen through crossings alone. The game is won when every slot is solved and lost when the budget runs out.
5. **Input.** Locked green cells are pre-filled and the cursor skips them, so a guess must agree with known crossings. Tapping a crossing cell twice toggles between Across and Down. Tab and the arrow keys cycle words.
6. **Codes and modes.**
   - Daily: `<d>-dYYYYMMDD`, using the device's local date.
   - Endless: `<d>-` plus 6 random characters.
   - Friend: any valid code, typed into the help sheet or opened from a `#code` link.
   - Codes must match `^[emh]-[a-z0-9]{3,12}$`.
7. **Storage.** `localStorage["crossle.v1"]`, best effort and per device. Contents: `{games:{code:{g:[[slot,word]...],t,counted}}, stats:{e|m|h:{played,won,streak,max,last,best}}, seen, mode, diff, endless:{d:code}}`. Games are stored as guess lists and replayed on load. The 40 most recent games are kept. Streaks count daily wins on consecutive days.
8. **Sharing.** "Copy result" gives a spoiler-free emoji summary per word plus a link. Endless and friend results link to `#code`, so the recipient gets the same grid.

## Word lists

- **Source:** SCOWL through the npm package `wordlist-english`. Answers come from sizes 10, 20 and 35. Accepted guesses come from sizes 10–55.
- **Answer filtering:** plurals, -ed, -ing and -ies forms are removed, because Wordle-style answers shouldn't be inflections.
- **`BLOCK_ALL`:** slurs and vulgarities. These are never answers and are rejected as guesses.
- **`DEMOTE`:** words that can be typed but are never answers (sperm, feces, enema, urine, vomit, lynch, queer).
- **Warning:** changing the answer list re-rolls every grid. Old friend codes and an in-progress daily then produce different puzzles, and a saved guess history can replay against the wrong answers. Change lists rarely, and bump the storage key (`crossle.v2`) when you do.

## Guess budgets

`tools/simulate_budgets.py` plays a solver that always guesses a random word consistent with what it knows, attacking the most-constrained word first. Results from 40 grids per shape:

| Shape | Median guesses | 90th percentile | Budget |
|---|---|---|---|
| H / I | 10 | 12 | 13 |
| Frame | 12 | 15 | 16 |
| Comb / E | 13–13.5 | 15 | 16 |
| Ladder / Gate | 16 | 18 | 19 |
| Waffle | 17 | 21 | 21 |

Real players are less consistent than the solver but choose words more cleverly. Tune these numbers from actual play.

## Constraints learned while setting this up

- The Claude GitHub connector on `unitrendus-git` **can push files** but **cannot create repos or change Pages settings** ("Resource not accessible by integration"). New repos and Pages settings must be done by hand on github.com.
- The connector only pushes text files. That's why the icon is SVG. iOS ignores SVG apple-touch-icons, so iPhones show a generic tile.
- The `gh` CLI in Claude's cloud sandbox has no valid token. Pushes go through the connector.
- The cloud sandbox can't reach `*.github.io`. Check the live site from a phone or browser. To verify a push, fetch `raw.githubusercontent.com` and diff it against the local file.
- Pushing through the connector means sending whole file contents. After any push, diff the raw file against the source.

## Known gaps

- **The Claude preview copy is out of date.** It has an older word list, so its grids differ from the live site, and its share text has no link. Republish it from the current `index.html` + `words.js` or retire it.
- **iPhone home-screen icon:** add `apple-touch-icon.png` (180×180) by uploading it on github.com, since the connector can't push binary files.
- **No offline mode:** a service worker would let the game run without signal.
- **Daily date:** the daily grid follows each device's local midnight, so people in different time zones roll over at different times.
- **No end-to-end test:** checks so far were a Node generation benchmark (180 grids, 0 failures) and a headless-browser smoke test.

## Backlog ideas (not started)

- **Themed word packs.** A WoW/Classic-era pack (the "WorldleOfWarcraft" idea, tabled), music, or test gear. This would need longer or variable-length slots, and the grid currently assumes 5-letter words throughout.
- **Live two-phone race** on one shared grid. That needs a backend; GitHub Pages is static.
- **Past-dailies archive**, a hard mode where yellows must be reused, and a guess-distribution chart in stats.
- Tune budgets from real play and possibly add a "par" score.
