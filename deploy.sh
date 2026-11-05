#!/usr/bin/env bash
# Deploy Sarathi to the VPS as a container behind the shared signal-desk-app Caddy.
# Run on the server from the repo folder:  sudo ./deploy.sh
# Safe to re-run: it rebuilds the image, replaces the container, and only
# appends the Caddy site block if it is not already there.
set -euo pipefail

DOMAIN="${DOMAIN:-gita.dhirajmakam.com}"
NAME="sarathi-web"
IMAGE="sarathi:latest"
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

echo "== 2. Checking DNS for $DOMAIN"
IP="$(getent hosts "$DOMAIN" | awk '{print $1}' | head -n1 || true)"
echo "$DOMAIN resolves to: ${IP:-nothing yet}"
[ -n "$IP" ] || echo "WARNING: add an A record for $DOMAIN pointing to this server, or Caddy cannot issue a certificate."

echo "== 3. Building image (downloads the pinned dataset, builds 1,500 pages)"
docker build --build-arg "SARATHI_BASE_URL=https://$DOMAIN" -t "$IMAGE" .

echo "== 4. Replacing container"
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" --restart unless-stopped --network "$NET" "$IMAGE"
sleep 2
docker exec "$PROXY" wget -q -O /dev/null "http://$NAME/2/47/" && echo "Container answers on the proxy network."

echo "== 5. Caddy site block"
if grep -q "^$DOMAIN" "$CADDYFILE"; then
  echo "Site block for $DOMAIN already present; leaving the Caddyfile alone."
else
  # Append in place (>>) so the bind-mounted inode stays the same.
  printf '\n%s {\n\tencode zstd gzip\n\treverse_proxy %s:80\n}\n' "$DOMAIN" "$NAME" >> "$CADDYFILE"
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

echo "== 6. Done. Check: https://$DOMAIN/"
