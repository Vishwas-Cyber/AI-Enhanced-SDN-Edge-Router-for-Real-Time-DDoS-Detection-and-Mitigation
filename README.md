AI-Enhanced-SDN-Edge-Router-for-Real-Time-DDoS-Detection-and-Mitigation

Explainable Closed-Loop DDoS Detection and OpenFlow Mitigation
SDN Sentinel is an explainable Software-Defined Networking security platform for authorized network laboratories. It monitors OpenFlow telemetry, detects suspicious high-rate traffic, records the reason for each decision, installs time-bounded OpenFlow mitigation rules, verifies switch counters, and presents the complete response lifecycle through a security-operations dashboard and authenticated API.

Scope: SDN Sentinel is a validated local-lab and commercial-MVP foundation. It is not a production Internet-scale DDoS scrubbing service. Use it only on networks and traffic you are authorized to test.

Project status
Area	Status
SDN/OpenFlow implementation	Complete
Explainable detection	Complete
Time-bounded mitigation	Complete
Dashboard	Complete
FastAPI service	Complete
Authentication foundation	Complete
Automated tests	16 passed
Release validation	Passed
Doctor checks	Passed
GitHub publication	Complete
Reproducible evaluation plan	Included
Why SDN Sentinel matters
Many DDoS demonstrations stop after producing a classification label. SDN Sentinel closes the operational loop:

text
Live traffic
    ↓
OpenFlow flow telemetry
    ↓
Explainable detection and policy decision
    ↓
Time-bounded OpenFlow drop rule
    ↓
Switch counter verification
    ↓
Dashboard, API, and audit evidence
The project connects security analytics to an actual programmable network response and makes every response inspectable.

Demonstrated results
The authorized Mininet/Open vSwitch experiment demonstrated:

0% packet loss during baseline connectivity checks.

Approximately 51,804 packets per second during the controlled high-rate experiment.

Approximately 5,076,860 bits per second during the attack interval.

Two structured DDoS detection events.

Two confirmed priority-500 OpenFlow source-MAC drop rules.

Packet and byte counters on installed rules.

60-second idle timeout and 180-second hard timeout.

Authenticated retrieval of events and topology through the API.

Automated validation with 16 passing tests.

The documented run verified threshold-based detection and OpenFlow mitigation. Runtime ML probability is reported only when the deployed model satisfies the declared feature contract.

Key capabilities
Detection and mitigation
Ryu controller integration.

OpenFlow 1.3 switch control.

OVS and Mininet laboratory topology.

Periodic flow-statistics collection.

Packets-per-second and bits-per-second analysis.

Explainable threshold and policy decisions.

Optional model-assisted classification under a validated feature contract.

Time-bounded source-MAC mitigation.

OpenFlow counter and timeout verification.

Structured detection and mitigation events.

Security operations dashboard
Overview security metrics.

Interactive topology graph.

Consistent controller, switch, router, host, and attack-state symbols.

Directional control-plane and data-plane flow view.

Local Lab Builder for topology modeling.

Detection timeline.

OpenFlow evidence view.

Authorized experiment runbook.

Security-operations presentation layer.

API and product foundation
FastAPI backend.

Health endpoint.

Bearer-token authentication foundation.

Analyst and admin role separation.

Protected topology endpoint.

Protected event endpoint.

Topology validation.

Docker Compose foundation.

Release validator and diagnostic script.

Engineering quality
requirements.txt dependency manifest.

pyproject.toml project configuration.

Makefile commands.

Pytest test suite.

Python compilation checks.

GitHub Actions CI workflow.

Model feature manifest.

Policy configuration.

Architecture and threat-model documentation.

Reproducible evaluation plan.

Architecture
text
┌────────────────────────────────────────────────────────────┐
│ Streamlit Security Operations Dashboard                    │
│ Overview · Topology · Flow · Detections · OpenFlow Evidence│
└───────────────────────┬────────────────────────────────────┘
                        │ authenticated API / local files
┌───────────────────────▼────────────────────────────────────┐
│ FastAPI Service                                             │
│ Health · Auth · RBAC foundation · Events · Topology         │
└───────────────────────┬────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────┐
│ Ryu SDN Monitor and Policy Layer                            │
│ Flow polling · rate features · detection · mitigation       │
└───────────────────────┬────────────────────────────────────┘
                        │ OpenFlow 1.3
┌───────────────────────▼────────────────────────────────────┐
│ Open vSwitch s1                                            │
│ Timed source-MAC drop rules and flow counters               │
└───────────────────────┬────────────────────────────────────┘
                        │
             ┌──────────┼──────────┐
             │          │          │
           h1 victim   h2 source  h3 source
Repository structure
text
.
├── api/                         FastAPI service
├── configs/                     Topology, policy, experiment, model manifests
├── dashboard/                   Streamlit security dashboard
├── deployment/                  Docker and health-check assets
├── docs/                        Architecture, runbooks, reports, evaluation plan
├── results/                     Reviewed experiment and benchmark artifacts
├── scripts/                     Doctor, topology, and release validation utilities
├── src/
│   ├── controller/              Ryu monitor and OpenFlow mitigation
│   ├── model_contract.py        Runtime feature-contract validation
│   └── runtime_contract.py      Runtime feature helpers
├── tests/                       Automated tests
├── .github/workflows/           CI checks
├── Makefile                     Common development commands
├── pyproject.toml               Python project and pytest configuration
└── requirements.txt              Dependencies
Requirements
Recommended environment:

Ubuntu Linux.

Python 3.10.

Ryu 4.34.

Open vSwitch.

Mininet.

OpenFlow 1.3 support.

A local browser environment for the dashboard.

The project uses the dependency versions declared in requirements.txt.

Installation
bash
git clone git@github.com:Vishwas-Cyber/AI-Enhanced-SDN-Edge-Router-for-Real-Time-DDoS-Detection-and-Mitigation.git
cd AI-Enhanced-SDN-Edge-Router-for-Real-Time-DDoS-Detection-and-Mitigation

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Run the initial release checks:

bash
python -m pytest -q
python scripts/validate_release.py
./scripts/doctor.sh
Expected result:

text
16 passed
RELEASE READY: artifacts, topology, policy, and model contract validated
Run the dashboard
Keep the dashboard local to the lab machine:

bash
streamlit run dashboard/app.py \
  --server.address 127.0.0.1 \
  --server.port 8501
Open http://127.0.0.1:8501.

Dashboard sections:

Overview: operational status, metrics, activity chart, and topology snapshot.

Local Lab Builder: add and validate topology nodes and links in the model.

Topology & Flow: inspect symbols, paths, planes, states, and packets per second.

Detections: review structured events and latency charts.

OpenFlow Evidence: inspect captured mitigation rules and counters.

Runbook: follow the authorized demonstration workflow.

The dashboard does not execute arbitrary shell commands.

Run the API
Start the local API:

bash
uvicorn api.main:app \
  --host 127.0.0.1 \
  --port 8000
Health check:

bash
curl http://127.0.0.1:8000/health
Interactive API documentation:

http://127.0.0.1:8000/docs

Local authentication test
For local testing only, configure credentials through environment variables:

bash
export SDN_ADMIN_PASSWORD='replace-with-a-long-random-password'
export SDN_ANALYST_PASSWORD='replace-with-a-different-long-random-password'
Log in:

bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"YOUR_LOCAL_PASSWORD"}'
Use the returned token without committing it:

bash
export SDN_ACCESS_TOKEN='TOKEN_RETURNED_BY_API'

curl http://127.0.0.1:8000/events \
  -H "Authorization: Bearer $SDN_ACCESS_TOKEN"

curl http://127.0.0.1:8000/topology \
  -H "Authorization: Bearer $SDN_ACCESS_TOKEN"
Never commit tokens, passwords, private keys, or .streamlit/secrets.toml.

Run the authorized SDN experiment
Use separate terminals.

Terminal 1 — Ryu controller
bash
cd ~/ai-router-project
source .venv/bin/activate
ryu-manager src/controller/monitor.py
Terminal 2 — Mininet topology
bash
cd ~/ai-router-project
sudo python3 scripts/custom_topology.py
Inside Mininet
Verify baseline connectivity:

text
pingall
h2 ping -c 10 h1
Run the controlled authorized traffic experiment:

text
h2 ping -f h1
Stop it with Ctrl+C, then exit Mininet:

text
exit
Verify switch evidence:

bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
Look for rules containing:

text
priority=500
idle_timeout=60
hard_timeout=180
actions=drop
Only run these experiments on systems and traffic paths you are authorized to test.

Model and detection boundary
The model contract is declared in:

text
configs/model_manifest.json
The declared runtime feature order is:

text
pps
bps
packets
bytes
duration_sec
The system must not fabricate a model probability when the persisted artifact does not match the live schema. If the model cannot be used, the event is labelled rule-based or hybrid and the OpenFlow mitigation path remains independently verifiable.

Control the scikit-learn version used to train and load persisted models. Retrain or validate the model whenever the feature schema or framework version changes.

Policy configuration
The default authorized-lab policy is stored in:

text
configs/policy.yaml
It defines:

Packets-per-second threshold.

Bits-per-second threshold.

Model probability threshold.

OpenFlow priority.

Idle timeout.

Hard timeout.

Allowlists.

Manual approval mode.

Lab scope.

Testing and release validation
Run the complete check suite:

bash
source .venv/bin/activate
python -m pytest -q
python -m compileall api dashboard src scripts tests
python scripts/validate_release.py
./scripts/doctor.sh
git diff --check
Useful Make targets:

bash
make install
make test
make compile
make check
make dashboard
The GitHub Actions workflow runs compilation and tests on pushes and pull requests.

Reproducible evaluation
The complete evaluation plan is in:

text
docs/SDN_SENTINEL_10_10_PLAN.md
The plan covers:

Normal ICMP traffic.

High-rate ICMP traffic.

UDP traffic.

TCP SYN traffic.

Low-rate periodic traffic.

Multiple authorized sources.

Mixed benign and attack traffic.

Model-unavailable behavior.

Controller restart and recovery.

Rule timeout and reconciliation.

API authentication and authorization failures.

Invalid topology, policy, and model-contract inputs.

Recommended metrics:

Precision.

Recall.

F1 score.

False-positive rate.

False-negative rate.

Detection latency.

Mitigation latency.

Recovery time.

Controller resource usage.

Switch flow-table usage.

Event-ingestion lag.

Only publish measured results. Do not invent probabilities, latency, accuracy, or recovery values.

Security and production boundary
This release is intended for authorized local research environments.

Before external or production deployment, add and validate:

TLS for API, dashboard, and device channels.

Persistent identity provider, strong password hashing, MFA, and SSO.

PostgreSQL or TimescaleDB for durable events and metrics.

Persistent audit records and retention controls.

Rate limiting and reverse-proxy protection.

Controller high availability and rule reconciliation.

Device enrollment and certificate rotation.

Multi-tenant isolation.

Production monitoring, backup, and incident response.

Device-specific integration and load testing.

Do not expose the local API or dashboard directly to the public Internet.

Commercial positioning
SDN Sentinel is best positioned as an explainable SDN security platform for:

Universities and network-security laboratories.

Private clouds and data centers.

SDN/OpenFlow research teams.

Programmable-network testbeds.

Managed network-security providers.

The product differentiator is:

text
Explainable detection
+ topology awareness
+ programmable enforcement
+ switch-counter verification
+ reproducible evidence
The current release is a validated local-lab and commercial-MVP foundation. It is not a carrier-scale or Internet-wide DDoS scrubbing service.

Documentation
Architecture

Project status

Threat model

Demo script

Final experiment results

Known limitations

Commercial MVP

Release readiness

Submission checklist

Research benchmark plan

Research claims

Commercial gap analysis

Final 10/10 evaluation plan

License
Add the license that matches your intended distribution before public commercial use.

Author
Vishwas Manjunath

GitHub: Vishwas-Cyber
