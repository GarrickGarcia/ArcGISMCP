# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server for ArcGIS that provides tools for searching and querying ArcGIS Online feature layers. The server authenticates with ArcGIS Online and exposes two main tools:

1. `search_layers` - Searches for feature layers by keyword
2. `get_feature_table` - Retrieves attribute data from feature layers as CSV

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

## Key Implementation Details

- The server authenticates with ArcGIS Online at startup using GIS class
- Feature layer searches use `item_type="Feature Layer"` (must be string, not list)
- Multi-layer feature services are handled by iterating through item.layers
- CSV output excludes geometry for LLM consumption
- Error handling returns descriptive error messages as strings