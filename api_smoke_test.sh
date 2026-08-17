#!/usr/bin/env bash
set -Eeuo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"
TOKEN="${SDN_ACCESS_TOKEN:-}"

if [[ -z "$TOKEN" ]]; then
  echo "Set the token without committing it:" >&2
  echo "export SDN_ACCESS_TOKEN='paste-your-token-here'" >&2
  exit 1
fi

curl --fail-with-body -sS "$API_URL/health"
printf '\n\n--- protected events ---\n'
curl --fail-with-body -sS "$API_URL/events" \
  -H "Authorization: Bearer $TOKEN"
printf '\n\n--- protected topology ---\n'
curl --fail-with-body -sS "$API_URL/topology" \
  -H "Authorization: Bearer $TOKEN"
printf '\n'
