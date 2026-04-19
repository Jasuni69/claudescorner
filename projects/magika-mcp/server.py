"""
magika-mcp — MCP stdio server wrapping google/magika file-type detection.

Detects 200+ file content types with ~99% accuracy at ~5ms/file.
Use as a pre-filter before markitdown-mcp or before Fabric ingestion.

Tools:
    detect_file    — detect content type of a local file path
    detect_bytes   — detect content type from base64-encoded bytes
    batch_detect   — detect content types for all files in a directory

Usage:
    pip install magika
    python server.py

To wire into settings.json mcpServers:
    "magika": {
        "command": "C:\\Python314\\python.exe",
        "args": ["E:\\2026\\ClaudesCorner\\projects\\magika-mcp\\server.py"]
    }
"""
from __future__ import annotations

import base64
import tempfile
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

try:
    from magika import Magika
except ImportError:
    raise SystemExit("magika not installed: pip install magika")

mcp = FastMCP("magika")
_magika = Magika()


@mcp.tool()
def detect_file(path: str, confidence_mode: str = "high-confidence") -> dict:
    """
    Detect the content type of a local file.

    Args:
        path: Absolute path to the file.
        confidence_mode: One of 'high-confidence', 'medium-confidence', 'best-guess'.
                         Defaults to 'high-confidence'.

    Returns:
        dict with keys: path, label, mime_type, description, score, is_text
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    result = _magika.identify_path(file_path)
    return _format_result(str(file_path), result)


@mcp.tool()
def detect_bytes(data_b64: str, filename: Optional[str] = None) -> dict:
    """
    Detect the content type of base64-encoded bytes.

    Args:
        data_b64: Base64-encoded file content.
        filename: Optional hint filename (not used for detection, only returned in output).

    Returns:
        dict with keys: path, label, mime_type, description, score, is_text
    """
    raw = base64.b64decode(data_b64)
    result = _magika.identify_bytes(raw)
    label = filename or "<bytes>"
    return _format_result(label, result)


@mcp.tool()
def batch_detect(directory: str, recursive: bool = True, extensions: Optional[list[str]] = None) -> list[dict]:
    """
    Detect content types for all files in a directory.

    Args:
        directory: Absolute path to directory.
        recursive: Whether to scan subdirectories. Default True.
        extensions: Optional list of file extensions to filter (e.g. ['.csv', '.parquet']).
                    If None, all files are scanned.

    Returns:
        List of detection dicts (same shape as detect_file).
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    pattern = "**/*" if recursive else "*"
    paths = [p for p in dir_path.glob(pattern) if p.is_file()]

    if extensions:
        exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}
        paths = [p for p in paths if p.suffix.lower() in exts]

    if not paths:
        return []

    results = _magika.identify_paths(paths)
    return [_format_result(str(p), r) for p, r in zip(paths, results)]


def _format_result(label: str, result) -> dict:
    ct = result.output
    # score moved to MagikaResult top-level in recent versions
    score = getattr(result, "score", None)
    return {
        "path": label,
        "label": ct.label,
        "mime_type": ct.mime_type,
        "description": ct.description,
        "score": round(score, 4) if score is not None else None,
        "is_text": ct.is_text,
        "group": getattr(ct, "group", None),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
