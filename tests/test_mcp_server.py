import importlib.util
import json

import pytest

from kie_cli import mcp_server


def test_mcp_supported_models_resource_is_valid_json():
    payload = json.loads(mcp_server.resource_supported_models())

    assert payload["schemaVersion"] == 1
    assert any(workflow["family"] == "image" for workflow in payload["workflows"])
    assert any("kie_generate_image" in workflow["tools"] for workflow in payload["workflows"])


def test_mcp_tool_contracts_resource_is_valid_json():
    payload = json.loads(mcp_server.resource_tool_contracts())
    names = {tool["name"] for tool in payload["tools"]}

    assert "kie_generate_image" in names
    assert "kie_wait_for_job" in names


def test_mcp_agent_quickstart_resource_mentions_dry_run():
    text = mcp_server.resource_agent_quickstart()

    assert "dry-run" in text
    assert "kie://models/supported" in text


def test_mcp_comprehensive_guide_resource_reads_repo_doc():
    text = mcp_server.resource_comprehensive_guide()

    assert "KIE CLI Comprehensive Guide" in text


def test_mcp_image_dry_run_builds_gpt_image_payload():
    result = mcp_server.kie_generate_image(
        "gpt-image-2",
        "make a product render",
        image=["https://example.com/ref.png"],
    )

    assert result["ok"] is True
    assert result["status"] == "dry_run"
    assert result["model"] == "gpt-image-2-image-to-image"
    assert result["payload"]["input"]["input_urls"] == ["https://example.com/ref.png"]
    assert result["resolvedMedia"][0]["uploaded"] is False


def test_mcp_video_dry_run_builds_veo_payload():
    result = mcp_server.kie_generate_video(
        "veo3",
        "cinematic dolly shot",
        veo_model="veo3_fast",
    )

    assert result["status"] == "dry_run"
    assert result["route"] == "veo"
    assert result["model"] == "veo3_fast"
    assert result["payload"]["generationType"] == "TEXT_2_VIDEO"


def test_mcp_chat_dry_run_builds_gpt_payload():
    result = mcp_server.kie_chat_completion(
        "gpt-5-2",
        "describe this image",
        image=["https://example.com/ref.png"],
        max_completion_tokens=128,
    )

    assert result["status"] == "dry_run"
    assert result["kind"] == "chat_completions"
    assert result["model"] == "gpt-5-2"
    assert result["payload"]["max_completion_tokens"] == 128


def test_mcp_suno_music_dry_run_builds_payload():
    result = mcp_server.kie_suno_music(
        "dreamy synth-pop",
        custom_mode=True,
        instrumental=True,
        style="synth-pop",
        title="Neon Rain",
    )

    assert result["status"] == "dry_run"
    assert result["model"] == "suno-music"
    assert result["payload"]["customMode"] is True
    assert result["payload"]["instrumental"] is True


def test_mcp_prompt_builders_return_actionable_prompts():
    image_prompt = mcp_server.kie_image_prompt_builder("a glass perfume bottle")
    video_prompt = mcp_server.kie_video_prompt_builder("a city at night")
    debug_prompt = mcp_server.kie_debug_failed_job("job_123", "nano-banana-pro")

    assert "glass perfume bottle" in image_prompt
    assert "city at night" in video_prompt
    assert "kie_get_job_status" in debug_prompt


def test_create_mcp_server_has_helpful_message_without_optional_dependency():
    if importlib.util.find_spec("mcp") is not None:
        pytest.skip("MCP SDK is installed; optional dependency error path is not active.")

    with pytest.raises(RuntimeError, match="MCP SDK is not installed"):
        mcp_server.create_mcp_server()
