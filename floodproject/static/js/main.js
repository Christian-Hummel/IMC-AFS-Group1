
// This script is responsible for fetching data from the backend and displaying it on the map.
// It also handles user interactions, such as toggling the visibility of data layers.
// To see the console output, open the browser's developer tools (F12) and go to the console tab.

document.addEventListener("DOMContentLoaded", function () {

    // Initialize the map
    const autmap = initializeMap();

    // Create a cluster groups (for aggregating markers) for each data type

    var waterLevelCluster = L.markerClusterGroup({
    maxClusterRadius: 40,
    iconCreateFunction: function (cluster) {
        var childCount = cluster.getChildCount();
        var size = Math.min(30 + childCount * 2, 150);
        var color = childCount < 10 ? '#ffd400' : '#4d9553';

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
            className: 'cluster-cluster-icon',
            iconSize: [size, size]
        });
    }
});



var reportCluster = L.markerClusterGroup({
    maxClusterRadius: 40,
    iconCreateFunction: function (cluster) {
        var childCount = cluster.getChildCount();
        var size = Math.min(30 + childCount * 2, 150);
        var color = childCount < 10 ? '#f59c00' : '#ca0237';

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
            className: 'cluster-cluster-icon',
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


    // Ensuring the map resizes correctly on window resize (thought for mobile devices)

    window.addEventListener('resize', function () {
        autmap.invalidateSize();
    });

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

    // Custom zoom reminder control
    const zoomReminder = L.control({position: 'bottomright'});

    zoomReminder.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'zoom-reminder');
        div.innerHTML = 'Zoom in to see flood zones';

        div.style.display = 'none';  // Hidden by default (when starting the app)
        return div;
    };
    zoomReminder.addTo(map);

     // Zoom level check
     map.on('zoomend', function() {
        const reminderDiv = document.querySelector('.zoom-reminder');
        
        if (map.getZoom() < 11 && (document.getElementById('toggleHQ30').checked || document.getElementById('toggleHQ100').checked)) {
            reminderDiv.style.display = 'block';
        } else {
            reminderDiv.style.display = 'none';
        }
    });

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

                    if (!isNaN(lon) && !isNaN(lat)) {
                        
                        // Create and retutn the circle marker
                        return L.circleMarker([lat, lon], {
                            radius: 8,
                            fillColor: color,
                            color: '#000',
                            weight: 1,
                            opacity: 1,
                            fillOpacity: 0.8,
                        });
                        
                    }
                    // console.warn("Invalid coordinates for feature:", feature);
                    return null; // Skip invalid markers
                },

                onEachFeature: function (feature, layer) {
                    if (layer) {
                        let trend = getTrendText(feature.properties.gesamtcode);
                        var infoContent = `
                            <strong>Measuring point:</strong> ${feature.properties.messstelle || "N/A"} <br>
                            <strong>Water body:</strong> ${feature.properties.gewaesser || "N/A"} <br>
                            <strong>Amount:</strong> ${feature.properties.wert || "N/A"} ${feature.properties.einheit} <br>
                            <strong>Trend:</strong> ${trend} <br>
                            <strong>Time:</strong> ${feature.properties.zeitpunkt || "N/A"} <br>
                            <strong>More info:</strong> <a href="${feature.properties.internet}" target="_blank">Details</a> <br>
                                <a href="/water-levels/${feature.properties.hzbnr}" style="margin-left: 1.8cm;">Previous Levels</a> 
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
            // Show zoom reminder if HQ layers are toggled and zoom level is too low
            if ((checkboxId === 'toggleHQ30' || checkboxId === 'toggleHQ100') && map.getZoom() < 11) {
                document.querySelector('.zoom-reminder').style.display = 'block';
            }

        } else {
            if (map.hasLayer(clusterGroup)) {
                map.removeLayer(clusterGroup);
            }
            // Hide zoom reminder if HQ layers are not checked
            if ((checkboxId === 'toggleHQ30' || checkboxId === 'toggleHQ100') && !document.getElementById('toggleHQ30').checked && !document.getElementById('toggleHQ100').checked) {
                document.querySelector('.zoom-reminder').style.display = 'none';
            }
        }
    });
}




// gesamtcode (INTEGER): Categorization from https://ehyd.gv.at an.
// 1. digit: 1...Niederwasser, 2...Mittelwasser, 3...erhöhte Wasserführung, 4...Hochwasser Stufe 1, 5...Hochwasser Stufe 2, 6...Hochwasser Stufe 3, 9...keine Daten;
// 2. digit: 0...gleichbleibend, 1...steigend, 2...sinkend, 3...normal;
// 3. digit: 0...normal, 1... older than 24 hours

// Helper function to get color
function getColor(gesamtcode) {
    if (gesamtcode == null) {
        return '#eff4f7';
    }

    let firstDigit = parseInt(gesamtcode.toString()[0]);
    switch(firstDigit) {
        case 1: return '#3bacbe'; // Niederwasser
        case 2: return '#4e8fcc'; // Mittelwasser
        case 3: return '#003d84'; // erhöhte Wasserführung
        case 4: return '#ffd400'; // Hochwasser Stufe 1
        case 5: return '#f59c00'; // Hochwasser Stufe 2
        case 6: return '#e6320f'; // Hochwasser Stufe 3
        default: return '#eff4f7'; // no data
    }
}

function getTrendText(gesamtcode) {
    if (gesamtcode == null) return 'Unknown';
    
    let secondDigit = parseInt(gesamtcode.toString()[1]);
    switch(secondDigit) {
        case 1: return 'Rising';
        case 2: return 'Falling';
        case 0: return 'Steady';
        case 3: return 'Normal';
        default: return 'Unknown';
    }
}


