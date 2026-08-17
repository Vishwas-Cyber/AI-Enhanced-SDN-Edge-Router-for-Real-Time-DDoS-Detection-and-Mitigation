# Final experiment results

## Observed run

- Baseline `pingall`: 0% packet loss, 6/6 reachable pairs.
- Baseline `h2 ping -c 10 h1`: 0% packet loss.
- Controlled flood: 157,984 packets transmitted in approximately 3.025 seconds.
- Observed flood rate: approximately 51,804.70 packets/s and 5,076,860.14 bits/s.
- Detection events: 2.
- Confirmed priority-500 drop rules: 2.
- Rule idle timeout: 60 seconds.
- Rule hard timeout: 180 seconds.
- Model probability: unavailable because the persisted model schema requires additional fields not present in the live flow record.
- DDoS decision mode: threshold-only for this run.

## Interpretation

The OpenFlow mitigation loop is verified. Runtime ML inference is not claimed
for this run. The persisted model expects fields such as protocol/port,
time-derived fields, timeout fields, and per-nanosecond rates. The runtime
collector currently supplies a smaller flow-statistics record. These schemas
must be aligned and the model retrained or replaced before claiming runtime ML.
