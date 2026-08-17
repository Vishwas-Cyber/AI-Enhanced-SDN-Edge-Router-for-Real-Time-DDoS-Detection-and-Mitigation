# Known limitations

- The current final run verified rule-based DDoS detection and OpenFlow drop enforcement.
- Runtime model probability was null due to a feature-schema mismatch.
- `h2 ping -f h1` is the supported lab traffic command; `hping` is not installed and is not required.
- The Local Lab Builder writes a topology model; it does not launch arbitrary Mininet code.
- The dashboard is a local authorized-lab prototype, not a production DDoS service.
