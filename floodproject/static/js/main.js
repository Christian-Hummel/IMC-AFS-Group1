
// This script is responsible for fetching data from the backend and displaying it on the map.
// It also handles user interactions, such as toggling the visibility of data layers.
// To see the console output, open the browser's developer tools (F12) and go to the console tab.

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM is fully loaded");

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

    // ... more cluster groups to be added for other data types (HQ100?,..)



    // Fetch the water level data from the backend and add it to the map
    fetchWaterLevelData(waterLevelCluster, autmap);

    // Fetch and display report data
    fetchReportData(reportCluster);

    // console.log("reportCluster", reportCluster)



    // ... more to be added (HQ100, ...)



    // Add event listener for the checkbox to toggle water level layer visibility
    //setupCheckboxToggle(waterLevelCluster, autmap);

    // Add event listeners for toggling layers
    setupCheckboxToggle('toggleWaterLevels', waterLevelCluster, autmap);
    setupCheckboxToggle('toggleReports', reportCluster, autmap);


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

    console.log("Map initialized");

    return map;
}


function fetchWaterLevelData(waterLevelCluster, autmap) {
    fetch('/water-levels/')
        .then(response => response.json())
        .then(data => {
            console.log("Water level data fetched:", data);



            // Create GeoJSON layer and add markers to the cluster
            L.geoJSON(data, {
                pointToLayer: function (feature, latlng) {
                    // Parse the lon and lat from the feature properties
                    let lon = parseFloat(feature.properties.lon.replace(",", "."));
                    let lat = parseFloat(feature.properties.lat.replace(",", "."));

                    if (!isNaN(lon) && !isNaN(lat)) { // Check if coordinates are valid
                        return L.marker([lat, lon]); // Use the parsed coordinates
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