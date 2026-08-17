# SDN Sentinel benchmark plan

A 10/10 research claim requires measured comparisons, not dashboard appearance.
Run every scenario at least five times and report mean, median, standard
deviation, minimum, and maximum.

## Scenarios

| ID | Traffic | Expected |
|---|---|---|
| N1 | Normal ping | Allow |
| N2 | Normal burst | Allow |
| A1 | High-rate ICMP | Detect and block |
| A2 | Multiple authorized sources | Detect and block each source |
| A3 | UDP test traffic | Detect according to policy |
| A4 | TCP test traffic | Detect according to policy |
| F1 | Controller unavailable | Degraded state, no false healthy claim |
| F2 | Model unavailable | Explicit rule-based fallback |

## Metrics

- Precision.
- Recall.
- F1 score.
- False-positive rate.
- False-negative rate.
- Detection latency.
- Rule-installation latency.
- Mitigation effectiveness.
- Recovery time.
- Controller CPU and memory.
- Switch flow-table usage.
- Event-ingestion lag.

## Required comparisons

1. Threshold-only.
2. ML-only.
3. Hybrid threshold plus ML.
4. No mitigation baseline.

## Evidence policy

Only values produced by the experiment may be reported. Do not invent
probabilities, latency, accuracy, or recovery values.
