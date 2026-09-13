"""Command-line interface for focused KIE image/video generation."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .client import KieClient, KieUploadClient
from .config import load_config
from .errors import ApiError, ConfigurationError, KieCliError
from .jobs import build_job_record, read_job_record, write_job_record
from .llm import (
    GEMINI_3_PRO,
    GPT_5_2,
    SUPPORTED_LLM_MODELS,
    build_llm_payload,
    build_gemini_vision_payload,
    normalize_llm_response,
    normalize_chat_completion,
    route_name,
    resolve_llm_model,
)
from .media import resolve_media_inputs
from .polling import get_status_once, poll_until_complete
from .payloads import (
    SUNO_LYRICS_MODEL,
    SUNO_MUSIC_MODEL,
    SUNO_SOUNDS_MODEL,
    ELEVENLABS_ALIASES,
    ELEVENLABS_DEFAULT_VOICE,
    ELEVENLABS_DIALOGUE,
    ELEVENLABS_TTS,
    GPT_IMAGE_2_5_ALIASES,
    GPT_IMAGE_2_5_BACKGROUNDS,
    GPT_IMAGE_2_5_MODELS,
    build_elevenlabs_dialogue_payload,
    build_elevenlabs_tts_payload,
    build_gpt_image_2_5_payload,
    build_gpt_image_2_payload,
    build_grok_video_payload,
    build_nano_banana_pro_payload,
    build_seedance_payload,
    build_suno_lyrics_payload,
    build_suno_music_payload,
    build_suno_sounds_payload,
    build_veo_payload,
)
from .status import (
    normalize_market_status,
    normalize_submit,
    normalize_suno_lyrics_status,
    normalize_suno_music_status,
    normalize_veo_status,
)

IMAGE_MODEL_CHOICES = [
    "nano-banana-pro",
    "gpt-image-2",
    *GPT_IMAGE_2_5_ALIASES,
    *sorted(GPT_IMAGE_2_5_MODELS),
]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = dispatch(args)
    except (ApiError, ConfigurationError, KieCliError, ValueError, FileNotFoundError) as exc:
        payload = {
            "ok": False,
            "status": "failed",
            "error": {
                "code": getattr(exc, "code", exc.__class__.__name__),
                "message": str(exc),
            },
        }
        if getattr(args, "json", False):
            print_json(payload)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    if getattr(args, "json", False):
        print_json(result)
    elif args.model == "veo3":
        print_human(result)

    return 0 if result.get("ok", True) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kie-cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload = subparsers.add_parser("upload", help="Upload a local file to KIE temporary storage.")
    upload.add_argument("file")
    upload.add_argument("--upload-path", default="kie-cli/uploads")
    upload.add_argument("--json", action="store_true")
    upload.add_argument("--dry-run", action="store_true")

    image = subparsers.add_parser("image", help="Submit an image generation task.")
    image.add_argument(
        "model",
        choices=IMAGE_MODEL_CHOICES,
        help=(
            "Image model alias or full slug. `gpt-image-2` and the "
            "`gpt-image-2-5*` aliases pick text-to-image or image-to-image "
            "from whether --image was given; a full GPT Image 2.5 slug "
            "forces the mode."
        ),
    )
    add_prompt_args(image)
    add_image_args(image)
    image.add_argument("--aspect-ratio", default=None)
    image.add_argument("--resolution", default="1K")
    image.add_argument(
        "--background",
        default=None,
        choices=list(GPT_IMAGE_2_5_BACKGROUNDS),
        help="GPT Image 2.5 only: background handling. Omitted unless given.",
    )
    image.add_argument("--output-format", default="png", choices=["png", "jpg"])
    image.add_argument("--callback-url")
    image.add_argument("--upload-path", default="kie-cli/images")
    image.add_argument("--save-job")
    image.add_argument("--dry-run", action="store_true")
    image.add_argument("--json", action="store_true")

    video = subparsers.add_parser("video", help="Submit a video generation task.")
    video.add_argument("model", choices=["grok", "veo3", "seedance"], help="Focused video model alias.")
    add_prompt_args(video)
    add_image_args(video)
    video.add_argument("--aspect-ratio", default=None)
    video.add_argument("--mode", default="normal", choices=["fun", "normal", "spicy"])
    video.add_argument("--duration", type=int)
    video.add_argument("--resolution", default=None)
    video.add_argument("--nsfw-checker", action="store_true")
    video.add_argument("--veo-model", default="veo3_fast", choices=["veo3", "veo3_fast", "veo3_lite"])
    video.add_argument(
        "--seedance-model",
        default="seedance-2-fast",
        choices=["seedance-2-fast", "seedance-2", "seedance-1.5-pro", "seedance-2.5"],
    )
    video.add_argument(
        "--generation-type",
        choices=["TEXT_2_VIDEO", "FIRST_AND_LAST_FRAMES_2_VIDEO", "REFERENCE_2_VIDEO"],
    )
    video.add_argument("--disable-translation", action="store_true")
    video.add_argument("--watermark")
    video.add_argument("--first-frame")
    video.add_argument("--last-frame")
    video.add_argument("--reference-image", action="append", default=[])
    video.add_argument("--reference-video", action="append", default=[])
    video.add_argument("--reference-audio", action="append", default=[])
    video.add_argument("--generate-audio", action="store_true")
    video.add_argument("--web-search", action="store_true")
    video.add_argument("--fixed-lens", action="store_true")
    video.add_argument("--callback-url")
    video.add_argument("--upload-path", default="kie-cli/videos")
    video.add_argument("--save-job")
    video.add_argument("--dry-run", action="store_true")
    video.add_argument("--json", action="store_true")

    llm = subparsers.add_parser("llm", help="Run a KIE Claude, GPT, Codex, or Gemini completion.")
    llm.add_argument("model", choices=SUPPORTED_LLM_MODELS)
    add_prompt_args(llm)
    add_image_args(llm)
    llm.add_argument("--reasoning-effort", default="high", choices=["low", "medium", "high", "xhigh"])
    llm.add_argument("--thinking", action="store_true", help="Enable KIE Claude thinking when supported.")
    llm.add_argument("--request-timeout", type=float, default=60)
    llm.add_argument("--max-completion-tokens", type=int)
    llm.add_argument("--web-search", action="store_true")
    llm.add_argument("--upload-path", default="kie-cli/llm")
    llm.add_argument("--dry-run", action="store_true")
    llm.add_argument("--json", action="store_true")

    gemini = subparsers.add_parser("gemini", help="Run KIE Gemini multimodal chat completion.")
    gemini.add_argument("model", choices=[GEMINI_3_PRO])
    add_prompt_args(gemini)
    add_image_args(gemini)
    gemini.add_argument("--reasoning-effort", default="high", choices=["low", "high"])
    gemini.add_argument("--include-thoughts", action="store_true")
    gemini.add_argument("--web-search", action="store_true")
    gemini.add_argument("--upload-path", default="kie-cli/gemini")
    gemini.add_argument("--dry-run", action="store_true")
    gemini.add_argument("--json", action="store_true")

    suno = subparsers.add_parser("suno", help="Submit focused Suno music, lyrics, or sounds tasks.")
    suno_subparsers = suno.add_subparsers(dest="suno_command", required=True)

    suno_music = suno_subparsers.add_parser("music", help="Submit a Suno music generation task.")
    add_prompt_args(suno_music)
    suno_music.add_argument("--custom-mode", action="store_true")
    suno_music.add_argument("--instrumental", action="store_true")
    suno_music.add_argument("--model")
    suno_music.add_argument("--style")
    suno_music.add_argument("--title")
    suno_music.add_argument("--negative-tags")
    suno_music.add_argument("--callback-url")
    suno_music.add_argument("--save-job")
    suno_music.add_argument("--dry-run", action="store_true")
    suno_music.add_argument("--json", action="store_true")

    suno_lyrics = suno_subparsers.add_parser("lyrics", help="Submit a Suno lyrics generation task.")
    add_prompt_args(suno_lyrics)
    suno_lyrics.add_argument("--callback-url")
    suno_lyrics.add_argument("--dry-run", action="store_true")
    suno_lyrics.add_argument("--json", action="store_true")

    suno_sounds = suno_subparsers.add_parser("sounds", help="Submit a Suno sounds generation task.")
    add_prompt_args(suno_sounds)
    suno_sounds.add_argument("--model", choices=["V5", "V5_5"])
    suno_sounds.add_argument("--sound-loop", action="store_true")
    suno_sounds.add_argument("--sound-tempo", type=int)
    suno_sounds.add_argument("--sound-key")
    suno_sounds.add_argument("--grab-lyrics", action="store_true")
    suno_sounds.add_argument("--callback-url")
    suno_sounds.add_argument("--save-job")
    suno_sounds.add_argument("--dry-run", action="store_true")
    suno_sounds.add_argument("--json", action="store_true")

    status = subparsers.add_parser("job-status", help="Query a submitted task once.")
    status.add_argument("job_id")
    status.add_argument("--kind", choices=["auto", "market", "veo"], default="auto")
    status.add_argument("--model", help="Model used to submit the job. Preferred over --kind.")
    status.add_argument("--json", action="store_true")

    speech = subparsers.add_parser("speech", help="Submit an ElevenLabs text-to-speech or dialogue task.")
    speech.add_argument(
        "model", nargs="?", default="elevenlabs-tts", choices=sorted(ELEVENLABS_ALIASES),
        help=(
            "elevenlabs-tts / elevenlabs-v2 is multilingual-v2 (single voice, supports --timestamps); "
            "elevenlabs-dialogue / elevenlabs-v3 is text-to-dialogue-v3 (multi-speaker, NO timestamps)"
        ),
    )
    add_prompt_args(speech)
    speech.add_argument("--voice", default=ELEVENLABS_DEFAULT_VOICE, help="voice id (preferred) or preset name")
    speech.add_argument("--stability", type=float)
    speech.add_argument("--similarity-boost", dest="similarity_boost", type=float)
    speech.add_argument("--style", dest="voice_style", type=float)
    speech.add_argument("--speed", type=float, help="0.7-1.2")
    speech.add_argument(
        "--timestamps", action="store_true",
        help="return WORD-LEVEL timings; multilingual-v2 only, and the only way to sync captions to the read",
    )
    speech.add_argument("--previous-text", dest="previous_text", help="the copy just before this segment, for continuous prosody")
    speech.add_argument("--next-text", dest="next_text", help="the copy just after this segment")
    speech.add_argument("--language-code", dest="language_code", help="ISO 639-1")
    speech.add_argument(
        "--dialogue", help="text-to-dialogue-v3 only: JSON array of {text, voice} items (or @path to a JSON file)",
    )
    speech.add_argument("--callback-url")
    speech.add_argument("--save-job")
    speech.add_argument("--dry-run", action="store_true")
    speech.add_argument("--json", action="store_true")

    voices = subparsers.add_parser("voices", help="Print the ElevenLabs voice preview URL for a voice id.")
    voices.add_argument("voice_id")
    voices.add_argument("--json", action="store_true")

    wait = subparsers.add_parser("wait", help="Poll an async KIE job until completion.")
    wait.add_argument("job_id", nargs="?")
    wait.add_argument("--model")
    wait.add_argument("--job-file")
    wait.add_argument("--poll-interval", type=float, default=5.0)
    wait.add_argument("--timeout", type=float, default=900.0)
    wait.add_argument("--json", action="store_true")

    return parser


def add_prompt_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt")
    group.add_argument("--prompt-file")


def add_image_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="Image reference. Can be repeated. Use local file paths or http(s) URLs.",
    )


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "upload":
        return command_upload(args)
    if args.command == "image":
        return command_image(args)
    if args.command == "speech":
        return command_speech(args)
    if args.command == "voices":
        return command_voices(args)
    if args.command == "video":
        return command_video(args)
    if args.command == "llm":
        return command_llm(args)
    if args.command == "gemini":
        return command_gemini(args)
    if args.command == "suno":
        return command_suno(args)
    if args.command == "job-status":
        return command_job_status(args)
    if args.command == "wait":
        return command_wait(args)
    raise KieCliError(f"Unsupported command: {args.command}")


def command_upload(args: argparse.Namespace) -> dict[str, Any]:
    if args.dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "file": args.file,
            "uploadPath": args.upload_path,
            "uploaded": False,
        }

    config = load_config()
    upload = KieUploadClient(config).upload_file(args.file, upload_path=args.upload_path)
    return {
        "ok": True,
        "downloadUrl": upload["downloadUrl"],
        "fileName": upload.get("fileName"),
        "filePath": upload.get("filePath"),
        "mimeType": upload.get("mimeType"),
        "fileSize": upload.get("fileSize"),
        "expiresInDays": 3,
    }


def command_image(args: argparse.Namespace) -> dict[str, Any]:
    prompt = read_prompt(args)
    config = load_config()
    uploader = None if args.dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        args.image,
        kind="image",
        uploader=uploader,
        upload_path=args.upload_path,
        dry_run=args.dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]

    if args.model == "nano-banana-pro":
        payload = build_nano_banana_pro_payload(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=args.aspect_ratio or "1:1",
            resolution=args.resolution,
            output_format=args.output_format,
            callback_url=args.callback_url,
        )
        model = "nano-banana-pro"
    elif args.model in GPT_IMAGE_2_5_ALIASES or args.model in GPT_IMAGE_2_5_MODELS:
        payload = build_gpt_image_2_5_payload(
            prompt=prompt,
            model=args.model,
            image_urls=image_urls,
            aspect_ratio=args.aspect_ratio or "auto",
            resolution=args.resolution,
            background=args.background,
            callback_url=args.callback_url,
        )
        model = payload["model"]
    else:
        payload = build_gpt_image_2_payload(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=args.aspect_ratio or "auto",
            resolution=args.resolution,
            callback_url=args.callback_url,
        )
        model = payload["model"]

    if args.dry_run:
        return dry_run_result(model=model, payload=payload, resolved_media=resolved, kind="market")

    response = KieClient(config).create_market_task(payload)
    result = normalize_submit(response, model=model)
    result["resolvedMedia"] = [asdict(item) for item in resolved]
    maybe_save_job(args, result=result, payload=payload, resolved_media=result["resolvedMedia"], raw=response)
    return result


def command_speech(args: argparse.Namespace) -> dict[str, Any]:
    model = ELEVENLABS_ALIASES[args.model]
    config = load_config()

    if model == ELEVENLABS_DIALOGUE:
        if not args.dialogue:
            raise ValueError("text-to-dialogue-v3 needs --dialogue (a JSON array of {text, voice} items)")
        raw = args.dialogue
        if raw.startswith("@"):
            raw = Path(raw[1:]).read_text()
        payload = build_elevenlabs_dialogue_payload(
            dialogue=json.loads(raw), stability=args.stability,
            language_code=args.language_code, callback_url=args.callback_url,
        )
    else:
        payload = build_elevenlabs_tts_payload(
            text=read_prompt(args), voice=args.voice, stability=args.stability,
            similarity_boost=args.similarity_boost, style=args.voice_style, speed=args.speed,
            timestamps=args.timestamps or None, previous_text=args.previous_text,
            next_text=args.next_text, language_code=args.language_code,
            callback_url=args.callback_url,
        )

    if args.dry_run:
        return dry_run_result(model=model, payload=payload, resolved_media=[], kind="market")

    response = KieClient(config).create_market_task(payload)
    result = normalize_submit(response, model=model)
    maybe_save_job(args, result=result, payload=payload, resolved_media=[], raw=response)
    return result


def command_voices(args: argparse.Namespace) -> dict[str, Any]:
    """The preview URL for a voice id.

    Previews are plain files at a predictable URL, so listening to a voice
    needs no API call and no backend -- just this URL in a browser or an
    `<audio>` tag.
    """
    from .payloads import voice_preview_url

    return {"ok": True, "voiceId": args.voice_id, "previewUrl": voice_preview_url(args.voice_id)}


def command_video(args: argparse.Namespace) -> dict[str, Any]:
    prompt = read_prompt(args)
    config = load_config()
    uploader = None if args.dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        args.image,
        kind="image",
        uploader=uploader,
        upload_path=args.upload_path,
        dry_run=args.dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]
    resolved_media = resolved

    if args.model == "grok":
        payload = build_grok_video_payload(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=args.aspect_ratio or ("16:9" if image_urls else "2:3"),
            mode=args.mode,
            duration=args.duration or 6,
            resolution=args.resolution or "480p",
            nsfw_checker=args.nsfw_checker,
            callback_url=args.callback_url,
        )
        kind = "market"
        model = payload["model"]
    elif args.model == "veo3":
        payload = build_veo_payload(
            prompt=prompt,
            image_urls=image_urls,
            model=args.veo_model,
            generation_type=args.generation_type,
            aspect_ratio=args.aspect_ratio or "16:9",
            resolution=args.resolution or "720p",
            enable_translation=not args.disable_translation,
            watermark=args.watermark,
            callback_url=args.callback_url,
        )
        kind = "veo"
        model = args.veo_model
    else:
        first_frame = resolve_media_inputs(
            [args.first_frame] if args.first_frame else [],
            kind="image",
            uploader=uploader,
            upload_path=args.upload_path,
            dry_run=args.dry_run,
        )
        last_frame = resolve_media_inputs(
            [args.last_frame] if args.last_frame else [],
            kind="image",
            uploader=uploader,
            upload_path=args.upload_path,
            dry_run=args.dry_run,
        )
        reference_images = resolve_media_inputs(
            args.reference_image,
            kind="image",
            uploader=uploader,
            upload_path=args.upload_path,
            dry_run=args.dry_run,
        )
        reference_videos = resolve_media_inputs(
            args.reference_video,
            kind="video",
            uploader=uploader,
            upload_path=args.upload_path,
            dry_run=args.dry_run,
        )
        reference_audios = resolve_media_inputs(
            args.reference_audio,
            kind="audio",
            uploader=uploader,
            upload_path=args.upload_path,
            dry_run=args.dry_run,
        )
        resolved_media = [
            *resolved,
            *first_frame,
            *last_frame,
            *reference_images,
            *reference_videos,
            *reference_audios,
        ]
        payload = build_seedance_payload(
            prompt=prompt,
            model=args.seedance_model,
            input_urls=image_urls,
            first_frame_url=first_frame[0].resolved_url if first_frame else None,
            last_frame_url=last_frame[0].resolved_url if last_frame else None,
            reference_image_urls=[item.resolved_url for item in reference_images],
            reference_video_urls=[item.resolved_url for item in reference_videos],
            reference_audio_urls=[item.resolved_url for item in reference_audios],
            aspect_ratio=args.aspect_ratio or "16:9",
            resolution=args.resolution or "720p",
            duration=args.duration or 5,
            fixed_lens=args.fixed_lens,
            generate_audio=args.generate_audio,
            web_search=args.web_search,
            nsfw_checker=args.nsfw_checker,
            callback_url=args.callback_url,
        )
        kind = "market"
        model = payload["model"]

    if args.dry_run:
        return dry_run_result(model=model, payload=payload, resolved_media=resolved_media, kind=kind)

    client = KieClient(config)
    response = client.create_veo_task(payload) if kind == "veo" else client.create_market_task(payload)
    result = normalize_submit(response, model=model)
    result["resolvedMedia"] = [asdict(item) for item in resolved_media]
    maybe_save_job(args, result=result, payload=payload, resolved_media=result["resolvedMedia"], raw=response)
    return result


def command_llm(args: argparse.Namespace) -> dict[str, Any]:
    prompt = read_prompt(args)
    config = load_config()
    uploader = None if args.dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        args.image,
        kind="image",
        uploader=uploader,
        upload_path=args.upload_path,
        dry_run=args.dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]
    spec = resolve_llm_model(args.model)
    payload = build_llm_payload(
        model=args.model,
        prompt=prompt,
        image_urls=image_urls,
        reasoning_effort=args.reasoning_effort,
        web_search=args.web_search,
        max_completion_tokens=args.max_completion_tokens,
        thinking=args.thinking,
    )

    if args.dry_run:
        result = dry_run_result(
            model=args.model,
            payload=payload,
            resolved_media=resolved,
            kind=route_name(spec.transport),
        )
        result["kind"] = route_name(spec.transport)
        return result

    response = KieClient(config, request_timeout=args.request_timeout).create_llm_completion(
        transport=spec.transport,
        payload=payload,
    )
    result = normalize_llm_response(response, model=args.model)
    result["resolvedMedia"] = [asdict(item) for item in resolved]
    return result


def command_gemini(args: argparse.Namespace) -> dict[str, Any]:
    prompt = read_prompt(args)
    config = load_config()
    uploader = None if args.dry_run else KieUploadClient(config)
    resolved = resolve_media_inputs(
        args.image,
        kind="image",
        uploader=uploader,
        upload_path=args.upload_path,
        dry_run=args.dry_run,
    )
    image_urls = [item.resolved_url for item in resolved]
    payload = build_gemini_vision_payload(
        prompt=prompt,
        image_urls=image_urls,
        reasoning_effort=args.reasoning_effort,
        include_thoughts=args.include_thoughts,
        web_search=args.web_search,
    )

    if args.dry_run:
        return dry_run_result(
            model=args.model,
            payload=payload,
            resolved_media=resolved,
            kind="chat_completions",
        )

    response = KieClient(config).create_gemini_3_pro_chat_completion(payload)
    result = normalize_chat_completion(response, model=args.model)
    result["resolvedMedia"] = [asdict(item) for item in resolved]
    return result


def command_suno(args: argparse.Namespace) -> dict[str, Any]:
    prompt = read_prompt(args)
    config = load_config()

    if args.suno_command == "music":
        payload = build_suno_music_payload(
            prompt=prompt,
            custom_mode=args.custom_mode,
            instrumental=args.instrumental,
            model=args.model,
            style=args.style,
            title=args.title,
            negative_tags=args.negative_tags,
            callback_url=args.callback_url,
        )
        if args.dry_run:
            return dry_run_result(model=SUNO_MUSIC_MODEL, payload=payload, resolved_media=[], kind="suno_music")

        response = KieClient(config).create_suno_music_task(payload)
        result = normalize_submit(response, model=SUNO_MUSIC_MODEL)
        maybe_save_job(args, result=result, payload=payload, resolved_media=[], raw=response)
        return result

    if args.suno_command == "lyrics":
        payload = build_suno_lyrics_payload(
            prompt=prompt,
            callback_url=args.callback_url,
        )
        if args.dry_run:
            return dry_run_result(model=SUNO_LYRICS_MODEL, payload=payload, resolved_media=[], kind="suno_lyrics")

        response = KieClient(config).create_suno_lyrics_task(payload)
        return normalize_submit(response, model=SUNO_LYRICS_MODEL)

    if args.suno_command == "sounds":
        payload = build_suno_sounds_payload(
            prompt=prompt,
            model=args.model,
            sound_loop=args.sound_loop,
            sound_tempo=args.sound_tempo,
            sound_key=args.sound_key,
            grab_lyrics=args.grab_lyrics,
            callback_url=args.callback_url,
        )
        if args.dry_run:
            return dry_run_result(model=SUNO_SOUNDS_MODEL, payload=payload, resolved_media=[], kind="suno_music")

        response = KieClient(config).create_suno_sounds_task(payload)
        result = normalize_submit(response, model=SUNO_SOUNDS_MODEL)
        maybe_save_job(args, result=result, payload=payload, resolved_media=[], raw=response)
        return result

    raise KieCliError(f"Unsupported Suno command: {args.suno_command}")


def command_job_status(args: argparse.Namespace) -> dict[str, Any]:
    config = load_config()
    client = KieClient(config)

    if args.model:
        return get_status_by_model(client=client, job_id=args.job_id, model=args.model)

    kind = infer_kind(args.job_id, args.kind)
    if kind == "veo":
        return normalize_veo_status(client.get_veo_task(args.job_id))
    return normalize_market_status(client.get_market_task(args.job_id))


def command_wait(args: argparse.Namespace) -> dict[str, Any]:
    config = load_config()
    client = KieClient(config)

    if args.job_file:
        record = read_job_record(args.job_file)
        job_id = record.jobId
        model = record.model
    else:
        if not args.job_id or not args.model:
            raise KieCliError("wait requires either --job-file or JOB_ID with --model")
        job_id = args.job_id
        model = args.model

    return poll_until_complete(
        client=client,
        job_id=job_id,
        model=model,
        market_normalizer=normalize_market_status,
        veo_normalizer=normalize_veo_status,
        suno_music_normalizer=normalize_suno_music_status,
        suno_lyrics_normalizer=normalize_suno_lyrics_status,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
    )


def maybe_save_job(
    args: argparse.Namespace,
    *,
    result: dict[str, Any],
    payload: dict[str, Any],
    resolved_media: list[dict[str, Any]],
    raw: dict[str, Any],
) -> None:
    save_path = getattr(args, "save_job", None)
    if not save_path or not result.get("ok"):
        return

    record = build_job_record(
        job_id=result["jobId"],
        model=result["model"],
        status=result.get("status", "queued"),
        submitted_payload=payload,
        resolved_media=resolved_media,
        raw_submit_response=raw,
    )
    path = write_job_record(record, save_path)
    result["jobFile"] = str(path)


def get_status_by_model(*, client: KieClient, job_id: str, model: str) -> dict[str, Any]:
    return get_status_once(
        client=client,
        job_id=job_id,
        model=model,
        market_normalizer=normalize_market_status,
        veo_normalizer=normalize_veo_status,
        suno_music_normalizer=normalize_suno_music_status,
        suno_lyrics_normalizer=normalize_suno_lyrics_status,
    )


def dry_run_result(
    *,
    model: str,
    payload: dict[str, Any],
    resolved_media: list[Any],
    kind: str,
) -> dict[str, Any]:
    return {
        "ok": True,
        "status": "dry_run",
        "model": model,
        "route": kind,
        "payload": payload,
        "resolvedMedia": [asdict(item) for item in resolved_media],
    }


def infer_kind(job_id: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if job_id.startswith("veo_") or job_id.startswith("veo_task_"):
        return "veo"
    return "market"


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt is not None:
        return args.prompt
    return Path(args.prompt_file).read_text(encoding="utf-8").strip()


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def print_human(payload: dict[str, Any]) -> None:
    if payload.get("status") == "dry_run":
        print_json(payload)
        return

    if payload.get("ok") is False:
        error = payload.get("error") or {}
        print(f"failed: {error.get('message') or payload}", file=sys.stderr)
        return

    if payload.get("text"):
        print(payload["text"])
        return

    if payload.get("jobId"):
        print(f"{payload.get('status', 'ok')}: {payload['jobId']}")
        return

    if payload.get("downloadUrl"):
        print(payload["downloadUrl"])
        return

    print_json(payload)


if __name__ == "__main__":
    raise SystemExit(main())
