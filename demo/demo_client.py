"""Call the server in memory and print the text a host without structured-output support would see.

Usage: uv run python demo/demo_client.py screen DEMO-03 hil-a-residential
       uv run python demo/demo_client.py search "lead HIL residential"
"""
import asyncio
import sys

from fastmcp import Client

from site_assess.server import mcp


async def main(argv: list[str]) -> None:
    if argv[0] == "screen":
        tool, args = "screen_lab_results", {"site_id": argv[1], "criteria_set": argv[2]}
    else:
        tool, args = "search_guidance", {"query": argv[1], "top_k": 3}
    async with Client(mcp) as c:
        print((await c.call_tool(tool, args)).content[0].text)


asyncio.run(main(sys.argv[1:]))
