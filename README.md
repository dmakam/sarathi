# Sarathi

A free reader for the Bhagavad Gita, word by word. All 701 verses with recitation,
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

## Deploy to the VPS

The app runs as one container (`sarathi-web`) on the shared `signal-desk-app` Caddy
network. No host web server is installed.

1. Add a DNS A record at Bluehost: `gita.dhirajmakam.com` to `50.6.226.244`.
2. On the server:
   ```
   git clone git@github.com:dmakam/sarathi.git /home/deploy/sarathi
   cd /home/deploy/sarathi && sudo ./deploy.sh
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
- `deploy.sh` - server deploy
