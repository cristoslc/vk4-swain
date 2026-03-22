"""MCP server with stdio transport."""

from __future__ import annotations

from mcp.server import Server
from mcp.server.stdio import stdio_server

from vk.adapters.mcp_tools import register_tools
from vk.config import Config


def run_stdio_server(config: Config) -> None:
    """Launch the MCP server over stdin/stdout."""
    import asyncio

    server = Server("vk")
    register_tools(server, config)

    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(_run())
