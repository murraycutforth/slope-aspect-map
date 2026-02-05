# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Slope Aspect Map is a geospatial tool for visualizing avalanche terrain risk in the Scottish Highlands. It downloads SRTM elevation data, calculates slope angles, classifies them by avalanche risk, and generates interactive web maps using Folium.

## Commands

```bash
# Run all tests
python -m pytest

# Start HTTP server (auto-opens browser, serves map)
./server.py

# Server options
python server.py --port 8000      # Custom port
python server.py --regenerate     # Regenerate map before serving
python server.py --no-browser     # Don't auto-open browser

# Run alignment diagnostics
python diagnose_alignment.py
```

## Architecture

The codebase follows a linear data pipeline:

```
DEM Loading → Slope Calculation → Risk Classification → Map Visualization
(dem.py)        (slope.py)          (classify.py)         (visualize.py)
```

**src/dem.py** - Fetches SRTM elevation data via `elevation` library, returns `DEMData` dataclass with elevation array, bounds, and resolution. Handles latitude-aware cell size conversion.

**src/slope.py** - Calculates slope angles (0-90°) using NumPy gradient operations on elevation data.

**src/classify.py** - Classifies slopes into 5 avalanche risk categories (Low <25°, Moderate 25-30°, High 30-45°, Very High 45-60°, Extreme >60°) with corresponding RGBA colors.

**src/visualize.py** - Creates Folium interactive maps with slope overlay, multiple base tile options, and risk legend.

**server.py** - Entry point that orchestrates the pipeline and serves the generated HTML map via Python's built-in HTTP server.

## Key Data Structures

- `DEMData` (dataclass in dem.py): Contains elevation array, bounds tuple (west, south, east, north), and cell resolution
- `RISK_CATEGORIES` (dict in classify.py): Defines thresholds and colors for each avalanche risk level

## Tech Stack

- numpy for array operations
- rasterio for GIS raster I/O
- elevation for SRTM data downloading
- folium for Leaflet-based web maps
- pillow for image processing
