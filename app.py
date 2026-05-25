import pandas as pd
import geopandas as gpd
import folium
import json

from folium.plugins import Search
from folium.plugins import Fullscreen
from folium.plugins import MiniMap

from branca.element import Template, MacroElement

# ====================================
# BACA EXCEL
# ====================================

df = pd.read_excel("data.xlsx")

# RAPIIKAN CLIENT
df["Client"] = (
    df["Client"]
    .fillna("")
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# RAPIIKAN COMMODITY
df["Commodity"] = (
    df["Commodity"]
    .fillna("")
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Rapikan huruf

df["kabupaten"] = (
    df["kabupaten"]
    .astype(str)
    .str.upper()
    .str.strip()
)

# ====================================
# GROUP DATA PER KABUPATEN
# ====================================

grouped = df.groupby("kabupaten").agg({

    "Client": lambda x:
        "<br>".join(

            sorted(

                set(

                    str(i).strip()

                    for i in x.dropna()

                    if str(i).strip()

                )

            )

        ),

    "Commodity": lambda x:
        "<br>".join(

            sorted(

                set(

                    item.strip().upper()

                    for value in x.dropna()

                    for item in str(value).split(",")

                    if item.strip()

                )

            )

        )

}).reset_index()

# ====================================
# BACA GEOJSON
# ====================================

gdf = gpd.read_file(
    "GeoJson-Indonesia-38-Provinsi/Kabupaten/38 Provinsi Indonesia - Kabupaten.json"
)

gdf["WADMKK"] = (
    gdf["WADMKK"]
    .astype(str)
    .str.upper()
    .str.strip()
)
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

    "<div class='popupContainer'>"

    # TITLE
    "<div class='popupTitle'>"
    + gdf["WADMKK"].fillna("")
    + "</div>"

    # CLIENT
    "<div class='popupSection'>"

    "<div class='popupLabel'>"
    "Client"
    "</div>"

    "<div class='popupContent'>"

    + gdf["Client"].fillna("-")

    + "</div>"
    "</div>"

    # COMMODITY
    "<div class='popupSection'>"

    "<div class='popupLabel'>"
    "Commodity"
    "</div>"

    "<div class='popupContent'>"

    + gdf["Commodity"].fillna("-")

    + "</div>"
    "</div>"

    "</div>"
)

# ====================================
# BUAT PETA
# ====================================

m = folium.Map(
    location=[-2.5, 118],
    zoom_start=5,
    tiles=None
)

folium.TileLayer(
    "OpenStreetMap",
    name="OpenStreetMap",
    show=True
).add_to(m)

# ====================================
# BASEMAPS
# ====================================

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Terrain",
    show=False
).add_to(m)

folium.TileLayer(
    "CartoDB positron",
    name="Light Mode",
    show=False
).add_to(m)

folium.TileLayer(
    "CartoDB dark_matter",
    name="Dark Mode",
    show=False
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
    control=False,
    zoom_on_click=True,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip,
    embed=True,

    popup=folium.GeoJsonPopup(
        fields=["popup_html"],
        aliases=[""],
        labels=False,
        parse_html=True,
        max_width=380
    )
)

geojson.add_to(m)

# ====================================
# MARKER
# ====================================

for idx, row in gdf.iterrows():

    if row["ADA_DATA"]:

        folium.CircleMarker(

            location=[row["lat"], row["lon"]],

            radius=2,

            color="#00aa00",

            fill=True,

            fill_color="#00cc00",

            fill_opacity=0.9,

            tooltip=row["WADMKK"]

        ).add_to(m)

# ====================================
# LAYER CONTROL
# ====================================

folium.LayerControl().add_to(m)

# ====================================
# STATISTIK DASHBOARD
# ====================================

kabupaten_aktif = gdf["ADA_DATA"].sum()

total_client = df["Client"].nunique()

total_commodity = (

    df["Commodity"]

    .dropna()

    .astype(str)

    .str.split(",")

    .explode()

    .str.strip()

    .nunique()

)

# ====================================
# DROPWON FILTER CLIENT
# ====================================

client_list = sorted(df["Client"].dropna().unique())

client_options = ""

for client in client_list:
    client_options += f'<option value="{client}">{client}</option>'

# ====================================
# COMMODITY ANALYTICS
# ====================================


# ====================================
# DROPDOWN FILTER COMMODITY
# ====================================

commodity_list = sorted(

    df["Commodity"]

    .dropna()

    .astype(str)

    .str.split(",")

    .explode()

    .str.strip()

    .str.upper()

    .unique()

)

options = "".join([
    f'<option value="{c}">{c}</option>'
    for c in commodity_list
])

# ====================================
# RAW CLIENT-COMMODITY RELATION
# ====================================

raw_relation = []

for _, row in df.iterrows():

    client = str(row["Client"]).strip()

    commodities = (
        str(row["Commodity"])
        .split(",")
    )

    for com in commodities:

        clean_com = com.strip().upper()

        if client and clean_com:

            raw_relation.append({
                "client": client,
                "commodity": clean_com
            })

raw_relation_json = json.dumps(raw_relation)

template = f"""
{{% macro html(this, kwargs) %}}

<div id="loadingSpinner">

    <div class="spinner"></div>

    <div class="loadingText">
        Loading GIS Dashboard...
    </div>

</div>

<link rel="stylesheet" href="/static/css/style.css">

<button id="toggleSidebar">
☰
</button>

<div id='sidebar'>

<h2 class="dashboardTitle">
GIS Dashboard
</h2>

<input
type="text"
id="searchBox"
placeholder="Cari Kabupaten..."
>

<div class="cardBox">

<div class="infoItem">
<b>Kabupaten Aktif</b><br>
<span id="kpiKabupaten">
{kabupaten_aktif}
</span>
</div>

<div class="infoItem">
<b>Total Client</b><br>
<span id="kpiClient">
{total_client}
</span>
</div>

<div>
<b>Total Commodity</b><br>
<span id="kpiCommodity">
{total_commodity}
</span>
</div>

</div>

<b>Filter Client</b><br><br>

<select id="clientFilter"
class="filterSelect">

<option value="ALL">All Client</option>

{client_options}

</select>

<br><br>

<b>Filter Commodity</b><br><br>

<select id="commodityFilter"
class="filterSelect">

<option value="ALL">All Commodity</option>

{options}

</select>

<br><br>

<button id="clearFilterBtn">
Clear Filter
</button>

<br><br>

<div class="cardBox">

    <h3 class="sectionTitle">
        Related Analytics
    </h3>

    <div id="relatedAnalytics">

        No Filter Selected

    </div>

</div>

<br>

<div class="cardBox">

    <h3
    class="sectionTitle"
    id="topCommodityTitle"
    >
        Top 5 Commodity National
    </h3>

    <div id="topCommodityBox">

        Loading...

    </div>

</div>

<div id="floatingLegend">
<h3 style="
margin-top:0;
margin-bottom:12px;
font-size:18px;
">
Legend
</h3>

<div class="infoItem">

<span class="legendColor redLegend"></span>

Kabupaten dengan data

</div>

<div class="infoItem">

<span class="legendColor grayLegend"></span>

Kabupaten tanpa data

</div>

<div>
<span class="legendColor greenLegend"></span>

Marker lokasi client
</div>

</div>

<script>

const rawRelationData =
{raw_relation_json};

</script>

<script src="/static/js/main.js"></script>

{{% endmacro %}}
"""

macro = MacroElement()
macro._template = Template(template)

m.get_root().add_child(macro)

# ====================================
# SIMPAN
# ====================================

m.save("templates/index.html")

print("Peta persebaran berhasil dibuat!")