# SDN Sentinel project status

## Scope

SDN Sentinel is a local, authorized SDN laboratory prototype. It monitors
OpenFlow flow statistics, detects high-rate traffic, records explainable
events, installs timed source-MAC drop rules, verifies switch counters, and
presents topology, flow, detection, and mitigation evidence in a dashboard.

## Verified final run

- Ryu controller connected to an OpenFlow 1.3 OVS switch.
- Baseline `pingall`: 0% packet loss.
- Baseline victim ping: 0% packet loss.
- Controlled flood: approximately 51,804.70 packets/s.
- Two detection events recorded.
- Two priority-500 OpenFlow drop rules confirmed.
- Idle timeout: 60 seconds.
- Hard timeout: 180 seconds.

## Evidence boundary

The final run verified threshold-based detection and OpenFlow mitigation.
The persisted model could not produce a probability because its required
feature schema differs from the live monitor schema. The dashboard and events
therefore label that run as `rule_based` or `hybrid`, not fully ML-driven.

## Release status

This repository is feature-complete for the authorized local-lab objective.
Future work is optional research work, not required for the demonstrated
prototype: runtime model retraining/alignment, multi-switch experiments,
additional attack classes, and production-grade authentication/deployment.
