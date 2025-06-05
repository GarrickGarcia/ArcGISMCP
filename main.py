
import os
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
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

if __name__ == "__main__":
    print("Starting ArcGIS MCP server...")
    mcp.run(transport="stdio")
