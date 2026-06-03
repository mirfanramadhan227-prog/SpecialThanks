def build_popup_html(gdf):

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

    return gdf