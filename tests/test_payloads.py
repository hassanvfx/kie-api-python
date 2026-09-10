import pytest


from kie_cli.payloads import (
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


def test_nano_banana_pro_payload_with_references():
    payload = build_nano_banana_pro_payload(
        prompt="make a poster",
        image_urls=["https://example.com/ref.png"],
        aspect_ratio="1:1",
        resolution="1K",
        output_format="png",
    )

    assert payload["model"] == "nano-banana-pro"
    assert payload["input"]["prompt"] == "make a poster"
    assert payload["input"]["image_input"] == ["https://example.com/ref.png"]
    assert payload["input"]["aspect_ratio"] == "1:1"


def test_gpt_image_2_text_payload_without_images():
    payload = build_gpt_image_2_payload(prompt="make an image")

    assert payload["model"] == "gpt-image-2-text-to-image"
    assert "input_urls" not in payload["input"]


def test_gpt_image_2_image_payload_with_images():
    payload = build_gpt_image_2_payload(
        prompt="edit this image",
        image_urls=["https://example.com/input.png"],
        aspect_ratio="16:9",
        resolution="2K",
    )

    assert payload["model"] == "gpt-image-2-image-to-image"
    assert payload["input"]["input_urls"] == ["https://example.com/input.png"]
    assert payload["input"]["resolution"] == "2K"


def test_grok_text_to_video_payload_without_images():
    payload = build_grok_video_payload(prompt="camera moves forward", aspect_ratio="2:3")

    assert payload["model"] == "grok-imagine/text-to-video"
    assert payload["input"]["duration"] == 6
    assert "image_urls" not in payload["input"]


def test_grok_image_to_video_payload_with_images():
    payload = build_grok_video_payload(
        prompt="@image1 animate this",
        image_urls=["https://example.com/ref.png"],
        duration=8,
        resolution="720p",
    )

    assert payload["model"] == "grok-imagine/image-to-video"
    assert payload["input"]["image_urls"] == ["https://example.com/ref.png"]
    assert payload["input"]["duration"] == "8"


def test_veo_payload_defaults_generation_type_from_images():
    payload = build_veo_payload(
        prompt="transition between frames",
        image_urls=["https://example.com/a.png", "https://example.com/b.png"],
        model="veo3_fast",
    )

    assert payload["model"] == "veo3_fast"
    assert payload["generationType"] == "FIRST_AND_LAST_FRAMES_2_VIDEO"
    assert payload["imageUrls"] == ["https://example.com/a.png", "https://example.com/b.png"]


def test_veo_payload_text_to_video_without_images():
    payload = build_veo_payload(prompt="a dog runs", model="veo3")

    assert payload["model"] == "veo3"
    assert payload["generationType"] == "TEXT_2_VIDEO"
    assert "imageUrls" not in payload


def test_seedance_2_fast_text_payload_defaults():
    payload = build_seedance_payload(prompt="a cinematic city flythrough")

    assert payload["model"] == "bytedance/seedance-2-fast"
    assert payload["input"]["prompt"] == "a cinematic city flythrough"
    assert payload["input"]["aspect_ratio"] == "16:9"
    assert payload["input"]["resolution"] == "720p"
    assert payload["input"]["duration"] == 5
    assert payload["input"]["generate_audio"] is False
    assert payload["input"]["web_search"] is False


def test_seedance_2_payload_with_multimodal_references():
    payload = build_seedance_payload(
        prompt="match the references and create a dramatic reveal",
        model="seedance-2",
        reference_image_urls=["https://example.com/ref.png"],
        reference_video_urls=["https://example.com/ref.mp4"],
        reference_audio_urls=["https://example.com/ref.mp3"],
        duration=12,
        generate_audio=True,
        web_search=True,
        callback_url="https://example.com/callback",
    )

    assert payload["model"] == "bytedance/seedance-2"
    assert payload["callBackUrl"] == "https://example.com/callback"
    assert payload["input"]["reference_image_urls"] == ["https://example.com/ref.png"]
    assert payload["input"]["reference_video_urls"] == ["https://example.com/ref.mp4"]
    assert payload["input"]["reference_audio_urls"] == ["https://example.com/ref.mp3"]
    assert payload["input"]["duration"] == 12
    assert payload["input"]["generate_audio"] is True


def test_seedance_1_5_payload_uses_input_urls_and_string_duration():
    payload = build_seedance_payload(
        prompt="animate these frames",
        model="seedance-1.5-pro",
        input_urls=["https://example.com/a.png", "https://example.com/b.png"],
        duration=8,
        fixed_lens=True,
    )

    assert payload["model"] == "bytedance/seedance-1.5-pro"
    assert payload["input"]["input_urls"] == ["https://example.com/a.png", "https://example.com/b.png"]
    assert payload["input"]["duration"] == "8"
    assert payload["input"]["fixed_lens"] is True


def test_seedance_2_5_payload_supports_extended_reference_images():
    payload = build_seedance_payload(
        prompt="a 30-second cinematic product journey",
        model="seedance-2.5",
        reference_image_urls=[f"https://example.com/ref{i}.png" for i in range(30)],
        duration=30,
        resolution="1080p",
        aspect_ratio="9:16",
        generate_audio=True,
    )

    assert payload["model"] == "bytedance/seedance-2-5"
    assert len(payload["input"]["reference_image_urls"]) == 30
    assert payload["input"]["duration"] == 30
    assert payload["input"]["resolution"] == "1080p"
    assert payload["input"]["aspect_ratio"] == "9:16"
    assert payload["input"]["generate_audio"] is True


def test_seedance_2_5_rejects_more_than_30_reference_images():
    try:
        build_seedance_payload(
            prompt="too many references",
            model="seedance-2.5",
            reference_image_urls=[f"https://example.com/ref{i}.png" for i in range(31)],
        )
    except ValueError as exc:
        assert "30 reference images" in str(exc)
    else:
        raise AssertionError("Expected more than 30 reference images to fail for seedance-2.5")


def test_seedance_2_fast_still_rejects_more_than_9_reference_images():
    try:
        build_seedance_payload(
            prompt="too many references",
            model="seedance-2-fast",
            reference_image_urls=[f"https://example.com/ref{i}.png" for i in range(10)],
        )
    except ValueError as exc:
        assert "9 reference images" in str(exc)
    else:
        raise AssertionError("Expected more than 9 reference images to fail for seedance-2-fast")


def test_seedance_2_rejects_mixed_frame_and_reference_inputs():
    try:
        build_seedance_payload(
            prompt="animate this",
            model="seedance-2-fast",
            first_frame_url="https://example.com/start.png",
            reference_image_urls=["https://example.com/ref.png"],
        )
    except ValueError as exc:
        assert "mutually exclusive" in str(exc)
    else:
        raise AssertionError("Expected mixed Seedance inputs to fail")


def test_suno_music_payload_includes_optional_fields():
    payload = build_suno_music_payload(
        prompt="dreamy synth-pop under neon rain",
        custom_mode=True,
        instrumental=True,
        model="V3_5",
        style="synth-pop",
        title="Neon Rain",
        negative_tags="harsh, noisy",
        callback_url="https://example.com/callback",
    )

    assert payload == {
        "prompt": "dreamy synth-pop under neon rain",
        "customMode": True,
        "instrumental": True,
        "model": "V3_5",
        "style": "synth-pop",
        "title": "Neon Rain",
        "negativeTags": "harsh, noisy",
        "callBackUrl": "https://example.com/callback",
    }


def test_suno_lyrics_payload_omits_callback_when_absent():
    payload = build_suno_lyrics_payload(prompt="a nostalgic song about small town summers")

    assert payload == {"prompt": "a nostalgic song about small town summers"}


def test_suno_sounds_payload_with_options():
    payload = build_suno_sounds_payload(
        prompt="looping cyberpunk ambience",
        model="V5_5",
        sound_loop=True,
        sound_tempo=110,
        sound_key="Am",
        grab_lyrics=True,
        callback_url="https://example.com/callback",
    )

    assert payload == {
        "prompt": "looping cyberpunk ambience",
        "soundLoop": True,
        "grabLyrics": True,
        "model": "V5_5",
        "soundTempo": 110,
        "soundKey": "Am",
        "callBackUrl": "https://example.com/callback",
    }


def test_gpt_image_2_5_family_alias_defaults_to_sunburst_text_to_image():
    payload = build_gpt_image_2_5_payload(prompt="a poster")

    assert payload["model"] == "gpt-image-2-5-sunburst-text-to-image"
    assert payload["input"] == {"prompt": "a poster", "aspect_ratio": "auto"}


def test_gpt_image_2_5_alias_switches_to_image_to_image_when_images_given():
    payload = build_gpt_image_2_5_payload(
        prompt="edit this",
        image_urls=["https://example.com/in.png"],
        aspect_ratio="9:16",
        resolution="2K",
        background="opaque",
    )

    assert payload["model"] == "gpt-image-2-5-sunburst-image-to-image"
    assert payload["input"]["input_urls"] == ["https://example.com/in.png"]
    assert payload["input"]["resolution"] == "2K"
    assert payload["input"]["background"] == "opaque"


def test_gpt_image_2_5_flare_variant_alias_is_honored():
    payload = build_gpt_image_2_5_payload(prompt="draft", model="gpt-image-2-5-flare")

    assert payload["model"] == "gpt-image-2-5-flare-text-to-image"


def test_gpt_image_2_5_omits_resolution_and_background_when_not_requested():
    payload = build_gpt_image_2_5_payload(prompt="a poster", model="gpt-image-2-5-sunburst")

    assert "resolution" not in payload["input"]
    assert "background" not in payload["input"]


def test_gpt_image_2_5_full_slug_forces_the_mode_and_rejects_a_mismatch():
    payload = build_gpt_image_2_5_payload(
        prompt="edit",
        model="gpt-image-2-5-flare-image-to-image",
        image_urls=["https://example.com/in.png"],
    )
    assert payload["model"] == "gpt-image-2-5-flare-image-to-image"

    with pytest.raises(ValueError, match="image-to-image model but no images"):
        build_gpt_image_2_5_payload(prompt="x", model="gpt-image-2-5-flare-image-to-image")

    with pytest.raises(ValueError, match="text-to-image model but images"):
        build_gpt_image_2_5_payload(
            prompt="x",
            model="gpt-image-2-5-sunburst-text-to-image",
            image_urls=["https://example.com/in.png"],
        )


def test_gpt_image_2_5_rejects_more_than_sixteen_input_images():
    with pytest.raises(ValueError, match="at most 16"):
        build_gpt_image_2_5_payload(
            prompt="edit",
            image_urls=[f"https://example.com/{n}.png" for n in range(17)],
        )


def test_gpt_image_2_5_aspect_ratio_enums_differ_per_mode():
    # 5:4 is image-to-image only; 9:8 is text-to-image only.
    assert build_gpt_image_2_5_payload(
        prompt="edit", image_urls=["https://example.com/in.png"], aspect_ratio="5:4"
    )["input"]["aspect_ratio"] == "5:4"
    with pytest.raises(ValueError, match="Unsupported aspect_ratio"):
        build_gpt_image_2_5_payload(prompt="draw", aspect_ratio="5:4")

    assert build_gpt_image_2_5_payload(prompt="draw", aspect_ratio="9:8")["input"]["aspect_ratio"] == "9:8"
    with pytest.raises(ValueError, match="Unsupported aspect_ratio"):
        build_gpt_image_2_5_payload(
            prompt="edit", image_urls=["https://example.com/in.png"], aspect_ratio="9:8"
        )


def test_gpt_image_2_5_rejects_high_resolution_on_a_one_k_only_aspect_ratio():
    with pytest.raises(ValueError, match="supports 1K only"):
        build_gpt_image_2_5_payload(prompt="draw", aspect_ratio="27:16", resolution="4K")

    assert build_gpt_image_2_5_payload(
        prompt="draw", aspect_ratio="27:16", resolution="1K"
    )["input"]["resolution"] == "1K"


def test_gpt_image_2_5_rejects_unknown_resolution_background_and_variant():
    with pytest.raises(ValueError, match="Unsupported resolution"):
        build_gpt_image_2_5_payload(prompt="x", resolution="8K")
    with pytest.raises(ValueError, match="Unsupported background"):
        build_gpt_image_2_5_payload(prompt="x", background="blurred")
    with pytest.raises(ValueError, match="Unsupported GPT Image 2.5 variant"):
        build_gpt_image_2_5_payload(prompt="x", model="gpt-image-2-5-supernova")


def test_gpt_image_2_5_slugs_route_to_the_market_endpoints():
    from kie_cli.routes import MARKET_STATUS_ENDPOINT, route_for_model
    from kie_cli.payloads import GPT_IMAGE_2_5_MODELS

    for slug in GPT_IMAGE_2_5_MODELS:
        route = route_for_model(slug)
        assert route.route == "market"
        assert route.status_endpoint == MARKET_STATUS_ENDPOINT
