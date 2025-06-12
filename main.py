
import os
import json
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
# from arcgis.map import Map
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

mcp = FastMCP("arcgismcp")

# Load credentials from .env file
load_dotenv()
ARCGIS_USERNAME = os.getenv("ARCGIS_USERNAME")
ARCGIS_PASSWORD = os.getenv("ARCGIS_PASSWORD")

# Authenticate with ArcGIS Online
gis = GIS("https://www.arcgis.com", ARCGIS_USERNAME, ARCGIS_PASSWORD)

@mcp.tool()
def search_layers(keyword: str) -> str:
    """Searches ArcGIS Online for layers and sublayers matching a keyword and returns their REST URLs.
    Args:
        keyword: The keyword or description to search for (e.g., 'Hydrants').
    Returns:
        A list of matching layer names and their REST URLs as a string.
    """
    try:
        matches = []

        # IMPORTANT: item_type must be a *string*
        items = gis.content.search(
            query=keyword,
            item_type="Feature Layer",
            max_items=20
        )

        for item in items:
            # Feature Layer collections often contain multiple layers
            if getattr(item, "layers", None):
                for lyr in item.layers:
                    name = lyr.properties.name
                    if keyword.lower() in name.lower():
                        matches.append(f"{name}: {lyr.url}")
            # Single-layer items fall through here
            elif item.url and keyword.lower() in (item.title or "").lower():
                matches.append(f"{item.title}: {item.url}")

        return "\n".join(matches) if matches else "No matching layers found."
    except Exception as exc:
        return f"Error searching layers: {exc}"

@mcp.tool()
def get_feature_table(service_url: str) -> str:
    """Fetches the attribute table from an ArcGIS Online hosted feature layer using the REST service URL.
    Args:
        service_url: The REST service URL of the feature layer.
    Returns:
        The attribute table as a string (CSV format) for LLM analysis.
    """
    try:
        flayer = FeatureLayer(service_url, gis=gis)
        features = flayer.query(where="1=1", out_fields="*", return_geometry=False)
        if not features.features:
            return "No features found."
        # Convert to CSV string
        fields = [f.name for f in flayer.properties.fields]
        rows = [fields]
        for feat in features:
            row = [str(feat.attributes.get(f, "")) for f in fields]
            rows.append(row)
        csv_str = "\n".join([",".join(row) for row in rows])
        return csv_str
    except Exception as e:
        return f"Error fetching table: {e}"

@mcp.tool()
def search_content(keyword: str, item_type: str = None) -> str:
    """Searches ArcGIS Online for content items of any type and returns their Item IDs.
    Args:
        keyword: The keyword or description to search for (e.g., 'Traffic', 'Population').
        item_type: Optional filter for specific item type (e.g., 'Web Map', 'Dashboard', 'Feature Service').
    Returns:
        A list of matching item titles with their Item IDs and types as a string.
    """
    try:
        matches = []
        
        # Search for content items
        items = gis.content.search(
            query=keyword,
            item_type=item_type,
            max_items=20
        )
        
        for item in items:
            title = item.title or "Untitled"
            item_id = item.id
            content_type = item.type or "Unknown"
            matches.append(f"{title}: {item_id} | Type: {content_type}")
        
        return "\n".join(matches) if matches else "No matching content found."
    except Exception as exc:
        return f"Error searching content: {exc}"

@mcp.tool()
def get_item_definition(item_id: str) -> str:
    """Fetches the JSON definition of an ArcGIS Online content item using its Item ID.
    Args:
        item_id: The Item ID of the content item from search_content results.
    Returns:
        Item metadata header plus the complete JSON definition as a compact string.
    """
    try:
        # Get the item
        item = gis.content.get(item_id)
        if not item:
            return f"Error: Item with ID '{item_id}' not found or not accessible."
        
        # Get basic item info
        title = item.title or "Untitled"
        item_type = item.type or "Unknown"
        created = item.created or "Unknown"
        
        # Get JSON definition based on item type
        if item_type in ["Feature Service", "Feature Layer"]:
            # For feature services, get the service definition
            if hasattr(item, 'url') and item.url:
                flayer = FeatureLayer(item.url)
                definition = flayer.properties
            else:
                definition = item.get_data()
        else:
            # For web maps, dashboards, apps, etc.
            definition = item.get_data()
        
        if definition is None:
            return f"Item: {title} | Type: {item_type} | Created: {created}\nNo JSON definition available for this item type."
        
        # Format as compact JSON
        json_str = json.dumps(definition, separators=(',', ':'))
        
        # Return with header
        header = f"Item: {title} | Type: {item_type} | Created: {created}"
        return f"{header}\n{json_str}"
        
    except Exception as exc:
        return f"Error fetching item definition: {exc}"

# @mcp.tool()
# def recreate_item(item_json: str, new_title: str, new_tags: str = None) -> str:
#     """Recreates an ArcGIS Online item from a JSON definition obtained from get_item_definition.
#     Args:
#         item_json: The complete JSON definition string from get_item_definition tool.
#         new_title: Title for the new item.
#         new_tags: Optional comma-separated tags for the new item.
#     Returns:
#         Success message with new item ID and URL, or error message.
#     """
#     try:
#         # Parse the input - split header from JSON
#         lines = item_json.strip().split('\n', 1)
#         if len(lines) < 2:
#             return "Error: Invalid item_json format. Expected header line followed by JSON definition."
        
#         header_line = lines[0]
#         json_definition = lines[1]
        
#         # Extract item type from header
#         # Format: "Item: Title | Type: ITEM_TYPE | Created: DATE"
#         if " | Type: " not in header_line:
#             return "Error: Could not parse item type from header line."
        
#         type_part = header_line.split(" | Type: ")[1]
#         item_type = type_part.split(" | ")[0].strip()
        
#         # Parse JSON definition
#         try:
#             definition = json.loads(json_definition)
#         except json.JSONDecodeError as e:
#             return f"Error: Invalid JSON definition: {e}"
        
#         # Prepare tags
#         tags_list = [tag.strip() for tag in new_tags.split(',')] if new_tags else ['recreated']
        
#         # Create item based on type
#         new_item = None
        
#         if item_type == "Web Map":
#             # Create Map from definition and save
#             try:
#                 # Create empty map first
#                 webmap = Map()
#                 # Apply the definition
#                 webmap.definition = definition
#                 item_properties = {
#                     'title': new_title,
#                     'tags': tags_list,
#                     'snippet': f'Recreated web map based on existing definition'
#                 }
#                 new_item = webmap.save(item_properties=item_properties)
#             except Exception as e:
#                 return f"Error creating Web Map: {e}"
                
#         elif item_type == "Dashboard":
#             # Create empty dashboard then update with definition
#             try:
#                 item_properties = {
#                     'title': new_title,
#                     'type': 'Dashboard',
#                     'tags': tags_list,
#                     'snippet': f'Recreated dashboard based on existing definition',
#                     'text': json.dumps(definition)
#                 }
#                 new_item = gis.content.add(item_properties=item_properties)
#             except Exception as e:
#                 return f"Error creating Dashboard: {e}"
                
#         elif item_type in ["Feature Service", "Feature Layer"]:
#             # Create feature service from definition
#             try:
#                 new_item = gis.content.create_service(
#                     name=new_title,
#                     service_definition=definition,
#                     item_properties={
#                         'tags': tags_list,
#                         'snippet': f'Recreated feature service based on existing definition'
#                     }
#                 )
#             except Exception as e:
#                 return f"Error creating Feature Service: {e}"
                
#         elif item_type in ["StoryMap", "Web Experience", "Web Mapping Application"]:
#             # Create empty item then update with definition
#             try:
#                 item_properties = {
#                     'title': new_title,
#                     'type': item_type,
#                     'tags': tags_list,
#                     'snippet': f'Recreated {item_type.lower()} based on existing definition',
#                     'text': json.dumps(definition)
#                 }
#                 new_item = gis.content.add(item_properties=item_properties)
#             except Exception as e:
#                 return f"Error creating {item_type}: {e}"
                
#         else:
#             # Generic approach for other item types
#             try:
#                 item_properties = {
#                     'title': new_title,
#                     'type': item_type,
#                     'tags': tags_list,
#                     'snippet': f'Recreated {item_type.lower()} based on existing definition',
#                     'text': json.dumps(definition)
#                 }
#                 new_item = gis.content.add(item_properties=item_properties)
#             except Exception as e:
#                 return f"Error creating {item_type}: {e}"
        
#         if new_item:
#             # Build the item URL
#             org_url = gis.properties.portalHostname
#             item_url = f"https://{org_url}/home/item.html?id={new_item.id}"
#             return f"Successfully recreated item: {new_title} | Item ID: {new_item.id} | URL: {item_url}"
#         else:
#             return "Error: Failed to create new item."
            
#     except Exception as exc:
#         return f"Error recreating item: {exc}"

if __name__ == "__main__":
    print("Starting ArcGIS MCP server...")
    mcp.run(transport="stdio")
