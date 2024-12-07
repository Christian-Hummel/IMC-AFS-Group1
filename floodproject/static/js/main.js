
// This script is responsible for fetching data from the backend and displaying it on the map.
// It also handles user interactions, such as toggling the visibility of data layers.
// To see the console output, open the browser's developer tools (F12) and go to the console tab.

document.addEventListener("DOMContentLoaded", function () {

    // Initialize the map
    const autmap = initializeMap();



    // Create a cluster groups (for aggregating markers) for each data type
    var waterLevelCluster = L.markerClusterGroup({
        maxClusterRadius: 40,      // Smaller radius (more clusters) for better visibility
        iconCreateFunction: function (cluster) {
            // Count the number of markers in the cluster
            var childCount = cluster.getChildCount();

            // Define a base size and scale it based on the child count
            var size = Math.min(30 + childCount * 2, 150); // Base size of 30px, scales up to a max of 150px


            // Define a base size and scale it based on the child count
            var size = Math.min(30 + childCount * 2, 150); // Base size of 30px, scales up to a max of 150px

            // Define color based on the number of markers in the cluster
            var color = '#4d9553'; // Default color
            if (childCount < 10) {
                color = '#ffd400';
            }

            // Return a custom icon for the cluster
            return L.divIcon({
                html: `<div style="background-color: ${color}; 
                    border-radius: 50%; 
                    height: ${size}px; 
                    width: ${size}px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: bold;
                    font-size: ${size / 4}px;">
                        ${childCount}
                    </div>`,
                className: 'cluster-cluster-icon', // can also be used for more styling in CSS
                iconSize: [size, size]
            });
        }
    });

    var reportCluster = L.markerClusterGroup({
        maxClusterRadius: 40,      // Smaller radius (more clusters) for better visibility
        iconCreateFunction: function (cluster) {
            // Count the number of markers in the cluster
            var childCount = cluster.getChildCount();

            // Define a base size and scale it based on the child count
            var size = Math.min(30 + childCount * 2, 150); // Base size of 30px, scales up to a max of 150px

            // Define color based on the number of markers in the cluster
            var color = '#ca0237'; // Default color
            if (childCount < 10) {
                color = '#f59c00';
            }

            // Return a custom icon for the cluster
            return L.divIcon({
                html: `<div style="background-color: ${color}; 
                    border-radius: 50%; 
                    height: ${size}px; 
                    width: ${size}px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: bold;
                    font-size: ${size / 4}px;">
                        ${childCount}
                    </div>`,
                className: 'cluster-cluster-icon', // can also be used for more styling in CSS
                iconSize: [size, size]
            });
        }

    });


    // Fetch the water level data from the backend and add it to the map
    fetchWaterLevelData(waterLevelCluster, autmap);
    // Fetch and display report data
    fetchReportData(reportCluster);

    /// Initialize the HQ30 WMS layer
    const hq30Layer = handleHQ30Layer(autmap);
    // Initialize the HQ100 WMS layer
    const hq100Layer = handleHQ100Layer(autmap);

    // Add event listeners for toggling layers
    setupCheckboxToggle('toggleWaterLevels', waterLevelCluster, autmap);
    setupCheckboxToggle('toggleReports', reportCluster, autmap);
    setupCheckboxToggle('toggleHQ30', hq30Layer, autmap);
    setupCheckboxToggle('toggleHQ100', hq100Layer, autmap);
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

    return map;
}


function fetchWaterLevelData(waterLevelCluster, autmap) {
    fetch('/water-levels/')
        .then(response => response.json())
        .then(data => {

            // Create GeoJSON layer and add markers to the cluster
            L.geoJSON(data, {
                pointToLayer: function (feature, latlng) {
                    // color-coding for water levels markers
                    let gesamtcode = feature.properties.gesamtcode;
                    let color = getColor(gesamtcode); // Get color based on the gesamtcodes first digit

                    // Parse the lon and lat from the feature properties
                    let lon = parseFloat(feature.properties.lon.replace(",", "."));
                    let lat = parseFloat(feature.properties.lat.replace(",", "."));


                    if (!isNaN(lon) && !isNaN(lat)) { // Check if coordinates are valid
                        return L.circleMarker([lat, lon], { // using circle markers because hex colors are not supported in leaflet
                            radius: 8,
                            fillColor: color,
                            color: '#000', // Optional border color
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 0.8
                        }); // Return a new marker
                    } else {
                        console.warn("Invalid coordinates for feature:", feature);
                        return null; // Skip invalid markers
                    }
                },

                onEachFeature: function (feature, layer) {
                    if (layer) {
                        var infoContent = `
                            <strong>Measuring point:</strong> ${feature.properties.messstelle || "N/A"} <br>
                            <strong>Water body:</strong> ${feature.properties.gewaesser || "N/A"} <br>
                            <strong>Amount:</strong> ${feature.properties.wert || "N/A"} ${feature.properties.einheit} <br>
                            <strong>Time:</strong> ${feature.properties.zeitpunkt || "N/A"} <br>
                            <strong>More info:</strong> <a href="${feature.properties.internet}" target="_blank">Details</a>
                            <strong></strong> <a href="/water-levels/${feature.properties.hzbnr}">previous levels</a>
                        `;
                        layer.bindPopup(infoContent);
                    }
                }
            }).eachLayer(function (layer) {
                waterLevelCluster.addLayer(layer); // Add each marker to the cluster group
            });

            // Add cluster layer to the map by default (when starting the app)
            waterLevelCluster.addTo(autmap);

        })
        .catch(err => console.error('Error fetching water levels:', err));
}


function fetchReportData(reportCluster) {
    fetch('/reports/')
        .then(response => response.json())
        .then(data => {
            console.log("Report data fetched:", data);
            console.log("latitude of first element in array:", data[0].fields.lat);
            console.log("id of first report", data[0].pk);

            // Create variable for custom marker icon
            var repMarker = L.ExtraMarkers.icon({
                icon: 'fa-exclamation-triangle',
                markerColor: '#ca0237',
                shape: 'square',
                prefix: 'fa'
                });

            data.forEach(report => {


                report_layer = L.layerGroup()
                marker = L.marker([report.fields.lat, report.fields.lon], {icon:repMarker})
                marker.addTo(report_layer)


                // info content for each marker


                if (marker) {
                        var infoContent = `
                            <strong>Title:</strong> ${report.fields.title || "N/A"} <br>
                            <p>Click below to view full report details:</p>
                            <a href="/report/${report.pk}" target="_blank" class="btn btn-primary">View Details</a>
                        `;
                        marker.bindPopup(infoContent);
                    }

                reportCluster.addLayer(report_layer)
            })



        })
        .catch(err => console.error('Error fetching report:', err));
}


function handleHQ30Layer(map) {
    // Create the WMS layer
    const hq30Layer = L.tileLayer.wms('https://inspire.lfrz.gv.at/000801/wms', {
        layers: 'Hochwasserueberflutungsflaechen HQ30', // Layer name
        format: 'image/png',
        transparent: true, // Make the layer transparent
        attribution: '© Umweltbundesamt', // Add attribution
    });
    return hq30Layer; // Return the WMS layer object
}

function handleHQ100Layer(map) {
    // Create the WMS layer
    const hq100Layer = L.tileLayer.wms('https://inspire.lfrz.gv.at/000801/wms', {
        layers: 'Hochwasserueberflutungsflaechen HQ100', // Layer name
        format: 'image/png',
        transparent: true,
        attribution: '© Umweltbundesamt',
    });
    return hq100Layer; // Return the WMS layer object
}


// Sidebar toggle
function setupCheckboxToggle(checkboxId, clusterGroup, map) {
    document.getElementById(checkboxId).addEventListener('change', function (event) {
        if (event.target.checked) {
            if (!map.hasLayer(clusterGroup)) {
                clusterGroup.addTo(map);
            }
        } else {
            if (map.hasLayer(clusterGroup)) {
                map.removeLayer(clusterGroup);
            }
        }
    });
}




// gesamtcode (INTEGER): Categorization from https://ehyd.gv.at an.
// 1. digit: 1...Niederwasser, 2...Mittelwasser, 3...erhöhte Wasserführung, 4...Hochwasser Stufe 1, 5...Hochwasser Stufe 2, 6...Hochwasser Stufe 3, 9...keine Daten;
// 2. digit: 0...gleichbleibend, 1...steigend, 2...sinkend, 3...normal;
// 3. digit: 0...normal, 1... older than 24 hours

// color-coding for water levels marker function
function getColor(gesamtcode) {
    if (gesamtcode == null) {
        return '#eff4f7'; // Default color for no data
    }

    gesamtcode = gesamtcode.toString().split('').map(Number); // Convert to array of digits
    if (gesamtcode[0] === 1) {
        return '#3bacbe'; // Niederwasser (Low water)
    } else if (gesamtcode[0] === 2) {
        return '#4e8fcc'; // Mittelwasser (Medium water)
    } else if (gesamtcode[0] === 3) {
        return '#003d84'; // erhöhte Wasserführung (Increased water flow)
    } else if (gesamtcode[0] === 4) {
        return '#ffd400'; // Hochwasser Stufe 1 (Flood level 1)
    } else if (gesamtcode[0] === 5) {
        return '#f59c00'; // Hochwasser Stufe 2 (Flood level 2)
    } else if (gesamtcode[0] === 6) {
        return '#e6320f'; // Hochwasser Stufe 3 (Flood level 3)
    } else {
        return '#eff4f7'; // no data (gesamtcode[0] == 9)
    }
}



