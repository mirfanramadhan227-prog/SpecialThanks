import pandas as pd
import geopandas as gpd
import folium

from folium.plugins import Search
from folium.plugins import Fullscreen
from folium.plugins import MiniMap

from branca.element import Template, MacroElement

# ====================================
# BACA EXCEL
# ====================================

df = pd.read_excel("data.xlsx")

# Rapikan huruf
df["kabupaten"] = df["kabupaten"].str.upper()

# ====================================
# GROUP DATA PER KABUPATEN
# ====================================

grouped = df.groupby("kabupaten").agg({

    "Client": lambda x:
        "<br>".join("- " + str(i) for i in x.dropna().unique()),

    "Commodity": lambda x:
        "<br>".join("- " + str(i) for i in x.dropna().unique())

}).reset_index()

# ====================================
# BACA GEOJSON
# ====================================

gdf = gpd.read_file(
    "GeoJson-Indonesia-38-Provinsi/Kabupaten/38 Provinsi Indonesia - Kabupaten.json"
)

gdf["WADMKK"] = gdf["WADMKK"].str.upper()

# ====================================
# JOIN DATA
# ====================================

gdf = gdf.merge(
    grouped,
    how="left",
    left_on="WADMKK",
    right_on="kabupaten"
)

# ====================================
# STATUS DATA
# ====================================

gdf["ADA_DATA"] = gdf["Client"].notnull()

# ====================================
# FILTER DATA STRING
# ====================================

gdf["FILTER_CLIENT"] = (
    gdf["Client"]
    .fillna("")
    .astype(str)
)

gdf["FILTER_COMMODITY"] = (
    gdf["Commodity"]
    .fillna("")
    .astype(str)
)

# ====================================
# BUAT TITIK TENGAH
# ====================================

center = gdf.to_crs(epsg=3857).geometry.centroid.to_crs(gdf.crs)

gdf["lat"] = center.y
gdf["lon"] = center.x

# ====================================
# BUAT HTML POPUP
# ====================================

gdf["popup_html"] = (

    "<div style='font-size:13px;'>"

    "<b>Kabupaten:</b> " +
    gdf["WADMKK"].fillna("") +

    "<br><br>"

    "<b>Client:</b><br>" +
    gdf["Client"].fillna("-") +

    "<br><br>"

    "<b>Commodity:</b><br>" +
    gdf["Commodity"].fillna("-") +

    "</div>"
)

# ====================================
# BUAT PETA
# ====================================

m = folium.Map(
    location=[-2.5, 118],
    zoom_start=5,
    tiles="OpenStreetMap"
)

# ====================================
# BASEMAPS
# ====================================

folium.TileLayer(
    "CartoDB positron",
    name="Light Mode"
).add_to(m)

folium.TileLayer(
    "CartoDB dark_matter",
    name="Dark Mode"
).add_to(m)

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Terrain"
).add_to(m)

# ====================================
# FULLSCREEN BUTTON
# ====================================

Fullscreen(
    position="topright",
    title="Fullscreen",
    title_cancel="Exit Fullscreen",
    force_separate_button=True
).add_to(m)

# ====================================
# MINI MAP
# ====================================

minimap = MiniMap(
    toggle_display=True,
    position="bottomright"
)

m.add_child(minimap)

# ====================================
# STYLE NORMAL
# ====================================

def style_function(feature):

    if feature["properties"]["ADA_DATA"]:

        return {
            "fillColor": "#ff8080",
            "color": "#b30000",
            "weight": 1.5,
            "fillOpacity": 0.55,
        }

    else:

        return {
            "fillColor": "#d9d9d9",
            "color": "#999999",
            "weight": 0.5,
            "fillOpacity": 0.08,
        }

# ====================================
# STYLE HOVER
# ====================================

def highlight_function(feature):

    return {
        "fillColor": "#ffff00",
        "color": "#000000",
        "weight": 4,
        "fillOpacity": 0.95,
    }

# ====================================
# TOOLTIP
# ====================================

tooltip = folium.GeoJsonTooltip(
    fields=["WADMKK"],
    aliases=["Kabupaten:"],
    sticky=True
)

# ====================================
# GEOJSON
# ====================================

geojson = folium.GeoJson(
    gdf,
    name="commodity_layer",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip,
    embed=True,

    popup=folium.GeoJsonPopup(
        fields=["popup_html"],
        aliases=[""],
        labels=False,
        parse_html=True,
        max_width=350
    )
)

geojson.add_to(m)

# ====================================
# SEARCH
# ====================================

Search(
    layer=geojson,
    search_label="WADMKK",
    placeholder="Cari Kabupaten...",
    collapsed=False,
).add_to(m)

# ====================================
# MARKER
# ====================================

for idx, row in gdf.iterrows():

    if row["ADA_DATA"]:

        folium.CircleMarker(

            location=[row["lat"], row["lon"]],

            radius=4,

            color="red",

            fill=True,

            fill_color="red",

            fill_opacity=1,

            tooltip=row["WADMKK"]

        ).add_to(m)

# ====================================
# LAYER CONTROL
# ====================================

folium.LayerControl().add_to(m)

# ====================================
# LEGEND
# ====================================

legend_html = """
<div style="
position: fixed;
bottom: 30px;
left: 30px;
width: 220px;
z-index:9999;
background-color:white;
border:2px solid grey;
border-radius:10px;
padding:15px;
font-size:14px;
box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
">

<b>Legend</b><br><br>

<div style="
width:18px;
height:18px;
background:#ff4d4d;
display:inline-block;
margin-right:8px;
border:1px solid black;
"></div>

Kabupaten dengan data client
<br><br>

<div style="
width:18px;
height:18px;
background:#d9d9d9;
display:inline-block;
margin-right:8px;
border:1px solid gray;
"></div>

Kabupaten tanpa data
<br><br>

📍 Marker lokasi client

</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

# ====================================
# STATISTIK DASHBOARD
# ====================================

kabupaten_aktif = gdf["ADA_DATA"].sum()

total_client = df["Client"].nunique()

total_commodity = df["Commodity"].nunique()

stats_html = f"""
<div style="
position: fixed;
top: 10px;
left: 50%;
transform: translateX(-50%);
z-index:9999;

background-color: white;
padding: 15px 25px;

border-radius: 12px;
box-shadow: 0 2px 10px rgba(0,0,0,0.25);

font-size: 14px;
font-family: Arial;

display: flex;
gap: 30px;
">

<div>
<b>Kabupaten Aktif</b><br>
{kabupaten_aktif}
</div>

<div>
<b>Total Client</b><br>
{total_client}
</div>

<div>
<b>Total Commodity</b><br>
{total_commodity}
</div>

</div>
"""

m.get_root().html.add_child(folium.Element(stats_html))

# ====================================
# DROPWON FILTER CLIENT
# ====================================

client_list = sorted(df["Client"].dropna().unique())

client_options = ""

for client in client_list:
    client_options += f'<option value="{client}">{client}</option>'

# ====================================
# DROPDOWN FILTER COMMODITY
# ====================================

commodity_list = sorted(df["Commodity"].dropna().unique())

options = "".join([
    f'<option value="{c}">{c}</option>'
    for c in commodity_list
])

template = f"""
{{% macro html(this, kwargs) %}}

<div id='maplegend'
style='
position: fixed;
top: 120px;
left: 10px;
z-index:9999;

background-color:white;
padding:10px;
border-radius:8px;
box-shadow:0 0 10px rgba(0,0,0,0.3);
font-size:14px;
'>

<b>Filter Client</b><br><br>

<select id="clientFilter"
style="
width:160px;
padding:5px;
">

<option value="ALL">All Client</option>

{client_options}

</select>

<br><br>

<b>Filter Commodity</b><br><br>

<select id="commodityFilter"
style="
width:160px;
padding:5px;
">

<option value="ALL">All Commodity</option>

{options}

</select>

<br><br>

<button id="clearFilterBtn"
style="
width:120px;
padding:6px;
background:white;
color:black;
border:1px solid black;
border-radius:5px;
cursor:pointer;
font-size:12px;
font-weight:600;
">
Clear Filter
</button>

</div>

<script>

document
.getElementById("commodityFilter")
.addEventListener("change", function() {{

    alert(
        "Filter commodity akan kita upgrade di tahap berikutnya"
    );

}});

document
.getElementById("clearFilterBtn")
.addEventListener("click", function() {{

    document.getElementById("commodityFilter").value = "ALL";

    document.getElementById("clientFilter").value = "ALL";

}});

</script>

{{% endmacro %}}
"""

macro = MacroElement()
macro._template = Template(template)

m.get_root().add_child(macro)

# ====================================
# SIMPAN
# ====================================

m.save("index.html")

print("Peta persebaran berhasil dibuat!")