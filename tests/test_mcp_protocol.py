import importlib.util
import json
import sys

import pytest


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("mcp") is None,
    reason='Install MCP support with: python -m pip install -e ".[mcp]"',
)


async def _run_stdio_smoke():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "kie_cli.mcp_server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            resources = await session.list_resources()
            prompts = await session.list_prompts()
            supported = await session.read_resource("kie://models/supported")
            dry_run = await session.call_tool(
                "kie_generate_image",
                {
                    "model": "gpt-image-2",
                    "prompt": "A cinematic product render",
                    "dry_run": True,
                },
            )

    dry_payload = json.loads(dry_run.content[0].text)
    supported_payload = json.loads(supported.contents[0].text)

    return {
        "server": init.serverInfo.name,
        "tools": {tool.name for tool in tools.tools},
        "resources": {str(resource.uri) for resource in resources.resources},
        "prompts": {prompt.name for prompt in prompts.prompts},
        "supported": supported_payload,
        "dry_run": dry_payload,
        "dry_run_is_error": dry_run.isError,
    }


def test_mcp_stdio_protocol_smoke():
    import anyio

    result = anyio.run(_run_stdio_smoke)

    assert result["server"] == "kie-api"
    assert "kie_generate_image" in result["tools"]
    assert "kie://models/supported" in result["resources"]
    assert "kie_image_prompt_builder" in result["prompts"]
    assert result["supported"]["schemaVersion"] == 1
    assert result["dry_run_is_error"] is False
    assert result["dry_run"]["status"] == "dry_run"
    assert result["dry_run"]["model"] == "gpt-image-2-text-to-image"
