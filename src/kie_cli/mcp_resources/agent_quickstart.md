# KIE MCP Agent Quickstart

Use the KIE MCP server when an agent needs to prepare, submit, inspect, or poll KIE.AI workflows.

## Safety Defaults

- Prefer dry-run tools first.
- Only submit live jobs when the user explicitly asks for a real KIE API call.
- Never reveal `KIE_API_KEY`.
- Keep polling timeouts bounded.
- Treat generated media URLs and job records as potentially sensitive.

## Common Agent Flow

1. Read `kie://models/supported`.
2. Choose a tool that matches the user's requested workflow.
3. Call the tool with `dry_run=true` to inspect the payload.
4. Ask for confirmation before a live call if the user has not already authorized one.
5. Submit the live call.
6. Use `kie_get_job_status` or `kie_wait_for_job` for async workflows.

## Useful Resources

- `kie://models/supported`
- `kie://tools/contracts`
- `kie://docs/comprehensive-guide`
- `kie://contributing/add-endpoint`
