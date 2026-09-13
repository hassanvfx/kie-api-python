"""Registry-driven synchronous LLM transports for KIE.

KIE exposes incompatible contracts. A model selects a transport as well as a
name: Claude uses Anthropic Messages, GPT-5.2 uses Chat Completions, and
current GPT/Codex models use OpenAI Responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


Transport = Literal["anthropic_messages", "openai_chat", "openai_responses", "gemini_chat"]


@dataclass(frozen=True)
class LLMModel:
    id: str
    transport: Transport


GPT_5_2 = "gpt-5-2"
GEMINI_3_PRO = "gemini-3-pro"
CLAUDE_MODELS = (
    "claude-opus-4-7", "claude-opus-4-8", "claude-fable-5", "claude-sonnet-5",
    "claude-haiku-4-5", "claude-opus-4-5", "claude-opus-4-6", "claude-opus-5",
    "claude-sonnet-4-5", "claude-sonnet-4-6",
)
OPENAI_RESPONSES_MODELS = (
    "gpt-5-4", "gpt-5-5", "gpt-5-6-luna", "gpt-6-astra", "gpt-5-6-terra",
    "gpt-5-6-sol", "gpt-codex",
)
# Current KIE catalog, transcribed from https://docs.kie.ai/llms.txt on
# 2026-09-12. Adding a model is one data row plus a test, never a new branch.
LLM_MODELS: dict[str, LLMModel] = {
    **{model: LLMModel(model, "anthropic_messages") for model in CLAUDE_MODELS},
    GPT_5_2: LLMModel(GPT_5_2, "openai_chat"),
    **{model: LLMModel(model, "openai_responses") for model in OPENAI_RESPONSES_MODELS},
    GEMINI_3_PRO: LLMModel(GEMINI_3_PRO, "gemini_chat"),
}
SUPPORTED_LLM_MODELS = tuple(LLM_MODELS)


def resolve_llm_model(model: str) -> LLMModel:
    try:
        return LLM_MODELS[model]
    except KeyError as exc:
        raise ValueError(f"Unsupported LLM model {model!r}. Supported: {', '.join(SUPPORTED_LLM_MODELS)}") from exc


def route_name(transport: Transport) -> str:
    """Stable, user-facing route labels; preserve chat-completions compatibility."""
    if transport in {"openai_chat", "gemini_chat"}:
        return "chat_completions"
    if transport == "openai_responses":
        return "responses"
    return "anthropic_messages"


def _content(prompt: str, image_urls: list[str] | None, *, text_type: str = "text") -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [{"type": text_type, "text": prompt}]
    for image_url in image_urls or []:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    return content


def build_gpt_5_2_chat_payload(
    *, prompt: str, image_urls: list[str] | None = None, reasoning_effort: str = "high",
    web_search: bool = False, max_completion_tokens: int | None = None,
) -> dict[str, Any]:
    """Legacy GPT-5.2 Chat Completions payload, kept compatible verbatim."""
    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": _content(prompt, image_urls)}],
        "reasoning_effort": reasoning_effort,
    }
    if max_completion_tokens is not None:
        payload["max_completion_tokens"] = max_completion_tokens
    if web_search:
        payload["tools"] = [{"type": "function", "function": {"name": "web_search"}}]
    return payload


def build_openai_responses_payload(
    *, model: str, prompt: str, image_urls: list[str] | None = None, reasoning_effort: str = "high",
    web_search: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model, "stream": False,
        "input": [{"role": "user", "content": _content(prompt, image_urls, text_type="input_text")}],
        "reasoning": {"effort": reasoning_effort},
    }
    if web_search:
        payload["tools"] = [{"type": "web_search"}]
    return payload


def build_anthropic_messages_payload(
    *, model: str, prompt: str, image_urls: list[str] | None = None, thinking: bool = False,
    max_completion_tokens: int | None = None,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for image_url in image_urls or []:
        content.append({"type": "image", "source": {"type": "url", "url": image_url}})
    payload: dict[str, Any] = {"model": model, "messages": [{"role": "user", "content": content}], "stream": False}
    if thinking:
        payload["thinkingFlag"] = True
    if max_completion_tokens is not None:
        payload["max_tokens"] = max_completion_tokens
    return payload


def build_gemini_vision_payload(
    *, prompt: str, image_urls: list[str], reasoning_effort: str = "high", include_thoughts: bool = False,
    web_search: bool = False, stream: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": _content(prompt, image_urls)}],
        "stream": stream, "include_thoughts": include_thoughts, "reasoning_effort": reasoning_effort,
    }
    if web_search:
        payload["tools"] = [{"type": "function", "function": {"name": "googleSearch"}}]
    return payload


def build_llm_payload(
    *, model: str, prompt: str, image_urls: list[str] | None = None, reasoning_effort: str = "high",
    web_search: bool = False, max_completion_tokens: int | None = None, thinking: bool = False,
    include_thoughts: bool = False,
) -> dict[str, Any]:
    spec = resolve_llm_model(model)
    if spec.transport == "anthropic_messages":
        if web_search:
            raise ValueError("KIE Claude messages does not document built-in web search")
        return build_anthropic_messages_payload(model=model, prompt=prompt, image_urls=image_urls, thinking=thinking, max_completion_tokens=max_completion_tokens)
    if spec.transport == "openai_chat":
        return build_gpt_5_2_chat_payload(prompt=prompt, image_urls=image_urls, reasoning_effort=reasoning_effort, web_search=web_search, max_completion_tokens=max_completion_tokens)
    if spec.transport == "openai_responses":
        if max_completion_tokens is not None:
            raise ValueError("KIE Responses models do not document --max-completion-tokens")
        return build_openai_responses_payload(model=model, prompt=prompt, image_urls=image_urls, reasoning_effort=reasoning_effort, web_search=web_search)
    return build_gemini_vision_payload(prompt=prompt, image_urls=image_urls or [], reasoning_effort=reasoning_effort, include_thoughts=include_thoughts, web_search=web_search)


def _success(*, response: dict[str, Any], model: str, text: str, finish_reason: str | None) -> dict[str, Any]:
    if not text:
        return {"ok": False, "model": response.get("model") or model, "status": "failed", "error": {"code": "NO_COMPLETION_TEXT", "message": "LLM response did not include output text"}, "raw": response}
    return {"ok": True, "model": response.get("model") or model, "status": "succeeded", "text": text, "finishReason": finish_reason, "usage": response.get("usage"), "raw": response}


def normalize_chat_completion(response: dict[str, Any], *, model: str = GPT_5_2) -> dict[str, Any]:
    choices = response.get("choices") or []
    first = choices[0] or {} if choices else {}
    content = (first.get("message") or {}).get("content")
    text = content if isinstance(content, str) else _extract_text_from_content_parts(content or [])
    return _success(response=response, model=model, text=text, finish_reason=first.get("finish_reason"))


def normalize_anthropic_message(response: dict[str, Any], *, model: str) -> dict[str, Any]:
    return _success(response=response, model=model, text=_extract_text_from_content_parts(response.get("content") or []), finish_reason=response.get("stop_reason"))


def normalize_openai_response(response: dict[str, Any], *, model: str) -> dict[str, Any]:
    parts: list[Any] = []
    for item in response.get("output") or []:
        if isinstance(item, dict) and item.get("type") == "message":
            parts.extend(item.get("content") or [])
    text = str(response.get("output_text") or "") or _extract_text_from_content_parts(parts)
    return _success(response=response, model=model, text=text, finish_reason=response.get("status"))


def normalize_llm_response(response: dict[str, Any], *, model: str) -> dict[str, Any]:
    transport = resolve_llm_model(model).transport
    if transport == "anthropic_messages":
        return normalize_anthropic_message(response, model=model)
    if transport == "openai_responses":
        return normalize_openai_response(response, model=model)
    return normalize_chat_completion(response, model=model)


def _extract_text_from_content_parts(parts: list[Any]) -> str:
    chunks: list[str] = []
    for part in parts:
        if isinstance(part, dict):
            if part.get("type") not in {None, "text", "output_text"}:
                continue
            value = part.get("text") or part.get("content")
            if isinstance(value, str):
                chunks.append(value)
        elif isinstance(part, str):
            chunks.append(part)
    return "".join(chunks)
