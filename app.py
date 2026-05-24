import pandas as pd
import geopandas as gpd
import folium

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

    style_function=style_function,

    highlight_function=highlight_function,

    tooltip=tooltip,

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
# SIMPAN
# ====================================

m.save("index.html")

print("Peta persebaran berhasil dibuat!")