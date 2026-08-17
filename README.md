# SDN Sentinel

Explainable closed-loop DDoS detection and OpenFlow mitigation for authorized
SDN laboratories.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
streamlit run dashboard/app.py
```

## Lab run

Terminal 1:

```bash
ryu-manager src/controller/monitor.py
```

Terminal 2:

```bash
sudo python3 scripts/custom_topology.py
```

Inside Mininet, use only the authorized experiment commands documented in
`docs/DEMO_SCRIPT.md`.

## Scope

This is a local research prototype. It is not a production DDoS protection
service. The dashboard does not execute arbitrary shell commands.

## Documentation

- `docs/ARCHITECTURE.md`
- `docs/PROJECT_STATUS.md`
- `docs/THREAT_MODEL.md`
- `docs/DEMO_SCRIPT.md`
- `docs/FINAL_EXPERIMENT_RESULTS.md`
- `docs/KNOWN_LIMITATIONS.md`
