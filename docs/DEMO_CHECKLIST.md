# Demo checklist

## Before starting

- Activate `.venv`.
- Confirm `configs/topology.json` is populated.
- Confirm the approved Mininet topology is available.
- Confirm the dashboard is configured for watchdog.

## Experiment

1. Start Ryu.
2. Start the approved Mininet topology.
3. Run `pingall`.
4. Record baseline packet loss.
5. Run the authorized controlled traffic experiment.
6. Observe the detection event.
7. Dump OpenFlow 1.3 flows.
8. Record rule priority, counters, and timeouts.
9. Stop traffic.
10. Record recovery and rule expiration.
11. Refresh the dashboard.

## Claims

Use “verified” only for values present in event logs or switch-flow output.
Do not claim production protection, arbitrary topology execution, or runtime ML
probabilities unless the corresponding artifact is present.
