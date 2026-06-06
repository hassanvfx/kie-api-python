# KIE MCP Server

`kie-mcp` exposes KIE.AI workflows through the Model Context Protocol so agents can inspect supported models, build payloads, submit live jobs, and poll async results.

This guide is intentionally detailed because MCP clients make it easy for agents to act quickly. The default design is dry-run-first and token-safe.

## What MCP Adds

The CLI is for humans and scripts. MCP is for agents.

`kie-mcp` exposes:

- Tools: callable KIE actions
- Resources: agent-readable KIE context
- Prompts: reusable prompting/checklist helpers

The real tested flow is:

```text
MCP client -> kie-mcp -> kie_cli package -> KIE.AI API -> async polling -> generated outputs
```

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,mcp]"
cp .env.example .env
```

Set:

```env
KIE_API_KEY=your_kie_api_key
KIE_BASE_URL=https://api.kie.ai
KIE_UPLOAD_BASE_URL=https://kieai.redpandaai.co
```

## Run

Manual server start:

```bash
.venv/bin/kie-mcp
```

Most MCP clients launch the server over stdio automatically.

## Token Safety For MCP

The safest rule: agents may use the token, but should never see, print, summarize, or store the token.

### Safe Places For `KIE_API_KEY`

| Context | Recommended Storage | Notes |
|---|---|---|
| Local CLI | `.env` | Ignored by Git. Good for development. |
| Codex/Claude/Cursor MCP config | `env` block or client secret manager | Use placeholders in committed examples. |
| CI | encrypted secrets | Only for explicit live tests. |
| Production service | process env or secret manager | Do not bake into images. |

### Unsafe Places

- Prompts
- README snippets with real values
- Screenshots
- GitHub issues
- Job records
- Generated output artifacts
- MCP resources
- Agent memory
- Shell history with exported real values, if your shell history is shared

### Safe MCP Config Pattern

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

Commit only placeholders. Put the real key in your private client config.

### Pre-Push Safety Checks

```bash
git check-ignore -q .env
git check-ignore -q .venv
git check-ignore -q outputs
git status --short
```

Optional scan:

```bash
rg --pcre2 -n --hidden -g '!.git/**' -g '!.env' -g '!.venv/**' -g '!outputs/**' \
  '(KIE_API_KEY\s*[:=]\s*(?!"?replace_with|your_)[^\s,}]+|BEGIN (RSA|OPENSSH|PRIVATE) KEY|sk-[A-Za-z0-9]{20,})' .
```

## Client Setup Cases

### Codex

Use the shape in `examples/mcp/codex_config.json`:

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

After adding it, reload Codex or start a new thread and ask:

```text
List KIE MCP tools and resources.
```

### Claude Desktop

Use `examples/mcp/claude_desktop_config.json` as the server block. Keep the real token in your local Claude Desktop config only.

Smoke prompt:

```text
Read kie://models/supported and summarize what KIE workflows you can call.
```

### Cursor Or Other MCP Clients

Use `examples/mcp/cursor_config.json` or the generic config shape. The important parts are:

- `command` points to the installed `kie-mcp`
- `KIE_API_KEY` is provided privately
- the working environment can read the source checkout if you want repo-local resources

## Recommended Agent Workflow

1. Read `kie://models/supported`.
2. Read `kie://tools/contracts`.
3. Choose the smallest tool that matches the user's intent.
4. Call the tool with `dry_run=true`.
5. Inspect payload, model routing, callback settings, and credit implications.
6. Ask for explicit user approval if the user has not already asked for a live call.
7. Call with `dry_run=false`.
8. For async jobs, call `kie_wait_for_job` with bounded timeout.
9. Return output URLs and job IDs without exposing tokens.

## Tools Reference

All submit-capable tools default to `dry_run=true`.

### `kie_upload_file`

Uploads a local file to KIE temporary storage.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `file_path` | string | Yes | None | Local file to upload. |
| `upload_path` | string | No | `kie-mcp/uploads` | KIE upload path. |
| `file_name` | string/null | No | null | Optional upload filename override. |
| `dry_run` | boolean | No | true | Shows intended upload without sending file. |

Use case:

```text
Dry-run upload ./reference.png, then upload it live if the path is correct.
```

### `kie_generate_image`

Submits or dry-runs an async image generation task.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `model` | string | Yes | None | `nano-banana-pro` or `gpt-image-2`. |
| `prompt` | string | Yes | None | Image prompt. |
| `image` | list[string]/null | No | null | Local paths or URLs. |
| `aspect_ratio` | string/null | No | model default | `1:1` for Nano Banana, `auto` for GPT Image 2. |
| `resolution` | string | No | `1K` | Provider-specific resolution. |
| `output_format` | string | No | `png` | `png` or `jpg`; relevant to Nano Banana. |
| `callback_url` | string/null | No | null | Sent as KIE `callBackUrl`. |
| `upload_path` | string | No | `kie-mcp/images` | Upload path for local image inputs. |
| `save_job` | string/null | No | null | Local job record path. |
| `dry_run` | boolean | No | true | Must be false for live submit. |

Routing:

- `gpt-image-2` without images -> `gpt-image-2-text-to-image`
- `gpt-image-2` with images -> `gpt-image-2-image-to-image`
- `nano-banana-pro` -> `nano-banana-pro`

Safe first call:

```json
{
  "model": "gpt-image-2",
  "prompt": "A cinematic product render",
  "dry_run": true
}
```

### `kie_generate_video`

Submits or dry-runs an async video generation task.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `model` | string | Yes | None | `grok` or `veo3`. |
| `prompt` | string | Yes | None | Video prompt. |
| `image` | list[string]/null | No | null | Local paths or URLs. |
| `aspect_ratio` | string/null | No | inferred | Grok text defaults `2:3`; image/Veo defaults `16:9`. |
| `mode` | string | No | `normal` | Grok: `fun`, `normal`, or `spicy`. |
| `duration` | integer | No | `6` | Grok duration. |
| `resolution` | string/null | No | `480p` Grok, `720p` Veo | Provider-specific. |
| `nsfw_checker` | boolean | No | false | Grok payload flag. |
| `veo_model` | string | No | `veo3_fast` | `veo3`, `veo3_fast`, or `veo3_lite`. |
| `generation_type` | string/null | No | inferred | Veo: `TEXT_2_VIDEO`, `FIRST_AND_LAST_FRAMES_2_VIDEO`, `REFERENCE_2_VIDEO`. |
| `disable_translation` | boolean | No | false | Veo translation toggle. |
| `watermark` | string/null | No | null | Veo watermark. |
| `callback_url` | string/null | No | null | Sent as `callBackUrl`. |
| `upload_path` | string | No | `kie-mcp/videos` | Upload path for local image inputs. |
| `save_job` | string/null | No | null | Local job record path. |
| `dry_run` | boolean | No | true | Must be false for live submit. |

Routing:

- `grok` without images -> `grok-imagine/text-to-video`
- `grok` with images -> `grok-imagine/image-to-video`
- `veo3` -> selected `veo_model`

### `kie_chat_completion`

Runs or dry-runs a synchronous chat completion.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `model` | string | Yes | None | `gpt-5-2` or `gemini-3-pro`. |
| `prompt` | string | Yes | None | User prompt. |
| `image` | list[string]/null | No | null | Optional local paths or URLs. |
| `reasoning_effort` | string | No | `high` | `low` or `high`. |
| `include_thoughts` | boolean | No | false | Gemini payload option. |
| `web_search` | boolean | No | false | Enables web-search payload option. |
| `max_completion_tokens` | integer/null | No | null | GPT completion cap. |
| `request_timeout` | number | No | `60` | HTTP timeout seconds. |
| `upload_path` | string | No | `kie-mcp/chat` | Upload path for local image inputs. |
| `dry_run` | boolean | No | true | Must be false for live call. |

Known live smoke result:

- `kie_chat_completion` with `gpt-5-2`, `dry_run=false`, and tiny token cap returned `KIE MCP OK`.

### `kie_suno_music`

Submits or dry-runs an async Suno music generation task.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `prompt` | string | Yes | None | Music prompt. |
| `custom_mode` | boolean | No | false | Sends `customMode`. |
| `instrumental` | boolean | No | false | Sends `instrumental`. |
| `model` | string/null | Recommended | null | Live validation used `V5_5`; provider may require it. |
| `style` | string/null | No | null | Style text. |
| `title` | string/null | No | null | Song title. |
| `negative_tags` | string/null | No | null | Negative tags. |
| `callback_url` | string/null | Recommended | null | Live provider required this in MCP media test. |
| `save_job` | string/null | No | null | Local job record path. |
| `dry_run` | boolean | No | true | Must be false for live submit. |

Live finding:

- Submitting without `callback_url` returned: `Please enter callBackUrl.`
- Retrying with an HTTPS callback placeholder succeeded and produced audio/artwork URLs.

### `kie_suno_lyrics`

Submits or dry-runs an async Suno lyrics generation task.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `prompt` | string | Yes | None | Lyrics prompt. |
| `callback_url` | string/null | Recommended | null | Live provider may require it. |
| `dry_run` | boolean | No | true | Must be false for live submit. |

### `kie_suno_sounds`

Submits or dry-runs an async Suno sound generation task.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `prompt` | string | Yes | None | Sound prompt. |
| `model` | string/null | No | null | `V5` or `V5_5`. |
| `sound_loop` | boolean | No | false | Sends `soundLoop`. |
| `sound_tempo` | integer/null | No | null | Tempo. |
| `sound_key` | string/null | No | null | Musical key. |
| `grab_lyrics` | boolean | No | false | Sends `grabLyrics`. |
| `callback_url` | string/null | Recommended | null | Provider callback URL. |
| `save_job` | string/null | No | null | Local job record path. |
| `dry_run` | boolean | No | true | Must be false for live submit. |

### `kie_get_job_status`

Reads one async job status.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `job_id` | string | Yes | None | KIE task/job ID. |
| `model` | string | Yes | None | Concrete routed model, e.g. `gpt-image-2-text-to-image`, `suno-music`, `veo3_fast`. |

### `kie_wait_for_job`

Polls an async job until terminal status or timeout.

Parameters:

| Parameter | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `job_id` | string | Yes | None | KIE task/job ID. |
| `model` | string | Yes | None | Concrete routed model. |
| `poll_interval` | number | No | `5.0` | Seconds between polls. |
| `timeout` | number | No | `900.0` | Total wait timeout in seconds. |

Use bounded timeouts. Agents should not poll forever.

## Resources Reference

### Package-Local Resources

These work from installed packages:

| URI | Purpose |
|---|---|
| `kie://docs/agent-quickstart` | Agent workflow and safety quickstart. |
| `kie://models/supported` | JSON list of implemented workflow families and models. |
| `kie://tools/contracts` | JSON tool contract summary. |
| `kie://contributing/add-endpoint` | Endpoint contribution checklist. |

### Source-Checkout Resources

These work best when running from this repository:

| URI | Purpose |
|---|---|
| `kie://docs/comprehensive-guide` | Long-form CLI guide. |
| `kie://docs/kie-ai/manifest` | Local mirror manifest for KIE docs. |

The package-local resources live in `src/kie_cli/mcp_resources/`, not GitHub Raw. That avoids network dependency and version drift.

## Prompts Reference

### `kie_image_prompt_builder`

Parameters:

| Parameter | Type | Default |
|---|---|---|
| `subject` | string | required |
| `style` | string | `cinematic` |
| `aspect_ratio` | string | `1:1` |

### `kie_video_prompt_builder`

Parameters:

| Parameter | Type | Default |
|---|---|---|
| `subject` | string | required |
| `camera_motion` | string | `slow dolly forward` |
| `mood` | string | `cinematic` |

### `kie_debug_failed_job`

Parameters:

| Parameter | Type | Default |
|---|---|---|
| `job_id` | string | required |
| `model` | string | required |
| `error_message` | string | empty |

### `kie_add_new_endpoint_contribution_plan`

Parameters:

| Parameter | Type | Default |
|---|---|---|
| `endpoint_name` | string | required |
| `docs_url` | string | required |

## Tested MCP Flows

Protocol smoke test:

- initialize
- tools/list
- resources/list
- prompts/list
- resources/read
- dry-run tools/call

Live smoke tests:

- `kie_chat_completion` returned `KIE MCP OK`.
- `kie_generate_image` submitted and polled to success.
- `kie_suno_music` submitted and polled to success after adding callback URL.

## Manual Test Script

Use this shape for local protocol tests:

```python
import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=".venv/bin/kie-mcp", args=[])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(await session.list_tools())
            print(await session.list_resources())
            result = await session.call_tool(
                "kie_generate_image",
                {
                    "model": "gpt-image-2",
                    "prompt": "A cinematic product render",
                    "dry_run": True
                },
            )
            print(result)

anyio.run(main)
```

## Live Call Safety Checklist

Before `dry_run=false`:

- Confirm `KIE_API_KEY` is configured privately.
- Confirm the user asked for a live call.
- Confirm model and routed model are correct.
- Confirm callback URL is present for Suno when needed.
- Confirm `save_job` points into ignored `outputs/` if saving artifacts.
- Confirm `timeout` is bounded for waits.
- Confirm generated URLs can be shared with the current user.

## Troubleshooting

### `The MCP SDK is not installed`

Install the MCP extra:

```bash
.venv/bin/python -m pip install -e ".[mcp]"
```

### `KIE_API_KEY is required`

Set the token in `.env` or the MCP client environment. Do not paste it into a prompt.

### Suno Says `Please enter callBackUrl`

Pass `callback_url` to `kie_suno_music`, `kie_suno_lyrics`, or `kie_suno_sounds`.

### A Wait Times Out

Keep the job ID and routed model. Resume later:

```text
Call kie_wait_for_job with the same job_id and model, a larger timeout, and a reasonable poll_interval.
```

### Agent Cannot See Repo-Local Docs

Package-local resources should still work. Source-checkout docs require running the MCP server from a checkout that includes `docs/`.
