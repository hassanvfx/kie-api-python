# Security Policy

## Supported Versions

This project is early-stage. Security fixes should target the current `main` branch unless a release branch exists.

## Reporting A Vulnerability

Please report security issues privately to the repository owner instead of opening a public issue.

Include:

- affected files or commands
- reproduction steps
- expected impact
- whether credentials, generated media URLs, or live KIE jobs may have been exposed

## Secret Handling

Never commit:

- `.env`
- KIE API keys
- callback secrets
- private keys
- generated live-test outputs that contain sensitive request/response data

The repository includes `.env.example` for safe placeholders. Real values belong in local environment variables or `.env`.

## Live API Calls

KIE workflows can spend account credits and create externally hosted media. Treat live calls as intentional actions:

- use `--dry-run` or MCP `dry_run=true` first
- keep polling timeouts bounded
- do not publish generated URLs unless intended
- avoid pasting secrets or private media into prompts

## MCP Safety

The MCP server is designed for explicit KIE workflows, not arbitrary shell or filesystem access. File upload tools should receive deliberate file paths from the user/agent, and tool responses should avoid echoing secrets.
