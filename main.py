from typing import Annotated, Dict, List, Optional, Union

from fastmcp import FastMCP
from rspace_client.eln import eln as e
from rspace_client.inv import inv as i
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

# New Inventory Models
class Sample(BaseModel):
    name: str = Field(description="Sample name")
    globalId: str = Field(description="Global identifier")
    created: str = Field(description="Creation date")
    tags: List[str] = Field(description="Sample tags")
    quantity: Optional[Dict] = Field(description="Sample quantity and units")


class Container(BaseModel):
    name: str = Field(description="Container name")
    globalId: str = Field(description="Global identifier")
    cType: str = Field(description="Container type (LIST, GRID, WORKBENCH, IMAGE)")
    capacity: Optional[int] = Field(description="Container capacity if applicable")


class GridLocation(BaseModel):
    x: int = Field(description="Column position (1-based)")
    y: int = Field(description="Row position (1-based)")


mcp = FastMCP("RSpace MCP Server")
load_dotenv()
api_key = os.getenv("RSPACE_API_KEY")
api_url = os.getenv("RSPACE_URL")
eln_cli = e.ELNClient(api_url, api_key);
inv_cli = i.InventoryClient(api_url, api_key);


@mcp.tool(tags={"rspace"})
def get_forms(query: str = None, order_by: str = "lastModified desc", page_number: int = 0, page_size: int = 20) -> dict:
    """
    Gets list of available forms in RSpace
    """
    return eln_cli.get_forms(query=query, order_by=order_by, page_number=page_number, page_size=page_size)


@mcp.tool(tags={"rspace"})
def get_form(form_id: int | str) -> dict:
    """
    Gets detailed information about a specific form by ID or global ID
    """
    return eln_cli.get_form(form_id)


@mcp.tool(tags={"rspace"})
def create_form(
    name: str,
    tags: List[str] = None,
    fields: List[dict] = None
) -> dict:
    """
    Creates a new custom form in RSpace
    
    Fields should be a list of dictionaries with structure:
    [
        {
            "name": "Field Name",
            "type": "String|Text|Number|Radio|Date|Choice", 
            "mandatory": True/False,
            "defaultValue": "optional default"
        }
    ]
    """
    return eln_cli.create_form(name=name, tags=tags, fields=fields)


@mcp.tool(tags={"rspace"})
def publish_form(form_id: int | str) -> dict:
    """
    Publishes a form to make it available for creating documents
    """
    return eln_cli.publish_form(form_id)


@mcp.tool(tags={"rspace"})
def unpublish_form(form_id: int | str) -> dict:
    """
    Unpublishes a form to hide it from document creation
    """
    return eln_cli.unpublish_form(form_id)


@mcp.tool(tags={"rspace"})
def share_form(form_id: int | str) -> dict:
    """
    Shares form with your groups
    """
    return eln_cli.share_form(form_id)


@mcp.tool(tags={"rspace"})
def unshare_form(form_id: int | str) -> dict:
    """
    Unshares form with your groups
    """
    return eln_cli.unshare_form(form_id)


@mcp.tool(tags={"rspace"})
def delete_form(form_id: int | str) -> dict:
    """
    Deletes a form (must be in NEW state)
    """
    return eln_cli.delete_form(form_id)


@mcp.tool(tags={"rspace"})
def create_document_from_form(
    form_id: int | str,
    name: str = None,
    parent_folder_id: int | str = None,
    tags: List[str] = None,
    fields: List[dict] = None
) -> dict:
    """
    Creates a new document using a specific form template
    """
    return eln_cli.create_document(
        name=name,
        parent_folder_id=parent_folder_id,
        tags=tags,
        form_id=form_id,
        fields=fields
    )

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

# ====== INVENTORY TOOLS (new) ======

# Sample Management
@mcp.tool(tags={"rspace", "inventory", "samples"})
def create_sample(
    name: str,
    tags: List[str] = None,
    description: str = None,
    subsample_count: int = 1,
    total_quantity_value: float = None,
    total_quantity_unit: str = "ml"
) -> dict:
    """Creates a new sample in the inventory with optional metadata"""
    tag_objects = i.gen_tags(tags) if tags else []
    
    quantity = None
    if total_quantity_value:
        from rspace_client.inv import quantity_unit as qu
        unit = qu.QuantityUnit.of(total_quantity_unit)
        quantity = i.Quantity(total_quantity_value, unit)
    
    return inv_cli.create_sample(
        name=name,
        tags=tag_objects,
        description=description,
        subsample_count=subsample_count,
        total_quantity=quantity
    )


@mcp.tool(tags={"rspace", "inventory", "samples"})
def get_sample(sample_id: Union[int, str]) -> dict:
    """Gets detailed information about a specific sample"""
    return inv_cli.get_sample_by_id(sample_id)


@mcp.tool(tags={"rspace", "inventory", "samples"})
def list_samples(page_size: int = 20, order_by: str = "lastModified", sort_order: str = "desc") -> dict:
    """Lists samples in the inventory with pagination"""
    pagination = i.Pagination(page_size=page_size, order_by=order_by, sort_order=sort_order)
    return inv_cli.list_samples(pagination)


@mcp.tool(tags={"rspace", "inventory", "samples"})
def search_inventory(query: str, result_type: str = None) -> dict:
    """Searches inventory items by query text. Result type can be 'SAMPLE', 'SUBSAMPLE', 'CONTAINER', or 'TEMPLATE'"""
    rt = None
    if result_type:
        rt = getattr(i.ResultType, result_type.upper(), None)
    return inv_cli.search(query, result_type=rt)


@mcp.tool(tags={"rspace", "inventory", "samples"})
def duplicate_sample(sample_id: Union[int, str], new_name: str = None) -> dict:
    """Creates a duplicate of an existing sample"""
    return inv_cli.duplicate(sample_id, new_name)


@mcp.tool(tags={"rspace", "inventory", "samples"})
def split_subsample(
    subsample_id: Union[int, str], 
    num_new_subsamples: int,
    quantity_per_subsample: float = None
) -> dict:
    """Splits a subsample into multiple new subsamples"""
    result = inv_cli.split_subsample(subsample_id, num_new_subsamples, quantity_per_subsample)
    return result.data if hasattr(result, 'data') else result


@mcp.tool(tags={"rspace", "inventory", "samples"})
def add_note_to_subsample(subsample_id: Union[int, str], note: str) -> dict:
    """Adds a note to a subsample"""
    return inv_cli.add_note_to_subsample(subsample_id, note)


# Container Management
@mcp.tool(tags={"rspace", "inventory", "containers"})
def create_list_container(
    name: str,
    description: str = None,
    tags: List[str] = None,
    can_store_containers: bool = True,
    can_store_samples: bool = True,
    parent_container_id: Union[int, str] = None
) -> dict:
    """Creates a new list container for organizing inventory items"""
    tag_objects = i.gen_tags(tags) if tags else []
    
    location = i.TopLevelTargetLocation()
    if parent_container_id:
        location = i.ListContainerTargetLocation(parent_container_id)
    
    return inv_cli.create_list_container(
        name=name,
        description=description,
        tags=tag_objects,
        can_store_containers=can_store_containers,
        can_store_samples=can_store_samples,
        location=location
    )


@mcp.tool(tags={"rspace", "inventory", "containers"})
def create_grid_container(
    name: str,
    rows: int,
    columns: int,
    description: str = None,
    tags: List[str] = None,
    can_store_containers: bool = True,
    can_store_samples: bool = True,
    parent_container_id: Union[int, str] = None
) -> dict:
    """Creates a new grid container with specified dimensions"""
    tag_objects = i.gen_tags(tags) if tags else []
    
    location = i.TopLevelTargetLocation()
    if parent_container_id:
        location = i.ListContainerTargetLocation(parent_container_id)
    
    return inv_cli.create_grid_container(
        name=name,
        row_count=rows,
        column_count=columns,
        description=description,
        tags=tag_objects,
        can_store_containers=can_store_containers,
        can_store_samples=can_store_samples,
        location=location
    )


@mcp.tool(tags={"rspace", "inventory", "containers"})
def get_container(container_id: Union[int, str], include_content: bool = False) -> dict:
    """Gets detailed information about a container"""
    return inv_cli.get_container_by_id(container_id, include_content)


@mcp.tool(tags={"rspace", "inventory", "containers"})
def list_containers(page_size: int = 20) -> dict:
    """Lists top-level containers"""
    pagination = i.Pagination(page_size=page_size)
    return inv_cli.list_top_level_containers(pagination)


@mcp.tool(tags={"rspace", "inventory", "containers"})
def get_workbenches() -> List[dict]:
    """Gets all available workbenches"""
    return inv_cli.get_workbenches()


# Item Movement and Organization
@mcp.tool(tags={"rspace", "inventory", "movement"})
def move_items_to_list_container(
    target_container_id: Union[int, str],
    item_ids: List[str]
) -> dict:
    """Moves items (containers or subsamples) to a list container"""
    result = inv_cli.add_items_to_list_container(target_container_id, *item_ids)
    return {"success": result.is_ok(), "results": result.data if hasattr(result, 'data') else str(result)}


@mcp.tool(tags={"rspace", "inventory", "movement"})
def move_items_to_grid_container_by_row(
    target_container_id: Union[int, str],
    item_ids: List[str],
    start_column: int = 1,
    start_row: int = 1,
    total_columns: int = None,
    total_rows: int = None
) -> dict:
    """Moves items to a grid container, filling by rows"""
    # Get container info if dimensions not provided
    if total_columns is None or total_rows is None:
        container = inv_cli.get_container_by_id(target_container_id)
        container_obj = i.Container.of(container)
        if hasattr(container_obj, 'column_count'):
            total_columns = container_obj.column_count()
            total_rows = container_obj.row_count()
        else:
            raise ValueError("Container dimensions required for non-grid containers")
    
    placement = i.ByRow(start_column, start_row, total_columns, total_rows, *item_ids)
    result = inv_cli.add_items_to_grid_container(target_container_id, placement)
    return {"success": result.is_ok(), "results": result.data if hasattr(result, 'data') else str(result)}


@mcp.tool(tags={"rspace", "inventory", "movement"})
def move_items_to_grid_container_by_column(
    target_container_id: Union[int, str],
    item_ids: List[str],
    start_column: int = 1,
    start_row: int = 1,
    total_columns: int = None,
    total_rows: int = None
) -> dict:
    """Moves items to a grid container, filling by columns"""
    # Get container info if dimensions not provided
    if total_columns is None or total_rows is None:
        container = inv_cli.get_container_by_id(target_container_id)
        container_obj = i.Container.of(container)
        if hasattr(container_obj, 'column_count'):
            total_columns = container_obj.column_count()
            total_rows = container_obj.row_count()
        else:
            raise ValueError("Container dimensions required for non-grid containers")
    
    placement = i.ByColumn(start_column, start_row, total_columns, total_rows, *item_ids)
    result = inv_cli.add_items_to_grid_container(target_container_id, placement)
    return {"success": result.is_ok(), "results": result.data if hasattr(result, 'data') else str(result)}


@mcp.tool(tags={"rspace", "inventory", "movement"})
def move_items_to_specific_grid_locations(
    target_container_id: Union[int, str],
    item_ids: List[str],
    grid_locations: List[GridLocation]
) -> dict:
    """Moves items to specific locations in a grid container"""
    if len(item_ids) != len(grid_locations):
        raise ValueError("Number of items must match number of grid locations")
    
    locations = [i.GridLocation(loc.x, loc.y) for loc in grid_locations]
    placement = i.ByLocation(locations, *item_ids)
    result = inv_cli.add_items_to_grid_container(target_container_id, placement)
    return {"success": result.is_ok(), "results": result.data if hasattr(result, 'data') else str(result)}


# Template Management
@mcp.tool(tags={"rspace", "inventory", "templates"})
def create_sample_template(template_data: dict) -> dict:
    """Creates a new sample template from template definition"""
    return inv_cli.create_sample_template(template_data)


@mcp.tool(tags={"rspace", "inventory", "templates"})
def get_sample_template(template_id: Union[int, str]) -> dict:
    """Gets a sample template by ID"""
    return inv_cli.get_sample_template_by_id(template_id)


@mcp.tool(tags={"rspace", "inventory", "templates"})
def list_sample_templates(page_size: int = 20) -> dict:
    """Lists available sample templates"""
    pagination = i.Pagination(page_size=page_size)
    return inv_cli.list_sample_templates(pagination)


# Utility Functions
@mcp.tool(tags={"rspace", "inventory", "utility"})
def rename_inventory_item(item_id: Union[int, str], new_name: str) -> dict:
    """Renames any inventory item (sample, subsample, container, or template)"""
    return inv_cli.rename(item_id, new_name)


@mcp.tool(tags={"rspace", "inventory", "utility"})
def add_extra_fields_to_item(item_id: Union[int, str], field_data: List[dict]) -> dict:
    """Adds extra fields to an inventory item
    
    field_data should be list of dicts with 'name', 'type' ('text' or 'number'), and 'content'
    """
    extra_fields = []
    for field in field_data:
        field_type = i.ExtraFieldType.TEXT if field.get('type', 'text').lower() == 'text' else i.ExtraFieldType.NUMBER
        ef = i.ExtraField(field['name'], field_type, field.get('content', ''))
        extra_fields.append(ef)
    
    return inv_cli.add_extra_fields(item_id, *extra_fields)


@mcp.tool(tags={"rspace", "inventory", "utility"})
def generate_barcode(global_id: str, barcode_type: str = "BARCODE") -> bytes:
    """Generates a barcode for an inventory item. Type can be 'BARCODE' or 'QR'"""
    bc_type = i.Barcode.BARCODE if barcode_type.upper() == "BARCODE" else i.Barcode.QR
    return inv_cli.barcode(global_id, barcode_type=bc_type)


@mcp.tool(tags={"rspace", "inventory", "utility"})
def get_container_summary(container_id: int | str) -> dict:
    """Get container info WITHOUT content to avoid large payloads"""
    return inv_cli.get_container_by_id(container_id, include_content=False)


@mcp.tool(tags={"rspace", "inventory", "utility"})
def get_container_contents_only(container_id: int | str) -> list:
    """Get just the items in a container, not full container details"""
    container = inv_cli.get_container_by_id(container_id, include_content=True)
    return container.get('locations', [])


@mcp.tool(tags={"rspace", "inventory", "utility"})
def bulk_create_samples(sample_definitions: List[dict]) -> dict:
    """Create multiple samples at once - much more efficient than individual calls"""
    # Use the existing bulk_create_sample functionality


@mcp.tool(tags={"rspace", "inventory", "utility"})
def get_recent_samples_summary(days_back: int = 7, page_size: int = 10) -> list:
    """Get just basic info about recent samples, not full details"""
    # Use pagination and date filtering to get minimal data

@mcp.tool(tags={"rspace"}, name="downloadFile")
def download_file(
        file_id: int,
        file_path:str
) -> Dict[str, any]:
    """
    Get the file contents given a file id, and a file-system location to save to

    """
    resp = eln_cli.download_file(file_id=file_id, filename=file_path, chunk_size=1024)
    return resp


if __name__ == "__main__":
    mcp.run()
