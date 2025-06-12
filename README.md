# ArcGIS MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with ArcGIS Online, enabling AI assistants to search for and query geospatial feature layers.

## Overview

This MCP server acts as a bridge between AI language models and ArcGIS Online, allowing for intelligent geospatial data discovery and analysis. It authenticates with ArcGIS Online and exposes powerful tools for finding and retrieving feature layer data in a format optimized for AI consumption.

## Features

- **Secure Authentication**: Connects to ArcGIS Online using environment-based credentials
- **Intelligent Layer Search**: Discover feature layers using natural language keywords
- **Data Extraction**: Retrieve attribute tables from feature layers as structured CSV data
- **Multi-layer Support**: Handles both single layers and feature service collections
- **Error Handling**: Robust error reporting for troubleshooting

## Available Tools

### `search_layers`
Searches ArcGIS Online for feature layers matching a keyword and returns REST service URLs for individual layers.

**Parameters:**
- `keyword` (string): The search term to find matching layers (e.g., "Hydrants", "Roads", "Parks")

**Returns:**
A formatted list of matching layer names with their REST service URLs.

**Example:**
```
Fire Hydrants: https://services.arcgis.com/.../FeatureServer/0
Water Distribution System: https://services.arcgis.com/.../FeatureServer/1
```

### `search_content`
Searches ArcGIS Online for content items of any type and returns their Item IDs.

**Parameters:**
- `keyword` (string): The search term to find matching content (e.g., "Traffic", "Population", "Dashboard")
- `item_type` (optional string): Filter for specific content type (e.g., "Web Map", "Dashboard", "Feature Service")

**Returns:**
A formatted list of matching item titles with their Item IDs and content types.

**Example:**
```
Traffic Analysis Dashboard: abc123def456 | Type: Dashboard
Population Web Map: xyz789uvw012 | Type: Web Map
Transportation Network: def456ghi789 | Type: Feature Service
```

### `get_feature_table`
Retrieves the complete attribute table from a specified feature layer using REST service URLs.

**Parameters:**
- `service_url` (string): The REST service URL of the target feature layer

**Returns:**
Attribute data in CSV format with all fields and records, excluding geometry for efficient processing.

**Example:**
```csv
OBJECTID,Name,Type,Status,Install_Date
1,Hydrant_001,Fire Hydrant,Active,2020-01-15
2,Hydrant_002,Fire Hydrant,Maintenance,2019-08-22
```

### `get_item_definition`
Retrieves the complete JSON definition of any ArcGIS Online content item using its Item ID.

**Parameters:**
- `item_id` (string): The Item ID of the content item from search_content results

**Returns:**
Item metadata header followed by the complete JSON definition in compact format.

**Example:**
```
Item: Traffic Dashboard | Type: Dashboard | Created: 1609459200000
{"widgets":[{"type":"indicator","config":{"dataSource":"layer1"}}],"theme":"dark"}
```


## Setup

### Prerequisites
- Python 3.11 or higher
- ArcGIS Online account with appropriate permissions

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Create a `.env` file with your ArcGIS Online credentials:
   ```
   ARCGIS_USERNAME=your_username
   ARCGIS_PASSWORD=your_password
   ```

### Running the Server

```bash
python main.py
```

The server will start and listen for MCP connections via stdio transport.

## Architecture

The server is built using the FastMCP framework and leverages the ArcGIS Python API for seamless integration with ArcGIS Online services. It handles authentication at startup and maintains a persistent connection for efficient querying.

## Workflows

### Content Discovery and Analysis
1. **Search for content**: Use `search_content` to find items by keyword
2. **Get JSON definitions**: Use `get_item_definition` with Item IDs to analyze service configurations, web map structures, or dashboard layouts
3. **Extract data**: For feature layers, use `search_layers` to find specific layers, then `get_feature_table` to retrieve attribute data

### Layer-Specific Data Extraction
1. **Find layers**: Use `search_layers` to locate specific feature layers
2. **Extract data**: Use `get_feature_table` with REST URLs to get attribute tables as CSV


## Use Cases

- **Data Discovery**: Find relevant geospatial datasets and applications using natural language queries
- **Configuration Analysis**: Examine JSON definitions of web maps, dashboards, and services to understand their structure
- **Spatial Analysis**: Extract attribute data for AI-powered analysis and insights
- **Report Generation**: Automatically gather data from multiple feature layers for comprehensive reports
- **Quality Assurance**: Programmatically inspect feature layer contents, metadata, and service configurations
- **Application Development**: Understand web map and dashboard configurations for building similar applications
