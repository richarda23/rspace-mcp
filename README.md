# RSpace MCP server

Exposes some RSpace API endpoints to LLM agents

To run,[ install `uv`](https://docs.astral.sh/uv/#highlights) and `python`, then add this to your Claude or VS Code mcp.json

- clone this repo
- run `uv sync` to install dependencies
- create a `.env` file in this folder. Add 
  - RSPACE_URL=RSpace URL # e.g. https://community.researchspace.com 
  - RSPACE_API_KEY=your API key
  
Configure your LLM app. Below is config for VSCode Copilot.

For Claude Desktop  add the "rspace" server definition below to your MCP config file.

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


