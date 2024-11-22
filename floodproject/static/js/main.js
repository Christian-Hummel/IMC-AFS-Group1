
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
    const map = L.map('mapid', {
        center: [47.6964, 13.3458],
        zoom: 7,
        minZoom: 7,
    });

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
    }).addTo(map);

    console.log("Map initialized");

    // Test marker (to be removed later)
    L.marker([47.6964, 13.3458]).addTo(map)
        .bindPopup("Test Marker")
        .openPopup();

    return map;
}


function fetchWaterLevelData(waterLevelLayer, autmap) {
    fetch('/water-levels/')
        .then(response => response.json())
        .then(data => {
            console.log("Water level data fetched:", data);

            // Create GeoJSON layer and add to waterLevelLayer
            const geoJsonLayer = L.geoJSON(data, {
                pointToLayer: function (feature, latlng) {
                    // Parse the lon and lat from the feature properties
                    let lon = parseFloat(feature.properties.lon.replace(",", "."));
                    let lat = parseFloat(feature.properties.lat.replace(",", "."));

                    if (!isNaN(lon) && !isNaN(lat)) {
                        console.log("Using parsed coordinates:", { lon, lat });
                        return L.marker([lat, lon]); // Use the parsed coordinates
                    } else {
                        console.warn("Invalid coordinates for feature:", feature);
                        return null; // Skip invalid markers
                    }
                },

                // Add popup with feature properties
                onEachFeature: function (feature, layer) {
                    if (layer) { // Ensure the layer is valid
                        var infoContent = `
                            <strong>Measuring point:</strong> ${feature.properties.messstelle || "N/A"} <br>
                            <strong>Waters:</strong> ${feature.properties.gewaesser || "N/A"} <br>
                            <strong>Amount:</strong> ${feature.properties.wert || "N/A"} ${feature.properties.einheit} <br>
                            <strong>More info:</strong> <a href="${feature.properties.internet}" target="_blank">Details</a>
                        `;
                        layer.bindPopup(infoContent);
                    }
                }
            });

            // Add GeoJSON layer to the waterLevelLayer group
            geoJsonLayer.addTo(waterLevelLayer);

            console.log("GeoJSON data added to layer");

            // Add waterLevelLayer to the map by default (when starting the app)
            waterLevelLayer.addTo(autmap);

        })
        .catch(err => console.error('Error fetching water levels:', err));
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
