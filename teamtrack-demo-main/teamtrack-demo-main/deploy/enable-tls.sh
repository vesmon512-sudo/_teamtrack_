#!/usr/bin/env bash
# Usage:  ./enable-tls.sh <your-domain>
# Requirement: your-domain must resolve (A/AAAA) to this server's public IP.
set -e
DOMAIN="${1:?Usage: ./enable-tls.sh <domain>}"
CADDYFILE=/etc/caddy/Caddyfile
IP=42.114.42.231

cp "$CADDYFILE" "${CADDYFILE}.bak.$(date +%s)"

if ! grep -qE "^[[:space:]]*${DOMAIN}[[:space:]]*{" "$CADDYFILE"; then
  cat >> "$CADDYFILE" <<EOF

# ===== TeamTrack HTTPS (automatic Let's Encrypt) - added $(date '+%Y-%m-%d %H:%M') =====
$DOMAIN {
	reverse_proxy 127.0.0.1:5000
	encode zstd gzip
}
EOF
  echo "Added HTTPS site for: $DOMAIN"
else
  echo "Site for $DOMAIN already present in Caddyfile"
fi

caddy validate --config "$CADDYFILE" >/dev/null && echo "Caddyfile is valid"
systemctl reload caddy
echo "Waiting for certificate (Caddy obtains it automatically from Let's Encrypt)..."

ok=0
for i in $(seq 1 12); do
  sleep 5
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://$DOMAIN/" || true)
  echo "  attempt $i: https code=$code"
  if [ "$code" = "200" ] || [ "$code" = "302" ]; then ok=1; break; fi
done

echo "--- certificate check ---"
curl -skv "https://$DOMAIN/" -o /dev/null 2>&1 | grep -E "issuer|expire|SSL certificate" || true
if [ "$ok" = "1" ]; then
  echo "SUCCESS: https://$DOMAIN/ is live and the certificate is auto-managed by Caddy."
else
  echo "Not up yet: make sure $DOMAIN points (A/AAAA record) to $IP, then rerun."
  echo "Inspect logs: journalctl -u caddy -n 50"
fi
