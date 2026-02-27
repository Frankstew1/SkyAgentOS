"""MCP server exposing shared OpenClaw workspace read/write operations."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

WORKSPACE = Path(os.getenv("MCP_WORKSPACE_PATH", "/workspace/shared"))
WORKSPACE.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("skyagentos-workspace")


@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Read a UTF-8 text file from the shared workspace."""
    target = (WORKSPACE / path).resolve()
    if WORKSPACE not in target.parents and target != WORKSPACE:
        raise ValueError("Path escapes workspace root")
    return target.read_text(encoding="utf-8")


@mcp.tool()
def write_workspace_file(path: str, content: str) -> str:
    """Write a UTF-8 text file into the shared workspace."""
    target = (WORKSPACE / path).resolve()
    if WORKSPACE not in target.parents and target != WORKSPACE:
        raise ValueError("Path escapes workspace root")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"wrote:{path}"


if __name__ == "__main__":
    mcp.run()
