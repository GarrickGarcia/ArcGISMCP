# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server for ArcGIS that provides tools for searching and querying ArcGIS Online content. The server authenticates with ArcGIS Online and exposes four main tools:

1. `search_layers` - Searches for feature layers by keyword, returns REST URLs
2. `search_content` - Searches for any content type by keyword, returns Item IDs  
3. `get_feature_table` - Retrieves sample attribute data (20 rows) from feature layers as CSV
4. `summarize_field` - Provides detailed statistics for a specific field in a feature layer

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

**Main workflow patterns:**
- `search_layers` → `get_feature_table` → `summarize_field` (complete data analysis workflow)
- `search_content` → find specific content items by keyword and type (for non-layer content)

## Key Implementation Details

- The server authenticates with ArcGIS Online at startup using GIS class
- Feature layer searches use `item_type="Feature Layer"` (must be string, not list)
- Multi-layer feature services are handled by iterating through item.layers
- Content searches can filter by item_type or search all types
- CSV output excludes geometry for LLM consumption, limited to 20 rows for token efficiency
- Field summaries provide type-appropriate statistics (numeric, text, date)
- Error handling returns descriptive error messages as strings