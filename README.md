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

**Workflow Tip:** Use this tool first to discover feature layers, then chain the returned URLs to other tools.

### `summarize_field`
Provides comprehensive statistics for a specific field in an ArcGIS feature layer.

**Parameters:**
- `service_url` (string): The REST service URL of the feature layer (obtained from `search_layers`)
- `field_name` (string): The name of the field to analyze (obtained from `get_feature_table`)

**Returns:**
Field-type-appropriate statistics including:
- **All types**: Total count, null percentage, unique values, top 10 most common values with frequencies
- **Numeric fields**: Min, max, mean, median, mode, standard deviation
- **Date fields**: Earliest, latest dates, and date range

**Example:**
```
Field: Status
Type: esriFieldTypeString
Total features: 150
Null values: 5 (3.3%)
Unique values: 3

Top 10 values:
  'Active': 120 (82.8%)
  'Maintenance': 20 (13.8%)
  'Inactive': 5 (3.4%)
```

**Workflow Tip:** Complete workflow: `search_layers` → `get_feature_table` (to see fields) → `summarize_field` (to analyze).

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
Retrieves a sample (first 20 rows) of the attribute table from a specified feature layer using REST service URLs.

**Parameters:**
- `service_url` (string): The REST service URL of the target feature layer (obtained from `search_layers`)

**Returns:**
First 20 rows of attribute data in CSV format, excluding geometry for efficient processing. Note: This is a sample, not the complete table.

**Example:**
```csv
OBJECTID,Name,Type,Status,Install_Date
1,Hydrant_001,Fire Hydrant,Active,2020-01-15
2,Hydrant_002,Fire Hydrant,Maintenance,2019-08-22
```

**Workflow Tip:** Use after `search_layers` to preview data structure and identify field names for further analysis.


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

### Content Discovery
1. **Search for content**: Use `search_content` to find items by keyword and type (Web Maps, Dashboards, etc.)
2. **For feature layer analysis**: Use `search_layers` instead to find specific layers for data extraction

### Layer-Specific Data Analysis (Recommended Workflow)
1. **Find layers**: Use `search_layers` to locate specific feature layers by keyword
2. **Preview data**: Use `get_feature_table` with REST URLs to see field names and sample data (20 rows)
3. **Analyze fields**: Use `summarize_field` to get detailed statistics for specific fields of interest


## Use Cases

- **Data Discovery**: Find relevant geospatial datasets and applications using natural language queries
- **Spatial Analysis**: Extract attribute data for AI-powered analysis and insights
- **Report Generation**: Automatically gather data from multiple feature layers for comprehensive reports
- **Quality Assurance**: Programmatically inspect feature layer contents and service configurations
