# Release readiness

## Completed scope

SDN Sentinel provides an authorized local SDN laboratory with Ryu, OpenFlow
1.3, OVS, Mininet, structured telemetry, explainable threshold detection,
timed source-MAC drop rules, topology visualization, traffic-flow analysis,
Streamlit operations UI, FastAPI API, authentication foundation, tests,
packaging, policy configuration, model contract, and release validation.

## Security boundary

The dashboard and API do not execute arbitrary shell commands. The system is
not exposed to the public Internet and is not a production DDoS scrubbing
service.

## ML boundary

The model manifest fixes feature names, order, threshold, framework version,
and artifact name. Runtime ML must remain labelled unavailable until a model
trained on exactly this contract produces a real probability. Threshold-based
mitigation remains valid and verified independently.

## Release acceptance

- Python compilation passes.
- Test suite passes.
- Release validator passes.
- Local API authentication passes.
- Dashboard launches.
- OpenFlow mitigation evidence is captured.
- Baseline and attack experiments are documented.
