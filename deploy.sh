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
# The recitation coach uses the 8-bit model (server/model-int8.pt, copied in separately)
# and needs about 1.0 to 1.4 GB while scoring. With swap that fits a 2 GB server.
# Without it the site still works: the practice page hides recording and offers the
# "I recited it from memory" check instead.
SWAP_MB="$(awk '/SwapFree/ {print int($2/1024)}' /proc/meminfo)"
WITH_COACH="${WITH_COACH:-auto}"
if [ "$WITH_COACH" = auto ]; then
  if [ ! -f server/model-int8.pt ]; then
    WITH_COACH=0; echo "Skipping the recitation coach: server/model-int8.pt is not here yet."
  elif [ $(( ${AVAIL_MB:-0} + ${SWAP_MB:-0} )) -lt 1800 ]; then
    WITH_COACH=0; echo "Skipping the recitation coach: ${AVAIL_MB} MB free and ${SWAP_MB} MB swap; it needs about 1,800 together. Run ./add-swap.sh first."
  else
    WITH_COACH=1
  fi
fi
[ "${DISK_GB:-99}" -ge 4 ] || echo "WARNING: the coach image is about 2 GB. Free some disk space first."

echo "== 2. Checking DNS for $DOMAIN"
IP="$(getent hosts "$DOMAIN" | awk '{print $1}' | head -n1 || true)"
echo "$DOMAIN resolves to: ${IP:-nothing yet}"
[ -n "$IP" ] || echo "WARNING: add an A record for $DOMAIN pointing to this server, or Caddy cannot issue a certificate."

echo "== 3. Building images (site: pinned dataset, about 2,200 pages; coach: CPU PyTorch and the 1.2 GB aligner)"
docker build --build-arg "SARATHI_BASE_URL=https://$DOMAIN" -t "$WEB_IMAGE" .
if [ "$WITH_COACH" = 1 ]; then docker build -t "$COACH_IMAGE" server; fi

echo "== 4. Replacing containers"
docker rm -f "$WEB" "$COACH" >/dev/null 2>&1 || true
docker run -d --name "$WEB" --restart unless-stopped --network "$NET" "$WEB_IMAGE"
if [ "$WITH_COACH" = 1 ]; then
  docker run -d --name "$COACH" --restart unless-stopped --network "$NET" --memory 1300m --memory-swap 2600m \
    -e "SARATHI_ORIGINS=https://$DOMAIN" "$COACH_IMAGE"
  echo "Waiting for the coach to load its model..."
  for i in $(seq 1 60); do
    docker exec "$PROXY" wget -q -O /dev/null "http://$COACH:8000/api/health" 2>/dev/null && break
    sleep 2
  done
fi
docker exec "$PROXY" wget -q -O /dev/null "http://$WEB/2/47/" && echo "Site answers on the proxy network."
if [ "$WITH_COACH" = 1 ]; then
  docker exec "$PROXY" wget -q -O /dev/null "http://$COACH:8000/api/health" && echo "Coach answers on the proxy network." \
    || echo "WARNING: the coach is not answering yet. Check: docker logs $COACH"
fi

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
