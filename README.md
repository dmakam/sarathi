# Sarathi

A free reader for the Bhagavad Gita, word by word, with a recitation coach. All 701 verses with recitation,
every Sanskrit word linked to every verse that uses it, seven translations, sixteen
classical commentaries grouped by tradition, "what are you facing" entry points,
reading plans and shareable verse cards.

Data: the public-domain [gita/gita](https://github.com/gita/gita) dataset (Unlicense),
pinned to commit `c6fce39` in the Dockerfile.

## Build locally

```
git clone https://github.com/gita/gita.git src-data
python3 -I build/build.py          # writes ./site (about 190 MB with audio)
python3 -I build/build.py --no-audio   # faster, skips copying the MP3s
cd site && python3 -m http.server 8000
```

## Try it on your own computer first

```
./run-local.sh
```

Then open http://localhost:8080/practice/2/47/ in Chrome. It sets up its own Python
environment in `.venv` (no admin rights or Homebrew), builds the site, and runs the site
and the coach together. The first run downloads about 2 GB and takes a few minutes; later
runs start in seconds. Press Ctrl+C to stop.

## Deploy to the VPS

Two containers on the shared `signal-desk-app` Caddy network, no host web server:

- `sarathi-web` serves the static site.
- `sarathi-coach` scores recitations at `/api/score`. It force-aligns the take against
  the known verse with Meta's MMS aligner (CPU PyTorch), using an 8-bit copy of the model
  (`server/model-int8.pt`, made by `server/quantize.py`, not in git). That copy gave the same
  word marks as the full model in testing and needs about 0.6 GB idle and 1.4 GB while scoring.
  Audio is scored in memory and dropped; nothing is written to disk or logged.

On a 2 GB server, run `./add-swap.sh` once before deploying so the coach fits.

1. Add a DNS A record at Bluehost: `sarathi.dhirajmakam.com` to `50.6.226.244`.
2. On the server:
   ```
   git clone git@github.com:dmakam/sarathi.git /home/deploy/sarathi
   cd /home/deploy/sarathi && ./deploy.sh
   ```
3. Re-run `./deploy.sh` after any `git pull` to rebuild and replace the container.

`deploy.sh` checks the running containers first, appends the site block to the shared
Caddyfile with `>>` (never replaces the file), confirms the proxy container sees it,
then runs `caddy validate` and `caddy reload`.

## Layout

- `build/build.py` - the generator (dataset to static HTML and JSON, ASCII-only output)
- `build/content.py` - curated layers: traditions, concepts, situations
- `assets/` - CSS, JS, icon
- `Dockerfile`, `Caddyfile.app` - image and its internal server
- `server/` - the coach: `align.py` (forced alignment and per-word scores), `app.py` (HTTP API),
  `practice-words.json` (written by the site build), `Dockerfile`
- `deploy.sh` - server deploy
