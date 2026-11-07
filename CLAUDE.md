# Sarathi: notes for Claude

Bhagavad Gita reader with a recitation coach. Live at https://sarathi.dhirajmakam.com.
Owner: Dhiraj (repo dmakam/sarathi, public). Most users are on phones; pilot users are family.

## Branches
- `mobile-first` is the working branch and is what is live (bottom tab bar, one-screen phone home).
- `main` is the older desktop-first version. If Dhiraj asks to revert the mobile-first changes,
  `main` is that earlier state (the "deploy-9" build); `mobile-first` starts at `37c9ed8`.

## Build and run
- Data: `git clone https://github.com/gita/gita.git src-data` (pinned to `c6fce39` in the Dockerfile).
- `python3 -I build/build.py --no-audio` writes `./site`; `cd site && python3 -m http.server 8000`.
- `./run-local.sh` runs the site plus the recitation coach locally (first run ~2 GB of downloads).
- Tests: `./run-tests.sh` (report in `tests/last-report.txt`).
- Output must be ASCII-only HTML: encode every non-ASCII character as an entity (`&#183;`, `&#8250;`)
  so nothing renders as mojibake on Dhiraj's Windows setup. Never leave literal `·` text in markup.

## Code map
- `build/build.py` generator (pages, nav, home cards, practice path, theme pages, chant attributes,
  `asset_version()` adds `?v=<hash>` to CSS/JS links). `build/content.py` curated layers.
- `assets/app.css` (phone rules appended at the end, breakpoint `max-width:760px`), `assets/app.js`
  (player with Chant / Word-by-word switch, home toggles, journey card), `assets/recite.js` (coach UI).
- `server/` recitation scorer (MMS forced aligner). `server/model-int8.pt` is NOT in git.
- `tools/avv_*.py` cut the Aarsha Vidya Varshini chanting into per-verse clips (permission granted;
  credit them on the player and the Sources page). Clips are NOT in git; on the server they live in
  `/home/deploy/sarathi-chant` and are mounted read-only at `/srv/chant`.

## Deploy (VPS 50.6.226.244, user `deploy`)
- Two containers on the shared `signal-desk-app` Caddy network: `sarathi-web` (static) and
  `sarathi-coach` (`/api/score`). Never install a host web server or systemd service.
- Server copy: `/home/deploy/sarathi`. Get the latest `mobile-first` code there, then `./deploy.sh`.
  It checks `docker ps`, only appends to `/home/deploy/signal-desk-app/Caddyfile`, then
  `caddy validate` and `caddy reload`.
- Caddy: `/assets/* /data/* /audio/* /chant/*` cached 7 days (CSS/JS are fingerprinted), pages `no-cache`.
- Ask before running anything on the server.

## Design rules (agreed with Dhiraj)
- Dark is the default for everyone, Light behind a toggle remembered per device. Production dark palette:
  page `#071E22`, cards `#0C2A2F`, borders `#1D4247`, text `#E4EFEC`, muted `#9DB6B3`,
  teal text `#86CDC2`, teal buttons `#2A8C82`, saffron CTA gradient `#F6C46A` to `#E39A35`.
- Fonts: Newsreader (400/500) for English, Tiro Devanagari Sanskrit for Sanskrit.
- Keep the sacred feel and the rising chariot wheel on the phone home. Not cream, not cartoonish.
- Phone home: everything on one screen, no scrolling. Bottom tab bar: Home, Ask, Learn, Explore.
- Verse wrapping: each half-verse on its own line; `text-wrap: balance` for Sanskrit and
  transliteration; a no-break space before the danda (`&#160;&#2404;` / `&#160;&#2405;`);
  English with `text-wrap: pretty`.
- Lamps on a theme = one per verse in that theme; lit = learned.

## Current phase: phone-first redesign
Pilot users found the UI unintuitive, so the whole phone flow was prototyped first on the Claude
Design canvas: https://claude.ai/artifact/4SsnoBQKhtFi5NqXEE69BY (dark boards in the main row,
light boards below). The generator for those boards is in `design/prototype/`
(`python3 gen.py boards && python3 dark.py boards boards`; dark.py also applies the DPractice mic
colour and the DVerse selected tab, which used to be hand edits). Exported boards: `design/prototype/boards/`.

Screens: Home, Ask (guided consult), Learn (themes with lamps), Verse (tabs Words / Explained /
Connected, an "In Theme" lamp card, one "Learn it by heart" button plus a labelled "Next 3.43" pill),
Learn it by heart (focused recite screen), Explore, Map (feeling journey, chains, find a path).
The Connected tab's verse map is a vertical thread of plain-worded stops (not a radial graph): it stays
legible at phone width. Tapping a word opens its "why" under that stop.

## Open items
- Waiting on Dhiraj's approval of the prototype, then rebuild the live site to match it.
- Map boards (PMap/DMap) use real data from `build/graph_data.py`; the gunas table from the live
  `/map/` page is left out on the phone. Map boards are on the Claude Design canvas as column 7.
- Desktop nav hover fix (`e714fa7`) is committed but not yet deployed.
- Dhiraj to spot-check the chant clips listed in SPOT-CHECK.txt. Theme 12's first shloka is held back
  until he confirms it.
