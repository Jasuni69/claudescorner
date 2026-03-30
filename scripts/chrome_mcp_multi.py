"""Call multiple chrome-devtools MCP tools in sequence, same session."""
import json
import subprocess
import sys

NODE = "node"
MCP_BIN = "C:/Users/JasonNicolini/AppData/Roaming/npm/node_modules/chrome-devtools-mcp/build/src/bin/chrome-devtools-mcp.js"
BROWSER_URL = "http://127.0.0.1:9222"


def call_tools(calls: list[tuple[str, dict]]) -> list[dict]:
    """calls: list of (tool_name, arguments) tuples."""
    init_msg = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "claude-bridge", "version": "1.0"}
        }
    })

    messages = [init_msg]
    for i, (tool_name, arguments) in enumerate(calls, start=2):
        messages.append(json.dumps({
            "jsonrpc": "2.0", "id": i, "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}}
        }))

    proc = subprocess.Popen(
        [NODE, MCP_BIN, "--browserUrl", BROWSER_URL],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace"
    )

    proc.stdin.write("\n".join(messages) + "\n")
    proc.stdin.close()

    results = []
    max_id = len(calls) + 1  # last expected id
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if msg.get("id", 0) >= 2:
                results.append(msg)
            if msg.get("id") == max_id:
                break
        except json.JSONDecodeError:
            continue

    proc.kill()
    return results


if __name__ == "__main__":
    # Usage: python chrome_mcp_multi.py '[["tool1",{}],["tool2",{"arg":"val"}]]'
    calls_raw = json.loads(sys.argv[1])
    calls = [(c[0], c[1] if len(c) > 1 else {}) for c in calls_raw]
    results = call_tools(calls)
    for r in results:
        print(json.dumps(r, indent=2))
