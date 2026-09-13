import json

from kie_cli.cli import main
from kie_cli.llm import (
    CLAUDE_MODELS,
    OPENAI_RESPONSES_MODELS,
    LLM_MODELS,
    build_anthropic_messages_payload,
    build_gemini_vision_payload,
    build_gpt_5_2_chat_payload,
    build_openai_responses_payload,
    normalize_chat_completion,
    normalize_llm_response,
)


def test_current_anthropic_and_openai_catalog_is_registry_backed():
    expected = {
        "claude-opus-4-7", "claude-opus-4-8", "claude-fable-5", "claude-sonnet-5",
        "claude-haiku-4-5", "claude-opus-4-5", "claude-opus-4-6", "claude-opus-5",
        "claude-sonnet-4-5", "claude-sonnet-4-6", "gpt-5-2", "gpt-5-4", "gpt-5-5",
        "gpt-5-6-luna", "gpt-6-astra", "gpt-5-6-terra", "gpt-5-6-sol", "gpt-codex",
    }

    assert expected <= set(LLM_MODELS)
    assert set(CLAUDE_MODELS) <= set(LLM_MODELS)
    assert set(OPENAI_RESPONSES_MODELS) <= set(LLM_MODELS)
    assert LLM_MODELS["claude-opus-4-8"].transport == "anthropic_messages"
    assert LLM_MODELS["gpt-5-5"].transport == "openai_responses"


def test_build_anthropic_messages_payload_with_image_and_thinking():
    payload = build_anthropic_messages_payload(
        model="claude-opus-4-8",
        prompt="Inspect the label.",
        image_urls=["https://example.com/label.png"],
        thinking=True,
        max_completion_tokens=128,
    )

    assert payload == {
        "model": "claude-opus-4-8",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "Inspect the label."},
            {"type": "image", "source": {"type": "url", "url": "https://example.com/label.png"}},
        ]}],
        "stream": False,
        "thinkingFlag": True,
        "max_tokens": 128,
    }


def test_build_openai_responses_payload_and_normalize_response():
    payload = build_openai_responses_payload(
        model="gpt-5-5",
        prompt="Describe the image.",
        image_urls=["https://example.com/ref.png"],
        reasoning_effort="xhigh",
        web_search=True,
    )

    assert payload["input"] == [{"role": "user", "content": [
        {"type": "input_text", "text": "Describe the image."},
        {"type": "image_url", "image_url": {"url": "https://example.com/ref.png"}},
    ]}]
    assert payload["reasoning"] == {"effort": "xhigh"}
    assert payload["tools"] == [{"type": "web_search"}]
    result = normalize_llm_response(
        {"model": "gpt-5-5", "status": "completed", "output_text": "A clear label.", "usage": {"total_tokens": 7}},
        model="gpt-5-5",
    )
    assert result["ok"] is True
    assert result["text"] == "A clear label."


def test_build_gpt_5_2_chat_payload():
    payload = build_gpt_5_2_chat_payload(
        prompt="Write a tagline.",
        reasoning_effort="low",
    )

    assert payload == {
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Write a tagline."}],
            }
        ],
        "reasoning_effort": "low",
    }


def test_build_gpt_5_2_chat_payload_with_image():
    payload = build_gpt_5_2_chat_payload(
        prompt="What is in this image?",
        image_urls=["https://example.com/reference.png"],
        reasoning_effort="low",
    )

    assert payload == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/reference.png"},
                    },
                ],
            }
        ],
        "reasoning_effort": "low",
    }


def test_build_gpt_5_2_chat_payload_with_web_search():
    payload = build_gpt_5_2_chat_payload(
        prompt="What changed today?",
        reasoning_effort="high",
        web_search=True,
    )

    assert payload["tools"] == [{"type": "function", "function": {"name": "web_search"}}]


def test_build_gpt_5_2_chat_payload_with_web_search_and_image():
    payload = build_gpt_5_2_chat_payload(
        prompt="What changed today?",
        image_urls=["https://example.com/reference.png"],
        reasoning_effort="high",
        web_search=True,
    )

    assert payload["tools"] == [{"type": "function", "function": {"name": "web_search"}}]
    assert payload["messages"][0]["content"][1] == {
        "type": "image_url",
        "image_url": {"url": "https://example.com/reference.png"},
    }


def test_build_gemini_vision_payload():
    payload = build_gemini_vision_payload(
        prompt="What do you see?",
        image_urls=["https://example.com/reference.png"],
        reasoning_effort="low",
    )

    assert payload == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/reference.png"},
                    },
                ],
            }
        ],
        "stream": False,
        "include_thoughts": False,
        "reasoning_effort": "low",
    }


def test_build_gemini_vision_payload_with_web_search():
    payload = build_gemini_vision_payload(
        prompt="What current context matters?",
        image_urls=["https://example.com/reference.png"],
        web_search=True,
    )

    assert payload["tools"] == [{"type": "function", "function": {"name": "googleSearch"}}]


def test_normalize_chat_completion_success():
    result = normalize_chat_completion(
        {
            "id": "chatcmpl_123",
            "model": "gpt-5-2",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello from KIE."},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 4, "total_tokens": 9},
        }
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["text"] == "Hello from KIE."
    assert result["usage"]["total_tokens"] == 9


def test_normalize_chat_completion_missing_text():
    result = normalize_chat_completion({"model": "gpt-5-2", "choices": []})

    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["error"]["code"] == "NO_COMPLETION_TEXT"


def test_cli_llm_dry_run_local_image(capsys):
    exit_code = main(
        [
            "llm",
            "gpt-5-2",
            "--prompt",
            "What do you see?",
            "--image",
            "tests/fixtures/images/synthetic_reference_a.png",
            "--reasoning-effort",
            "low",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["status"] == "dry_run"
    assert output["model"] == "gpt-5-2"
    assert output["kind"] == "chat_completions"
    assert output["route"] == "chat_completions"
    assert output["resolvedMedia"][0]["uploaded"] is True
    assert output["resolvedMedia"][0]["resolved_url"] == "dry-run://uploaded/synthetic_reference_a.png"
    content = output["payload"]["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "What do you see?"}
    assert content[1] == {
        "type": "image_url",
        "image_url": {"url": "dry-run://uploaded/synthetic_reference_a.png"},
    }
    assert output["payload"]["reasoning_effort"] == "low"


def test_cli_llm_dry_run_claude_opus_4_8(capsys):
    exit_code = main(
        [
            "llm",
            "claude-opus-4-8",
            "--prompt",
            "Inspect this reference.",
            "--image",
            "tests/fixtures/images/synthetic_reference_a.png",
            "--thinking",
            "--max-completion-tokens",
            "128",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["route"] == "anthropic_messages"
    assert output["kind"] == "anthropic_messages"
    assert output["payload"]["model"] == "claude-opus-4-8"
    assert output["payload"]["thinkingFlag"] is True
    assert output["payload"]["messages"][0]["content"][1]["type"] == "image"


def test_cli_llm_dry_run_gpt_5_5(capsys):
    exit_code = main(
        [
            "llm",
            "gpt-5-5",
            "--prompt",
            "Describe this reference.",
            "--reasoning-effort",
            "xhigh",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["route"] == "responses"
    assert output["kind"] == "responses"
    assert output["payload"]["model"] == "gpt-5-5"
    assert output["payload"]["reasoning"] == {"effort": "xhigh"}


def test_cli_gemini_dry_run_local_image(capsys):
    exit_code = main(
        [
            "gemini",
            "gemini-3-pro",
            "--prompt",
            "What do you see?",
            "--image",
            "tests/fixtures/images/synthetic_reference_a.png",
            "--reasoning-effort",
            "low",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["status"] == "dry_run"
    assert output["model"] == "gemini-3-pro"
    assert output["route"] == "chat_completions"
    assert output["resolvedMedia"][0]["uploaded"] is True
    assert output["resolvedMedia"][0]["resolved_url"] == "dry-run://uploaded/synthetic_reference_a.png"
    content = output["payload"]["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "What do you see?"}
    assert content[1] == {
        "type": "image_url",
        "image_url": {"url": "dry-run://uploaded/synthetic_reference_a.png"},
    }
    assert output["payload"]["stream"] is False
    assert output["payload"]["include_thoughts"] is False
    assert output["payload"]["reasoning_effort"] == "low"


def test_cli_llm_dry_run(capsys):
    exit_code = main(
        [
            "llm",
            "gpt-5-2",
            "--prompt",
            "Write a tagline.",
            "--reasoning-effort",
            "low",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["model"] == "gpt-5-2"
    assert output["kind"] == "chat_completions"
    assert output["payload"]["messages"][0]["content"][0]["text"] == "Write a tagline."
    assert output["payload"]["reasoning_effort"] == "low"
