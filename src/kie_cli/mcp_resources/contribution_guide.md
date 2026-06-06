# Adding A KIE Endpoint

Follow this checklist when extending `kie-api` for a new KIE.AI endpoint or model.

1. Read the official KIE docs for the endpoint.
2. Add a focused payload builder in `src/kie_cli/payloads.py`.
3. Add route metadata in `src/kie_cli/routes.py` when the endpoint creates an async job.
4. Add response normalization in `src/kie_cli/status.py` when the status shape is new.
5. Add CLI and MCP inputs that map directly to documented fields.
6. Add unit tests for payloads, routing, and dry-run behavior.
7. Add gated live tests only when provider behavior cannot be validated locally.
8. Update `src/kie_cli/mcp_resources/supported_models.json`.
9. Update `src/kie_cli/mcp_resources/tool_contracts.json`.
10. Update human docs in `README.md` or `docs/kie-cli/comprehensive-guide.md`.

Keep additions small and commit in reviewable slices.
