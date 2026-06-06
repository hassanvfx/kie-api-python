# Contributing

Thanks for helping make `kie-api` better for developers and agents.

This project tracks the official KIE.AI API documentation at <https://docs.kie.ai/> and turns focused workflows into:

- a Python CLI for humans and scripts
- an MCP server for AI agents
- tests and documentation that preserve the request/response contracts

## Development Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
```

Set `KIE_API_KEY` only in `.env` or your shell. Never commit real credentials.

To develop MCP features:

```bash
.venv/bin/python -m pip install -e ".[dev,mcp]"
```

## Contribution Flow

1. Pick an endpoint, model, or workflow from the KIE docs.
2. Add or update payload builders in `src/kie_cli/payloads.py`.
3. Add routing/status handling when the workflow is asynchronous.
4. Add CLI flags or MCP tools only when they map to a stable, documented contract.
5. Add focused unit tests first.
6. Add gated live tests only when real provider behavior must be validated.
7. Update README, MCP docs, or resource contracts so agents can understand the new surface.
8. Add or update the ClineFlow journal entry in `docs/journals/`.

## Testing

Run unit tests:

```bash
.venv/bin/python -m pytest -q
```

Run live tests only when you intentionally want to make network calls and spend KIE credits:

```bash
RUN_KIE_LIVE_TESTS=1 .venv/bin/python -m pytest tests/integration -q
```

Useful live-test controls:

- `KIE_LIVE_SCOPE=llm|gemini|image|video|suno|generation|all`
- `KIE_LIVE_POLL_INTERVAL=10`
- `KIE_LIVE_TIMEOUT=900`
- `KIE_SUNO_CALLBACK_URL=https://your-callback.example/path`

## Agent-Surface Guidelines

When adding MCP features:

- Prefer dry-run support for expensive or irreversible operations.
- Keep tool inputs explicit and typed.
- Do not expose secrets in tool results.
- Use bounded polling timeouts.
- Keep agent resources compact and package-local under `src/kie_cli/mcp_resources/`.
- Keep larger human docs under `docs/`.

## Commit Style

Use small commits with clear messages. A good sequence is:

- docs/open-source basics
- MCP resources/contracts
- MCP implementation
- tests
- docs/examples

That makes rollback and review easier.
