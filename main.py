import time
from typing import Annotated, Dict, List

from fastmcp import FastMCP, Context
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
def get_documents(context: Context, page_size: int = 20) -> list[Document]:
    """
    Gets most recent  RSpace documents up to 100 at a time
    """
    if page_size > 200 or page_size < 0:
        raise ValueError("page size must be less than 200")
    resp = eln_cli.get_documents(page_size=page_size)
    return resp['documents']


@mcp.prompt()
def literature_search(topic: str, result_count: int = 5) -> str:
    """Performs a literature review using pubmed on the given topic"""
    return f"Please do  a literature search on the following topic: {topic}. Search PubMed if possible, else do a " \
           f"general internet search. Then, select {result_count} best " \
           "results, and return the abstracts, along with author contact detail. Then save the results in an RSpace " \
           "notebook, creating one entry per article. When saving the text, convert the text to simple HTML, " \
           "including links, bullets and  text formatting. "


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


@mcp.tool(tags={"rspace"}, name="renameDocumentOrNotebookEntry")
def rename_document(
        doc_id: int | str,
        name: str
) -> Dict[str, any]:
    """
    Renames a document or notebook entry
    :param doc_id:
    :param name: the new name
    :return:
    """
    resp = eln_cli.update_document(document_id=doc_id, name=name)
    return resp


@mcp.tool(tags={"rspace"}, name="getAuditEvents")
def activity(
        username: str = None,
        global_id: str = None,
        date_from: str = None,
        date_to: str = None
) -> Dict[str, any]:
    """
    Gets audit trail of all actions performed in RSpace. Optionally can filter by:
     - username(s)
     - a single document id
     - a date from in ISO8601 format
     - a date to in ISO8601 format
    """
    resp = eln_cli.get_activity(users=[username], global_id=global_id, date_from=date_from, date_to=date_to)
    return resp


@mcp.tool(tags={"rspace"}, name="downloadFile")
def download_file(
        file_id: int,
        file_path: str
) -> Dict[str, any]:
    """
    Get the file contents given a file id, and a file-system location to save to

    """
    resp = eln_cli.download_file(file_id=file_id, filename=file_path, chunk_size=1024)
    return resp


if __name__ == "__main__":
    mcp.run()
