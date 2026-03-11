"""
Map builder — generates a Folium map and returns the HTML snippet
that can be embedded directly into the frontend as an iframe srcdoc.
"""

import folium
import re
from app.geo_service import GeoResult


def build_map_html(result: GeoResult) -> str:
    """
    Build an interactive dark Folium map for the given GeoResult.
    Returns a full <iframe> tag with the map embedded as srcdoc.
    """
    m = folium.Map(
        location=[result.latitude, result.longitude],
        zoom_start=11,
        tiles="CartoDB dark_matter",
        control_scale=True,
        prefer_canvas=True,
    )

    # Accuracy radius circle
    folium.CircleMarker(
        location=[result.latitude, result.longitude],
        radius=55,
        color="#00f5c4",
        fill=True,
        fill_color="#00f5c4",
        fill_opacity=0.07,
        weight=1,
    ).add_to(m)

    popup_html = f"""
    <div style="font-family:monospace;font-size:13px;line-height:1.9;min-width:210px;padding:4px">
      <strong style="font-size:15px">{result.city}, {result.country}</strong>
      <hr style="margin:6px 0;border-color:#ddd;opacity:.3"/>
      <b>IP:</b> {result.ip}<br/>
      <b>ISP:</b> {result.org}<br/>
      <b>Timezone:</b> {result.timezone}<br/>
      <b>Coords:</b> {result.latitude:.4f}, {result.longitude:.4f}
    </div>
    """

    folium.Marker(
        location=[result.latitude, result.longitude],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"📍 {result.display_location}",
        icon=folium.Icon(color="green", icon="map-marker", prefix="fa"),
    ).add_to(m)

    raw_html = m._repr_html_()

    # Wrap in a nicely sized iframe
    iframe = (
        f'<iframe srcdoc="{_escape_for_attr(raw_html)}" '
        f'style="width:100%;height:480px;border:none;border-radius:16px;" '
        f'sandbox="allow-scripts allow-same-origin"></iframe>'
    )
    return iframe


def _escape_for_attr(html: str) -> str:
    """Escape HTML string so it can be safely used in an HTML attribute."""
    return (
        html.replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )
