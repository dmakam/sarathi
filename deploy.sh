#!/usr/bin/env bash
# Deploy Sarathi to the VPS behind the shared signal-desk-app Caddy:
#   sarathi-web    the static site (pages, data, audio)
#   sarathi-coach  the recitation scorer, reached at /api/
# Run on the server from the repo folder:  ./deploy.sh
# Safe to re-run: it rebuilds both images, replaces both containers, and only
# appends the Caddy site block if it is not already there.
set -euo pipefail

DOMAIN="${DOMAIN:-sarathi.dhirajmakam.com}"
WEB="sarathi-web";   WEB_IMAGE="sarathi:latest"
COACH="sarathi-coach"; COACH_IMAGE="sarathi-coach:latest"
PROXY="signal-desk-app-caddy-1"
CADDYFILE="/home/deploy/signal-desk-app/Caddyfile"

echo "== 1. Checking what the server already runs"
docker ps --format '{{.Names}}\t{{.Ports}}'
if ! docker ps --format '{{.Names}}' | grep -qx "$PROXY"; then
  echo "Shared proxy $PROXY is not running. Stopping so nothing else grabs ports 80/443." >&2
  exit 1
fi
[ -f "$CADDYFILE" ] || { echo "Caddyfile not found at $CADDYFILE" >&2; exit 1; }
NET="$(docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' "$PROXY" | head -n1)"
echo "Proxy network: $NET"
AVAIL_MB="$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)"
DISK_GB="$(df -BG --output=avail /var/lib/docker 2>/dev/null | tail -1 | tr -dc 0-9)"
echo "Memory available: ${AVAIL_MB} MB, disk free for Docker: ${DISK_GB:-?} GB"
[ "${AVAIL_MB:-0}" -ge 2500 ] || echo "WARNING: the coach needs about 2.5 GB of free memory while scoring. It may be killed on this server."
[ "${DISK_GB:-99}" -ge 6 ] || echo "WARNING: the coach image is estimated at 3 to 4 GB. Free some disk space first."

echo "== 2. Checking DNS for $DOMAIN"
IP="$(getent hosts "$DOMAIN" | awk '{print $1}' | head -n1 || true)"
echo "$DOMAIN resolves to: ${IP:-nothing yet}"
[ -n "$IP" ] || echo "WARNING: add an A record for $DOMAIN pointing to this server, or Caddy cannot issue a certificate."

echo "== 3. Building images (site: pinned dataset, about 2,200 pages; coach: CPU PyTorch and the 1.2 GB aligner)"
docker build --build-arg "SARATHI_BASE_URL=https://$DOMAIN" -t "$WEB_IMAGE" .
docker build -t "$COACH_IMAGE" server

echo "== 4. Replacing containers"
docker rm -f "$WEB" "$COACH" >/dev/null 2>&1 || true
docker run -d --name "$WEB" --restart unless-stopped --network "$NET" "$WEB_IMAGE"
docker run -d --name "$COACH" --restart unless-stopped --network "$NET" --memory 3g \
  -e "SARATHI_ORIGINS=https://$DOMAIN" "$COACH_IMAGE"
echo "Waiting for the coach to load its model..."
for i in $(seq 1 60); do
  docker exec "$PROXY" wget -q -O /dev/null "http://$COACH:8000/api/health" 2>/dev/null && break
  sleep 2
done
docker exec "$PROXY" wget -q -O /dev/null "http://$WEB/2/47/" && echo "Site answers on the proxy network."
docker exec "$PROXY" wget -q -O /dev/null "http://$COACH:8000/api/health" && echo "Coach answers on the proxy network." \
  || echo "WARNING: the coach is not answering yet. Check: docker logs $COACH"

echo "== 5. Caddy site block"
if grep -q "^$DOMAIN" "$CADDYFILE"; then
  if grep -q "$COACH:8000" "$CADDYFILE"; then
    echo "Site block for $DOMAIN already present; leaving the Caddyfile alone."
  else
    echo "WARNING: an older $DOMAIN block without the coach route exists. Edit it in place (not with sed -i) to match README.md, then re-run."
  fi
else
  # Append in place (>>) so the bind-mounted inode stays the same.
  cat >> "$CADDYFILE" <<CADDY

$DOMAIN {
	encode zstd gzip
	handle /api/* {
		request_body {
			max_size 5MB
		}
		reverse_proxy $COACH:8000
	}
	handle {
		reverse_proxy $WEB:80
	}
}
CADDY
  echo "Appended site block."
fi
if ! docker exec "$PROXY" grep -q "$DOMAIN" /etc/caddy/Caddyfile; then
  echo "The proxy container does not see the new block (file was replaced, not edited)."
  echo "Restarting $PROXY once to pick up the file. All sites blip for a second."
  docker restart "$PROXY"
  sleep 3
fi
docker exec "$PROXY" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker exec "$PROXY" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile

echo "== 6. Done. Check: https://$DOMAIN/ and https://$DOMAIN/practice/2/47/"
