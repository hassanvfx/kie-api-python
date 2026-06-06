# LinkedIn Campaign: KIE API Python + MCP

GitHub link for every post:

https://github.com/hassanvfx/kie-api-python

Campaign positioning:

After a year working with KIE.AI, I open sourced `kie-api-python`: a Python CLI and MCP server that gives agents fast, safe access to KIE image, video, music, chat, upload, and async job workflows.

Core promise:

Give any agent instant creative API access without hand-wiring endpoints, payloads, polling, uploads, callbacks, or token handling from scratch.

Visual system for all images:

- viral LinkedIn deck-slide style, not wallpaper
- 16:9 presentation slide / technical carousel cover
- matte graphite or near-black background with subtle grid
- cyan and acid-emerald gradients
- crisp glass panels, isometric/vector icons, and clean arrows
- bold minimal typography with only the requested slide title
- strong margins, clear hierarchy, high contrast
- Figma/Keynote-quality principal-engineer launch aesthetic
- persistent brand lockup on every slide: `KIE.AI all-in-one agent-first MCP/CLI`
- byline on every slide: `by Hassan Uriostegui`
- no fake UI text beyond the slide title, brand lockup, and byline; no extra logos or clutter

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

### Monday (Week 1) - Post 1: Launch

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Agents, meet KIE". Create a launch slide with a central glowing MCP hub connecting to five clean icon tiles: image, video, music, chat, and upload. Add a small repository cube in one corner. The slide should feel like a polished open-source launch keynote cover.
```

### Tuesday (Week 1) - Post 2: The Convenience Pitch

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Stop rebuilding API glue". Create a before/after slide: left side shows tangled abstract integration nodes, right side shows one clean pipeline into KIE workflows. Use visual icons for upload, payloads, polling, callbacks, token safety, and outputs; no labels except the title.
```

### Wednesday (Week 1) - Post 3: CLI + MCP

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "CLI for humans. MCP for agents.". Create a split architecture slide: left panel is a terminal-shaped block, right panel is an agent-tool graph, both converging into a shared KIE API core. Make it clean, symmetrical, and executive-demo ready.
```

### Thursday (Week 1) - Post 4: Dry Run First

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Dry-run before spend". Create a safety-checkpoint slide showing an agent workflow paused at a glowing shield/check node before entering live API execution. Include small abstract credit meter, payload card, and polling loop icons.
```


---

## Week 2: Show Specific Workflows

Goal: demonstrate concrete implementations while reminding people the same interface handles other media types.

### Monday (Week 2) - Post 5: Image Generation Example

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Image jobs through MCP". Create a process slide with six numbered-looking visual stages but no readable numbers: dry-run, inspect payload, submit, job ID, wait, generated image. End with a polished image frame tile. Keep it clean and diagrammatic.
```

### Tuesday (Week 2) - Post 6: Song Generation Example

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Music jobs need orchestration". Create a music workflow slide with a prompt card flowing through callback, provider model, saved job, polling, and MP3 output icons. Use waveform geometry and album-art tiles in the same deck style.
```

### Wednesday (Week 2) - Post 7: Async Polling

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Async is the real work". Create a technical slide centered on a luminous polling loop around a job token. Multiple endpoint paths converge into normalized output cards. Make it feel like an elegant systems diagram.
```

### Thursday (Week 2) - Post 8: Upload-First Media

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Local files become agent-ready URLs". Create a slide showing a local file tile transforming into a secure URL node, then branching into image-to-image, image-to-video, and multimodal chat icons. Keep the transformation visually obvious.
```


---

## Week 3: Agent-Native Architecture

Goal: explain why this is built for agents, not just wrapped for demos.

### Monday (Week 3) - Post 9: MCP Resources

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Tools are not enough". Create a slide showing an MCP server exposing both tool cards and resource cards. Package-local resources should appear as cards inside a Python package cube, connected to an agent node.
```

### Tuesday (Week 3) - Post 10: Token Safety

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Powerful agents need boring security". Create a security slide with a private .env vault icon, placeholder config cards, ignored outputs, and an agent using tools without seeing the key. Strong shield motif, clean and serious, still visually cool.
```

### Wednesday (Week 3) - Post 11: Contributor Angle

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Add endpoints. Keep the contract.". Create a contributor workflow slide with modular blocks for docs, payload builder, routing, status normalization, CLI, MCP, tests, and resources snapping into a shared framework.
```

### Thursday (Week 3) - Post 12: Real MCP Test

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Tested end to end". Create an end-to-end validation slide: MCP client to kie-mcp to KIE API to async polling to generated media outputs. Use check icons and clean pipeline arrows, no extra text.
```


---

## Week 4: Adoption And Specific Implementation

Goal: show a random concrete implementation, then pull back to the wider value.

### Monday (Week 4) - Post 13: Specific Implementation - Product Render Agent

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Build a product-render agent". Create a product-render agent slide showing a premium perfume bottle render tile generated from a brief card and reference image card. Show downstream branches to video, soundtrack, and launch copy icons.
```

### Tuesday (Week 4) - Post 14: Why Principal Engineers Should Care

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Reduce repeated integration work". Create a principal-engineer architecture slide showing clean system blocks for CLI, MCP, payloads, routes, polling, docs, resources, and tests. Calm, authoritative, minimal, boardroom-ready.
```

### Wednesday (Week 4) - Post 15: Contributor CTA

LinkedIn copy:

```text
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
```

Image prompt:

```text
Viral LinkedIn engineering deck-slide style, 16:9 widescreen. Matte graphite/near-black background, subtle grid, crisp glass panels, cyan and acid-emerald gradients, sharp Figma/Keynote-quality layout, high-end principal-engineer aesthetic. Use bold minimal typography with only the exact slide title requested plus a persistent brand lockup reading "KIE.AI all-in-one agent-first MCP/CLI" and a small byline reading "by Hassan Uriostegui". Put the brand lockup in the lower-left footer and the byline in the lower-right footer on every slide. No other readable words, no fake UI text, no extra logos. Use simple isometric/vector icons, clean margins, strong hierarchy, designed like slide 1 of a premium technical carousel, not a cinematic photo. Slide title text: "Open-source agent access for KIE". Create a final call-to-action slide with an open-source repository launchpad branching into image, video, music, chat, upload, and contributor nodes. Make it feel like the closing slide of a high-energy technical launch deck.
```
