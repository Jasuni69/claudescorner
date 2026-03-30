"""Thin wrapper to call chrome-devtools MCP tools via stdio."""
import json
import subprocess
import sys
import threading

NODE = "node"
MCP_BIN = "C:/Users/JasonNicolini/AppData/Roaming/npm/node_modules/chrome-devtools-mcp/build/src/bin/chrome-devtools-mcp.js"
BROWSER_URL = "http://127.0.0.1:9222"


def call_tool(tool_name: str, arguments: dict | None = None) -> dict:
    init_msg = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "claude-bridge", "version": "1.0"}
        }
    })
    call_msg = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments or {}}
    })

    proc = subprocess.Popen(
        [NODE, MCP_BIN, "--browserUrl", BROWSER_URL],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace"
    )

    # Write both messages then close stdin
    proc.stdin.write(init_msg + "\n")
    proc.stdin.write(call_msg + "\n")
    proc.stdin.close()

    # Read lines until we get our tool call response (id=2)
    lines = []
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        lines.append(line)
        try:
            msg = json.loads(line)
            if msg.get("id") == 2:
                proc.kill()
                return msg
        except json.JSONDecodeError:
            continue

    proc.kill()
    if lines:
        return json.loads(lines[-1])
    return {"error": "no response"}


if __name__ == "__main__":
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    result = call_tool(tool, args)
    print(json.dumps(result, indent=2))
