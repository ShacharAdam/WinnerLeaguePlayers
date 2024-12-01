import folium
from folium.plugins import MarkerCluster, Search
import json
from collections import defaultdict

# Load the GeoJSON data
with open("WinnerLeague.geojson", "r") as file:
    winner_league_data = json.load(file)

# Color mapping for teams
team_to_color = {
    "hapoel jerusalem": "darkred", "bnei herzliya": "blue", "hapoel tel aviv": "red",
    "maccabi tel aviv": "blue", "hapoel holon": "purple", "hapoel galil elion": "red",
    "ironi ness ziona": "orange", "hapoel afula": "gray", "maccabi ramat gan": "cadetblue",
    "ironi kiryat ata": "darkblue", "hapoel gilboa galil": "lightred", "elizur netanya": "black",
    "hapoel be'er sheva dimona": "lightred", "hapoel haifa": "red"
}

# Initialize the map centered on Tel-Aviv
m = folium.Map(location=(32.0853, 34.7818), zoom_start=8, tiles='OpenStreetMap')

# Group markers by city into layers with clusters
city_layers = defaultdict(lambda: (folium.FeatureGroup(name="City Group"), MarkerCluster()))

# Add all player points to their city-based layers
for feature in winner_league_data["features"]:
    properties = feature["properties"]
    geometry = feature["geometry"]

    # Handle Point geometry only
    if geometry["type"] == "Point":
        coordinates = geometry["coordinates"]
        city = properties.get("City", "Unknown City")
        team = properties.get("Team", "").lower()

        # Create a marker
        marker = folium.Marker(
            location=(coordinates[1], coordinates[0]),  # GeoJSON coordinates are [lon, lat]
            tooltip=properties["Name"],  # Tooltip field for search
            popup=f"{properties['Name']}, {properties['City']}, {properties['Age']}, {properties['Position']} - {properties['Team']}",
            icon=folium.Icon(
                icon="fa-solid fa-basketball",
                color=team_to_color.get(team, "gray"),
                prefix="fa"
            ),
        )

        # Get the feature group and cluster for the city
        feature_group, cluster = city_layers[city]
        cluster.add_child(marker)

# Add city-based layers with clusters to the map
for city, (feature_group, cluster) in city_layers.items():
    feature_group.add_child(cluster)  # Add the cluster to the feature group
    feature_group.add_to(m)  # Add the feature group to the map

# Add GeoJSON layer with tooltips and styling
winner_league_geo = folium.GeoJson(
    winner_league_data,
    name="Winner League Geo",
    tooltip=folium.GeoJsonTooltip(
        fields=["Name", "City", "Age", "Position", "Team"],  # Match property keys in your GeoJSON
        aliases=["Player", "City", "Age", "Position", "Team"],  # Labels for tooltip
        localize=True,
    ),
    style_function=lambda feature: {
        "color": team_to_color.get(feature["properties"]["Team"].lower(), "gray"),
        "weight": 2,
    },
    show=False,
).add_to(m)

# Add a search control to allow searching for players by name
search = Search(
    layer=winner_league_geo,  # Attach search to the GeoJSON layer
    search_label="Name",  # Match the property key for player names
    placeholder='Search for a player',
    collapsed=False
).add_to(m)

# Add LayerControl to toggle city layers
folium.LayerControl(collapsed=True).add_to(m)


# Save the map to an HTML file
m.save("index.html")
