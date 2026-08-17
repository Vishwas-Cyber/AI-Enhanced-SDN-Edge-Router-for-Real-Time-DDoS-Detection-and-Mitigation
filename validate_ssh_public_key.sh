#!/usr/bin/env bash
set -Eeuo pipefail
KEY="$HOME/.ssh/id_ed25519.pub"

if [[ ! -f "$KEY" ]]; then
  echo "Missing $KEY" >&2
  exit 1
fi

# Normalize CRLF and remove surrounding whitespace without exposing the key.
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
tr -d '\r' < "$KEY" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' > "$TMP"

if ssh-keygen -lf "$TMP" >/dev/null 2>&1; then
  echo "Valid OpenSSH public key found: $KEY"
  echo "Fingerprint:"
  ssh-keygen -lf "$TMP"
else
  echo "The existing file is not a valid OpenSSH public key." >&2
  exit 1
fi

if command -v xclip >/dev/null 2>&1; then
  xclip -selection clipboard < "$TMP"
  echo "Normalized public key copied to clipboard. Paste it directly into GitHub."
fi
