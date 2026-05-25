let commodityChart = null;

let clientChart = null;

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
        .value
        .toUpperCase();

    const selectedCommodity =
        document
        .getElementById("commodityFilter")
        .value
        .toUpperCase();

    const layers = Object.values(window);

    let activeKabupaten = 0;

    const clientSet = new Set();

    const commoditySet = new Set();

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

                if(clientMatch && commodityMatch){

                    if(props.ADA_DATA){

                        activeKabupaten++;

                        // CLIENT
                        if(selectedClient !== "ALL"){

                            clientSet.add(selectedClient);

                        } else {

                            client.split(/<br\s*\/?>/i).forEach(c => {

                                const clean =
                                    c.replace("- ","").trim();

                                if(clean){
                                    clientSet.add(clean);
                                }

                            });

                        }

                        // COMMODITY
                        if(selectedCommodity !== "ALL"){

                            commoditySet.add(selectedCommodity);

                        } else {

                            commodity.split(/<br\s*\/?>/i).forEach(c => {

                                const clean =
                                    c.replace("- ","").trim();

                                if(clean){
                                    commoditySet.add(clean);
                                }

                            });

                        }

                    }

                }

            }

        });

    }

});

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

function updateCharts(){

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

    const commodityCount = {};

    const clientCount = {};

    layers.forEach(obj => {

        if(obj instanceof L.GeoJSON){

            obj.eachLayer(function(layer){

                if(layer.feature){

                    const props =
                        layer.feature.properties;

                    const clients =
                        String(props.FILTER_CLIENT || "");

                    const commodities =
                        String(props.FILTER_COMMODITY || "");

                    const clientMatch =
                        selectedClient === "ALL"
                        || clients.toUpperCase()
                        .includes(selectedClient);

                    const commodityMatch =
                        selectedCommodity === "ALL"
                        || commodities.toUpperCase()
                        .includes(selectedCommodity);

                    if(clientMatch && commodityMatch){

                        // CLIENT
                        clients.split(/<br\s*\/?>/i).forEach(c => {

                            const clean = c.trim();

                            if(clean){

                                clientCount[clean] =
                                    (clientCount[clean] || 0) + 1;
                            }

                        });

                        // COMMODITY
                        commodities.split(/<br\s*\/?>/i).forEach(c => {

                            const clean = c.trim();

                            if(clean){

                                commodityCount[clean] =
                                    (commodityCount[clean] || 0) + 1;
                            }

                        });

                    }

                }

            });

        }

    });

    // =========================
    // TOP 10
    // =========================

    const topCommodity = Object.entries(
        commodityCount
    )
    .sort((a,b) => b[1]-a[1])
    .slice(0,10);

    const topClient = Object.entries(
        clientCount
    )
    .sort((a,b) => b[1]-a[1])
    .slice(0,10);

    // =========================
    // DESTROY OLD CHART
    // =========================

    if(commodityChart){

        commodityChart.destroy();
    }

    if(clientChart){

        clientChart.destroy();
    }

    // =========================
    // COMMODITY PIE
    // =========================

    commodityChart = new Chart(

        document.getElementById(
            "commodityChart"
        ),

        {
            type:"pie",

            data:{

                labels:
                    topCommodity.map(x => x[0]),

                datasets:[{

                    data:
                        topCommodity.map(x => x[1])

                }]
            }
        }
    );

    // =========================
    // CLIENT BAR
    // =========================

    clientChart = new Chart(

        document.getElementById(
            "clientChart"
        ),

        {
            type:"bar",

            data:{

                labels:
                    topClient.map(x => x[0]),

                datasets:[{

                    data:
                        topClient.map(x => x[1])

                }]
            },

            options:{
                indexAxis:'y'
            }
        }
    );

}

function applyFilters(){

    showLoading();

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

    // UPDATE CHARTS
    updateCharts();

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

    sidebar.style.transform =
        "translateX(-120%)";

    sidebar.style.opacity = "0";

    sidebarOpen = false;

    } else {

    sidebar.style.transform =
        "translateX(0)";

    sidebar.style.opacity = "1";

    sidebarOpen = true;

    }

});
window.onload = function(){

    setupLayerClick();

    updateCharts();

    hideLoading();

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
        
        updateKPI();
    }

});