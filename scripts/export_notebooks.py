"""Export Clementine notebooks to local ipynb files via Fabric MCP."""
import json
import subprocess
import sys

WORKSPACE = "Clementine [prod]"
OUT_DIR = r"E:\2026\ClaudesCorner\projects\clementine\notebooks"

NOTEBOOKS = {
    "Silver_Gold_ExecutionBook": "11349b54-a5df-4728-9437-bb3f6f865407",
    "Silver_ExecutionBook": "578491a0-85d2-4797-a5b9-b41c66e39d52",
    "Gold_ExecutionBook": "fbb844d2-1968-4d12-bfea-b38650851d5c",
}

# This script is meant to be called from Claude Code which has the MCP connection.
# For now, just take JSON from stdin and write it.
if __name__ == "__main__":
    name = sys.argv[1]
    raw = sys.stdin.read()
    # The MCP returns {"result": "<json-string>"}, parse it
    try:
        data = json.loads(raw)
        if "result" in data:
            notebook = json.loads(data["result"])
        else:
            notebook = data
    except json.JSONDecodeError:
        notebook = json.loads(raw)

    outpath = f"{OUT_DIR}\\{name}.ipynb"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    print(f"Saved {outpath} ({len(json.dumps(notebook))} chars)")
