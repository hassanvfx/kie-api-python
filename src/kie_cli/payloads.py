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
SEEDANCE_2_5 = "bytedance/seedance-2-5"
SEEDANCE_MODELS = {SEEDANCE_2_FAST, SEEDANCE_2, SEEDANCE_1_5_PRO, SEEDANCE_2_5}
SEEDANCE_MODEL_ALIASES = {
    "seedance-2-fast": SEEDANCE_2_FAST,
    "seedance-2": SEEDANCE_2,
    "seedance-1.5-pro": SEEDANCE_1_5_PRO,
    "seedance-2.5": SEEDANCE_2_5,
    SEEDANCE_2_FAST: SEEDANCE_2_FAST,
    SEEDANCE_2: SEEDANCE_2,
    SEEDANCE_1_5_PRO: SEEDANCE_1_5_PRO,
    SEEDANCE_2_5: SEEDANCE_2_5,
}
SEEDANCE_2X_REFERENCE_IMAGE_CAP = {SEEDANCE_2_5: 30}
"""Seedance 2.5 accepts up to 30 combined reference_image_urls/first-last-frame
images (docs.kie.ai/market/bytedance/seedance-2-5), vs the 9-image cap that
applies to seedance-2/seedance-2-fast -- everything else about the "2.x"
payload shape (duration is never range-validated client-side here, matching
this module's existing posture of leaving that to the caller; resolution/
aspect_ratio are unrestricted strings) is identical across all three."""
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
    max_reference_images = SEEDANCE_2X_REFERENCE_IMAGE_CAP.get(provider_model, 9)
    if len(reference_images) > max_reference_images:
        raise ValueError(f"Seedance 2.x supports at most {max_reference_images} reference images.")
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


GPT_IMAGE_2_5_FLARE_TEXT = "gpt-image-2-5-flare-text-to-image"
GPT_IMAGE_2_5_FLARE_IMAGE = "gpt-image-2-5-flare-image-to-image"
GPT_IMAGE_2_5_SUNBURST_TEXT = "gpt-image-2-5-sunburst-text-to-image"
GPT_IMAGE_2_5_SUNBURST_IMAGE = "gpt-image-2-5-sunburst-image-to-image"
GPT_IMAGE_2_5_MODELS = {
    GPT_IMAGE_2_5_FLARE_TEXT,
    GPT_IMAGE_2_5_FLARE_IMAGE,
    GPT_IMAGE_2_5_SUNBURST_TEXT,
    GPT_IMAGE_2_5_SUNBURST_IMAGE,
}
GPT_IMAGE_2_5_VARIANTS = {
    # variant -> (text-to-image slug, image-to-image slug)
    "flare": (GPT_IMAGE_2_5_FLARE_TEXT, GPT_IMAGE_2_5_FLARE_IMAGE),
    "sunburst": (GPT_IMAGE_2_5_SUNBURST_TEXT, GPT_IMAGE_2_5_SUNBURST_IMAGE),
}
GPT_IMAGE_2_5_ALIASES = ("gpt-image-2-5", "gpt-image-2-5-flare", "gpt-image-2-5-sunburst")
"""Family and variant aliases. Like `gpt-image-2`, each resolves to the
text-to-image or image-to-image slug depending on whether images were
supplied; the bare family alias resolves to the default variant."""

GPT_IMAGE_2_5_DEFAULT_VARIANT = "sunburst"
"""Sunburst is OpenAI's most capable GPT Image 2.5 tier for generation and
editing; Flare is the faster, cheaper default OpenAI recommends for bulk
exploration. Callers doing reference-driven or final-quality work want
Sunburst, so it is this module's default and Flare is the opt-in."""

GPT_IMAGE_2_5_MAX_INPUT_IMAGES = 16
"""docs.kie.ai/market/gpt/gpt-image-2-5-sunburst-image-to-image: `input_urls`
accepts at most 16 image URLs."""

GPT_IMAGE_2_5_BACKGROUNDS = ("transparent", "opaque", "auto")
GPT_IMAGE_2_5_RESOLUTIONS = ("1K", "2K", "4K")
GPT_IMAGE_2_5_TEXT_ASPECT_RATIOS = (
    "auto", "1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16",
    "21:9", "27:16", "16:27", "9:8", "8:9",
)
GPT_IMAGE_2_5_IMAGE_ASPECT_RATIOS = (
    "auto", "1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5",
    "16:9", "9:16", "2:1", "1:2", "3:1", "1:3", "21:9", "9:21",
)
"""The two modes publish DIFFERENT aspect-ratio enums: text-to-image adds the
wide/tall 27:16, 16:27, 9:8 and 8:9 ratios, image-to-image adds 5:4, 4:5,
2:1, 1:2, 3:1, 1:3 and 9:21. Validating per mode turns a 422 round-trip into
a local error naming the values that actually work for the mode in play."""

GPT_IMAGE_2_5_ONE_K_ONLY_ASPECT_RATIOS = ("27:16", "16:27", "9:8", "8:9")
"""Documented on both text-to-image pages: "The 27:16, 16:27, 9:8 and 8:9
aspect ratios support 1K only"."""


def resolve_gpt_image_2_5_model(variant_or_slug: str, *, has_images: bool) -> str:
    """Map a caller's model string onto one of the four real slugs.

    Accepts a family alias (`gpt-image-2-5`), a variant alias
    (`gpt-image-2-5-flare`, `gpt-image-2-5-sunburst`) -- both of which pick
    text-to-image or image-to-image from whether images were supplied, the
    same way `build_gpt_image_2_payload` already does for GPT Image 2 -- or a
    fully qualified slug, which forces the mode explicitly and is checked for
    consistency with the inputs.
    """
    if variant_or_slug in GPT_IMAGE_2_5_MODELS:
        wants_images = variant_or_slug.endswith("-image-to-image")
        if wants_images and not has_images:
            raise ValueError(
                f"{variant_or_slug} is an image-to-image model but no images were supplied."
            )
        if not wants_images and has_images:
            raise ValueError(
                f"{variant_or_slug} is a text-to-image model but images were supplied. "
                f"Use the image-to-image slug or a variant alias."
            )
        return variant_or_slug

    variant = variant_or_slug
    if variant in ("gpt-image-2-5", "gpt-image-2.5"):
        variant = GPT_IMAGE_2_5_DEFAULT_VARIANT
    for prefix in ("gpt-image-2-5-", "gpt-image-2.5-"):
        if variant.startswith(prefix):
            variant = variant[len(prefix):]
            break
    if variant not in GPT_IMAGE_2_5_VARIANTS:
        raise ValueError(
            f"Unsupported GPT Image 2.5 variant: {variant_or_slug!r}. "
            f"Use one of: gpt-image-2-5, "
            f"{', '.join(f'gpt-image-2-5-{name}' for name in sorted(GPT_IMAGE_2_5_VARIANTS))}, "
            f"or a full slug ({', '.join(sorted(GPT_IMAGE_2_5_MODELS))})."
        )
    text_slug, image_slug = GPT_IMAGE_2_5_VARIANTS[variant]
    return image_slug if has_images else text_slug


def build_gpt_image_2_5_payload(
    *,
    prompt: str,
    model: str = "gpt-image-2-5",
    image_urls: list[str] | None = None,
    aspect_ratio: str = "auto",
    resolution: str | None = None,
    background: str | None = None,
    callback_url: str | None = None,
) -> dict[str, Any]:
    """Build a GPT Image 2.5 (Flare / Sunburst) market-job payload.

    The `input` block is shaped exactly like GPT Image 2's -- prompt,
    aspect_ratio, resolution, and input_urls for the image-to-image mode --
    plus the new optional `background`. `resolution` and `background` are
    omitted entirely when not given, so the model's own default applies
    rather than a default this client invents.
    """
    image_urls = image_urls or []
    has_images = bool(image_urls)
    resolved_model = resolve_gpt_image_2_5_model(model, has_images=has_images)

    if len(image_urls) > GPT_IMAGE_2_5_MAX_INPUT_IMAGES:
        raise ValueError(
            f"{resolved_model} accepts at most {GPT_IMAGE_2_5_MAX_INPUT_IMAGES} "
            f"input images, got {len(image_urls)}."
        )

    allowed_aspect = (
        GPT_IMAGE_2_5_IMAGE_ASPECT_RATIOS if has_images else GPT_IMAGE_2_5_TEXT_ASPECT_RATIOS
    )
    if aspect_ratio not in allowed_aspect:
        raise ValueError(
            f"Unsupported aspect_ratio {aspect_ratio!r} for {resolved_model}. "
            f"Supported: {', '.join(allowed_aspect)}."
        )
    if resolution is not None and resolution not in GPT_IMAGE_2_5_RESOLUTIONS:
        raise ValueError(
            f"Unsupported resolution {resolution!r}. "
            f"Supported: {', '.join(GPT_IMAGE_2_5_RESOLUTIONS)}."
        )
    if (
        resolution not in (None, "1K")
        and aspect_ratio in GPT_IMAGE_2_5_ONE_K_ONLY_ASPECT_RATIOS
    ):
        raise ValueError(
            f"Aspect ratio {aspect_ratio!r} supports 1K only, got resolution {resolution!r}."
        )
    if background is not None and background not in GPT_IMAGE_2_5_BACKGROUNDS:
        raise ValueError(
            f"Unsupported background {background!r}. "
            f"Supported: {', '.join(GPT_IMAGE_2_5_BACKGROUNDS)}."
        )

    input_payload: dict[str, Any] = {"prompt": prompt, "aspect_ratio": aspect_ratio}
    if has_images:
        input_payload["input_urls"] = image_urls
    if resolution is not None:
        input_payload["resolution"] = resolution
    if background is not None:
        input_payload["background"] = background

    payload: dict[str, Any] = {"model": resolved_model, "input": input_payload}
    if callback_url:
        payload["callBackUrl"] = callback_url
    return payload
