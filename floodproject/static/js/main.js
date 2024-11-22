// to see the console.log messages, open the browser console (F12 and go to the console tab)

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM is fully loaded");

    // Initialize the map
    const autmap = initializeMap();

    // Create a layer group to hold the water level data
    var waterLevelLayer = L.layerGroup();

    // fetch information of water levels from main.html
    levels = fetchWaterLevelData();

    // no data yet
    reports = fetchReportData();

    var overlayMaps = {
        "Surface Water Levels": levels,
        "Reports": reports
    };

    var layerControl = L.control.layers(null,overlayMaps,{collapsed:false}).addTo(autmap);

    // Fetch the water level data from the backend and add it to the map
    // fetchWaterLevelData(waterLevelLayer, autmap);

    // Add event listener for the checkbox to toggle water level layer visibility
    setupCheckboxToggle(waterLevelLayer, autmap);


});


function initializeMap() {



    const map = L.map('mapid', {
        center: [47.6964, 13.3458],
        zoom: 7,
        minZoom: 7,
        layers: []
    });

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
    }).addTo(map);

    console.log("Map initialized");


    return map;
}




function fetchWaterLevelData() {

    var levels = L.layerGroup();


    // JSON function to parse json data from main.html
    let watermarks = JSON.parse(document.getElementById('waterlevels_json').textContent);

    // console.log(watermarks[0])

    watermarks.forEach(watermark => {
        var lat = watermark.latitude;
        var lon = watermark.longitude;
        var location = new L.latLng(lat, lon);
        var marker = new L.marker(location);
        marker.addTo(levels)
    });

    var marker1 = L.marker([watermarks[0].latitude, watermarks[0].longitude]);

    var marker2 = L.marker([50, 14]);



    marker1.addTo(levels);


    console.log(levels[0]);


    return levels;

}

// test function with example markers to show functionality with layer control
function fetchReportData() {



    var test1 = L.marker([47.6964, 13.3458]).bindPopup('Test Marker 1')
        test2 = L.marker([47.6964, 13.3624]).bindPopup('Test Marker 2');

    var reports = L.layerGroup()

    test1.addTo(reports);
    test2.addTo(reports);

    return reports;

}

// Sidebar checkbox toggle
function setupCheckboxToggle(waterLevelLayer, autmap) {
    document.getElementById('toggleWaterLevels').addEventListener('change', function (event) {
        console.log("Checkbox state changed");

        if (event.target.checked) {
            console.log("Water levels checkbox checked");

            if (!autmap.hasLayer(waterLevelLayer)) {
                waterLevelLayer.addTo(autmap); // Add the layer group to the map if not already added
            }
        } else {
            console.log("Water levels checkbox unchecked");

            if (autmap.hasLayer(waterLevelLayer)) {
                autmap.removeLayer(waterLevelLayer); // Remove the layer group from the map
            }
        }
    });
}