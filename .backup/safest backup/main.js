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

    const selectedClients =
        getSelectedClients();

    const selectedCommodities =
        getSelectedCommodities();

    let filteredData = rawRelationData;

    // =========================
    // FILTER CLIENT
    // =========================

    if(selectedClients.length > 0){

        filteredData =
            filteredData.filter(
                x => selectedClients.includes(
                    x.client.toUpperCase()
                )
            );

    }

    // =========================
    // FILTER COMMODITY
    // =========================

    if(selectedCommodities.length > 0){

        filteredData =
            filteredData.filter(
                x => selectedCommodities.includes(
                    x.commodity.toUpperCase()
                )
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

                    if(selectedClients.length > 0){

                        match =
                            match &&
                            selectedClients.includes(client);

                    }

                    if(selectedCommodities.length > 0){

                        match =
                            match &&
                            selectedCommodities.includes(commodity);

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

    const selectedClients =
        getSelectedClients();

    const selectedCommodities =
        getSelectedCommodities();

    const analyticsBox =
        document.getElementById(
            "relatedAnalytics"
        );

    // =========================
    // CLIENT FILTER
    // =========================

    if(selectedClients.length > 0){

        const commodities = [

            ...new Set(

                rawRelationData

                .filter(x =>
                    selectedClients.includes(
                        x.client.toUpperCase()
                    )
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

    if(selectedCommodities.length > 0){

        const clients = [

            ...new Set(

                rawRelationData

                .filter(x =>
                    selectedCommodities.includes(
                        x.commodity.toUpperCase()
                    )
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

// ======================================
// ADVANCED FILTER
// ======================================

function getSelectedClients(){

    return [

        ...document.querySelectorAll(
            ".clientCheckbox:checked"
        )

    ].map(x => x.value.toUpperCase());

}

function getSelectedCommodities(){

    return [

        ...document.querySelectorAll(
            ".commodityCheckbox:checked"
        )

    ].map(x => x.value.toUpperCase());

}

function applyFilters(){

    showLoading();

    // RESET ZOOM NASIONAL

    Object.values(window).forEach(obj => {

        if(obj instanceof L.Map){

            obj.setView([-2.5, 118], 5);

        }

    });

    const selectedClients =
        getSelectedClients();

    const selectedCommodities =
        getSelectedCommodities();

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

                        selectedClients.length === 0

                        ||

                        selectedClients.some(x =>
                            client.includes(x)
                        );

                    const commodityMatch =

                        selectedCommodities.length === 0

                        ||

                        selectedCommodities.some(x =>
                            commodity.includes(x)
                        );

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
.getElementById("clearFilterBtn")
.addEventListener("click", function() {

    document
    .querySelectorAll(
        ".clientCheckbox"
    )
    .forEach(x => x.checked = false);

    document
    .querySelectorAll(
        ".commodityCheckbox"
    )
    .forEach(x => x.checked = false);

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

    // JIKA EXPORT MODAL TERBUKA
    // JANGAN JALANKAN EVENT GLOBAL
    if(
        !document
        .getElementById("exportModal")
        .classList.contains("hiddenExportModal")
    ){
        return;
    }

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

async function waitForTilesLoaded(){
    
    const tiles =
        document.querySelectorAll(
            ".leaflet-tile"
        );

    const promises = [];

    tiles.forEach(tile => {

        if(!tile.complete){

            promises.push(
                new Promise(resolve => {

                    tile.onload = resolve;

                    tile.onerror = resolve;

                })
            );

        }

    });

    await Promise.all(promises);

    // tambahan penting
    await new Promise(resolve =>
        setTimeout(resolve, 1500)
    );

}

const mapContainer =
    document.querySelector(
        ".folium-map"
    );

const watermark =
    document.getElementById(
        "exportWatermark"
    );

if(
    mapContainer &&
    watermark &&
    !mapContainer.contains(watermark)
){
    mapContainer.appendChild(
        watermark
    );
}

// ======================================
// EXPORT PNG
// ======================================

document
.getElementById("exportPNG")
.addEventListener("click", async function(){

    const exportTarget =
        document.querySelector(
            ".folium-map"
        );

    showExportLoading();

    exportWatermark.style.display =
        "flex";

    document.body.classList.add(
        "exporting"
    );

    let sidebarParent;
    let legendParent;
    let sidebar;
    let legend;

    try{

        await waitForTilesLoaded();

        const logo =
            document.querySelector(
                "#exportWatermark img"
            );

        if(logo && !logo.complete){

            await new Promise(resolve => {

                logo.onload = resolve;

                logo.onerror = resolve;

            });

        }

        await new Promise(resolve =>
            setTimeout(resolve, 1200)
        );

        sidebar =
            document.getElementById("sidebar");

        legend =
            document.getElementById("floatingLegend");

        // SIMPAN POSISI ASLI
        sidebarParent =
            sidebar.parentNode;

        legendParent =
            legend.parentNode;

        // PINDAHKAN KE MAP
        exportTarget.appendChild(sidebar);

        exportTarget.appendChild(legend);

        const canvas =
            await html2canvas(
                exportTarget,
                {
                    useCORS:true,

                    allowTaint:true,

                    backgroundColor:"#ffffff",

                    scale:1.5,

                    logging:false,

                    scrollX:0,
                    scrollY:0,

                    windowWidth:
                        exportTarget.offsetWidth,

                    windowHeight:
                        exportTarget.offsetHeight,

                    ignoreElements: (el) => {

                        return (
                            el.id === "exportModal" ||
                            el.id === "exportLoading" ||
                            el.id === "loadingSpinner"
                        );

                    }
                }
            );

        const link =
            document.createElement("a");

        link.download =
            `GIS_Dashboard_${
                new Date()
                .toISOString()
                .split("T")[0]
            }.png`;

        const imageData =
            canvas.toDataURL(
                "image/png",
                1.0
            );

        if(
            imageData === "data:,"
        ){
            throw new Error(
                "Canvas kosong"
            );
        }

        link.href = imageData;

        link.click();

    }

    catch(err){

        console.error(err);

        alert(
            "Export PNG gagal"
        );

    }

    finally{

        exportWatermark.style.display =
            "none";

        document.body.classList.remove(
            "exporting"
        );

        sidebarParent.appendChild(sidebar);

        legendParent.appendChild(legend);

        hideExportLoading();

    }

});

// =========================
// EXPORT MODAL
// =========================

let isExporting = false;

const exportBtn =
    document.getElementById("exportBtn");

const exportModal =
    document.getElementById("exportModal");

const exportWatermark =
    document.getElementById(
        "exportWatermark"
    );

const closeExportModal =
    document.getElementById("closeExportModal");

exportBtn.addEventListener("click", function(e){

    e.stopPropagation();

    if(isExporting) return;

    exportModal.classList.remove(
        "hiddenExportModal"
    );

});

closeExportModal.addEventListener("click", function(){

    exportModal.classList.add(
        "hiddenExportModal"
    );

});

// klik background modal → close

exportModal.addEventListener("click", function(e){

    if(e.target === exportModal){

        exportModal.classList.add(
            "hiddenExportModal"
        );

    }

});

// ======================================
// EXPORT PDF
// ======================================

document
.getElementById("exportPDF")
.addEventListener("click", async function(){

    const exportTarget =
        document.querySelector(
            ".folium-map"
        );

    showExportLoading();

    exportWatermark.style.display =
        "flex";

    document.body.classList.add(
        "exporting"
    );

    let sidebarParent;
    let legendParent;
    let sidebar;
    let legend;

    try{

        await waitForTilesLoaded();

        const logo =
            document.querySelector(
                "#exportWatermark img"
            );

        if(logo && !logo.complete){

            await new Promise(resolve => {

                logo.onload = resolve;

                logo.onerror = resolve;

            });

        }

        await new Promise(resolve =>
            setTimeout(resolve, 1200)
        );

        sidebar =
            document.getElementById("sidebar");

        legend =
            document.getElementById("floatingLegend");

        const watermark =
            document.getElementById(
                "exportWatermark"
            );

        const watermarkParent =
            watermark.parentNode;

        // SIMPAN POSISI ASLI
        sidebarParent =
            sidebar.parentNode;

        legendParent =
            legend.parentNode;

        // PINDAHKAN KE MAP
        exportTarget.appendChild(sidebar);

        exportTarget.appendChild(legend);

        const canvas =
            await html2canvas(
                exportTarget,
                {
                    useCORS:true,

                    allowTaint:true,

                    backgroundColor:"#ffffff",

                    scale:1,

                    logging:false,

                    scrollX:0,
                    scrollY:0,

                    windowWidth:
                        exportTarget.offsetWidth,

                    windowHeight:
                        exportTarget.offsetHeight,

                    ignoreElements: (el) => {

                        return (
                            el.id === "exportModal" ||
                            el.id === "exportLoading" ||
                            el.id === "loadingSpinner"
                        );

                    }
                }
            );

        const imgData =
            canvas.toDataURL(
                "image/png",
            );

        if(
            imgData === "data:,"
        ){
            throw new Error(
                "PDF canvas kosong"
            );
        }

        const pdf =
            new window.jspdf.jsPDF(
                "landscape",
                "mm",
                "a4"
            );

        const pdfWidth =
            pdf.internal.pageSize.getWidth();

        const pdfHeight =
            pdf.internal.pageSize.getHeight();

        const ratio =
            canvas.width / canvas.height;

        let imgWidth = pdfWidth;

        let imgHeight =
            imgWidth / ratio;

        if(imgHeight > pdfHeight){

            imgHeight = pdfHeight;

            imgWidth =
                imgHeight * ratio;
        }

        pdf.addImage(
            imgData,
            "PNG",
            0,
            0,
            imgWidth,
            imgHeight
        );

        pdf.save(
            `GIS_Dashboard_${
                new Date()
                .toISOString()
                .split("T")[0]
            }.pdf`
        );

    }

    catch(err){

        console.error(err);

        alert(
            "Export PDF gagal"
        );

    }

    finally{

        exportWatermark.style.display =
            "none";
        
        document.body.classList.remove(
            "exporting"
        );

        sidebarParent.appendChild(sidebar);

        legendParent.appendChild(legend);

        hideExportLoading();

    }

});

// ======================================
// EXPORT CSV
// ======================================

document
.getElementById("exportCSV")
.addEventListener("click", function(){

    const selectedClients =
        getSelectedClients();

    const selectedCommodities =
        getSelectedCommodities();

    let filteredData = rawRelationData;

    // FILTER CLIENT
    if(selectedClients.length > 0){

        filteredData =
            filteredData.filter(
                x => selectedClients.includes(x.client.toUpperCase())
            );
    }

    // FILTER COMMODITY
    if(selectedCommodities.length > 0){

        filteredData =
            filteredData.filter(
                x => selectedCommodities.includes(x.commodity.toUpperCase())
            );
    }

    // VALIDASI DATA
    if(filteredData.length === 0){

        alert("Tidak ada data untuk export");

        return;
    }

    // HEADER CSV
    let csvContent =
        "Client,Commodity\n";

    // ROW
    filteredData.forEach(item => {

        csvContent +=
            `"${item.client}","${item.commodity}"\n`;

    });

    // BUAT FILE
    const blob = new Blob(
        [csvContent],
        {
            type:"text/csv;charset=utf-8;"
        }
    );

    const link =
        document.createElement("a");

    const url =
        URL.createObjectURL(blob);

    link.href = url;

    link.download =
        `GIS_Filtered_Data_${new Date().toISOString().split("T")[0]}.csv`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

});

// =========================
// EXPORT LOADING
// =========================

function showExportLoading(){

    document
    .getElementById("exportLoading")
    .classList
    .remove("hiddenExportLoading");

}

function hideExportLoading(){

    document
    .getElementById("exportLoading")
    .classList
    .add("hiddenExportLoading");

}

// ======================================
// ADVANCED FILTER EVENT
// ======================================

document
.querySelectorAll(
    ".clientCheckbox"
)
.forEach(item => {

    item.addEventListener(
        "change",
        applyFilters
    );

});

document
.querySelectorAll(
    ".commodityCheckbox"
)
.forEach(item => {

    item.addEventListener(
        "change",
        applyFilters
    );

});

// ======================================
// SEARCH CLIENT
// ======================================

document
.getElementById("clientSearch")
.addEventListener("keyup", function(){

    const keyword =
        this.value.toUpperCase();

    document
    .querySelectorAll(
        "#clientCheckboxContainer .checkboxItem"
    )
    .forEach(item => {

        const text =
            item.innerText.toUpperCase();

        if(text.includes(keyword)){

            item.style.display = "flex";

        }

        else{

            item.style.display = "none";

        }

    });

});

// ======================================
// SEARCH COMMODITY
// ======================================

document
.getElementById("commoditySearch")
.addEventListener("keyup", function(){

    const keyword =
        this.value.toUpperCase();

    document
    .querySelectorAll(
        "#commodityCheckboxContainer .checkboxItem"
    )
    .forEach(item => {

        const text =
            item.innerText.toUpperCase();

        if(text.includes(keyword)){

            item.style.display = "flex";

        }

        else{

            item.style.display = "none";

        }

    });

});