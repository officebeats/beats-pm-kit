#!/bin/bash
# rc-keeper.sh — Keeps antigravity-remote.pages.dev/cmnvz4bp registered
# Polls cloudflared metrics every 30s and re-registers when URL changes

USER_ID="cmnvz4bp"
SECRET="v9ipe2soo9lnhtaz4nj779"
GATEWAY="https://antigravity-remote.pages.dev"
METRICS_URL="http://127.0.0.1:20241/metrics"
LAST_URL=""

echo "🎮 RC Keeper started — monitoring tunnel registration for $USER_ID"

while true; do
  # Get current tunnel URL from cloudflared metrics
  TUNNEL_URL=$(curl -s "$METRICS_URL" 2>/dev/null | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | head -1)

  if [ -z "$TUNNEL_URL" ]; then
    echo "$(date +%H:%M:%S) ⏳ cloudflared not running yet, waiting..."
    sleep 10
    continue
  fi

  if [ "$TUNNEL_URL" != "$LAST_URL" ]; then
    echo "$(date +%H:%M:%S) 🔄 New tunnel URL detected: $TUNNEL_URL"
    RESPONSE=$(curl -s -X POST "$GATEWAY/api/register" \
      -H "Content-Type: application/json" \
      -d "{\"userId\":\"$USER_ID\",\"tunnelUrl\":\"$TUNNEL_URL\",\"secret\":\"$SECRET\"}")
    
    if echo "$RESPONSE" | grep -q '"ok":true'; then
      echo "$(date +%H:%M:%S) ✅ Registered: $GATEWAY/$USER_ID → $TUNNEL_URL"
      LAST_URL="$TUNNEL_URL"
    else
      echo "$(date +%H:%M:%S) ❌ Registration failed: $RESPONSE"
    fi
  fi

  sleep 30
done
