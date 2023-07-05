import pandas as pd
import geopandas
from geopandas import GeoDataFrame
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from itertools import permutations

# button = tk.Button(master=root, text="Erstellen", command=_firstPlot)
# button.pack(side=tk.BOTTOM)
# button = tk.Button(master=root, text="Verlassen", command=_quit)
# button.pack(side=tk.BOTTOM)
# Dateipfade der shp-Dateien
fp_bzr = "lor_bzr.shp"
fp_bzr = "lor_bzr.shp"
fp_pgr = "lor_pgr.shp"
fp_plr = "lor_plr.shp"
straßennetz = "Detailnetz-Strassenabschnitte.shp"
fp_pgr = "lor_pgr.shp"

# Laden der Gewerbedaten
dfGewerbe = pd.read_csv("IHKBerlin_Gewerbedaten.csv", sep=",")
# Laden der Zugstationen
train_stations = pd.read_json("train_stations.json")
# Laden der Bezirksregionen
data_bzr = geopandas.read_file(fp_bzr)
# Lesen der PGR-Daten
data_pgr = geopandas.read_file(fp_pgr)
# Laden der Planungsräume
data_plr = geopandas.read_file(fp_plr)
# Laden des Straßennetzes
data_straßennetz = geopandas.read_file(straßennetz)
# Laden der Fallzahlen
dfKrimi = pd.read_csv(
    "Fallzahlen&HZ 2013-2022.csv",
    delimiter=";",
    dtype={"LOR-Schlüssel (Bezirksregion)": str},
)
# Kitas laden
dfKitas = pd.read_csv("berlin_kitas.csv", delimiter=";")  # error_bad_lines=False

# Krimi Daten aufbereiten
dfKrimi["Straftaten -insgesamt-"] = dfKrimi["Straftaten -insgesamt-"].str.replace(
    ".", ""
)

dfKrimi["Straftaten -insgesamt-"] = (
    pd.to_numeric(dfKrimi["Straftaten -insgesamt-"], errors="coerce")
    .fillna(0)
    .astype(float)
)
dfKrimiWithGeoData = pd.merge(
    dfKrimi,
    data_bzr,
    left_on="LOR-Schlüssel (Bezirksregion)",
    right_on="BZR_ID",
)
gdfKrimiWithGeoData = GeoDataFrame(
    dfKrimiWithGeoData, crs="EPSG:25833", geometry="geometry"
)

gdfGewerbe = geopandas.GeoDataFrame(
    dfGewerbe,
    geometry=geopandas.points_from_xy(dfGewerbe["longitude"], dfGewerbe["latitude"]),
    crs="ETRS89",
)
gdfGewerbe = gdfGewerbe.to_crs(epsg=25833)

train_stations_df = pd.DataFrame(train_stations)

train_stations_gdf = geopandas.GeoDataFrame(
    train_stations_df,
    geometry=geopandas.points_from_xy(
        train_stations_df["Longitude"], train_stations_df["Latitude"]
    ),
    crs="ETRS89",
)
train_stations_gdf = train_stations_gdf.to_crs(epsg=25833)

gdfKitas = geopandas.GeoDataFrame(
    dfKitas,
    geometry=geopandas.points_from_xy(dfKitas["lon"], dfKitas["lat"]),
    crs="ETRS89",
)

gdfKitas = gdfKitas.to_crs(epsg=25833)

# Create the tkinter window
window = tk.Tk()
window.title("IHK-Projekt Gruppe NOLL")
window.state("zoomed")

fig, ax = plt.subplots(figsize=(4, 3))

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Create the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.pack(side=tk.BOTTOM, fill=tk.X)

# Create a frame with a scrollbar for the dropdowns
frame = tk.Frame(window)
frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

dropdown_frame = tk.Canvas(frame, yscrollcommand=scrollbar.set)
dropdown_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=dropdown_frame.yview)

# Generate all possible color combinations
colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
color_combinations = list(permutations(colors, 3))

legends = {
    "filteredGewerbe": "Gewerbe",
    "gdfKitas": "Kitas",
    "train_stations_gdf": "Bahnhöfe",
}


def update_figure(event=None):
    ax.clear()
    ax.set_axis_off()

    # Get the values from the sliders and dropdown
    slider1_value = dropdown1.get()
    slider2_value = dropdown2.get()
    slider3_value = dropdown3.get()
    dropdown_value = dropdown.get()

    # Get the selected color combination
    selected_colors = color_dropdown.get().split(",")
    selected_colors = selected_colors[0].split()

    color1, color2, color3 = (
        selected_colors if len(selected_colors) == 3 else ["green", "red", "blue"]
    )

    edgecolor = "black"
    slider1_marker = int(slider1_value) if int(slider1_value) else 0
    slider2_marker = int(slider2_value) if int(slider2_value) else 0
    slider3_marker = int(slider3_value) if int(slider3_value) else 0
    filteredGewerbe = (
        gdfGewerbe[gdfGewerbe["ihk_branch_desc"] == dropdown_value]
        if dropdown_value
        else gdfGewerbe
    )

    alphaGewerbe = 1 if dropdown_value else 0.1

    # data_bzr.geometry.boundary.plot(color=None,edgecolor='red',linewidth = 1,ax=ax)
    # data_plr.geometry.boundary.plot(color=None,edgecolor='black',linewidth = 1,ax=ax)
    # data_straßennetz.plot(color=None,edgecolor='grey',linewidth = 0.2,ax=ax)
    # data_pgr.geometry.boundary.plot(color=None, edgecolor="black", linewidth=1, ax=ax)

    # Plot the combined GeoDataFrame

    gdfKrimiWithGeoData.plot(
        column="Straftaten -insgesamt-",
        cmap="YlOrRd",
        linewidth=0.3,
        edgecolor=edgecolor,
        ax=ax,
    )
    filteredGewerbe.plot(
        markersize=(slider2_marker),
        color=color1,
        ax=ax,
        label=legends["filteredGewerbe"],
        alpha=alphaGewerbe,
    )
    gdfKitas.plot(
        markersize=slider1_marker,
        color=color2,
        ax=ax,
        marker="s",
        label=legends["gdfKitas"],
    )
    train_stations_gdf.plot(
        markersize=(slider3_marker),
        color=color3,
        ax=ax,
        label=legends["train_stations_gdf"],
    )
    plt.tight_layout()
    # Add legend to the plot
    legend = ax.legend(loc="lower left", prop={"size": 5})

    # Set marker sizes in the legend
    for lh in legend.legend_handles:
        lh._sizes = [30]
    # Re-render the matplotlib figure
    canvas.draw()


# Create a new dropdown for color combinations
color_dropdown_label = tk.Label(dropdown_frame, text="Color Combination")
color_dropdown_label.grid(row=0, column=0, sticky="w")
color_dropdown = ttk.Combobox(dropdown_frame, values=color_combinations)
color_dropdown.grid(row=0, column=1, sticky="w")
color_dropdown.bind("<<ComboboxSelected>>", update_figure)
# Set default value for the color dropdown
color_dropdown.set(color_combinations[0])

dropdown_label1 = tk.Label(dropdown_frame, text="Kitas")
dropdown_label1.grid(row=1, column=0, sticky="w")
dropdown1 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown1.set("1")
dropdown1.grid(row=1, column=1, sticky="w")
dropdown1.bind("<<ComboboxSelected>>", update_figure)

dropdown_label2 = tk.Label(dropdown_frame, text="Gewerbe")
dropdown_label2.grid(row=1, column=2, sticky="w")
dropdown2 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown2.set("1")
dropdown2.grid(row=1, column=3, sticky="w")
dropdown2.bind("<<ComboboxSelected>>", update_figure)

dropdown_label3 = tk.Label(dropdown_frame, text="Bahnhöfe")
dropdown_label3.grid(row=2, column=0, sticky="w")
dropdown3 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown3.set("1")
dropdown3.grid(row=2, column=1, sticky="w")
dropdown3.bind("<<ComboboxSelected>>", update_figure)

# Create the searchable dropdown
dropdown_label = tk.Label(dropdown_frame, text="Branche")
dropdown_label.grid(row=2, column=2, sticky="w")
dropdown_values = dfGewerbe["ihk_branch_desc"].unique().tolist()
dropdown = ttk.Combobox(dropdown_frame, values=dropdown_values)
dropdown.grid(row=2, column=3, sticky="w")
dropdown.bind("<<ComboboxSelected>>", update_figure)

update_figure()

window.mainloop()


def calculateScore():
    gdfKitas = geopandas.GeoDataFrame(
        dfKitas,
        geometry=geopandas.points_from_xy(dfKitas["lon"], dfKitas["lat"]),
        crs="ETRS89",
    )

    gdfKitas = gdfKitas.to_crs(epsg=25833)

    # Create GeoDataFrames from the DataFrames
    #gdfKitas = gpd.GeoDataFrame(dfKitas, geometry=gpd.points_from_xy(dfKitas['lon'], dfKitas['lat']))
    #gdfDataBzr = gpd.GeoDataFrame(data_bzr)
    data_bzr.info()

    # Create an empty column 'Bezirksregion' in dfKitas
    gdfKitas['Bezirksregion'] = ''

    # Iterate over each row in dfKitas
    for indexKita, kita in gdfKitas.iterrows():
        # Iterate over each row in data_bzr
        for index, bzr in data_bzr.iterrows():
            # Check if the point is within the polygon
            if kita['geometry'].within(bzr['geometry']):
                # Assign the Bezirksregion value to dfKitas
                gdfKitas.at[indexKita, 'Bezirksregion'] = bzr['BZR_NAME']
                break  # Exit the inner loop if a match is found

    gdfKitas.groupby('Bezirksregion').count().sort_values(by=['postcode'], ascending=False).head(25)
