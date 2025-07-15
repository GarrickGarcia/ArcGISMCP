
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



if __name__ == "__main__":
    print("Starting ArcGIS MCP server...")
    mcp.run(transport="stdio")
