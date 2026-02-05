"""Folium map generation for slope angle visualization."""

import io
import base64
import numpy as np
from PIL import Image
import folium
from folium import IFrame

from .classify import slope_to_rgba, RISK_CATEGORIES


def create_slope_overlay_image(slopes: np.ndarray) -> str:
    """
    Create a base64-encoded PNG image from slope data.

    Args:
        slopes: 2D array of slope angles in degrees

    Returns:
        Base64-encoded PNG image string
    """
    # Convert slopes to RGBA image
    rgba = slope_to_rgba(slopes)

    # Create PIL image
    img = Image.fromarray(rgba, mode='RGBA')

    # Encode to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return f'data:image/png;base64,{img_base64}'


def create_legend_html() -> str:
    """Create HTML for the map legend."""
    legend_html = '''
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        z-index: 1000;
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        border: 2px solid grey;
        font-family: Arial, sans-serif;
    ">
        <h4 style="margin: 0 0 10px 0;">Avalanche Terrain Risk</h4>
        <div><span style="background-color: rgb(0,255,0); width: 20px; height: 12px; display: inline-block; margin-right: 5px;"></span> Low (&lt;25°)</div>
        <div><span style="background-color: rgb(255,255,0); width: 20px; height: 12px; display: inline-block; margin-right: 5px;"></span> Moderate (25-30°)</div>
        <div><span style="background-color: rgb(255,165,0); width: 20px; height: 12px; display: inline-block; margin-right: 5px;"></span> High (30-45°)</div>
        <div><span style="background-color: rgb(255,0,0); width: 20px; height: 12px; display: inline-block; margin-right: 5px;"></span> Very High (45-60°)</div>
        <div><span style="background-color: rgb(128,0,128); width: 20px; height: 12px; display: inline-block; margin-right: 5px;"></span> Extreme (&gt;60°)</div>
        <p style="font-size: 10px; margin: 10px 0 0 0; color: grey;">
            Most avalanches start on 30-45° slopes
        </p>
    </div>
    '''
    return legend_html


def create_slope_map(slopes: np.ndarray,
                     bounds: tuple,
                     output_file: str = 'slope_map.html',
                     center: tuple = None,
                     zoom_start: int = 8) -> folium.Map:
    """
    Create a Folium map with slope angle overlay.

    Args:
        slopes: 2D array of slope angles in degrees
        bounds: (west, south, east, north) in degrees
        output_file: Path to save the HTML map
        center: (lat, lon) center point for the map
        zoom_start: Initial zoom level

    Returns:
        Folium Map object
    """
    west, south, east, north = bounds

    # Calculate center if not provided
    if center is None:
        center = ((south + north) / 2, (west + east) / 2)

    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )

    # Add terrain tiles as an option
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Topo',
        overlay=False,
        control=True
    ).add_to(m)

    # Create slope overlay as RGBA array
    from .classify import slope_to_rgba
    rgba = slope_to_rgba(slopes)

    # Downsample large images for mobile compatibility
    # Images over ~1500px can cause mobile browser crashes during zoom
    max_dimension = 1500
    height, width = rgba.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_height = int(height * scale)
        new_width = int(width * scale)
        img = Image.fromarray(rgba, mode='RGBA')
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        rgba = np.array(img)

    # Add image overlay
    # Note: ImageOverlay bounds are [[south, west], [north, east]]
    # mercator_project=True reprojects the WGS84 image to Web Mercator to match base tiles
    folium.raster_layers.ImageOverlay(
        image=rgba,
        bounds=[[south, west], [north, east]],
        origin='upper',
        mercator_project=True,
        opacity=0.6,
        name='Slope Angle',
        interactive=False,
        cross_origin=False,
        zindex=1
    ).add_to(m)

    # Add legend
    legend = folium.Element(create_legend_html())
    m.get_root().html.add_child(legend)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save to file
    m.save(output_file)
    print(f"Map saved to {output_file}")

    return m


def generate_scottish_highlands_map(slopes: np.ndarray,
                                    bounds: tuple,
                                    output_file: str = 'scottish_highlands_slope_map.html') -> folium.Map:
    """
    Generate a slope map specifically for the Scottish Highlands.

    Args:
        slopes: 2D array of slope angles
        bounds: DEM bounds
        output_file: Output HTML file path

    Returns:
        Folium Map object
    """
    # Center on Cairngorms (notable mountain area)
    center = (57.0, -5.0)

    return create_slope_map(
        slopes=slopes,
        bounds=bounds,
        output_file=output_file,
        center=center,
        zoom_start=8
    )
