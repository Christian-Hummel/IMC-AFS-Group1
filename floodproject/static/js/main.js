// to see the console.log messages, open the browser console (F12 and go to the console tab)

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM is fully loaded");

    // Initialize the map
    const autmap = initializeMap();

    // Create a layer group to hold the water level data
    var waterLevelLayer = L.layerGroup();

    // Fetch the water level data from the backend and add it to the map
    fetchWaterLevelData(waterLevelLayer, autmap);

    // Add event listener for the checkbox to toggle water level layer visibility
    setupCheckboxToggle(waterLevelLayer, autmap);


});


function initializeMap() {

    var test1 = L.marker([47.6964, 13.3458]).bindPopup('Test Marker 1')
        test2 = L.marker([47.6964, 13.3624]).bindPopup('Test Marker 2');

    var info = L.layerGroup([test1, test2])

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


    var overlayMaps = {
        "Surface Water Levels": info
    };

    var layerControl = L.control.layers(null,overlayMaps,{collapsed:false}).addTo(map);
    //
    // console.log("Layer Control initialized")





    // Test marker (to be removed later)
    // L.marker([47.6964, 13.3458]).addTo(map)
    //     .bindPopup("Test Marker")
    //     .openPopup();



    return map;
}






// this does not work so far (the data is not displayed on the map), but the data is fetched correctly
function fetchWaterLevelData(waterLevelLayer, autmap) {
    let watermarks = JSON.parse(document.getElementById('water_json').textContent)

    watermarks.forEach(watermark => {
        L.marker([watermark.latitude, watermark.longitude]).addTo(waterLevelLayer)
    })





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