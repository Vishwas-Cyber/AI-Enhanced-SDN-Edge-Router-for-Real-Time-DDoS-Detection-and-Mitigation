# SDN Sentinel v1.0.0

## Product

SDN Sentinel is an explainable closed-loop DDoS detection and OpenFlow
mitigation platform for authorized SDN laboratories. It combines live Ryu
flow telemetry, configurable policy decisions, timed switch enforcement,
structured evidence, topology visualization, traffic-flow analysis, and a
secured API foundation.

## Verified capabilities

- OpenFlow 1.3 switch control.
- High-rate traffic detection.
- Timed source-MAC drop rules.
- Packet/byte counter verification.
- Topology and traffic-flow dashboard.
- Local lab topology model builder.
- Protected FastAPI telemetry endpoints.
- Release validation and automated tests.

## Explicit boundary

This release is for authorized local research laboratories. It is not a
production Internet DDoS scrubbing service. Runtime ML probability is only
reported when the deployed model matches the declared feature contract.
