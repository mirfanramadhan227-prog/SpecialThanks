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
        "<br>".join("- " + i for i in x.unique()),

    "Commodity": lambda x:
        "<br>".join("- " + i for i in x.unique())

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
# BUAT TITIK TENGAH KABUPATEN
# ====================================

center = gdf.to_crs(epsg=3857).geometry.centroid.to_crs(gdf.crs)

gdf["lat"] = center.y
gdf["lon"] = center.x

# ====================================
# BUAT PETA
# ====================================

m = folium.Map(
    location=[-2.5, 118],
    zoom_start=5,
    tiles="OpenStreetMap"
)

# ====================================
# STYLE WARNA
# ====================================

def style_function(feature):

    if feature["properties"]["ADA_DATA"] == True:
        return {
            "fillColor": "red",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7
        }

    else:
        return {
            "fillColor": "gray",
            "color": "gray",
            "weight": 0.5,
            "fillOpacity": 0.1
        }

# ====================================
# BUAT HTML POPUP CUSTOM
# ====================================

gdf["popup_html"] = (

    "<b>Kabupaten:</b> " + gdf["WADMKK"].fillna("") +

    "<br><br>" +

    "<b>Client:</b><br>" +
    gdf["Client"].fillna("") +

    "<br><br>" +

    "<b>Commodity:</b><br>" +
    gdf["Commodity"].fillna("")
)

# ====================================
# TOOLTIP
# ====================================

tooltip = folium.GeoJsonTooltip(
    fields=["WADMKK"],
    aliases=["Kabupaten:"]
)

# ====================================
# TAMBAHKAN KE PETA
# ====================================

geojson = folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=tooltip,
    popup=folium.GeoJsonPopup(
    fields=["popup_html"],
    aliases=[""],
    labels=False,
    parse_html=True
)
)

geojson.add_to(m)

# ====================================
# TAMBAHKAN MARKER
# ====================================

for idx, row in gdf.iterrows():

    # hanya kabupaten yang ada data
    if row["ADA_DATA"] == True:

        popup_text = f"""
        <b>Kabupaten:</b> {row['WADMKK']}<br><br>

        <b>Client:</b><br>
        {row['Client']}<br><br>

        <b>Commodity:</b><br>
        {row['Commodity']}
        """

        folium.Marker(
            location=[row["lat"], row["lon"]],

            popup=folium.Popup(
                popup_text,
                max_width=300
            ),

            tooltip=row["WADMKK"],

            icon=folium.Icon(
                color="red",
                icon="info-sign"
            )

        ).add_to(m)

# ====================================
# SIMPAN HTML
# ====================================

m.save("peta_persebaran.html")

print("Peta persebaran berhasil dibuat!")