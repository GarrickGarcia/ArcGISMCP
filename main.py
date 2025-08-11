
import os
import json
from collections import Counter
from datetime import datetime
import statistics
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
    
    Workflow:
        Use this tool first to find feature layers, then use the returned REST URLs with 
        get_feature_table to preview data or summarize_field to analyze specific fields.
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
    """Fetches a sample of the attribute table from an ArcGIS Online hosted feature layer using the REST service URL.
    
    Args:
        service_url: The REST service URL of the feature layer (obtained from search_layers).
    
    Returns:
        The first 20 rows of the attribute table as a string (CSV format) for LLM analysis. 
        Note: This is a sample, not the complete table.
    
    Workflow:
        Use after search_layers to preview data structure and identify field names. 
        Then use summarize_field for detailed analysis of specific fields.
    """
    try:
        flayer = FeatureLayer(service_url, gis=gis)
        features = flayer.query(where="1=1", out_fields="*", return_geometry=False, result_record_count=20)
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
def summarize_field(service_url: str, field_name: str) -> str:
    """Provides summary statistics for a specific field in an ArcGIS feature layer.
    
    Args:
        service_url: The REST service URL of the feature layer (obtained from search_layers).
        field_name: The name of the field to summarize (obtained from get_feature_table).
    
    Returns:
        Summary statistics appropriate to the field type (numeric, text, date) as a concise string.
    
    Workflow:
        Typical sequence: search_layers → get_feature_table (to see fields) → summarize_field (to analyze).
        For numeric fields: returns min, max, mean, median, mode, std dev.
        For text/date fields: returns unique values, top 10 frequencies, date ranges.
    """
    try:
        flayer = FeatureLayer(service_url, gis=gis)
        
        # Get field metadata to determine type
        field_info = None
        for field in flayer.properties.fields:
            if field.name.lower() == field_name.lower():
                field_info = field
                field_name = field.name  # Use exact case
                break
        
        if not field_info:
            return f"Field '{field_name}' not found in the feature layer."
        
        # Query for field values
        features = flayer.query(where="1=1", out_fields=field_name, return_geometry=False)
        
        if not features.features:
            return "No features found in the layer."
        
        # Extract values
        values = [f.attributes.get(field_name) for f in features.features]
        non_null_values = [v for v in values if v is not None]
        
        # Basic statistics for all types
        total_count = len(values)
        null_count = len(values) - len(non_null_values)
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        summary = []
        summary.append(f"Field: {field_name}")
        summary.append(f"Type: {field_info.type}")
        summary.append(f"Total features: {total_count}")
        summary.append(f"Null values: {null_count} ({null_percentage:.1f}%)")
        
        if not non_null_values:
            return "\n".join(summary) + "\nAll values are null."
        
        # Type-specific statistics
        if field_info.type in ["esriFieldTypeDouble", "esriFieldTypeInteger", "esriFieldTypeSingle", "esriFieldTypeSmallInteger"]:
            # Numeric field statistics
            try:
                numeric_values = [float(v) for v in non_null_values if v is not None]
                if numeric_values:
                    summary.append(f"Min: {min(numeric_values)}")
                    summary.append(f"Max: {max(numeric_values)}")
                    summary.append(f"Mean: {statistics.mean(numeric_values):.2f}")
                    summary.append(f"Median: {statistics.median(numeric_values)}")
                    if len(numeric_values) >= 2:
                        summary.append(f"Std Dev: {statistics.stdev(numeric_values):.2f}")
                    # Mode (if exists)
                    try:
                        mode_val = statistics.mode(numeric_values)
                        summary.append(f"Mode: {mode_val}")
                    except statistics.StatisticsError:
                        pass  # No unique mode
            except (ValueError, TypeError):
                pass
                
        elif field_info.type == "esriFieldTypeDate":
            # Date field statistics
            date_values = []
            for v in non_null_values:
                if isinstance(v, (int, float)):
                    # ArcGIS dates are often milliseconds since epoch
                    try:
                        date_values.append(datetime.fromtimestamp(v/1000))
                    except:
                        pass
            
            if date_values:
                earliest = min(date_values)
                latest = max(date_values)
                summary.append(f"Earliest: {earliest.strftime('%Y-%m-%d')}")
                summary.append(f"Latest: {latest.strftime('%Y-%m-%d')}")
                summary.append(f"Date range: {(latest - earliest).days} days")
        
        # For all types, show unique values and top frequencies
        value_counts = Counter(non_null_values)
        unique_count = len(value_counts)
        summary.append(f"Unique values: {unique_count}")
        
        # Top 10 most common values
        if unique_count > 0:
            summary.append("\nTop 10 values:")
            for value, count in value_counts.most_common(10):
                percentage = (count / len(non_null_values) * 100)
                summary.append(f"  '{value}': {count} ({percentage:.1f}%)")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"Error summarizing field: {e}"

@mcp.tool()
def search_content(keyword: str, item_type: str = None) -> str:
    """Searches ArcGIS Online for content items of any type and returns their Item IDs.
    
    Args:
        keyword: The keyword or description to search for (e.g., 'Traffic', 'Population').
        item_type: Optional filter for specific item type (e.g., 'Web Map', 'Dashboard', 'Feature Service').
    
    Returns:
        A list of matching item titles with their Item IDs and types as a string.
    
    Workflow:
        Use this for finding non-layer content like Web Maps, Dashboards, or StoryMaps.
        For feature layer data analysis, use search_layers instead.
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
