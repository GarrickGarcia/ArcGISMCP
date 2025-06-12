# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server for ArcGIS that provides tools for searching, querying, and recreating ArcGIS Online content. The server authenticates with ArcGIS Online and exposes five main tools:

1. `search_layers` - Searches for feature layers by keyword, returns REST URLs
2. `search_content` - Searches for any content type by keyword, returns Item IDs  
3. `get_feature_table` - Retrieves attribute data from feature layers as CSV
4. `get_item_definition` - Retrieves JSON definitions from any content item using Item ID
5. `recreate_item` - Creates new items from JSON definitions obtained from get_item_definition

## Architecture

- **main.py**: Single-file MCP server using FastMCP framework
- **Authentication**: Uses ArcGIS Online credentials from .env file
- **Dependencies**: Built on arcgis Python API, httpx, and mcp frameworks

## Development Commands

### Running the server
```bash
python main.py
```

### Installing dependencies
```bash
pip install -e .
```

## Configuration

The server requires ArcGIS Online credentials in a `.env` file:
- `ARCGIS_USERNAME`: ArcGIS Online username
- `ARCGIS_PASSWORD`: ArcGIS Online password

## Workflows

**Three main workflow patterns:**
- `search_layers` → `get_feature_table` (for layer-specific data extraction)
- `search_content` → `get_item_definition` (for JSON definition analysis)
- `search_content` → `get_item_definition` → `recreate_item` (for item duplication/recreation)

## Key Implementation Details

- The server authenticates with ArcGIS Online at startup using GIS class
- Feature layer searches use `item_type="Feature Layer"` (must be string, not list)
- Multi-layer feature services are handled by iterating through item.layers
- Content searches can filter by item_type or search all types
- CSV output excludes geometry for LLM consumption
- JSON definitions are returned in compact format for efficient LLM processing
- Different item types require different JSON extraction methods:
  - Feature Services: Use FeatureLayer(url).properties
  - Web Maps/Dashboards/Apps: Use item.get_data()
- Item recreation uses type-specific creation methods:
  - Web Maps: WebMap(definition).save() with item_properties
  - Dashboards/Apps: gis.content.add() with text parameter containing JSON
  - Feature Services: gis.content.create_service() with service_definition
- The recreate_item tool parses header format: "Item: Title | Type: TYPE | Created: DATE"
- Error handling returns descriptive error messages as strings