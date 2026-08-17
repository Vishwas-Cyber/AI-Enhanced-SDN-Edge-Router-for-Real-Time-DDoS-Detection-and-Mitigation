# SDN Sentinel commercial MVP foundation

This release adds a localhost-bound FastAPI service with bearer-token login,
role separation, validated topology access, event retrieval, and a Docker
entry point. The Streamlit dashboard remains the analyst interface.

## Production requirements before external deployment

- Replace in-memory tokens with a persistent identity provider.
- Store passwords only as strong password hashes in a secret manager.
- Use PostgreSQL/TimescaleDB for events and metrics.
- Put the API behind TLS and a reverse proxy.
- Add controller/device certificates and rotation.
- Add controller high availability and rule reconciliation.
- Add rate limiting, CSRF protection where applicable, and audit storage.
- Never use default credentials.
- Do not expose the lab API or dashboard directly to the Internet.

## Current safe scope

The API is a commercial-MVP foundation for an authorized lab. It validates
node identifiers and links, reads local telemetry, and does not execute
arbitrary shell commands or automatically launch network experiments.
