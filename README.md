# RSpace MCP server

Exposes some RSpace API endpoints to LLM agents

To run, install `uv` and `python`, then add this to your Claude or VS Code mcp.json

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "rspace-apikey",
      "description": "RSpace API Key",
      "password": true
    },
    {
      "type": "promptString",
      "id": "rspace-url",
      "description": "RSpace base URL",
      "password": false
    }
  ],
  "servers": {
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
}
```