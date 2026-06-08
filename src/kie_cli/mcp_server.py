"""MCP server for agent-native KIE workflows."""

from __future__ import annotations

from dataclasses import asdict
from importlib import resources
from pathlib import Path
from typing import Any

from .client import KieClient, KieUploadClient
from .config import load_config
from .jobs import build_job_record, write_job_record
from .llm import (
    GEMINI_3_PRO,
    GPT_5_2,
    build_gemini_vision_payload,
    build_gpt_5_2_chat_payload,
    normalize_chat_completion,
)
from .media import resolve_media_inputs
from .payloads import (
    SUNO_LYRICS_MODEL,
    SUNO_MUSIC_MODEL,
    SUNO_SOUNDS_MODEL,
    build_gpt_image_2_payload,
    build_grok_video_payload,
    build_nano_banana_pro_payload,
    build_seedance_payload,
    build_suno_lyrics_payload,
    build_suno_music_payload,
    build_suno_sounds_payload,
    build_veo_payload,
)
from .polling import get_status_once, poll_until_complete
from .status import (
    normalize_market_status,
    normalize_submit,
    normalize_suno_lyrics_status,
    normalize_suno_music_status,
    normalize_veo_status,
)


RESOURCE_FILES = {
    "kie://docs/agent-quickstart": "agent_quickstart.md",
    "kie://models/supported": "supported_models.json",
    "kie://tools/contracts": "tool_contracts.json",
    "kie://contributing/add-endpoint": "contribution_guide.md",
}


def main() -> None:
    server = create_mcp_server()
    server.run()


def create_mcp_server() -> Any:
    """Create the FastMCP server.

    The MCP SDK is an optional dependency so the normal CLI remains usable
    without installing agent-server support.
    """

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - depends on optional package.
        raise RuntimeError(
            "The MCP SDK is not installed. Install with: "
            'python -m pip install -e ".[mcp]"'
        ) from exc

    server = FastMCP("kie-api")

    server.tool()(kie_upload_file)
    server.tool()(kie_generate_image)
    server.tool()(kie_generate_video)
    server.tool()(kie_chat_completion)
    server.tool()(kie_suno_music)
    server.tool()(kie_suno_lyrics)
    server.tool()(kie_suno_sounds)
    server.tool()(kie_get_job_status)
    server.tool()(kie_wait_for_job)

    server.resource("kie://docs/agent-quickstart")(resource_agent_quickstart)
    server.resource("kie://models/supported")(resource_supported_models)
    server.resource("kie://tools/contracts")(resource_tool_contracts)
    server.resource("kie://contributing/add-endpoint")(resource_add_endpoint)
    server.resource("kie://docs/comprehensive-guide")(resource_comprehensive_guide)
    server.resource("kie://docs/kie-ai/manifest")(resource_kie_docs_manifest)

    server.prompt()(kie_image_prompt_builder)
    server.prompt()(kie_video_prompt_builder)
    server.prompt()(kie_debug_failed_job)
    server.prompt()(kie_add_new_endpoint_contribution_plan)

    return server


def kie_upload_file(
    file_path: str,
    upload_path: str = "kie-mcp/uploads",
    file_name: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Upload a local file to KIE temporary storage."""

    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "file": file_path,
            "uploadPath": upload_path,
            "fileName": file_name,
            "uploaded": False,
        }

    config = load_config()
    upload = KieUploadClient(config).upload_file(
        file_path,
        upload_path=upload_path,
        file_name=file_name,
    )
    return {
        "ok": True,
        "downloadUrl": upload["downloadUrl"],
        "fileName": upload.get("fileName"),
        "filePath": upload.get("filePath"),
        "mimeType": upload.get("mimeType"),
        "fileSize": upload.get("fileSize"),
        "expiresInDays": 3,
    }


def kie_generate_image(
    model: str,
    prompt: str,
    image: list[str] | None = None,
    aspect_ratio: str | None = None,
    resolution: str = "1K",
    output_format: str = "png",
    callback_url: str | None = None,
    upload_path: str = "kie-mcp/images",
    save_job: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Submit or dry-run a KIE image generation task."""

    config = load_config()
    uploader = None if dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        image or [],
        kind="image",
        uploader=uploader,
        upload_path=upload_path,
        dry_run=dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]

    if model == "nano-banana-pro":
        payload = build_nano_banana_pro_payload(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=aspect_ratio or "1:1",
            resolution=resolution,
            output_format=output_format,
            callback_url=callback_url,
        )
        resolved_model = "nano-banana-pro"
    elif model == "gpt-image-2":
        payload = build_gpt_image_2_payload(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=aspect_ratio or "auto",
            resolution=resolution,
            callback_url=callback_url,
        )
        resolved_model = payload["model"]
    else:
        raise ValueError("Unsupported image model. Use 'nano-banana-pro' or 'gpt-image-2'.")

    if dry_run:
        return _dry_run_result("market", resolved_model, payload, resolved)

    response = KieClient(config).create_market_task(payload)
    result = normalize_submit(response, model=resolved_model)
    return _with_job_record(
        result,
        save_job=save_job,
        payload=payload,
        resolved_media=[asdict(item) for item in resolved],
        raw=response,
    )


def kie_generate_video(
    model: str,
    prompt: str,
    image: list[str] | None = None,
    aspect_ratio: str | None = None,
    mode: str = "normal",
    duration: int | None = None,
    resolution: str | None = None,
    nsfw_checker: bool = False,
    veo_model: str = "veo3_fast",
    seedance_model: str = "seedance-2-fast",
    generation_type: str | None = None,
    disable_translation: bool = False,
    watermark: str | None = None,
    first_frame: str | None = None,
    last_frame: str | None = None,
    reference_image: list[str] | None = None,
    reference_video: list[str] | None = None,
    reference_audio: list[str] | None = None,
    generate_audio: bool = False,
    web_search: bool = False,
    fixed_lens: bool = False,
    callback_url: str | None = None,
    upload_path: str = "kie-mcp/videos",
    save_job: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Submit or dry-run a KIE video generation task."""

    config = load_config()
    uploader = None if dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        image or [],
        kind="image",
        uploader=uploader,
        upload_path=upload_path,
        dry_run=dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]
    resolved_media = resolved

    if model == "grok":
        payload = build_grok_video_payload(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=aspect_ratio or ("16:9" if image_urls else "2:3"),
            mode=mode,
            duration=duration or 6,
            resolution=resolution or "480p",
            nsfw_checker=nsfw_checker,
            callback_url=callback_url,
        )
        route = "market"
        resolved_model = payload["model"]
    elif model == "veo3":
        payload = build_veo_payload(
            prompt=prompt,
            image_urls=image_urls,
            model=veo_model,
            generation_type=generation_type,
            aspect_ratio=aspect_ratio or "16:9",
            resolution=resolution or "720p",
            enable_translation=not disable_translation,
            watermark=watermark,
            callback_url=callback_url,
        )
        route = "veo"
        resolved_model = veo_model
    elif model == "seedance":
        first_frame_resolved = resolve_media_inputs(
            [first_frame] if first_frame else [],
            kind="image",
            uploader=uploader,
            upload_path=upload_path,
            dry_run=dry_run,
        )
        last_frame_resolved = resolve_media_inputs(
            [last_frame] if last_frame else [],
            kind="image",
            uploader=uploader,
            upload_path=upload_path,
            dry_run=dry_run,
        )
        reference_images = resolve_media_inputs(
            reference_image or [],
            kind="image",
            uploader=uploader,
            upload_path=upload_path,
            dry_run=dry_run,
        )
        reference_videos = resolve_media_inputs(
            reference_video or [],
            kind="video",
            uploader=uploader,
            upload_path=upload_path,
            dry_run=dry_run,
        )
        reference_audios = resolve_media_inputs(
            reference_audio or [],
            kind="audio",
            uploader=uploader,
            upload_path=upload_path,
            dry_run=dry_run,
        )
        resolved_media = [
            *resolved,
            *first_frame_resolved,
            *last_frame_resolved,
            *reference_images,
            *reference_videos,
            *reference_audios,
        ]
        payload = build_seedance_payload(
            prompt=prompt,
            model=seedance_model,
            input_urls=image_urls,
            first_frame_url=first_frame_resolved[0].resolved_url if first_frame_resolved else None,
            last_frame_url=last_frame_resolved[0].resolved_url if last_frame_resolved else None,
            reference_image_urls=[item.resolved_url for item in reference_images],
            reference_video_urls=[item.resolved_url for item in reference_videos],
            reference_audio_urls=[item.resolved_url for item in reference_audios],
            aspect_ratio=aspect_ratio or "16:9",
            resolution=resolution or "720p",
            duration=duration or 5,
            fixed_lens=fixed_lens,
            generate_audio=generate_audio,
            web_search=web_search,
            nsfw_checker=nsfw_checker,
            callback_url=callback_url,
        )
        route = "market"
        resolved_model = payload["model"]
    else:
        raise ValueError("Unsupported video model. Use 'grok', 'veo3', or 'seedance'.")

    if dry_run:
        return _dry_run_result(route, resolved_model, payload, resolved_media)

    client = KieClient(config)
    response = client.create_veo_task(payload) if route == "veo" else client.create_market_task(payload)
    result = normalize_submit(response, model=resolved_model)
    return _with_job_record(
        result,
        save_job=save_job,
        payload=payload,
        resolved_media=[asdict(item) for item in resolved_media],
        raw=response,
    )


def kie_chat_completion(
    model: str,
    prompt: str,
    image: list[str] | None = None,
    reasoning_effort: str = "high",
    include_thoughts: bool = False,
    web_search: bool = False,
    max_completion_tokens: int | None = None,
    request_timeout: float = 60,
    upload_path: str = "kie-mcp/chat",
    dry_run: bool = True,
) -> dict[str, Any]:
    """Run or dry-run a KIE chat completion."""

    config = load_config()
    uploader = None if dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        image or [],
        kind="image",
        uploader=uploader,
        upload_path=upload_path,
        dry_run=dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]

    if model == GPT_5_2:
        payload = build_gpt_5_2_chat_payload(
            prompt=prompt,
            image_urls=image_urls,
            reasoning_effort=reasoning_effort,
            web_search=web_search,
            max_completion_tokens=max_completion_tokens,
        )
        if dry_run:
            result = _dry_run_result("chat_completions", model, payload, resolved)
            result["kind"] = "chat_completions"
            return result
        response = KieClient(config, request_timeout=request_timeout).create_gpt_5_2_chat_completion(payload)
    elif model == GEMINI_3_PRO:
        payload = build_gemini_vision_payload(
            prompt=prompt,
            image_urls=image_urls,
            reasoning_effort=reasoning_effort,
            include_thoughts=include_thoughts,
            web_search=web_search,
        )
        if dry_run:
            return _dry_run_result("chat_completions", model, payload, resolved)
        response = KieClient(config, request_timeout=request_timeout).create_gemini_3_pro_chat_completion(payload)
    else:
        raise ValueError("Unsupported chat model. Use 'gpt-5-2' or 'gemini-3-pro'.")

    result = normalize_chat_completion(response, model=model)
    result["resolvedMedia"] = [asdict(item) for item in resolved]
    return result


def kie_suno_music(
    prompt: str,
    custom_mode: bool = False,
    instrumental: bool = False,
    model: str | None = None,
    style: str | None = None,
    title: str | None = None,
    negative_tags: str | None = None,
    callback_url: str | None = None,
    save_job: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Submit or dry-run a Suno music task."""

    payload = build_suno_music_payload(
        prompt=prompt,
        custom_mode=custom_mode,
        instrumental=instrumental,
        model=model,
        style=style,
        title=title,
        negative_tags=negative_tags,
        callback_url=callback_url,
    )
    if dry_run:
        return _dry_run_result("suno_music", SUNO_MUSIC_MODEL, payload, [])

    config = load_config()
    response = KieClient(config).create_suno_music_task(payload)
    result = normalize_submit(response, model=SUNO_MUSIC_MODEL)
    return _with_job_record(result, save_job=save_job, payload=payload, resolved_media=[], raw=response)


def kie_suno_lyrics(
    prompt: str,
    callback_url: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Submit or dry-run a Suno lyrics task."""

    payload = build_suno_lyrics_payload(prompt=prompt, callback_url=callback_url)
    if dry_run:
        return _dry_run_result("suno_lyrics", SUNO_LYRICS_MODEL, payload, [])

    config = load_config()
    response = KieClient(config).create_suno_lyrics_task(payload)
    return normalize_submit(response, model=SUNO_LYRICS_MODEL)


def kie_suno_sounds(
    prompt: str,
    model: str | None = None,
    sound_loop: bool = False,
    sound_tempo: int | None = None,
    sound_key: str | None = None,
    grab_lyrics: bool = False,
    callback_url: str | None = None,
    save_job: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Submit or dry-run a Suno sounds task."""

    payload = build_suno_sounds_payload(
        prompt=prompt,
        model=model,
        sound_loop=sound_loop,
        sound_tempo=sound_tempo,
        sound_key=sound_key,
        grab_lyrics=grab_lyrics,
        callback_url=callback_url,
    )
    if dry_run:
        return _dry_run_result("suno_music", SUNO_SOUNDS_MODEL, payload, [])

    config = load_config()
    response = KieClient(config).create_suno_sounds_task(payload)
    result = normalize_submit(response, model=SUNO_SOUNDS_MODEL)
    return _with_job_record(result, save_job=save_job, payload=payload, resolved_media=[], raw=response)


def kie_get_job_status(job_id: str, model: str) -> dict[str, Any]:
    """Read one async job status using model-routed KIE endpoints."""

    config = load_config()
    return get_status_once(
        client=KieClient(config),
        job_id=job_id,
        model=model,
        market_normalizer=normalize_market_status,
        veo_normalizer=normalize_veo_status,
        suno_music_normalizer=normalize_suno_music_status,
        suno_lyrics_normalizer=normalize_suno_lyrics_status,
    )


def kie_wait_for_job(
    job_id: str,
    model: str,
    poll_interval: float = 5.0,
    timeout: float = 900.0,
) -> dict[str, Any]:
    """Poll an async KIE job until completion, failure, or timeout."""

    config = load_config()
    return poll_until_complete(
        client=KieClient(config),
        job_id=job_id,
        model=model,
        market_normalizer=normalize_market_status,
        veo_normalizer=normalize_veo_status,
        suno_music_normalizer=normalize_suno_music_status,
        suno_lyrics_normalizer=normalize_suno_lyrics_status,
        poll_interval=poll_interval,
        timeout=timeout,
    )


def resource_agent_quickstart() -> str:
    return read_package_resource("agent_quickstart.md")


def resource_supported_models() -> str:
    return read_package_resource("supported_models.json")


def resource_tool_contracts() -> str:
    return read_package_resource("tool_contracts.json")


def resource_add_endpoint() -> str:
    return read_package_resource("contribution_guide.md")


def resource_comprehensive_guide() -> str:
    return read_repo_doc(Path("docs/kie-cli/comprehensive-guide.md"))


def resource_kie_docs_manifest() -> str:
    return read_repo_doc(Path("docs/kie-ai/manifest.json"))


def kie_image_prompt_builder(subject: str, style: str = "cinematic", aspect_ratio: str = "1:1") -> str:
    """Build a concise image-generation prompt for KIE image models."""

    return (
        f"Create a {style} image of {subject}. "
        f"Use aspect ratio {aspect_ratio}. "
        "Include clear composition, lighting, subject detail, and a production-ready finish."
    )


def kie_video_prompt_builder(subject: str, camera_motion: str = "slow dolly forward", mood: str = "cinematic") -> str:
    """Build a concise video-generation prompt for KIE video models."""

    return (
        f"Create a {mood} video of {subject}. "
        f"Camera motion: {camera_motion}. "
        "Describe subject action, scene continuity, lighting, and temporal changes clearly."
    )


def kie_debug_failed_job(job_id: str, model: str, error_message: str = "") -> str:
    """Build an agent checklist for debugging a failed KIE job."""

    details = f" Job error message: {error_message}" if error_message else ""
    return (
        f"Debug KIE job {job_id} for model {model}.{details}\n"
        "1. Fetch job status using kie_get_job_status.\n"
        "2. Check provider fail code/message and normalized status.\n"
        "3. Compare submitted payload against kie://tools/contracts.\n"
        "4. Dry-run a corrected payload before submitting another live job.\n"
        "5. Document any provider-specific caveat if this is a new failure mode."
    )


def kie_add_new_endpoint_contribution_plan(endpoint_name: str, docs_url: str) -> str:
    """Build a contribution plan for adding a KIE endpoint."""

    return (
        f"Plan a contribution for KIE endpoint {endpoint_name} using docs at {docs_url}.\n"
        "1. Read the endpoint docs and identify request/response shapes.\n"
        "2. Add payload builder and route/status handling if async.\n"
        "3. Add CLI and MCP dry-run support.\n"
        "4. Add unit tests and optional gated live tests.\n"
        "5. Update supported models, tool contracts, README/docs, and the journal."
    )


def read_package_resource(filename: str) -> str:
    if filename not in RESOURCE_FILES.values():
        raise ValueError(f"Unsupported MCP resource file: {filename}")
    resource = resources.files("kie_cli").joinpath("mcp_resources", filename)
    return resource.read_text(encoding="utf-8")


def read_repo_doc(path: Path) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    doc_path = repo_root / path
    if doc_path.is_file():
        return doc_path.read_text(encoding="utf-8")
    return (
        f"{path} is available in the source repository but was not included in this installed package. "
        "Use package-local resources such as kie://docs/agent-quickstart, "
        "kie://models/supported, and kie://tools/contracts for installed agent context."
    )


def _dry_run_result(
    route: str,
    model: str,
    payload: dict[str, Any],
    resolved_media: list[Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "status": "dry_run",
        "model": model,
        "route": route,
        "payload": payload,
        "resolvedMedia": [asdict(item) for item in resolved_media],
    }


def _with_job_record(
    result: dict[str, Any],
    *,
    save_job: str | None,
    payload: dict[str, Any],
    resolved_media: list[dict[str, Any]],
    raw: dict[str, Any],
) -> dict[str, Any]:
    result["resolvedMedia"] = resolved_media
    if not save_job or not result.get("ok"):
        return result

    record = build_job_record(
        job_id=result["jobId"],
        model=result["model"],
        status=result.get("status", "queued"),
        submitted_payload=payload,
        resolved_media=resolved_media,
        raw_submit_response=raw,
    )
    path = write_job_record(record, save_job)
    result["jobFile"] = str(path)
    return result


if __name__ == "__main__":
    main()
