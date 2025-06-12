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
Searches ArcGIS Online for feature layers matching a keyword.

**Parameters:**
- `keyword` (string): The search term to find matching layers (e.g., "Hydrants", "Roads", "Parks")

**Returns:**
A formatted list of matching layer names with their REST service URLs.

**Example:**
```
Fire Hydrants: https://services.arcgis.com/.../FeatureServer/0
Water Distribution System: https://services.arcgis.com/.../FeatureServer/1
```

### `get_feature_table`
Retrieves the complete attribute table from a specified feature layer.

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

## Use Cases

- **Data Discovery**: Find relevant geospatial datasets using natural language queries
- **Spatial Analysis**: Extract attribute data for AI-powered analysis and insights
- **Report Generation**: Automatically gather data from multiple feature layers for comprehensive reports
- **Quality Assurance**: Programmatically inspect feature layer contents and metadata
