"""Payload builders for focused KIE image/video models."""

from __future__ import annotations

from typing import Any

NANO_BANANA_PRO = "nano-banana-pro"
GPT_IMAGE_2_TEXT = "gpt-image-2-text-to-image"
GPT_IMAGE_2_IMAGE = "gpt-image-2-image-to-image"
GROK_TEXT_TO_VIDEO = "grok-imagine/text-to-video"
GROK_IMAGE_TO_VIDEO = "grok-imagine/image-to-video"
VEO_MODELS = {"veo3", "veo3_fast", "veo3_lite"}
SEEDANCE_2_FAST = "bytedance/seedance-2-fast"
SEEDANCE_2 = "bytedance/seedance-2"
SEEDANCE_1_5_PRO = "bytedance/seedance-1.5-pro"
SEEDANCE_MODELS = {SEEDANCE_2_FAST, SEEDANCE_2, SEEDANCE_1_5_PRO}
SEEDANCE_MODEL_ALIASES = {
    "seedance-2-fast": SEEDANCE_2_FAST,
    "seedance-2": SEEDANCE_2,
    "seedance-1.5-pro": SEEDANCE_1_5_PRO,
    SEEDANCE_2_FAST: SEEDANCE_2_FAST,
    SEEDANCE_2: SEEDANCE_2,
    SEEDANCE_1_5_PRO: SEEDANCE_1_5_PRO,
}
SUNO_MUSIC_MODEL = "suno-music"
SUNO_LYRICS_MODEL = "suno-lyrics"
SUNO_SOUNDS_MODEL = "suno-sounds"
SUNO_SOUNDS_MODELS = {"V5", "V5_5"}


def build_nano_banana_pro_payload(
    *,
    prompt: str,
    image_urls: list[str] | None = None,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_format: str = "png",
    callback_url: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": NANO_BANANA_PRO,
        "input": {
            "prompt": prompt,
            "image_input": image_urls or [],
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": output_format,
        },
    }
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def build_gpt_image_2_payload(
    *,
    prompt: str,
    image_urls: list[str] | None = None,
    aspect_ratio: str = "auto",
    resolution: str = "1K",
    callback_url: str | None = None,
) -> dict[str, Any]:
    has_images = bool(image_urls)
    model = GPT_IMAGE_2_IMAGE if has_images else GPT_IMAGE_2_TEXT
    input_payload: dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if has_images:
        input_payload["input_urls"] = image_urls

    payload: dict[str, Any] = {"model": model, "input": input_payload}
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def build_grok_video_payload(
    *,
    prompt: str,
    image_urls: list[str] | None = None,
    aspect_ratio: str = "16:9",
    mode: str = "normal",
    duration: int | str = 6,
    resolution: str = "480p",
    nsfw_checker: bool = False,
    callback_url: str | None = None,
) -> dict[str, Any]:
    has_images = bool(image_urls)
    model = GROK_IMAGE_TO_VIDEO if has_images else GROK_TEXT_TO_VIDEO
    input_payload: dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "mode": mode,
        "duration": str(duration) if has_images else int(duration),
        "resolution": resolution,
        "nsfw_checker": nsfw_checker,
    }
    if has_images:
        input_payload["image_urls"] = image_urls

    payload: dict[str, Any] = {"model": model, "input": input_payload}
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def build_veo_payload(
    *,
    prompt: str,
    image_urls: list[str] | None = None,
    model: str = "veo3_fast",
    generation_type: str | None = None,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    enable_translation: bool = True,
    watermark: str | None = None,
    callback_url: str | None = None,
) -> dict[str, Any]:
    if model not in VEO_MODELS:
        raise ValueError(f"Unsupported Veo model: {model}")

    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "aspect_ratio": aspect_ratio,
        "enableTranslation": enable_translation,
        "resolution": resolution,
    }

    if image_urls:
        payload["imageUrls"] = image_urls

    if generation_type:
        payload["generationType"] = generation_type
    elif image_urls:
        payload["generationType"] = "FIRST_AND_LAST_FRAMES_2_VIDEO"
    else:
        payload["generationType"] = "TEXT_2_VIDEO"

    if watermark:
        payload["watermark"] = watermark
    if callback_url:
        payload["callBackUrl"] = callback_url

    return payload


def build_seedance_payload(
    *,
    prompt: str,
    model: str = "seedance-2-fast",
    input_urls: list[str] | None = None,
    first_frame_url: str | None = None,
    last_frame_url: str | None = None,
    reference_image_urls: list[str] | None = None,
    reference_video_urls: list[str] | None = None,
    reference_audio_urls: list[str] | None = None,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    duration: int | str = 5,
    fixed_lens: bool = False,
    generate_audio: bool = False,
    web_search: bool = False,
    nsfw_checker: bool = False,
    callback_url: str | None = None,
) -> dict[str, Any]:
    provider_model = SEEDANCE_MODEL_ALIASES.get(model)
    if provider_model is None:
        raise ValueError(f"Unsupported Seedance model: {model}")

    image_inputs = input_urls or []
    reference_images = reference_image_urls or []
    reference_videos = reference_video_urls or []
    reference_audios = reference_audio_urls or []

    if provider_model == SEEDANCE_1_5_PRO:
        if first_frame_url or last_frame_url:
            raise ValueError("Seedance 1.5 Pro does not support first/last frame fields; use --image.")
        if reference_images or reference_videos or reference_audios:
            raise ValueError("Seedance 1.5 Pro does not support reference media fields; use --image.")
        if web_search:
            raise ValueError("Seedance 1.5 Pro does not support web_search.")
        if len(image_inputs) > 2:
            raise ValueError("Seedance 1.5 Pro supports at most 2 input images.")

        input_payload: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration": str(duration),
            "fixed_lens": fixed_lens,
            "generate_audio": generate_audio,
            "nsfw_checker": nsfw_checker,
        }
        if image_inputs:
            input_payload["input_urls"] = image_inputs

        payload: dict[str, Any] = {"model": provider_model, "input": input_payload}
        if callback_url:
            payload["callBackUrl"] = callback_url
        return payload

    if image_inputs and (first_frame_url or last_frame_url):
        raise ValueError("Use either --image or explicit first/last frame fields for Seedance 2.x, not both.")

    if image_inputs:
        if len(image_inputs) > 2:
            raise ValueError("Seedance 2.x supports at most 2 --image values for first/last frames.")
        first_frame_url = first_frame_url or image_inputs[0]
        if len(image_inputs) == 2:
            last_frame_url = last_frame_url or image_inputs[1]

    has_frame_inputs = bool(first_frame_url or last_frame_url)
    has_reference_inputs = bool(reference_images or reference_videos or reference_audios)
    if has_frame_inputs and has_reference_inputs:
        raise ValueError("Seedance 2.x frame inputs and reference media inputs are mutually exclusive.")
    if len(reference_images) > 9:
        raise ValueError("Seedance 2.x supports at most 9 reference images.")
    if len(reference_videos) > 3:
        raise ValueError("Seedance 2.x supports at most 3 reference videos.")
    if len(reference_audios) > 3:
        raise ValueError("Seedance 2.x supports at most 3 reference audio files.")

    input_payload = {
        "prompt": prompt,
        "generate_audio": generate_audio,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "duration": int(duration),
        "web_search": web_search,
        "nsfw_checker": nsfw_checker,
    }
    if first_frame_url:
        input_payload["first_frame_url"] = first_frame_url
    if last_frame_url:
        input_payload["last_frame_url"] = last_frame_url
    if reference_images:
        input_payload["reference_image_urls"] = reference_images
    if reference_videos:
        input_payload["reference_video_urls"] = reference_videos
    if reference_audios:
        input_payload["reference_audio_urls"] = reference_audios
    if fixed_lens:
        input_payload["fixed_lens"] = fixed_lens

    payload = {"model": provider_model, "input": input_payload}
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def build_suno_music_payload(
    *,
    prompt: str,
    custom_mode: bool = False,
    instrumental: bool = False,
    model: str | None = None,
    style: str | None = None,
    title: str | None = None,
    negative_tags: str | None = None,
    callback_url: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "prompt": prompt,
        "customMode": custom_mode,
        "instrumental": instrumental,
    }
    if model:
        payload["model"] = model
    if style:
        payload["style"] = style
    if title:
        payload["title"] = title
    if negative_tags:
        payload["negativeTags"] = negative_tags
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def build_suno_lyrics_payload(
    *,
    prompt: str,
    callback_url: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"prompt": prompt}
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload


def build_suno_sounds_payload(
    *,
    prompt: str,
    model: str | None = None,
    sound_loop: bool = False,
    sound_tempo: int | None = None,
    sound_key: str | None = None,
    grab_lyrics: bool = False,
    callback_url: str | None = None,
) -> dict[str, Any]:
    if model is not None and model not in SUNO_SOUNDS_MODELS:
        raise ValueError(f"Unsupported Suno sounds model: {model}")

    payload: dict[str, Any] = {
        "prompt": prompt,
        "soundLoop": sound_loop,
        "grabLyrics": grab_lyrics,
    }
    if model:
        payload["model"] = model
    if sound_tempo is not None:
        payload["soundTempo"] = sound_tempo
    if sound_key:
        payload["soundKey"] = sound_key
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload
