import gpxpy
import folium

# Load GPX file
with open('gpsx\\order.gpx', 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Create base map (centered on first point)
first_point = gpx.tracks[0].segments[0].points[0]
m = folium.Map(location=[first_point.latitude, first_point.longitude], zoom_start=14)

# Extract coordinates
route = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            route.append((point.latitude, point.longitude))

# Add route to map
folium.PolyLine(route, color='blue', weight=3).add_to(m)

# Optional: Add markers for start/end
folium.Marker(route[0], tooltip="Start").add_to(m)
folium.Marker(route[-1], tooltip="End").add_to(m)

# Display map in Jupyter or save as HTML
m.save("gpx_route_map.html")