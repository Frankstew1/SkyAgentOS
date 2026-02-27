"""MCP hub stub: register/discover tool and resource endpoints."""

from __future__ import annotations


def registry() -> dict:
    return {"servers": ["workspace-mcp", "browser-mcp", "desktop-mcp"]}
