# SDN Sentinel validation report

## Scope

This project is a local authorized SDN laboratory prototype using Ryu,
OpenFlow 1.3, OVS, Mininet, structured event telemetry, and timed mitigation.
It is not a production DDoS protection service.

## Closed-loop evidence

- Normal connectivity was tested before the controlled experiment.
- A controlled high-rate source generated attack traffic.
- The controller recorded two detection events.
- The switch exposed two priority-500 drop rules.
- The rules included packet and byte counters plus idle and hard timeouts.
- The dashboard visualized topology, traffic flow, detection events, and rules.

## Runtime feature contract

The runtime contract is defined in `configs/runtime_features.json` and is
consumed by `src/runtime_contract.py`. Feature order is fixed:

1. pps
2. bps
3. flow_count
4. byte_count
5. duration

The contract prevents training/runtime column drift and provides an explicit
probability threshold of 0.8 for the documented model decision.

## Remaining interpretation boundary

This report distinguishes verified OpenFlow mitigation from model inference.
If a runtime event does not contain `model_probability`, the event must be
labelled rule-based or hybrid rather than fully ML-driven.
