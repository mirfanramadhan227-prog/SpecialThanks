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
    "CartoDB positron",
    name="Light Mode",
    show=False
).add_to(m)

folium.TileLayer(
    "CartoDB dark_matter",
    name="Dark Mode",
    show=False
).add_to(m)

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Terrain",
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
    name="Layer",
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
        max_width=350
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
# STATISTIK DASHBOARD
# ====================================

kabupaten_aktif = gdf["ADA_DATA"].sum()

total_client = df["Client"].nunique()

total_commodity = df["Commodity"].nunique()

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

commodity_count = (
    df["Commodity"]
    .value_counts()
)

commodity_html = ""

max_value = commodity_count.max()

for commodity, value in commodity_count.items():

    width_percent = (value / max_value) * 100

    commodity_html += f"""

    <div style="margin-bottom:12px;">

        <div style="
        display:flex;
        justify-content:space-between;
        font-size:13px;
        margin-bottom:4px;
        ">

            <span>{commodity}</span>
            <span>{value}</span>

        </div>

        <div style="
        width:100%;
        background:#e0e0e0;
        height:10px;
        border-radius:10px;
        overflow:hidden;
        ">

            <div style="
            width:{width_percent}%;
            height:100%;
            background:#444;
            ">
            </div>

        </div>

    </div>
    """

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

<button id="toggleSidebar"
style="
position:absolute;
bottom:7px;
left:10px;
top:auto;
z-index:10000;

background:white;
border:none;

width:38px;
height:38px;

border-radius:10px;

box-shadow:0 2px 10px rgba(0,0,0,0.25);

cursor:pointer;

font-size:18px;
font-weight:bold;
"
>
☰
</button>

<div id='sidebar'
style='
position: fixed;
top: 10px;
left: 10px;
transition: all 0.3s ease;left: 10px;

width: 260px;
height: 92vh;

z-index:9999;

background: rgba(255,255,255,0.96);

padding:18px;

border-radius:14px;

box-shadow: 0 4px 20px rgba(0,0,0,0.25);

overflow-y:auto;

font-family:Arial;
'
>
<h2 style="
margin-top:0;
margin-bottom:10px;
font-size:22px;
font-weight:700;
color:#222;
">
GIS Dashboard
</h2>

<input
type="text"
id="searchBox"
placeholder="Cari Kabupaten..."
style="
width:100%;
padding:10px;
margin-bottom:18px;
border-radius:8px;
border:1px solid #ccc;
font-size:14px;
box-sizing:border-box;
"
>
</h2>

<div style="
background:#f7f7f7;
padding:12px;
border-radius:10px;
margin-bottom:20px;
">

<div style="margin-bottom:10px;">
<b>Kabupaten Aktif</b><br>
{kabupaten_aktif}
</div>

<div style="margin-bottom:10px;">
<b>Total Client</b><br>
{total_client}
</div>

<div>
<b>Total Commodity</b><br>
{total_commodity}
</div>

</div>

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

<br><br>

<div style="
background:#f7f7f7;
padding:12px;
border-radius:10px;
">

<div style="
background:#f7f7f7;
padding:12px;
border-radius:10px;
margin-bottom:20px;
">

<h3 style="
margin-top:0;
font-size:18px;
">
Commodity Analytics
</h3>

{commodity_html}

</div>

<div id="floatingLegend"
style="
position:fixed;
bottom:180px;
right:10px;

z-index:9999;

background:rgba(255,255,255,0.95);

padding:12px;

border-radius:12px;

box-shadow:0 2px 10px rgba(0,0,0,0.25);

font-family:Arial;

width:220px;
">

<h3 style="
margin-top:0;
margin-bottom:12px;
font-size:18px;
">
Legend
</h3>

<div style="margin-bottom:10px;">

<span style="
display:inline-block;
width:18px;
height:18px;
background:#ff4d4d;
border:1px solid black;
margin-right:8px;
"></span>

Kabupaten dengan data

</div>

<div style="margin-bottom:10px;">

<span style="
display:inline-block;
width:18px;
height:18px;
background:#d9d9d9;
border:1px solid gray;
margin-right:8px;
"></span>

Kabupaten tanpa data

</div>

<div>
📍 Marker lokasi client
</div>

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

const searchInput =
    document.getElementById("searchBox");

searchInput.addEventListener("keyup", function(e) {{

    const keyword =
        this.value.toUpperCase().trim();

    const layers = Object.values(window);

    layers.forEach(obj => {{

        if(obj instanceof L.GeoJSON){{

            obj.eachLayer(function(layer){{

                if(layer.feature){{

                    const props =
                        layer.feature.properties;

                    const kabupaten =
                        String(props.WADMKK || "")
                        .toUpperCase();

                    const client =
                        String(props.FILTER_CLIENT || "")
                        .toUpperCase();

                    const commodity =
                        String(props.FILTER_COMMODITY || "")
                        .toUpperCase();

                    const isMatch =
                        kabupaten.includes(keyword) ||
                        client.includes(keyword) ||
                        commodity.includes(keyword);

                    // =====================
                    // JIKA SEARCH KOSONG
                    // =====================

                    if(keyword === ""){{

                        layer.setStyle({{
                            fillColor:
                                props.ADA_DATA
                                ? "#ff8080"
                                : "#d9d9d9",

                            fillOpacity:
                                props.ADA_DATA
                                ? 0.55
                                : 0.08,

                            color:
                                props.ADA_DATA
                                ? "#b30000"
                                : "#999999",

                            weight:
                                props.ADA_DATA
                                ? 1.5
                                : 0.5
                        }});

                        return;
                    }}

                    // =====================
                    // MATCH
                    // =====================

                    if(isMatch){{

                        layer.setStyle({{
                            fillColor:"#ffff00",
                            fillOpacity:0.9,
                            weight:4,
                            color:"#000000"
                        }});

                        if(e.key === "Enter"){{

                            layer._map.fitBounds(
                            layer.getBounds()
                            );

                            layer.openPopup();
                        }}

                    }}

                    // =====================
                    // TIDAK MATCH
                    // =====================

                    else {{

                        layer.setStyle({{
                            fillColor:"#d9d9d9",
                            fillOpacity:0.03,
                            color:"#cccccc",
                            weight:0.3
                        }});
                    }}

                }}

            }});

        }}

    }});

}});
const sidebar = document.getElementById("sidebar");

const toggleBtn = document.getElementById("toggleSidebar");

let sidebarOpen = true;

toggleBtn.addEventListener("click", function() {{

    if(sidebarOpen){{

        sidebar.style.left = "-280px";

        sidebarOpen = false;

    }} else {{

        sidebar.style.left = "10px";

        sidebarOpen = true;

    }}

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