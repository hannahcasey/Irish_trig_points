#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:07:10 2026
@author: hannahcasey
"""

# Import packages
import pandas as pd
from pyproj import Transformer
import folium
import branca.colormap as cm

# File paths
IG_csv = 'resources/irish_grid_trigs.csv'

# Load CSV data
IG_df = pd.read_csv(IG_csv)

print(IG_df.head())
print(IG_df.columns)

# Create coordinate transformer
transformer = Transformer.from_crs(
    "EPSG:29903",
    "EPSG:4326",
    always_xy=True
)

# Irish grid letter lookup
GRID_LOOKUP = {
    "A": (0, 4), "B": (1, 4), "C": (2, 4), "D": (3, 4), "E": (4, 4),
    "F": (0, 3), "G": (1, 3), "H": (2, 3), "J": (3, 3), "K": (4, 3),
    "L": (0, 2), "M": (1, 2), "N": (2, 2), "O": (3, 2), "P": (4, 2),
    "Q": (0, 1), "R": (1, 1), "S": (2, 1), "T": (3, 1), "U": (4, 1),
    "V": (0, 0), "W": (1, 0), "X": (2, 0), "Y": (3, 0), "Z": (4, 0)
}

# Convert Irish grid reference to latitude and longitude
def ig_to_latlon(grid_ref):
    
    """
    Convert Irish Grid Reference to WGS84 latitude/longitude.
    Example:"M 13742 08377" -> (53.119203, -9.289241)
    """

    letter, east, north = grid_ref.split()
    
    east = east.ljust(5, '0')
    north = north.ljust(5, '0')

    east_corr, north_corr = GRID_LOOKUP[letter]

    easting = '%s%s' % (east_corr, east)
    northing = '%s%s' % (north_corr, north)

    lon, lat = transformer.transform(easting, northing)

    return lat, lon



IG_df[["latitude", "longitude"]] = (
    IG_df["Grid Ref"]
    .apply(ig_to_latlon)
    .apply(pd.Series)
)

# Format elevation
IG_df["Height (m)"] = (
    IG_df["Height*"]
    .str.replace("~", "", regex=False)
    .str.replace("m", "", regex=False)
    .str.strip()
    .astype(float)
)


# Map of Ireland
m = folium.Map(
    location=[
        IG_df["latitude"].mean(),
        IG_df["longitude"].mean()
    ],
    zoom_start=7
)

# Colour scale for elevation
min_elev = IG_df["Height (m)"].min()
max_elev = IG_df["Height (m)"].max()

colormap = cm.LinearColormap(
    colors=["#2c7bb6", "#ffffbf", "#fdae61", "#d7191c"],
    vmin=min_elev,
    vmax=max_elev,
    caption="Elevation (m)"
)


fm = folium.Map(
    location=[
        IG_df["latitude"].mean(),
        IG_df["longitude"].mean()
    ],
    zoom_start=7
)

min_elev = IG_df["Height (m)"].min()
max_elev = IG_df["Height (m)"].max()

colormap = cm.LinearColormap(
    colors=["#2c7bb6", "#ffffbf", "#fdae61", "#d7191c"],
    vmin=min_elev,
    vmax=max_elev,
    caption="Elevation (m)"
)

for _, row in IG_df.iterrows():

    elev = row["Height (m)"]
    colour = colormap(elev)

    popup = f"""
    <b>{row['Nearest Place']}</b><br><br>
    Elevation: {elev} m*<br>
    Irish Grid Reference*: {row['Grid Ref']}<br>
    Latitude, Longitude*: {row['latitude']:.5f}, {row['longitude']:.5f}<br><br>
    <small>*Estimated elevation and location may not be accurate</small>
    """

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color='black',
        weight=2,
        fill=True,
        fill_color=colour,
        fill_opacity=1,
        
        popup=folium.Popup(popup, max_width=250)
    ).add_to(m)

colormap.add_to(m)

m.save("bin/index.html")