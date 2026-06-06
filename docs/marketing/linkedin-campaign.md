# LinkedIn Campaign: KIE API Python + MCP

GitHub link for every post:

https://github.com/hassanvfx/kie-api-python

Campaign positioning:

After a year working with KIE.AI, I open sourced `kie-api-python`: a Python CLI and MCP server that gives agents fast, safe access to KIE image, video, music, chat, upload, and async job workflows.

Core promise:

Give any agent instant creative API access without hand-wiring endpoints, payloads, polling, uploads, callbacks, or token handling from scratch.

Visual system for all images:

- cinematic dark graphite background
- glassy command terminal and agent workflow panels
- cyan and emerald accent lighting
- subtle KIE/API/MCP/network motifs
- one human principal-engineer presence or hand only when useful
- clean composition, high contrast, premium open-source launch feel
- no readable fake UI text unless specified
- no logos except a small abstract GitHub-style code repository symbol
- 16:9 aspect ratio

Suggested posting schedule:

| Week | Day | Post | Topic |
|---|---|---:|---|
| Week 1 | Monday | 1 | Launch |
| Week 1 | Tuesday | 2 | The Convenience Pitch |
| Week 1 | Wednesday | 3 | CLI + MCP |
| Week 1 | Thursday | 4 | Dry Run First |
| Week 2 | Monday | 5 | Image Generation Example |
| Week 2 | Tuesday | 6 | Song Generation Example |
| Week 2 | Wednesday | 7 | Async Polling |
| Week 2 | Thursday | 8 | Upload-First Media |
| Week 3 | Monday | 9 | MCP Resources |
| Week 3 | Tuesday | 10 | Token Safety |
| Week 3 | Wednesday | 11 | Contributor Angle |
| Week 3 | Thursday | 12 | Real MCP Test |
| Week 4 | Monday | 13 | Product Render Agent |
| Week 4 | Tuesday | 14 | Why Principal Engineers Should Care |
| Week 4 | Wednesday | 15 | Contributor CTA |

---

## Week 1: Convenience First

Goal: make the tool feel immediately useful before diving into implementation details.

### Post 1: Launch

Scheduled Day: Monday, Week 1

Text:

I spent the last year working with KIE.AI workflows.

Today I open sourced the tool I wish every agent had by default:

`kie-api-python`

It is both:

- a Python CLI for humans and scripts
- an MCP server for agents

The goal is simple:

Give agents instant access to KIE image, video, music, chat, upload, and async polling workflows without making every team rebuild the same API glue.

Dry-run first. Token-safe by default. Async jobs handled. Local uploads handled. MCP resources included.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a cinematic 16:9 editorial tech launch image in a dark graphite workspace. Show a principal engineer's desk with a glowing glass terminal labeled only with abstract code shapes, an agent network diagram flowing into creative outputs: image frame, video strip, music waveform, and chat bubble icons. Use cyan and emerald rim lighting, premium open-source launch aesthetic, crisp high contrast, shallow depth of field. Include a small abstract repository symbol, no readable fake UI text, no brand logos, no clutter.

### Post 2: The Convenience Pitch

Scheduled Day: Tuesday, Week 1

Text:

The annoying part of creative AI APIs is rarely the first request.

It is everything around it:

- upload local media
- build provider-specific payloads
- choose the right routed model
- save job IDs
- poll async status
- normalize outputs
- avoid leaking tokens
- document the contract for future agents

`kie-api-python` wraps that into a CLI and an MCP server.

So your agent can go from idea to KIE job without rediscovering the plumbing.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic diagram-style image in the same dark graphite, cyan, and emerald visual style. Show a messy tangle of API tasks on the left represented by abstract nodes for upload, payload, polling, callbacks, token safety, and outputs, transforming into a clean single glowing pipeline on the right labeled visually with icons only. Premium principal-engineer tool aesthetic, glass panels, high contrast, no readable text, no logos.

### Post 3: CLI + MCP

Scheduled Day: Wednesday, Week 1

Text:

I did not want this to be only a CLI.

CLIs are great for humans.
MCP is where this becomes useful for agents.

`kie-api-python` ships:

- `kie-cli` for terminal workflows
- `kie-mcp` for agent-native workflows
- package-local MCP resources
- dry-run-first tools
- async polling tools
- prompt helpers

That means an agent can inspect the supported models, dry-run a payload, submit a job, and poll it to completion through the same project.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 split-but-unified editorial tech image. Left side: a sleek command-line terminal represented by glass panels and code glyphs. Right side: an agent interface represented by connected nodes and tool cards. Both flow into the same glowing KIE creative API core in the center. Dark graphite background, cyan and emerald lighting, premium open-source engineering style, no readable UI text, no logos.

### Post 4: Dry Run First

Scheduled Day: Thursday, Week 1

Text:

One design choice I care about:

Every expensive MCP submit tool defaults to `dry_run=true`.

Agents should be able to inspect:

- model routing
- payload shape
- uploaded media handling
- callbacks
- job-save paths

before making a live API call.

This matters because creative APIs can spend credits, create hosted media, and produce async state that needs to be tracked.

Agent tools should be powerful.
They should also be careful.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic safety-first agent image. Show an AI agent workflow pausing at a glowing checkpoint labeled visually with a shield/checkmark icon before flowing into creative API outputs. Include abstract payload cards, a credit meter icon, and a job polling loop. Dark graphite, cyan and emerald accents, premium engineering aesthetic, high clarity, no readable fake text, no logos.

---

## Week 2: Show Specific Workflows

Goal: demonstrate concrete implementations while reminding people the same interface handles other media types.

### Post 5: Image Generation Example

Scheduled Day: Monday, Week 2

Text:

Example workflow:

Ask an agent to generate an image with KIE.

The agent can:

1. call `kie_generate_image` with `dry_run=true`
2. inspect the payload
3. submit with `dry_run=false`
4. receive a `jobId`
5. call `kie_wait_for_job`
6. return the generated image URL

I tested this through the real MCP server.

The image job succeeded.

The same MCP server also supports video, chat, upload, Suno music, lyrics, sounds, and job status tools.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic image-generation workflow scene. Show an agent node calling a glowing image-generation tool, then an async job loop, then a polished product image frame emerging at the end. Keep the same dark graphite, cyan, and emerald editorial style. Include subtle glass cards and a progress ring. No readable fake text, no logos, premium open-source engineering launch feel.

### Post 6: Song Generation Example

Scheduled Day: Tuesday, Week 2

Text:

I also tested Suno music generation through MCP.

The useful lesson:

The agent did not just submit a prompt.

It had to deal with real provider behavior:

- use a provider model
- include a callback URL
- save the job
- poll the routed `suno-music` status path
- return audio outputs

That is exactly the kind of operational detail I want agents to stop reimplementing from scratch.

`kie-api-python` handles the workflow.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic music-generation workflow image in the same style. Show an agent network sending a prompt into a glowing audio pipeline, with waveform arcs, album-art tiles, and async polling loops. Include subtle callback-route motif as connected nodes. Dark graphite background, cyan and emerald lighting, premium technical look, no readable text, no brand logos.

### Post 7: Async Polling

Scheduled Day: Wednesday, Week 2

Text:

Async APIs are where quick prototypes become fragile.

For KIE workflows, a submit call is often only the first step.

You still need:

- the job ID
- the routed model
- the right status endpoint
- terminal-state normalization
- timeout behavior
- output URL extraction

`kie-api-python` keeps that contract in one place.

For agents, this becomes `kie_wait_for_job`.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 premium technical image focused on async job polling. Show a glowing circular polling loop around a job ID token, with multiple provider endpoint paths converging into normalized output cards. Dark graphite, glass UI panels, cyan/emerald highlights, crisp diagrammatic composition, no readable text, no logos.

### Post 8: Upload-First Media

Scheduled Day: Thursday, Week 2

Text:

A small detail that makes agent workflows much nicer:

Local media references are upload-first.

An agent can receive:

`./reference.png`

and the tool handles:

- local file validation
- upload to KIE temporary storage
- resolving the remote URL
- inserting that URL into the final payload

That matters for image-to-image, image-to-video, and multimodal chat workflows.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic upload-first media workflow image. Show a local image file tile transforming into a secure cloud URL node, then flowing into image, video, and chat tool cards. Use the campaign style: dark graphite workspace, glass panels, cyan and emerald lighting, premium engineering quality, no readable fake text, no logos.

---

## Week 3: Agent-Native Architecture

Goal: explain why this is built for agents, not just wrapped for demos.

### Post 9: MCP Resources

Scheduled Day: Monday, Week 3

Text:

The MCP server does not only expose tools.

It also exposes resources.

Agents can read:

- supported models
- tool contracts
- quickstart guidance
- contribution instructions
- repo docs

The important bit:

The core agent resources live inside the Python package.

No GitHub Raw dependency.
No version drift.
No network fetch required after install.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic image of an agent reading package-local resources. Show glowing resource cards stored inside a code package cube, connected to tool nodes. Use dark graphite, cyan/emerald highlights, clean glassmorphism, high contrast, premium open-source engineering aesthetic, no readable text, no logos.

### Post 10: Token Safety

Scheduled Day: Tuesday, Week 3

Text:

Agent tools need boring security details.

For this project:

- `.env.example` is committed
- `.env` is ignored
- example MCP configs use placeholders only
- real keys live in local `.env` or private MCP client config
- outputs are ignored
- generated media URLs are treated as local artifacts unless intentionally shared

The goal is not just "make agents powerful."

The goal is "make agents useful without making them reckless."

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic token-safety image. Show a glowing key locked inside a private local environment vault, while an agent workflow accesses tools without exposing the key. Include shield icons, ignored output folders as abstract dark tiles, and clean secure pipelines. Dark graphite, cyan and emerald accents, premium engineering style, no readable text, no logos.

### Post 11: Contributor Angle

Scheduled Day: Wednesday, Week 3

Text:

KIE's API surface is bigger than this first implementation.

That is why the repo is designed for contributors.

To add a new endpoint:

1. read the KIE docs
2. add a payload builder
3. add route/status handling if async
4. expose CLI and MCP dry-run support
5. add tests
6. update the agent resources

I want this to become a living agent-access layer for KIE workflows.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic open-source contributor image. Show multiple abstract developer nodes adding new endpoint cards into a shared MCP/CLI framework. Include clean modular blocks for payload, route, status, tests, docs, resources. Dark graphite background, cyan/emerald lighting, premium collaborative engineering style, no readable fake text, no logos.

### Post 12: Real MCP Test

Scheduled Day: Thursday, Week 3

Text:

This was not just wired theoretically.

I tested the real MCP path:

MCP client
to `kie-mcp`
to KIE API
to async polling
to generated media URLs

Validated:

- image generation
- Suno music generation
- chat completion
- MCP resources
- MCP prompts
- dry-run tool calls

That is the difference between a wrapper and a usable agent tool.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic validation image showing a real end-to-end MCP pipeline. Include connected stages from MCP client to server to API to polling to generated outputs. Add checkmarks as abstract icons, not text. Dark graphite, cyan and emerald highlights, glass panels, premium launch aesthetic, no readable fake UI, no logos.

---

## Week 4: Adoption And Specific Implementation

Goal: show a random concrete implementation, then pull back to the wider value.

### Post 13: Specific Implementation - Product Render Agent

Scheduled Day: Monday, Week 4

Text:

Specific implementation idea:

Build a product-render agent.

Give it:

- a short creative brief
- optional reference image
- brand constraints
- output aspect ratio

It can use `kie-api-python` to:

1. upload the reference image
2. dry-run the image payload
3. submit a KIE image job
4. poll until complete
5. return the final render URL

The same repo can also support the next step:

turn the render into video, generate a soundtrack, or ask chat to write launch copy.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic product-render agent scene. Show a luxury glass perfume bottle product render being generated from a brief and reference image, with an agent workflow pipeline beside it. Include subtle downstream icons for video, music, and copywriting. Dark graphite studio, cyan and emerald rim lights, premium commercial photography mixed with technical glass panels, no readable text, no logos.

### Post 14: Why Principal Engineers Should Care

Scheduled Day: Tuesday, Week 4

Text:

As a principal engineer, I care about tools that remove repeated integration work.

This repo is not trying to be magical.

It is trying to make the boring parts reliable:

- parameter contracts
- payload construction
- routed models
- upload handling
- async polling
- normalized outputs
- token safety
- agent-readable docs

That is the part every serious agent workflow eventually needs.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic principal-engineer architecture image. Show a calm senior engineer reviewing a clean modular system map of CLI, MCP, payloads, routes, polling, resources, and tests. Dark graphite office, cyan/emerald highlights, premium thoughtful engineering aesthetic, no readable UI text, no logos.

### Post 15: Contributor CTA

Scheduled Day: Wednesday, Week 4

Text:

If you are building agents that need creative APIs, this is for you.

If you are using KIE.AI and want a faster path from agent intent to real jobs, this is for you.

If you want to contribute support for more KIE endpoints, even better.

The repo includes:

- CLI
- MCP server
- docs
- tests
- live validation notes
- token-safety guidance
- package-local agent resources

Open source is how this gets better.

GitHub:
https://github.com/hassanvfx/kie-api-python

Image prompt:

Create a 16:9 cinematic final campaign image. Show an open-source repository as a glowing launchpad where multiple agent workflows branch into image, video, music, chat, and upload outputs. Use the same dark graphite background, cyan and emerald light, glass panels, high contrast, premium engineering launch style. Add a subtle invitation feeling with connected contributor nodes. No readable fake text, no brand logos.
