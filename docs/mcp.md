# KIE MCP Server

`kie-mcp` exposes the KIE CLI workflows as an MCP server so AI agents can inspect docs, build payloads, submit KIE jobs, and poll async results.

The server is dry-run-first for expensive workflows. Tools that can spend KIE credits default to `dry_run=true`; set `dry_run=false` only when you want a real API call.

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,mcp]"
cp .env.example .env
```

Set `KIE_API_KEY` in `.env` or in your MCP client environment.

## Run

```bash
.venv/bin/kie-mcp
```

Most desktop agent clients start MCP servers over stdio, so you normally do not run this command manually except for smoke testing.

## Client Configuration

Generic MCP client config:

```json
{
  "mcpServers": {
    "kie-api": {
      "command": "/Users/hassan/repos/kie-api/.venv/bin/kie-mcp",
      "env": {
        "KIE_API_KEY": "replace_with_your_kie_api_key"
      }
    }
  }
}
```

Prefer loading the key from your local environment or client secret manager when available.

## Tools

Submit-capable tools default to dry-run mode:

- `kie_upload_file`
- `kie_generate_image`
- `kie_generate_video`
- `kie_chat_completion`
- `kie_suno_music`
- `kie_suno_lyrics`
- `kie_suno_sounds`
- `kie_get_job_status`
- `kie_wait_for_job`

Recommended agent flow:

1. Read `kie://models/supported`.
2. Call a generation/chat tool with `dry_run=true`.
3. Review the payload and credit implications.
4. Call again with `dry_run=false` only after the user authorizes the live call.
5. Use `kie_get_job_status` or `kie_wait_for_job` for async jobs.

## Resources

Package-local resources:

- `kie://docs/agent-quickstart`
- `kie://models/supported`
- `kie://tools/contracts`
- `kie://contributing/add-endpoint`

Repo-local resources when running from a source checkout:

- `kie://docs/comprehensive-guide`
- `kie://docs/kie-ai/manifest`

The package-local resources live under `src/kie_cli/mcp_resources/` so installed agents can use them without GitHub Raw or network access.

## Prompts

- `kie_image_prompt_builder`
- `kie_video_prompt_builder`
- `kie_debug_failed_job`
- `kie_add_new_endpoint_contribution_plan`

## Manual Smoke Test

After configuring an MCP client, ask the agent:

```text
List the KIE MCP resources and summarize supported models.
```

Then:

```text
Dry-run a KIE gpt-image-2 image generation payload for a cinematic product render.
```

Only after the dry-run looks right:

```text
Submit the live KIE image job and poll it until complete.
```

## Safety Notes

- Do not put `KIE_API_KEY` in prompts, screenshots, or committed config files.
- Treat generated media URLs as local/private unless you intentionally publish them.
- Keep polling timeouts bounded.
- Use live calls only when the user has explicitly authorized spending KIE credits.
