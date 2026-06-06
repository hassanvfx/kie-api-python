# kie-api

`kie-api` is a focused Python CLI for working with the [KIE.AI API](https://docs.kie.ai/). It wraps a practical subset of KIE image, video, chat, upload, Suno, and async job workflows so developers can submit tasks, inspect payloads, poll results, and extend coverage as KIE's docs evolve.

This project is intentionally open-source friendly: local secrets stay in `.env`, generated media and live-test outputs are ignored, and contributors are encouraged to keep the implementation aligned with the upstream KIE documentation.

## What It Supports

Current CLI surface:

- File upload to KIE temporary storage
- Image generation and editing:
  - `nano-banana-pro`
  - `gpt-image-2`
- Video generation:
  - `grok`
  - `veo3`
- OpenAI-compatible KIE chat completion:
  - `gpt-5-2`
- Gemini multimodal chat:
  - `gemini-3-pro`
- Suno workflows:
  - music generation
  - lyrics generation
  - sounds generation
- Async job utilities:
  - one-shot job status
  - wait/poll until terminal state
  - saved job records for later automation

KIE's API catalog is broader than this CLI. The goal is to keep this repo accurate for the implemented workflows while making it easy for contributors to add more endpoints from the official docs.

## Installation

Requirements:

- Python 3.11+
- A KIE API key

Set up a local environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` and set:

```env
KIE_API_KEY=your_kie_api_key
KIE_BASE_URL=https://api.kie.ai
KIE_UPLOAD_BASE_URL=https://kieai.redpandaai.co
```

Do not commit `.env`. The included `.gitignore` is configured to keep local secrets, generated outputs, Python caches, and virtual environments out of Git.

## CLI Usage

The installed console command is:

```bash
kie-cli
```

Most commands support `--json` for machine-readable output and `--dry-run` for payload inspection without making a network request.

Image generation:

```bash
kie-cli image gpt-image-2 --prompt "A cinematic night city poster" --json
kie-cli image nano-banana-pro --prompt-file ./prompt.txt --image ./reference.png --json
```

Video generation:

```bash
kie-cli video grok --prompt "A neon corridor dolly shot" --json
kie-cli video veo3 --prompt-file ./prompt.txt --veo-model veo3_fast --json
```

Chat completion:

```bash
kie-cli llm gpt-5-2 --prompt "Describe this image" --image ./image.png --json
kie-cli gemini gemini-3-pro --prompt "Analyze this reference" --image ./image.png --json
```

Suno:

```bash
kie-cli suno music --prompt "A dreamy synth-pop song" --json
kie-cli suno lyrics --prompt "Hopeful indie chorus about sunrise" --json
kie-cli suno sounds --prompt "Soft rain on a metal roof" --json
```

Async job polling:

```bash
kie-cli image gpt-image-2 \
  --prompt "A polished product render" \
  --save-job outputs/jobs/product-render.json \
  --json

kie-cli wait --job-file outputs/jobs/product-render.json --poll-interval 5 --timeout 900 --json
```

## Development

Run unit tests:

```bash
.venv/bin/python -m pytest -q
```

Run gated live integration tests only when you intentionally want to spend KIE credits:

```bash
RUN_KIE_LIVE_TESTS=1 .venv/bin/python -m pytest tests/integration -q
```

Useful live-test environment variables:

- `KIE_LIVE_SCOPE=llm|gemini|image|video|suno|generation|all`
- `KIE_LIVE_POLL_INTERVAL=10`
- `KIE_LIVE_TIMEOUT=900`
- `KIE_SUNO_CALLBACK_URL=https://your-callback.example/path`

Live test outputs are written under `outputs/`, which is ignored by Git.

## Project Layout

```text
src/kie_cli/             CLI implementation
tests/                   Unit tests
tests/integration/       Opt-in live KIE API tests
docs/kie-ai/raw/         Local mirror of KIE docs used for implementation reference
docs/kie-cli/            Project documentation
docs/journals/           ClineFlow task journals
scripts/                 Utility scripts, including KIE docs downloader
```

Key implementation modules:

- `cli.py` defines command arguments and dispatch.
- `client.py` performs authenticated KIE HTTP calls.
- `payloads.py` builds provider-specific request payloads.
- `routes.py` maps async models to submit/status endpoints.
- `status.py` normalizes provider responses.
- `polling.py` implements wait-until-terminal behavior.
- `media.py` resolves local media uploads and remote URLs.

## Contributing

Contributions are welcome, especially changes that expand or refresh coverage from the official KIE docs:

1. Pick an endpoint or model from [docs.kie.ai](https://docs.kie.ai/).
2. Add or update payload builders, routes, status normalization, and CLI flags as needed.
3. Add focused unit tests for payload shape and CLI behavior.
4. Add gated live-test coverage when the endpoint needs real async validation.
5. Update `README.md` or `docs/kie-cli/comprehensive-guide.md` so future contributors can follow the contract.

Please keep secrets out of commits. Use `.env.example` for documented variable names and `.env` for local values.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution workflow.

## Security Notes

- Never expose `KIE_API_KEY` in frontend code, screenshots, logs, commits, or issue reports.
- Use `--dry-run` when reviewing request payloads before live calls.
- Treat generated media URLs and live-test output as local artifacts unless you intentionally publish them.
- Before pushing a new public repository, run a secret scan and verify that `.env`, `.venv`, caches, and `outputs/` are not staged.

## License

MIT. See [LICENSE](LICENSE).
