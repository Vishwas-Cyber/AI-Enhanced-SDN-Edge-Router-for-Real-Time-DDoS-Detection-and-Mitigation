# Five-minute demo script

1. Open the Overview page and show nodes, events, attacks, and drop rules.
2. Open Local Lab Builder and add a router plus one link without launching commands.
3. Open Topology & Flow and explain controller, switch, victim, source, and attack colors.
4. Show baseline `pingall` with 0% loss.
5. Run the authorized `h2 ping -f h1` experiment.
6. Show the detection event and the two priority-500 drop rules.
7. Show packet and byte counters plus timeouts from `ovs-ofctl`.
8. Explain that the demonstrated run used threshold detection because the saved model schema did not match live telemetry.
9. Open OpenFlow Evidence and Runbook.
10. End with the safety boundary: local authorized research prototype, not a production service.
