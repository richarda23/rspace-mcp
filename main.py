from typing import Annotated, Dict, List

from fastmcp import FastMCP
from rspace_client.eln import eln as e
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Document(BaseModel):
    name: str = Field("document's name")
    globalId: str = Field(description="Global identifier"),
    created: str = Field(description="The document's creation date")


class RSField(BaseModel):
    textContent: str = Field(description="text content of a field as HTML")


class FullDocument(BaseModel):
    content: str = Field(description="concatenated text content from all fields")


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
    if page_size > 200 or page_size < 0:
        raise ValueError("page size must be less than 200")
    resp = eln_cli.get_documents(page_size=page_size)
    return resp['documents']


@mcp.tool(tags={"rspace"}, name="get_single_Rspace_document")
def get_document(doc_id: int | str) -> FullDocument:
    """
    Gets a single RSpace document by its numeric id or string globalId
    """
    resp = eln_cli.get_document(doc_id)
    resp['content'] = ''
    for fld in resp['fields']:
        resp['content'] = resp['content'] + fld['content']
    return resp


@mcp.tool(tags={"rspace"}, name="createNewNotebook")
def create_notebook(
        name: Annotated[str, Field(description="The name of the notebook to create")],
) -> Dict[str, any]:
    """
    Creates a new RSpace notebook
    """
    resp = eln_cli.create_folder(name, notebook=True)
    return resp


@mcp.tool(tags={"rspace"}, name="createNotebookEntry")
def create_notebook_entry(
        name: Annotated[str, Field(description="The name of the notebook entry")],
        text_content: Annotated[str, Field(description="html or plain text content ")],
        notebook_id: Annotated[int, Field(description="The id of the notebook to add the entry")],
) -> Dict[str, any]:
    """
    Adds content as a new notebook entry in an existing notebook
    """
    resp = eln_cli.create_document(name, parent_folder_id=notebook_id, fields=[{'content': text_content}])
    return resp


@mcp.tool(tags={"rspace"}, name="tagDocumentOrNotebookEntry")
def tag_document(
        doc_id: int | str,
        tags: Annotated[List[str], Field(description="One or more tags in a list")]
) -> Dict[str, any]:
    """
    Tags a document or notebook entry with one or more tags
    :param doc_id:
    :param tags:
    :return:
    """
    resp = eln_cli.update_document(document_id=doc_id, tags=tags)
    return resp


if __name__ == "__main__":
    mcp.run()
