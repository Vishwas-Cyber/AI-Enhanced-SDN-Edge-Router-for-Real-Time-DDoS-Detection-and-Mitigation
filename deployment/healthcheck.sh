#!/usr/bin/env bash
set -Eeuo pipefail
curl --fail --silent http://127.0.0.1:8000/health >/dev/null
echo 'API healthy'
