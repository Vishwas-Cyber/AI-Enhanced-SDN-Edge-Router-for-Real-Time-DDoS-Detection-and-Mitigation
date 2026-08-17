# SDN Sentinel — Final 10/10 Completion Plan

## Purpose

This plan defines the final evidence and hardening work required to present SDN Sentinel as a complete, research-grade and production-aware SDN security project.

The existing system already provides the core closed loop:

```text
OpenFlow telemetry → explainable detection → policy decision
→ time-bounded mitigation → switch-counter verification → audit evidence
```

The remaining work is validation and evidence. Do not claim measurements until the experiments have actually been run.

---

## 1. Final acceptance criteria

The release is complete when all of the following are true:

- The baseline topology starts reproducibly.
- The controller receives OpenFlow 1.3 statistics.
- Benign traffic does not trigger unintended mitigation.
- Authorized high-rate traffic creates a structured detection event.
- The controller installs the expected drop rule.
- The switch exposes packet and byte counters for that rule.
- Idle and hard timeouts expire as configured.
- The API rejects unauthenticated protected requests.
- The API permits only the required role for each protected operation.
- Invalid topology, policy, and model-contract inputs fail safely.
- Each experiment produces machine-readable results.
- The dashboard shows the same evidence as the API and captured switch state.
- The test suite and release validator pass.
- The final report contains only measured claims.

---

## 2. Reproducible experiment matrix

Run each scenario at least three times with the same declared configuration. Use a fresh topology and clean result directory for each trial.

| ID | Scenario | Expected result |
|---|---|---|
| B1 | Normal ICMP ping | Connectivity succeeds; no mitigation |
| B2 | Normal short burst | No false positive |
| A1 | High-rate ICMP | Detection and source mitigation |
| A2 | UDP high-rate traffic | Detection behavior recorded |
| A3 | TCP SYN traffic | Detection behavior recorded |
| A4 | Low-rate periodic traffic | Detection sensitivity recorded |
| A5 | Multiple authorized sources | Per-source decisions recorded |
| A6 | Mixed benign and attack traffic | Victim connectivity and policy behavior recorded |
| F1 | Model unavailable | Safe rule-based fallback or explicit refusal |
| F2 | Invalid feature contract | Event is rejected; no fabricated probability |
| F3 | Controller restart | Recovery and rule reconciliation recorded |
| F4 | Rule timeout | Rule expires and recovery is recorded |
| S1 | Unauthorized API request | HTTP 401 or 403 |
| S2 | Invalid topology input | Validation error; no unsafe execution |

Traffic must remain inside the authorized laboratory topology.

---

## 3. Result schema

Store one JSON document per trial in `results/raw/`:

```json
{
  "experiment_id": "A1",
  "trial": 1,
  "timestamp_utc": "REPLACE_WITH_MEASURED_VALUE",
  "git_commit": "REPLACE_WITH_COMMIT",
  "python_version": "REPLACE_WITH_VERSION",
  "controller_version": "REPLACE_WITH_VERSION",
  "switch_version": "REPLACE_WITH_VERSION",
  "topology": "REPLACE_WITH_TOPOLOGY",
  "traffic_profile": "REPLACE_WITH_PROFILE",
  "duration_sec": 0,
  "packets_sent": 0,
  "packets_observed": 0,
  "packets_dropped": 0,
  "bytes_observed": 0,
  "true_positive": false,
  "false_positive": false,
  "false_negative": false,
  "detection_latency_ms": null,
  "mitigation_latency_ms": null,
  "rule_installation_success": false,
  "rule_priority": null,
  "idle_timeout_sec": null,
  "hard_timeout_sec": null,
  "rule_packets": null,
  "rule_bytes": null,
  "controller_cpu_percent": null,
  "controller_memory_mb": null,
  "flow_table_entries": null,
  "notes": ""
}
```

Use `null` when a value was not measured. Never replace missing measurements with zero.

---

## 4. Metrics

Compute the confusion-matrix metrics only after each trial has been labelled:

\[
Precision = \frac{TP}{TP + FP}
\]

\[
Recall = \frac{TP}{TP + FN}
\]

\[
F1 = 2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}
\]

Also report:

- False-positive rate.
- False-negative rate.
- Median and 95th-percentile detection latency.
- Median and 95th-percentile mitigation latency.
- Rule-installation success rate.
- Rule-expiry success rate.
- Packets and bytes dropped per rule.
- Controller CPU and memory during baseline and attack traffic.
- Flow-table size before, during, and after mitigation.
- Recovery time after controller restart.

Report the number of trials and confidence intervals where practical. Do not report only the best run.

---

## 5. Comparative modes

Run the same traffic matrix in these modes:

| Mode | Detection | Mitigation | Purpose |
|---|---|---|---|
| M1 | Disabled | Disabled | Traffic baseline |
| M2 | Threshold | Disabled | Detection-only baseline |
| M3 | Threshold | Enabled | Rule-based operational response |
| M4 | Model-assisted | Disabled | Model decision analysis |
| M5 | Hybrid policy | Enabled | Complete system |

The model must use the exact feature order declared by `configs/model_manifest.json`. If the persisted model does not satisfy that contract, the system must not fabricate a probability. A rule-based or hybrid result must be labelled accordingly.

---

## 6. Failure and security tests

### API

- Missing bearer token.
- Invalid bearer token.
- Expired token.
- Analyst calling an admin-only operation.
- Malformed request body.
- Oversized request body.
- Invalid topology identifier.
- Repeated login attempts.

### Controller

- Empty flow statistics.
- Counter reset.
- Duplicate event.
- Duplicate mitigation request.
- Switch disconnect.
- Controller restart.
- Invalid MAC address.
- Allowlisted source.
- Timeout expiry.
- Rule reconciliation after restart.

### Configuration

- Missing policy file.
- Invalid threshold type.
- Negative timeout.
- Invalid OpenFlow priority.
- Empty allowlist.
- Model feature order mismatch.
- Missing model artifact.

Every failure test must record whether the result was expected, observed, and safe.

---

## 7. Final evidence package

Create these artifacts after real experiments:

```text
results/
├── raw/                         One JSON result per trial
├── aggregated_results.csv       Machine-readable summary
├── metrics_summary.md           Precision, recall, F1, latency, recovery
├── openflow_evidence/           Captured dump-flows output
├── screenshots/                 Dashboard and topology evidence
└── environment.json             Version and host metadata
```

The final report should include:

- Exact hardware and software versions.
- Topology diagram.
- Policy thresholds.
- Model feature contract.
- Traffic generation commands.
- Number of trials.
- Raw-result location.
- Aggregate metrics.
- Failure-test outcomes.
- Known limitations.
- Reproduction commands.

---

## 8. Release commands

Run these before committing:

```bash
source .venv/bin/activate
python -m pytest -q
python -m compileall api dashboard src scripts tests
python scripts/validate_release.py
./scripts/doctor.sh
git diff --check
```

Run the experiment only in the authorized lab:

```bash
ryu-manager src/controller/monitor.py
sudo python3 scripts/custom_topology.py
```

Verify OpenFlow evidence:

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

Check the repository:

```bash
git status
git log --oneline -3
```

Commit only measured results and documentation:

```bash
git add docs/SDN_SENTINEL_10_10_PLAN.md
git commit -m "Add final SDN Sentinel evaluation plan"
git push origin main
```

---

## 9. Final claim

After the acceptance criteria and experiments are completed, use this wording:

> SDN Sentinel is a reproducible, explainable, closed-loop SDN DDoS detection and mitigation platform. It analyzes OpenFlow telemetry, records policy reasoning, applies time-bounded OpenFlow enforcement, verifies switch counters, exposes authenticated operational APIs, and presents reproducible security evidence through a dashboard.

Use this wording only for measurements that are present in the final result files.

Do not claim carrier-scale protection, Internet-wide DDoS scrubbing, or production readiness without independent testing on production-grade infrastructure.
