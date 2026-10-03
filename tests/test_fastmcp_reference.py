"""Verified FastMCP 4 patterns (spike 1). Lanes copy these instead of guessing the API.

- a tool returning a TypedDict gets an output schema and structuredContent
- a ui:// resource plus AppConfig on the tool gives an MCP App
- fastmcp.Client(server) calls tools in memory, no Claude Desktop needed
- MCP SDK v2 naming: Tool.output_schema (not outputSchema); read results from
  result.structured_content (a dict). result.data is an object, not a dict.
"""
import asyncio
from typing import TypedDict

from fastmcp import Client, FastMCP
from fastmcp.apps.config import AppConfig


class Echo(TypedDict):
    text: str
    length: int


ref = FastMCP("reference")


@ref.resource("ui://reference/echo.html")
def echo_view() -> str:
    return "<html><body><div id='out'></div></body></html>"


@ref.tool(app=AppConfig(resource_uri="ui://reference/echo.html"))
def echo(text: str) -> Echo:
    """Echo text back with its length."""
    return {"text": text, "length": len(text)}


async def _run():
    async with Client(ref) as c:
        tools = {t.name: t for t in await c.list_tools()}
        result = await c.call_tool("echo", {"text": "abc"})
        resources = [str(r.uri) for r in await c.list_resources()]
    return tools, result, resources


def test_reference_server():
    tools, result, resources = asyncio.run(_run())
    tool = tools["echo"]
    assert tool.output_schema["properties"]["length"]["type"] == "integer"
    assert tool.meta["ui"]["resourceUri"] == "ui://reference/echo.html"
    assert result.structured_content == {"text": "abc", "length": 3}
    assert "ui://reference/echo.html" in resources
