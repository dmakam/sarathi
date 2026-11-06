#!/usr/bin/env bash
# Add a 2 GB swap file so the recitation coach fits on a 2 GB server.
# Safe to re-run: does nothing if /swapfile is already in use.
# Run once on the server:  ./add-swap.sh
set -euo pipefail
if swapon --show=NAME --noheadings | grep -qx /swapfile; then
  echo "Swap is already on:"; swapon --show; exit 0
fi
FREE_GB="$(df -BG --output=avail / | tail -1 | tr -dc 0-9)"
[ "${FREE_GB:-0}" -ge 6 ] || { echo "Only ${FREE_GB} GB of disk free; need at least 6 GB to add a 2 GB swap file." >&2; exit 1; }
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile >/dev/null
swapon /swapfile
grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
echo "Swap is on (and will come back after a reboot):"
free -h
