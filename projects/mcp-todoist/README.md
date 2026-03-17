# mcp-todoist

MCP server for Todoist integration — manage tasks, projects, and labels from Claude.

## Usage

```bash
npm install
npm run build
```

Add to your Claude MCP config:
```json
{
  "mcpServers": {
    "todoist": {
      "command": "node",
      "args": ["path/to/mcp-todoist/dist/index.js"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```
