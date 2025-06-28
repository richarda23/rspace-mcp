from fastmcp import FastMCP
from rspace_client.eln import eln as e
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Document(BaseModel):
    name: str = Field("document's name")
    globalId: str = Field(description="Global identifier"),
    created: str = Field(description="The document's creation date")


mcp = FastMCP("RSpace MCP Server")
load_dotenv()
api_key = os.getenv("RSPACE_API_KEY")
api_url = os.getenv("RSPACE_URL")
eln_cli = e.ELNClient(api_url, api_key);


@mcp.tool(tags={"rspace"})
def status() -> str:
    """
    Determines if RSpace server is running, returning its status
    """
    resp = eln_cli.get_status()
    return resp['message']


@mcp.tool(tags={"rspace"})
def get_documents(page_size: int = 20) -> list[Document]:
    """
    Gets most recent  RSpace documents up to 100 at a time
    """
    resp = eln_cli.get_documents(page_size=page_size)
    return resp['documents']


if __name__ == "__main__":
    mcp.run()
