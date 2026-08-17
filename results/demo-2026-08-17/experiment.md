# SDN DDoS Mitigation Experiment

## Environment

- Ubuntu WSL2
- Python 3.10.21
- Ryu 4.34
- Open vSwitch 3.7.1
- Mininet 2.3.0
- OpenFlow 1.3

## Topology

- Three hosts: h1, h2, h3
- One Open vSwitch bridge: s1
- Remote Ryu controller: 127.0.0.1:6633

## Normal traffic

- `pingall`
- Result: 0% packet loss

## Attack traffic

- Command: `h2 ping -f h1`
- Observed packet rate: approximately 2377 packets/second
- Observed byte rate: approximately 232958 bytes/second

## Detection

- Rule-based threshold triggered.
- DDoS event logged by the controller.
- Detection latency reported by controller: approximately 26 seconds.

## Mitigation

- Priority-500 source-MAC drop rules installed.
- Idle timeout: 60 seconds.
- Hard timeout: 180 seconds.
- OpenFlow dump confirmed actions=drop.

## ML status

The saved model loaded successfully, but runtime inference reported a feature-schema mismatch. The live rule-based mitigation path remained operational and successfully installed drop rules.
