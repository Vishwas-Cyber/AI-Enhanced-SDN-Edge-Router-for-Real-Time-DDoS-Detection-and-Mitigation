# Architecture

```text
Mininet hosts h1/h2/h3
        |
   OVS s1 OpenFlow 1.3
        |
Ryu monitor/controller
        |
flow statistics + event JSONL
        |
Streamlit security dashboard
```

## Closed loop

1. The switch reports flow statistics.
2. The monitor calculates packet and byte rates.
3. A threshold and optional model decision classify a flow.
4. The controller records an event with reason and metrics.
5. The controller installs a timed source-MAC drop rule.
6. Switch counters verify the action.
7. The dashboard presents topology, traffic, detection, and evidence.
