# RSpace MCP server

Exposes some RSpace API endpoints to LLMs

To run, install uv and python then add this to your Claude or VS Code mcp.json

```json
{
  "rspace": {
    "command": "uv",
    "args": [
      "--directory",
      "<full path to this directory>",
      "run",
      "main.py"
    ],
    "env": {
      "RSPACE_API_KEY": "${input:rspace-apikey}",
      "RSPACE_URL": "${input:rspace-url}"
    }
  }
}
```