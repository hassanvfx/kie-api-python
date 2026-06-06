# kie-api

`kie-api` is an open-source Python CLI and MCP server for working with the [KIE.AI API](https://docs.kie.ai/).

It gives humans and agents a focused, tested interface for KIE upload, image, video, chat, Suno audio, and async job polling workflows. The implementation follows the official KIE docs and is designed for contributors to expand as KIE adds or changes endpoints.

## Highlights

- Human CLI: `kie-cli`
- Agent MCP server: `kie-mcp`
- Dry-run support for inspecting payloads before spending credits
- Upload-first handling for local image/media references
- Async job records for durable polling and automation
- Package-local MCP resources so agents can understand supported models without fetching GitHub Raw
- Gated live tests for real KIE validation
- `.env` and generated outputs ignored by default

## Install

Requirements:

- Python 3.11+
- A KIE API key

CLI-only setup:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
```

CLI + MCP setup:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,mcp]"
cp .env.example .env
```

Edit `.env`:

```env
KIE_API_KEY=your_kie_api_key
KIE_BASE_URL=https://api.kie.ai
KIE_UPLOAD_BASE_URL=https://kieai.redpandaai.co
```

Do not commit `.env`. The repository ignores `.env`, `.venv`, caches, outputs, logs, and private-key-like files.

## Token Safety

### Where The Token Lives

For an external cloner, the real KIE token should live in their own local `.env` file or their own private MCP client config. It should never live in committed example JSON.

| File or Location | Should contain a real token? | Committed? | Purpose |
|---|---:|---:|---|
| `.env.example` | No | Yes | Shows required variable names with placeholders. |
| `.env` | Yes, locally | No | Local CLI/MCP development secrets. |
| `examples/mcp/*.json` | No | Yes | Safe example configs with placeholders only. |
| User's private MCP client config | Optional | No | Can pass `KIE_API_KEY` to `kie-mcp` through an `env` block. |

External setup:

```bash
git clone git@github.com:hassanvfx/kie-api-python.git
cd kie-api-python
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,mcp]"
cp .env.example .env
```

Then edit `.env`:

```env
KIE_API_KEY=their_own_kie_api_key
KIE_BASE_URL=https://api.kie.ai
KIE_UPLOAD_BASE_URL=https://kieai.redpandaai.co
```

Use one of these patterns:

- Local CLI development: put `KIE_API_KEY` in `.env`.
- MCP desktop clients: pass `KIE_API_KEY` in the MCP client `env` block or client secret manager.
- CI/live tests: use encrypted CI secrets.
- Never put real keys in `README.md`, screenshots, prompts, issue reports, job records, or committed MCP config examples.

Before pushing:

```bash
git check-ignore -q .env
git status --short
```

For extra safety, scan for common secret shapes:

```bash
rg --pcre2 -n --hidden -g '!.git/**' -g '!.env' -g '!.venv/**' -g '!outputs/**' \
  '(KIE_API_KEY\s*[:=]\s*(?!"?replace_with|your_)[^\s,}]+|BEGIN (RSA|OPENSSH|PRIVATE) KEY|sk-[A-Za-z0-9]{20,})' .
```

## CLI Overview

The installed command is:

```bash
kie-cli
```

Global behavior:

- Most submit commands support `--dry-run` to show the payload without calling KIE.
- Most commands support `--json` for machine-readable output.
- Prompted commands require exactly one of `--prompt` or `--prompt-file`.
- Image-capable commands accept repeated `--image` values.
- `--image` can be a local file path or `http(s)` URL.
- Local files are uploaded first unless `--dry-run` is set.

## Environment Variables

| Variable | Required | Default | Used By | Notes |
|---|---:|---|---|---|
| `KIE_API_KEY` | Yes for live calls | None | all live CLI/MCP calls | Bearer token for KIE. Never commit it. |
| `KIE_BASE_URL` | No | `https://api.kie.ai` | generation, chat, status | Override only for alternate deployments. |
| `KIE_UPLOAD_BASE_URL` | No | `https://kieai.redpandaai.co` | upload/local media | Used for temporary file uploads. |
| `RUN_KIE_LIVE_TESTS` | No | unset | integration tests | Set to `1` to run live tests. |
| `KIE_LIVE_SCOPE` | No | `all` | integration tests | `llm`, `gemini`, `image`, `video`, `suno`, `generation`, or `all`. |
| `KIE_LIVE_POLL_INTERVAL` | No | `10` | integration tests | Seconds between live poll attempts. |
| `KIE_LIVE_TIMEOUT` | No | `900` | integration tests | Live polling timeout in seconds. |
| `KIE_SUNO_CALLBACK_URL` | Sometimes | None | Suno live tests | Suno music/lyrics may require callback URLs. |

## CLI Reference

### `kie-cli upload`

Upload a local file to KIE temporary storage.

```bash
kie-cli upload FILE [--upload-path PATH] [--dry-run] [--json]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `FILE` | Yes | None | Local file path. |
| `--upload-path` | No | `kie-cli/uploads` | KIE-side upload folder/path. |
| `--dry-run` | No | false | Shows intended upload without sending file. |
| `--json` | No | false | Emits JSON output. |

Example:

```bash
kie-cli upload ./reference.png --upload-path kie-cli/uploads --json
```

### `kie-cli image`

Submit an async image generation/editing job.

```bash
kie-cli image MODEL (--prompt TEXT | --prompt-file FILE) [options]
```

Models:

| CLI Model | Routed Model | Notes |
|---|---|---|
| `nano-banana-pro` | `nano-banana-pro` | Supports prompt plus optional reference images. |
| `gpt-image-2` | `gpt-image-2-text-to-image` | Used when no images are provided. |
| `gpt-image-2` | `gpt-image-2-image-to-image` | Used when one or more images are provided. |

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `MODEL` | Yes | None | `nano-banana-pro` or `gpt-image-2`. |
| `--prompt` | Yes* | None | Inline prompt. Mutually exclusive with `--prompt-file`. |
| `--prompt-file` | Yes* | None | UTF-8 text file prompt. Mutually exclusive with `--prompt`. |
| `--image` | No | repeatable empty list | Local file or URL. Can be repeated. |
| `--aspect-ratio` | No | `1:1` for `nano-banana-pro`, `auto` for `gpt-image-2` | Provider-specific aspect ratio string. |
| `--resolution` | No | `1K` | Provider-specific resolution string. |
| `--output-format` | No | `png` | `png` or `jpg`. Used by `nano-banana-pro`. |
| `--callback-url` | No | None | Provider callback URL, sent as `callBackUrl`. |
| `--upload-path` | No | `kie-cli/images` | Upload path for local images. |
| `--save-job` | No | None | Writes a job record JSON for later polling. |
| `--dry-run` | No | false | Shows payload and resolved media without submitting. |
| `--json` | No | false | Emits JSON output. |

Examples:

```bash
kie-cli image gpt-image-2 --prompt "A cinematic night city poster" --json

kie-cli image gpt-image-2 \
  --prompt-file ./prompt.txt \
  --image ./reference.png \
  --aspect-ratio 16:9 \
  --resolution 1K \
  --save-job outputs/jobs/image.json \
  --json

kie-cli image nano-banana-pro \
  --prompt "Commercial product photo of a glass perfume bottle" \
  --output-format png \
  --dry-run \
  --json
```

### `kie-cli video`

Submit an async video generation job.

```bash
kie-cli video MODEL (--prompt TEXT | --prompt-file FILE) [options]
```

Models:

| CLI Model | Routed Model | Notes |
|---|---|---|
| `grok` | `grok-imagine/text-to-video` | Used when no images are provided. |
| `grok` | `grok-imagine/image-to-video` | Used when one or more images are provided. |
| `veo3` | `veo3`, `veo3_fast`, or `veo3_lite` | Chosen by `--veo-model`. |

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `MODEL` | Yes | None | `grok` or `veo3`. |
| `--prompt` | Yes* | None | Inline prompt. |
| `--prompt-file` | Yes* | None | Prompt file. |
| `--image` | No | repeatable empty list | Local file or URL. Can be repeated. |
| `--aspect-ratio` | No | `2:3` for Grok text, `16:9` for Grok image/Veo | Provider-specific aspect ratio. |
| `--mode` | No | `normal` | Grok only: `fun`, `normal`, or `spicy`. |
| `--duration` | No | `6` | Grok duration. Text mode sends integer; image mode sends string. |
| `--resolution` | No | `480p` for Grok, `720p` for Veo | Provider-specific resolution. |
| `--nsfw-checker` | No | false | Grok payload flag. |
| `--veo-model` | No | `veo3_fast` | Veo only: `veo3`, `veo3_fast`, or `veo3_lite`. |
| `--generation-type` | No | inferred | Veo only: `TEXT_2_VIDEO`, `FIRST_AND_LAST_FRAMES_2_VIDEO`, or `REFERENCE_2_VIDEO`. |
| `--disable-translation` | No | false | Veo only. Sends `enableTranslation=false`. |
| `--watermark` | No | None | Veo watermark string. |
| `--callback-url` | No | None | Provider callback URL. |
| `--upload-path` | No | `kie-cli/videos` | Upload path for local images. |
| `--save-job` | No | None | Writes a job record. |
| `--dry-run` | No | false | Shows payload without submitting. |
| `--json` | No | false | Emits JSON output. |

Examples:

```bash
kie-cli video grok --prompt "A neon corridor dolly shot" --json

kie-cli video grok \
  --prompt "Animate this product photo with a slow push-in" \
  --image ./product.png \
  --duration 8 \
  --resolution 720p \
  --save-job outputs/jobs/grok-video.json \
  --json

kie-cli video veo3 \
  --prompt-file ./video-prompt.txt \
  --veo-model veo3_fast \
  --generation-type TEXT_2_VIDEO \
  --watermark "kie-api" \
  --json
```

### `kie-cli llm`

Run a synchronous OpenAI-compatible KIE chat completion.

```bash
kie-cli llm gpt-5-2 (--prompt TEXT | --prompt-file FILE) [options]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `model` | Yes | `gpt-5-2` | Currently only `gpt-5-2`. |
| `--prompt` | Yes* | None | Inline prompt. |
| `--prompt-file` | Yes* | None | Prompt file. |
| `--image` | No | repeatable empty list | Optional image input, local file or URL. |
| `--reasoning-effort` | No | `high` | `low` or `high`. |
| `--request-timeout` | No | `60` | HTTP timeout in seconds. |
| `--max-completion-tokens` | No | None | Completion token cap. |
| `--web-search` | No | false | Enables web search field in payload. |
| `--upload-path` | No | `kie-cli/llm` | Upload path for local images. |
| `--dry-run` | No | false | Shows payload without calling the model. |
| `--json` | No | false | Emits JSON output. |

Examples:

```bash
kie-cli llm gpt-5-2 --prompt "Reply with a haiku" --json

kie-cli llm gpt-5-2 \
  --prompt "Describe this image" \
  --image ./image.png \
  --reasoning-effort low \
  --max-completion-tokens 256 \
  --json
```

### `kie-cli gemini`

Run KIE Gemini multimodal chat completion.

```bash
kie-cli gemini gemini-3-pro (--prompt TEXT | --prompt-file FILE) [options]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `model` | Yes | `gemini-3-pro` | Currently only `gemini-3-pro`. |
| `--prompt` | Yes* | None | Inline prompt. |
| `--prompt-file` | Yes* | None | Prompt file. |
| `--image` | No | repeatable empty list | Optional image input, local file or URL. |
| `--reasoning-effort` | No | `high` | `low` or `high`. |
| `--include-thoughts` | No | false | Requests thought inclusion in payload. |
| `--web-search` | No | false | Enables web search field in payload. |
| `--upload-path` | No | `kie-cli/gemini` | Upload path for local images. |
| `--dry-run` | No | false | Shows payload without calling the model. |
| `--json` | No | false | Emits JSON output. |

Example:

```bash
kie-cli gemini gemini-3-pro \
  --prompt "Analyze this reference image" \
  --image ./reference.png \
  --dry-run \
  --json
```

### `kie-cli suno music`

Submit an async Suno music generation job.

```bash
kie-cli suno music (--prompt TEXT | --prompt-file FILE) [options]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `--prompt` | Yes* | None | Inline prompt. |
| `--prompt-file` | Yes* | None | Prompt file. |
| `--custom-mode` | No | false | Sends `customMode=true`. |
| `--instrumental` | No | false | Sends `instrumental=true`. |
| `--model` | Recommended | None | Provider model. Live validation used `V5_5`; provider may require this. |
| `--style` | No | None | Suno style text. |
| `--title` | No | None | Song title. |
| `--negative-tags` | No | None | Negative tags. |
| `--callback-url` | Recommended | None | Live provider may require `callBackUrl`. |
| `--save-job` | No | None | Writes a job record. |
| `--dry-run` | No | false | Shows payload without submitting. |
| `--json` | No | false | Emits JSON output. |

Examples:

```bash
kie-cli suno music \
  --prompt "A dreamy synth-pop song" \
  --model V5_5 \
  --callback-url https://example.com/kie-callback \
  --save-job outputs/jobs/suno-music.json \
  --json
```

### `kie-cli suno lyrics`

Submit an async Suno lyrics generation job.

```bash
kie-cli suno lyrics (--prompt TEXT | --prompt-file FILE) [options]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `--prompt` | Yes* | None | Inline prompt. |
| `--prompt-file` | Yes* | None | Prompt file. |
| `--callback-url` | Recommended | None | Live provider may require `callBackUrl`. |
| `--dry-run` | No | false | Shows payload without submitting. |
| `--json` | No | false | Emits JSON output. |

Example:

```bash
kie-cli suno lyrics \
  --prompt "Hopeful indie chorus about sunrise" \
  --callback-url https://example.com/kie-callback \
  --json
```

### `kie-cli suno sounds`

Submit an async Suno sound generation job.

```bash
kie-cli suno sounds (--prompt TEXT | --prompt-file FILE) [options]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `--prompt` | Yes* | None | Inline prompt. |
| `--prompt-file` | Yes* | None | Prompt file. |
| `--model` | No | None | `V5` or `V5_5`. |
| `--sound-loop` | No | false | Sends `soundLoop=true`. |
| `--sound-tempo` | No | None | Integer tempo. |
| `--sound-key` | No | None | Musical key, e.g. `Am`. |
| `--grab-lyrics` | No | false | Sends `grabLyrics=true`. |
| `--callback-url` | Recommended | None | Provider callback URL. |
| `--save-job` | No | None | Writes a job record. |
| `--dry-run` | No | false | Shows payload without submitting. |
| `--json` | No | false | Emits JSON output. |

Example:

```bash
kie-cli suno sounds \
  --prompt "Soft rain on a metal roof" \
  --model V5_5 \
  --sound-loop \
  --sound-tempo 110 \
  --sound-key Am \
  --json
```

### `kie-cli job-status`

Query one async job once.

```bash
kie-cli job-status JOB_ID [--model MODEL] [--kind auto|market|veo] [--json]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `JOB_ID` | Yes | None | Task/job ID returned by submit command. |
| `--model` | Recommended | None | Preferred model-routed status lookup. |
| `--kind` | No | `auto` | Legacy fallback: `auto`, `market`, or `veo`. Prefer `--model`. |
| `--json` | No | false | Emits JSON output. |

Examples:

```bash
kie-cli job-status TASK_ID --model gpt-image-2-text-to-image --json
kie-cli job-status TASK_ID --model suno-music --json
```

### `kie-cli wait`

Poll an async job until success, failure, or timeout.

```bash
kie-cli wait [JOB_ID] (--model MODEL | --job-file FILE) [options]
```

Parameters:

| Parameter | Required | Default | Notes |
|---|---:|---|---|
| `JOB_ID` | Yes* | None | Required when not using `--job-file`. |
| `--model` | Yes* | None | Required with explicit `JOB_ID`. |
| `--job-file` | Yes* | None | Reads job ID and routed model from saved job record. |
| `--poll-interval` | No | `5.0` | Seconds between polls. |
| `--timeout` | No | `900.0` | Timeout in seconds. |
| `--json` | No | false | Emits JSON output. |

Examples:

```bash
kie-cli wait --job-file outputs/jobs/image.json --poll-interval 5 --timeout 900 --json

kie-cli wait TASK_ID --model suno-music --poll-interval 10 --timeout 900 --json
```

## Async Job Records

Commands with `--save-job` write a JSON file containing:

- job ID
- routed model
- submit endpoint
- status endpoint
- submitted payload
- resolved media
- raw submit response

Use job files when possible. They avoid later confusion between CLI aliases and concrete routed models.

## MCP Usage

Install MCP support:

```bash
.venv/bin/python -m pip install -e ".[dev,mcp]"
```

Run the server manually:

```bash
.venv/bin/kie-mcp
```

Most agents launch it for you. Example configs live in `examples/mcp/`, and the complete MCP guide is in [docs/mcp.md](docs/mcp.md).

Minimal MCP client config:

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

The committed files in `examples/mcp/` intentionally use placeholders. A real user should either let `kie-mcp` load their local `.env`, or put their real key only in a private MCP client config outside Git.

MCP safety:

- Tools that can spend credits default to `dry_run=true`.
- Agents should call dry-run first, review payloads, then submit live only after user approval.
- Keep `KIE_API_KEY` in MCP client environment settings, not in prompts.
- Use `kie_wait_for_job` with bounded `timeout`.

## Testing

Unit and MCP dry-run tests:

```bash
.venv/bin/python -m pytest -q
```

MCP stdio protocol test requires `.[mcp]`; it skips when MCP SDK is not installed.

Live integration tests are opt-in:

```bash
RUN_KIE_LIVE_TESTS=1 .venv/bin/python -m pytest tests/integration -q
```

## Project Layout

```text
src/kie_cli/                 CLI and MCP implementation
src/kie_cli/mcp_resources/   Package-local agent resources
tests/                       Unit and MCP protocol tests
tests/integration/           Opt-in live KIE API tests
docs/kie-ai/raw/             Local mirror of KIE docs
docs/kie-cli/                Long-form CLI guide
docs/mcp.md                  Comprehensive MCP guide
docs/journals/               ClineFlow task journals
examples/mcp/                MCP client config examples
scripts/                     Utility scripts
```

## Contributing

Contributions are welcome, especially changes that expand or refresh coverage from the official KIE docs:

1. Pick an endpoint or model from [docs.kie.ai](https://docs.kie.ai/).
2. Add or update payload builders, routes, status normalization, and CLI flags as needed.
3. Add MCP tool/resource updates when the feature should be agent-accessible.
4. Add focused unit tests for payload shape and dry-run behavior.
5. Add gated live-test coverage when real provider behavior needs validation.
6. Update `README.md`, [docs/mcp.md](docs/mcp.md), or `docs/kie-cli/comprehensive-guide.md`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## Security Notes

- Never expose `KIE_API_KEY` in frontend code, screenshots, logs, commits, issue reports, or prompts.
- Use dry-run mode before live calls.
- Treat generated media URLs and live-test output as local artifacts unless intentionally published.
- Keep callback URLs and job artifacts out of committed examples unless they are placeholders.
- Verify `.env`, `.venv`, caches, and `outputs/` are not staged before pushing.

## License

MIT. See [LICENSE](LICENSE).
