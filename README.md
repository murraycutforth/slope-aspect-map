# Slope Aspect Map - Scottish Highlands Avalanche Terrain

Interactive web map visualizing avalanche terrain risk in the Scottish Highlands based on slope angle analysis.

## Live Map

**[View the interactive map](https://murraycutforth.github.io/slope-aspect-map/scottish_highlands_slope_map.html)**

## Features

- Slope angle visualization derived from SRTM elevation data
- 5-tier avalanche risk classification:
  - **Low** (< 25°) - Green
  - **Moderate** (25-30°) - Yellow
  - **High** (30-45°) - Orange
  - **Very High** (45-60°) - Red
  - **Extreme** (> 60°) - Dark Red
- Multiple base map options (OpenStreetMap, OpenTopoMap, Satellite)
- Interactive legend and layer controls

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server (auto-opens browser)
./server.py

# Or regenerate the map and serve
python server.py --regenerate
```

## How It Works

The pipeline fetches SRTM elevation data, calculates slope angles using gradient analysis, classifies terrain by avalanche risk thresholds, and renders an interactive Folium/Leaflet map.

## Disclaimer

This map is for educational and planning purposes only. Always check official avalanche forecasts from SAIS (Scottish Avalanche Information Service) before venturing into the mountains.
