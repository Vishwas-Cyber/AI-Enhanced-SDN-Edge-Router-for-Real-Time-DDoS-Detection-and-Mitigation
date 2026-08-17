# SDN Sentinel

SDN Sentinel is a local research platform for designing an SDN topology,
visualizing switches, routers, hosts, and controller links, monitoring DDoS
events, and presenting verified OpenFlow mitigation rules.

## Safety boundary

The platform is for authorized Mininet laboratories. It does not expose
arbitrary shell execution or claim to protect production networks.

## Product flow

1. Design a topology in the dashboard.
2. Validate nodes and links.
3. Run the authorized Mininet experiment.
4. Monitor flow statistics through Ryu.
5. Detect suspicious traffic.
6. Install timed OpenFlow mitigation.
7. Review events, rules, and performance evidence.
