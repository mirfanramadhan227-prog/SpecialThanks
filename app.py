import pandas as pd
import geopandas as gpd
import folium
import json
from flask import Flask

from folium.plugins import Search
from folium.plugins import Fullscreen
from folium.plugins import MiniMap

from branca.element import Template, MacroElement
app = Flask(__name__)

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

    # HEADER
    "<div class='popupHeader'>"

    "<div class='popupKabupaten'>"

    + gdf["WADMKK"].fillna("")

    + "</div>"

    "<div class='popupStats'>"

    "<div class='popupBadge'>👥 Client</div>"

    "<div class='popupBadge'>📦 Commodity</div>"

    "</div>"

    "</div>"

    # BODY
    "<div class='popupBody'>"

    # CLIENT
    "<div class='popupSectionModern'>"

    "<div class='popupSectionTitle'>"
    "Client"
    "</div>"

    "<div class='popupList'>"

    +

    gdf["Client"]

    .fillna("-")

    .astype(str)

    .str.replace(
        "<br>",
        "</div><div class='popupItem'>"
    )

    .radd("<div class='popupItem'>")

    .add("</div>")

    +

    "</div>"

    "</div>"

    # COMMODITY
    "<div class='popupSectionModern'>"

    "<div class='popupSectionTitle'>"
    "Commodity"
    "</div>"

    "<div class='popupList'>"

    +

    gdf["Commodity"]

    .fillna("-")

    .astype(str)

    .str.replace(
        "<br>",
        "</div><div class='popupItem'>"
    )

    .radd("<div class='popupItem'>")

    .add("</div>")

    +

    "</div>"

    "</div>"

    "</div>"

    "</div>"
)

# ====================================
# FUNCTION BUILD MAP
# ====================================

def build_map():

    m = folium.Map(
        location=[-2.5, 118],
        zoom_start=5,
        tiles=None
    )

    folium.TileLayer(
        "OpenStreetMap",
        name="OpenStreetMap",
        show=True,
        control=True,
        attr="OpenStreetMap",
        overlay=False,
        crossOrigin=True
    ).add_to(m)

    # ====================================
    # BASEMAPS
    # ====================================

    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Terrain",
        show=False,
        crossOrigin=True
    ).add_to(m)

    folium.TileLayer(
        "CartoDB positron",
        name="Light Mode",
        show=False,
        crossOrigin=True
    ).add_to(m)

    folium.TileLayer(
        "CartoDB dark_matter",
        name="Dark Mode",
        show=False,
        crossOrigin=True
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

    # ====================================
    # CLIENT CHECKBOX HTML
    # ====================================

    client_checkbox_options = ""

    for client in client_list:

        client_checkbox_options += f"""

        <label class="checkboxItem">

            <input
            type="checkbox"
            class="clientCheckbox"
            value="{client}"
            >

            <span>{client}</span>

        </label>

        """

    # ====================================
    # COMMODITY CHECKBOX HTML
    # ====================================

    commodity_checkbox_options = ""

    for commodity in commodity_list:

        commodity_checkbox_options += f"""

        <label class="checkboxItem">

            <input
            type="checkbox"
            class="commodityCheckbox"
            value="{commodity}"
            >

            <span>{commodity}</span>

        </label>

        """

    template = f"""
    {{% macro html(this, kwargs) %}}

    <div id="loadingSpinner">

        <div class="spinner"></div>

        <div class="loadingText">
            Loading GIS Dashboard...
        </div>

    </div>

    <link
    rel="stylesheet"
    href="static/css/style.css"
    >

    <button id="toggleSidebar">
    ☰
    </button>

    <div id="mapExportContainer">

        <div id="exportWatermark">

            <img
            src="data:image/png;base64,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"
            alt="Logo"
            >

        </div>

    <div id='sidebar'>

        <h2 class="dashboardTitle">
        GIS Dashboard
        </h2>

        <input
        type="text"
        id="searchBox"
        placeholder="Cari Kabupaten..."
        >

        <div class="kpiContainer">

            <div class="kpiCard">

                <div class="kpiIcon">
                    🗺
                </div>

                <div class="kpiContent">

                    <div class="kpiTitle">
                        Kabupaten Aktif
                    </div>

                    <div
                    class="kpiValue"
                    id="kpiKabupaten"
                    >
                        {kabupaten_aktif}
                    </div>

                </div>

            </div>

            <div class="kpiCard">

                <div class="kpiIcon">
                    🏢
                </div>

                <div class="kpiContent">

                    <div class="kpiTitle">
                        Total Client
                    </div>

                    <div
                    class="kpiValue"
                    id="kpiClient"
                    >
                        {total_client}
                    </div>

                </div>

            </div>

            <div class="kpiCard">

                <div class="kpiIcon">
                    📦
                </div>

                <div class="kpiContent">

                    <div class="kpiTitle">
                        Total Commodity
                    </div>

                    <div
                    class="kpiValue"
                    id="kpiCommodity"
                    >
                        {total_commodity}
                    </div>

                </div>

            </div>

        </div>

        <b>Filter Client</b><br><br>

        <div class="advancedFilterBox">

        <div class="filterHeader">
                Client Filter
            </div>

            <input
            type="text"
            id="clientSearch"
            class="advancedSearch"
            placeholder="Search client..."
            >

            <div
            id="clientCheckboxContainer"
            class="checkboxContainer"
            >

                {client_checkbox_options}

            </div>

        </div>

        <br><br>

        <b>Filter Commodity</b><br><br>

        <div class="advancedFilterBox">

            <div class="filterHeader">
                Commodity Filter
            </div>

            <input
            type="text"
            id="commoditySearch"
            class="advancedSearch"
            placeholder="Search commodity..."
            >

            <div
            id="commodityCheckboxContainer"
            class="checkboxContainer"
            >

                {commodity_checkbox_options}

            </div>

        </div>

        <br><br>

        <button id="clearFilterBtn">
        Clear Filter
        </button>

        <br><br>

        <div class="exportWrapper">

        <button id="exportBtn">
            Export
        </button>

        </div>

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

    </div>

    <div id="exportModal" class="exportModal hiddenExportModal">

            <div class="exportModalContent">

                <h2>Export Dashboard</h2>

                <button id="exportPNG">
                    Export PNG
                </button>

                <button id="exportPDF">
                    Export PDF
                </button>

                <button id="exportCSV">
                    Export CSV Filtered Data
                </button>

                <button id="closeExportModal">
                    Cancel
                </button>

            </div>

        </div>

        <div id="exportLoading" class="hiddenExportLoading">

            <div class="exportLoadingBox">

                <div class="exportSpinner"></div>

                <h2>Preparing Export...</h2>

                <p>Please wait a moment</p>

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

    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

    <script src="static/js/main.js"></script>

    {{% endmacro %}}
    """

    macro = MacroElement()
    macro._template = Template(template)
    
    m.get_root().add_child(macro)

    return m

@app.route("/")
def home():

    m = build_map()

    return m.get_root().render()

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )