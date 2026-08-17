#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."

fail=0
check() { if "$@" >/dev/null 2>&1; then echo "PASS $*"; else echo "FAIL $*"; fail=1; fi; }
check python --version
check python -m pytest -q
check python -m py_compile dashboard/app.py
check python -m py_compile src/controller/monitor.py
check test -s configs/topology.json
check test -s configs/experiment.yaml
check test -s docs/PROJECT_STATUS.md
if command -v ovs-ofctl >/dev/null 2>&1; then echo "PASS ovs-ofctl available"; else echo "INFO ovs-ofctl unavailable outside Mininet host"; fi
exit "$fail"
