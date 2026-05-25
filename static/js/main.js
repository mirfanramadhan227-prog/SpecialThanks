function showLoading(){

    document
    .getElementById("loadingSpinner")
    .classList.remove("hidden");
}

function hideLoading(){

    document
    .getElementById("loadingSpinner")
    .classList.add("hidden");
}

function resetLayerStyle(layer, props){

    layer.setStyle({
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
    });
}

function updateKPI(){

    const selectedClient =
        document
        .getElementById("clientFilter")
        .value;

    const selectedCommodity =
        document
        .getElementById("commodityFilter")
        .value;

    let filteredData = rawRelationData;

    // =========================
    // FILTER CLIENT
    // =========================

    if(selectedClient !== "ALL"){

        filteredData =
            filteredData.filter(
                x => x.client === selectedClient
            );

    }

    // =========================
    // FILTER COMMODITY
    // =========================

    if(selectedCommodity !== "ALL"){

        filteredData =
            filteredData.filter(
                x => x.commodity === selectedCommodity
            );

    }

    // =========================
    // HITUNG KPI
    // =========================

    const clientSet =
        new Set();

    const commoditySet =
        new Set();

    filteredData.forEach(item => {

        clientSet.add(item.client);

        commoditySet.add(item.commodity);

    });

    // =========================
    // HITUNG KABUPATEN
    // =========================

    let activeKabupaten = 0;

    const layers = Object.values(window);

    layers.forEach(obj => {

        if(obj instanceof L.GeoJSON){

            obj.eachLayer(function(layer){

                if(layer.feature){

                    const props =
                        layer.feature.properties;

                    const client =
                        String(props.FILTER_CLIENT || "");

                    const commodity =
                        String(props.FILTER_COMMODITY || "");

                    let match = true;

                    if(selectedClient !== "ALL"){

                        match =
                            match &&
                            client.includes(
                                selectedClient
                            );

                    }

                    if(selectedCommodity !== "ALL"){

                        match =
                            match &&
                            commodity.includes(
                                selectedCommodity
                            );

                    }

                    if(match && props.ADA_DATA){

                        activeKabupaten++;

                    }

                }

            });

        }

    });

    // =========================
    // UPDATE HTML
    // =========================

    document.getElementById(
        "kpiKabupaten"
    ).innerText = activeKabupaten;

    document.getElementById(
        "kpiClient"
    ).innerText = clientSet.size;

    document.getElementById(
        "kpiCommodity"
    ).innerText = commoditySet.size;
}

function updateRelatedAnalytics(){

    const selectedClient =
        document
        .getElementById("clientFilter")
        .value;

    const selectedCommodity =
        document
        .getElementById("commodityFilter")
        .value;

    const analyticsBox =
        document.getElementById(
            "relatedAnalytics"
        );

    // =========================
    // CLIENT FILTER
    // =========================

    if(selectedClient !== "ALL"){

        const commodities = [

            ...new Set(

                rawRelationData

                .filter(x =>
                    x.client === selectedClient
                )

                .map(x => x.commodity)

            )

        ];

        analyticsBox.innerHTML = `

            <b>
            Commodity used by:
            </b>

            <br><br>

            ${commodities
                .sort()
                .map(x => `• ${x}`)
                .join("<br>")
            }

        `;

        return;
    }

    // =========================
    // COMMODITY FILTER
    // =========================

    if(selectedCommodity !== "ALL"){

        const clients = [

            ...new Set(

                rawRelationData

                .filter(x =>
                    x.commodity === selectedCommodity
                )

                .map(x => x.client)

            )

        ];

        analyticsBox.innerHTML = `

            <b>
            Client using:
            </b>

            <br><br>

            ${clients
                .sort()
                .map(x => `• ${x}`)
                .join("<br>")
            }

        `;

        return;
    }

    // =========================
    // CLEAR
    // =========================

    analyticsBox.innerHTML =
        "No Filter Selected";
}

function updateTopCommodity(kabupaten = null){

    const commodityCount = {};

    const title =
    document.getElementById(
        "topCommodityTitle"
    );

    // =========================
    // FILTER RAW DATA
    // =========================

    let filteredData = rawRelationData;

    title.innerText =
    "Top 5 Commodity National";

    // jika klik kabupaten
    if(kabupaten){

        title.innerText =
        `Top 5 Commodity ${kabupaten}`;

        const layers = Object.values(window);

        layers.forEach(obj => {

            if(obj instanceof L.GeoJSON){

                obj.eachLayer(function(layer){

                    if(layer.feature){

                        const props =
                            layer.feature.properties;

                        const kabName =
                            String(props.WADMKK || "")
                            .toUpperCase();

                        if(kabName === kabupaten){

                            const clients =
                                String(props.FILTER_CLIENT || "")
                                .split(/<br\s*\/?>/i)
                                .map(x => x.trim());

                            filteredData =
                                rawRelationData.filter(x =>
                                    clients.includes(x.client)
                                );
                        }

                    }

                });

            }

        });

    }

    // =========================
    // HITUNG COMMODITY
    // =========================

    filteredData.forEach(item => {

        const commodity =
            String(item.commodity || "")
            .trim()
            .toUpperCase();

        if(commodity){

            commodityCount[commodity] =
                (commodityCount[commodity] || 0) + 1;
        }

    });

    // =========================
    // SORT TOP 5
    // =========================

    const top5 = Object.entries(
        commodityCount
    )
    .sort((a,b) => b[1] - a[1])
    .slice(0,5);

    // =========================
    // HTML
    // =========================

    const html = top5.map(item => `

        <div style="
            margin-bottom:10px;
        ">

            <b>${item[0]}</b>

            <div style="
                height:10px;
                background:#eee;
                border-radius:6px;
                overflow:hidden;
                margin-top:4px;
            ">

                <div style="
                    width:${item[1] * 10}px;
                    height:100%;
                    background:#ff4d4f;
                "></div>

            </div>

            <small>
                ${item[1]} data
            </small>

        </div>

    `).join("");

    document.getElementById(
        "topCommodityBox"
    ).innerHTML = html || "No Data";
}

function applyFilters(){

    showLoading();

    // RESET ZOOM NASIONAL

    Object.values(window).forEach(obj => {

        if(obj instanceof L.Map){

            obj.setView([-2.5, 118], 5);

        }

    });

    const selectedClient =
        document
        .getElementById("clientFilter")
        .value
        .toUpperCase();

    const selectedCommodity =
        document
        .getElementById("commodityFilter")
        .value
        .toUpperCase();

    const layers = Object.values(window);

    layers.forEach(obj => {

        if(obj instanceof L.GeoJSON){

            obj.eachLayer(function(layer){

                if(layer.feature){

                    const props =
                        layer.feature.properties;

                    const client =
                        String(props.FILTER_CLIENT || "")
                        .toUpperCase();

                    const commodity =
                        String(props.FILTER_COMMODITY || "")
                        .toUpperCase();

                    const clientMatch =
                        selectedClient === "ALL"
                        || client.includes(selectedClient);

                    const commodityMatch =
                        selectedCommodity === "ALL"
                        || commodity.includes(selectedCommodity);

                    // =====================
                    // MATCH
                    // =====================

                    if(clientMatch && commodityMatch){

                        resetLayerStyle(layer, props);

                    }

                    // =====================
                    // TIDAK MATCH
                    // =====================

                    else {

                        layer.setStyle({
                            fillColor:"#d9d9d9",
                            fillOpacity:0.02,
                            color:"#cccccc",
                            weight:0.2
                        });

                    }

                }

            });

        }

    });

    // UPDATE KPI
    updateKPI();

    // UPDATE RELATED ANALYTICS
    updateRelatedAnalytics();

    // HIDE LOADING
    setTimeout(() => {

        hideLoading();

    }, 300);

}

let activeLayer = null;

function setupLayerClick(){

    const layers = Object.values(window);

    layers.forEach(obj => {

        if(obj instanceof L.GeoJSON){

            obj.eachLayer(function(layer){

                if(layer.feature){

                    layer.on("click", function(){

                        // RESET layer lama
                        if(activeLayer){

                            resetLayerStyle(
                                activeLayer,
                                activeLayer.feature.properties
                            );
                        }

                        activeLayer = layer;

                        // WARNA AKTIF
                        setTimeout(() => {

                            layer.setStyle({
                                fillColor:"#00BFFF",
                                fillOpacity:0.95,
                                color:"#0000FF",
                                weight:5,
                                opacity:1
                            });

                            layer.bringToFront();

                        }, 10);

                        // =====================
                        // UPDATE KPI
                        // =====================

                        const props =
                            layer.feature.properties;

                        const clients =
                            String(props.FILTER_CLIENT || "")
                            .split(/<br\s*\/?>/i)
                            .map(x => x.trim())
                            .filter(x => x);

                        const commodities =
                            String(props.FILTER_COMMODITY || "")
                            .split(/<br\s*\/?>/i)
                            .map(x => x.trim())
                            .filter(x => x);

                        document.getElementById(
                            "kpiKabupaten"
                        ).innerText = props.ADA_DATA ? 1 : 0;

                        document.getElementById(
                            "kpiClient"
                        ).innerText =
                            new Set(clients).size;

                        document.getElementById(
                            "kpiCommodity"
                        ).innerText =
                            new Set(commodities).size;
                        
                        updateTopCommodity(
                            String(props.WADMKK || "")
                            .toUpperCase()
                        );    

                    });

                }

            });

        }

    });

}

document
.getElementById("clientFilter")
.addEventListener("change", applyFilters);

document
.getElementById("commodityFilter")
.addEventListener("change", applyFilters);

document
.getElementById("clearFilterBtn")
.addEventListener("click", function() {

    document.getElementById("clientFilter").value =
        "ALL";

    document.getElementById("commodityFilter").value =
        "ALL";

    applyFilters();
});

const searchInput =
    document.getElementById("searchBox");

searchInput.addEventListener("keyup", function(e) {

    const keyword =
        this.value.toUpperCase().trim();

    const layers = Object.values(window);

    layers.forEach(obj => {

        if(obj instanceof L.GeoJSON){

            obj.eachLayer(function(layer){
               
                if(layer.feature){
                    
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

                    if(keyword === ""){

                        layer.setStyle({
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
                        });

                        return;
                    }

                    // =====================
                    // MATCH
                    // =====================

                    if(isMatch){

                        layer.setStyle({
                            fillColor:"#ffff00",
                            fillOpacity:0.9,
                            weight:4,
                            color:"#000000"
                        });

                        if(e.key === "Enter"){

                            layer._map.fitBounds(
                            layer.getBounds()
                            );

                            layer.openPopup();
                        }

                    }

                    // =====================
                    // TIDAK MATCH
                    // =====================

                    else {

                        layer.setStyle({
                            fillColor:"#d9d9d9",
                            fillOpacity:0.03,
                            color:"#cccccc",
                            weight:0.3
                        });
                    }

                }

            });

        }

    });

});
const sidebar = document.getElementById("sidebar");

const toggleBtn = document.getElementById("toggleSidebar");

let sidebarOpen = true;

toggleBtn.addEventListener("click", function() {

    if(sidebarOpen){
    sidebar.style.left = "-320px";
    sidebarOpen = false;
    } else {

    sidebar.style.left = "10px";
    sidebarOpen = true;
    }

});
window.onload = function(){

    setupLayerClick();

    updateRelatedAnalytics();

    updateTopCommodity();

    hideLoading();

    setupDarkModeListener();

};

document.addEventListener("click", function(e){

    // Abaikan jika klik polygon
    if(e.target.closest(".leaflet-interactive")){
        return;
    }

    // Abaikan jika klik sidebar kanan
    if(e.target.closest("#floatingLegend")){
        return;
    }

    // Abaikan jika klik sidebar kiri
    if(e.target.closest("#sidebar")){
        return;
    }

        // Reset style layer aktif
    if(activeLayer){

        activeLayer.closePopup();

        resetLayerStyle(
            activeLayer,
            activeLayer.feature.properties
        );

        activeLayer = null;
        
        updateTopCommodity();

        updateKPI();
    }

});

function setupDarkModeListener(){

    const labels =
        document.querySelectorAll(
            ".leaflet-control-layers-selector"
        );

    labels.forEach(input => {

        input.addEventListener("change", function(){

            const layerText =
                this.nextSibling.textContent
                .trim()
                .toLowerCase();

            // DARK MODE
            if(layerText.includes("dark")){

                document.body.classList.add(
                    "dark-mode"
                );

            }

            // LIGHT MODE
            else {

                document.body.classList.remove(
                    "dark-mode"
                );

            }

        });

    });

}