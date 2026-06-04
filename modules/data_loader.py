import pandas as pd
import geopandas as gpd

from modules.database import engine
from modules.popup_builder import build_popup_html

def load_data():
    
    sql_df = """
    SELECT *
    FROM client_project
    """

    df = pd.read_sql(
        sql_df,
        engine
    )

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
    # BACA SPATIAL DATA
    # ====================================

    sql_gdf = """
    SELECT *
    FROM kabupaten_indonesia
    """

    gdf = gpd.read_postgis(
        sql_gdf,
        engine,
        geom_col="geometry"
    )

    normalisasi = {
        "Ambon": "Kota Ambon",
        "Bandar Lampung": "Kota Bandar Lampung",
        "Banjarmasin": "Kota Banjarmasin",
        "Baubau": "Kota Bau Bau",
        "Medan": "Kota Medan",
        "Pontianak": "Kota Pontianak",
        "Samarinda": "Kota Samarinda",
        "Jakarta": "Kota Administrasi Jakarta Selatan"
    }

    grouped["kabupaten"] = (
        grouped["kabupaten"]
        .replace(normalisasi)
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

    gdf["ADA_DATA"] = (
        gdf["Client"]
        .fillna("")
        .str.strip()
        .ne("")
    )

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

    gdf = build_popup_html(gdf)

    return gdf, df