# Experiment matrix

| ID | Scenario | Expected result | Artifact |
|---|---|---|---|
| N1 | Baseline ping | Connectivity, no mitigation | ping output |
| A1 | High-rate ICMP source | Detection and source drop | events + flows |
| A2 | Multiple authorized sources | Multiple timed drops | events + flows |
| R1 | Stop attack | Traffic recovers | recovery log |
| F1 | Controller unavailable | Clear degraded state | controller log |
| M1 | Model mismatch | Rule-based label, no fake probability | event JSON |
| T1 | Invalid topology link | API validation error | API response |
| I1 | Unauthorized API request | 401/403 | API response |
