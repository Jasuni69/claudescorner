"""
markitdown-mcp — MCP stdio server wrapping microsoft/markitdown.

Converts PDF, DOCX, PPTX, XLSX, HTML, CSV, images → Markdown.
Uses the markitdown Python library (pip install markitdown).

Tools:
    convert_file     — convert a local file path to Markdown
    convert_url      — fetch a URL and convert to Markdown
    convert_base64   — convert base64-encoded bytes to Markdown

Usage:
    python server.py
"""
from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

try:
    from markitdown import MarkItDown
except ImportError:
    raise SystemExit("markitdown not installed: pip install markitdown")

mcp = FastMCP("markitdown")
_converter = MarkItDown()


@mcp.tool()
def convert_file(path: str, file_extension: str | None = None) -> str:
    """Convert a local file to Markdown.

    Args:
        path: Absolute path to the file (PDF, DOCX, PPTX, XLSX, HTML, CSV, image, etc.)
        file_extension: Optional explicit extension hint (e.g. '.pdf'). Auto-detected if omitted.

    Returns:
        Markdown text extracted from the file.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = file_extension or p.suffix or None
    result = _converter.convert(str(p), file_extension=ext)
    return result.text_content


@mcp.tool()
def convert_url(url: str) -> str:
    """Fetch a URL and convert its content to Markdown.

    Args:
        url: HTTP/HTTPS URL to fetch and convert.

    Returns:
        Markdown text extracted from the page or document.
    """
    result = _converter.convert(url)
    return result.text_content


@mcp.tool()
def convert_base64(data: str, file_extension: str) -> str:
    """Convert base64-encoded file bytes to Markdown.

    Useful for piping binary content without writing to disk first.

    Args:
        data: Base64-encoded file bytes.
        file_extension: File extension indicating format (e.g. '.pdf', '.docx').

    Returns:
        Markdown text extracted from the file.
    """
    raw = base64.b64decode(data)
    suffix = file_extension if file_extension.startswith(".") else f".{file_extension}"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(raw)
        tmp_path = f.name
    try:
        result = _converter.convert(tmp_path, file_extension=suffix)
        return result.text_content
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    mcp.run()
